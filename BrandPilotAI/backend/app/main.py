"""BrandPilot AI v2 — demonstrable, auditable brand governance workflow."""
import io
import json
import hashlib
import zipfile
import os
import re
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from collections import Counter

from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel as PydanticBaseModel, ConfigDict, Field

class BaseModel(PydanticBaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .ai import model_findings, get_openrouter_model, is_configured
from .db import Base, SessionLocal, engine, get_db
from .models import AuditEvent, Brand, Finding, Guideline, Submission, SubmissionVersion, AnalysisRun, PolicyEvent, utc_now
from .rules import inspect_text
from .seed import seed_database
from . import auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    if auth.private_mode():
        auth.secret()
        if not auth.accounts():
            raise RuntimeError('Private mode requires configured accounts')
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_database(db)
    yield


app = FastAPI(title='BrandPilot AI', version='3.0.0',
              description='Source-backed, human-controlled brand reviews. Demo personas are not production authentication.',
              lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in os.getenv('ALLOWED_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',') if x.strip()],
                   allow_credentials=False, allow_methods=['GET', 'POST', 'PATCH'], allow_headers=['*'])


@dataclass
class DemoContext:
    session_id: str
    role: str
    actor: str


def demo_context(x_demo_session: str = Header(default=''),
                 x_demo_role: str = Header(default='creator'),
                 x_demo_actor: str = Header(default='Demo Creator'),
                 authorization: str = Header(default='')) -> DemoContext:
    """Public demo selector, NOT secure identity verification or production RBAC."""
    if auth.private_mode():
        actor, role = auth.identity(authorization)
        return DemoContext(session_id='private-workspace', role=role, actor=actor)
    session_id = x_demo_session.strip()
    if not re.fullmatch(r'[a-zA-Z0-9-]{8,90}', session_id):
        raise HTTPException(400, 'Invalid demo session identifier')
    if x_demo_role not in ('creator', 'reviewer', 'manager'):
        raise HTTPException(400, 'Demo role must be creator or reviewer')
    actor = x_demo_actor.strip()[:90] or ('Demo Reviewer' if x_demo_role == 'reviewer' else 'Demo Creator')
    return DemoContext(session_id=session_id, role=x_demo_role, actor=actor)


def require_role(ctx: DemoContext, expected: str):
    if ctx.role != expected and not (expected == 'reviewer' and ctx.role == 'manager'):
        raise HTTPException(403, f'This action requires the {expected} demo persona')


def get_brand(db: Session):
    brand = db.query(Brand).filter_by(slug='lumaleaf').first()
    if not brand:
        brand = seed_database(db)
    return brand


def scoped_guidelines(db: Session, ctx: DemoContext):
    brand = get_brand(db)
    return db.query(Guideline).filter(Guideline.brand_id == brand.id).filter(
        or_(Guideline.session_id.is_(None), Guideline.session_id == ctx.session_id)
    ).order_by(Guideline.id).all()


def scoped_submission(db: Session, ctx: DemoContext, submission_id: int):
    item = db.query(Submission).filter_by(id=submission_id, session_id=ctx.session_id).with_for_update().first()
    if item and auth.private_mode() and ctx.role == "creator" and item.creator != ctx.actor:
        raise HTTPException(404, "Draft not found")
    if not item:
        raise HTTPException(404, 'Draft not found in this demo session')
    return item


def version_for(db: Session, item: Submission):
    version = db.query(SubmissionVersion).filter_by(
        submission_id=item.id, revision=item.revision).first()
    if not version:
        raise HTTPException(500, 'Current content revision is missing')
    return version


def iso(dt):
    if dt and dt.tzinfo is None:
        from datetime import timezone
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat() if dt else None


def serialize_guideline(g: Guideline):
    return dict(id=g.id, code=g.code, kind=g.kind, category=g.category,
                title=g.title, body=g.body, trigger=g.trigger, suggestion=g.suggestion,
                linked_fact_code=g.linked_fact_code, severity=g.severity,
                active=g.active, is_custom=g.session_id is not None)


def serialize_finding(f: Finding):
    return dict(id=f.id, revision=f.revision, rule_code=f.rule_code,
                issue_type=f.issue_type, severity=f.severity, excerpt=f.excerpt,
                explanation=f.explanation, suggestion=f.suggestion,
                source_code=f.source_code, source_title=f.source_title,
                source_excerpt=f.source_excerpt, source_version=hashlib.sha256(f.source_excerpt.encode()).hexdigest()[:12], evidence_status=f.evidence_status, origin=f.origin)


def serialize_submission(db: Session, item: Submission, detailed=True):
    latest = version_for(db, item)
    findings = db.query(Finding).filter_by(submission_id=item.id, revision=item.revision).order_by(Finding.id).all()
    summary = dict(id=item.id, title=item.title, channel=item.channel,
                   creator=item.creator, status=item.status, revision=item.revision,
                   last_analyzed_revision=item.last_analyzed_revision,
                   analysis_mode=item.analysis_mode, ai_status=item.ai_status,
                   content=latest.content, finding_count=len(findings),
                   high_risk_count=sum(f.severity in ('high', 'critical') for f in findings),
                   created_at=iso(item.created_at), updated_at=iso(item.updated_at))
    if detailed:
        versions = db.query(SubmissionVersion).filter_by(submission_id=item.id).order_by(SubmissionVersion.revision.desc()).all()
        events = db.query(AuditEvent).filter_by(submission_id=item.id).order_by(AuditEvent.id.desc()).all()
        summary['analysis_history'] = [dict(id=r.id, revision=r.revision, created_at=iso(r.created_at), **json.loads(r.snapshot)) for r in db.query(AnalysisRun).filter_by(submission_id=item.id).order_by(AnalysisRun.id.desc()).all()]
        summary['findings'] = [serialize_finding(f) for f in findings]
        summary['versions'] = [dict(revision=v.revision, content=v.content,
                                    actor=v.actor, created_at=iso(v.created_at)) for v in versions]
        summary['audit_events'] = [dict(id=e.id, revision=e.revision, actor=e.actor, role=e.role,
                                        action=e.action, note=e.note, created_at=iso(e.created_at)) for e in events]
    return summary


def audit(db, item, ctx, action, note=''):
    db.add(AuditEvent(submission_id=item.id, revision=item.revision,
                      actor=ctx.actor, role=ctx.role, action=action, note=note[:1000]))


class SubmissionIn(BaseModel):
    title: str = Field(min_length=3, max_length=130)
    channel: str = Field(pattern=r'^(social|advertisement|email|document)$')
    content: str = Field(min_length=8, max_length=10000)


class RevisionIn(BaseModel):
    content: str = Field(min_length=8, max_length=10000)


class DecisionIn(BaseModel):
    action: str = Field(pattern=r'^(approve|request_changes)$')
    comment: str = Field(default='', max_length=1000)
    override_high_risk: bool = False


class GuidelineIn(BaseModel):
    kind: str = Field(pattern=r'^(fact|rule)$')
    category: str = Field(default='terminology', max_length=35)
    title: str = Field(min_length=3, max_length=130)
    body: str = Field(min_length=8, max_length=1500)
    trigger: str | None = Field(default=None, max_length=180)
    suggestion: str | None = Field(default=None, max_length=300)
    severity: str = Field(default='medium', pattern=r'^(critical|high|medium|low|info)$')


class GuidelineChange(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=130)
    body: str | None = Field(default=None, min_length=8, max_length=1500)
    trigger: str | None = Field(default=None, max_length=180)
    suggestion: str | None = Field(default=None, max_length=300)
    active: bool | None = None


@app.get('/api/health')
def health():
    return {'status': 'ok', 'version': '3.0.0', 'demo_mode': not auth.private_mode()}


@app.get('/api/config')
def config():
    return {'app': 'BrandPilot AI', 'brand': 'LumaLeaf', 'demo_mode': not auth.private_mode(), 'auth_required': auth.private_mode(),
            'ai_configured': is_configured(),
            'ai_provider': 'OpenRouter',
            'ai_model': get_openrouter_model(),
            'ai_disclosure': 'OpenRouter is opt-in per review; marketing text is sent to a third-party model if enabled. Rules always run locally. Missing key or provider error = labelled rules-only results.',
            'accepted_formats': ['text', 'pdf', 'docx'],
            'security_note': 'Public demo personas are selectable and are not authenticated organisational identities.'}


@app.get('/api/brands')
def brands(db: Session = Depends(get_db)):
    brand = get_brand(db)
    return [{'id': brand.id, 'name': brand.name, 'slug': brand.slug, 'description': brand.description}]


@app.get('/api/guidelines')
def guidelines(ctx: DemoContext = Depends(demo_context), db: Session = Depends(get_db)):
    return [serialize_guideline(g) for g in scoped_guidelines(db, ctx)]


@app.post('/api/guidelines', status_code=201)
def add_guideline(data: GuidelineIn, ctx: DemoContext = Depends(demo_context),
                  db: Session = Depends(get_db)):
    require_policy_role(ctx)
    if data.kind == 'rule' and not (data.trigger or '').strip():
        raise HTTPException(422, 'A custom checking rule needs an exact trigger phrase')
    brand = get_brand(db)
    guide = Guideline(brand_id=brand.id, session_id=ctx.session_id,
                      code='CUSTOM-' + uuid.uuid4().hex[:10].upper(),
                      kind=data.kind, category=data.category,
                      title=data.title.strip(), body=data.body.strip(),
                      trigger=data.trigger.strip() if data.trigger else None,
                      suggestion=data.suggestion.strip() if data.suggestion else None,
                      severity=data.severity, active=True)
    db.add(guide)
    db.flush()
    record_policy(db, ctx, guide)
    db.commit()
    db.refresh(guide)
    return serialize_guideline(guide)


@app.patch('/api/guidelines/{guideline_id}')
def edit_guideline(guideline_id: int, data: GuidelineChange,
                   ctx: DemoContext = Depends(demo_context), db: Session = Depends(get_db)):
    require_policy_role(ctx)
    guide = db.query(Guideline).filter_by(id=guideline_id, session_id=ctx.session_id).first()
    if not guide:
        raise HTTPException(404, 'Only your custom demo policies are editable')
    for key, value in data.model_dump(exclude_unset=True).items():
        if value is None and key in ('title', 'body', 'active'):
            raise HTTPException(422, f'{key} cannot be null')
        setattr(guide, key, value)
    if guide.kind == 'rule' and not (guide.trigger or '').strip():
        raise HTTPException(422, 'Checking rules require a trigger phrase')
    record_policy(db, ctx, guide)
    db.commit()
    db.refresh(guide)
    return serialize_guideline(guide)


@app.get('/api/submissions')
def list_submissions(ctx: DemoContext = Depends(demo_context), db: Session = Depends(get_db)):
    items = db.query(Submission).filter_by(session_id=ctx.session_id).order_by(Submission.updated_at.desc(), Submission.id.desc()).all()
    return [serialize_submission(db, s, detailed=False) for s in items if not auth.private_mode() or ctx.role != "creator" or s.creator == ctx.actor]


@app.post('/api/submissions', status_code=201)
def create_submission(data: SubmissionIn, ctx: DemoContext = Depends(demo_context),
                      db: Session = Depends(get_db)):
    require_role(ctx, 'creator')
    brand = get_brand(db)
    item = Submission(brand_id=brand.id, session_id=ctx.session_id, creator=ctx.actor,
                      title=data.title.strip(), channel=data.channel, status='draft', revision=1)
    db.add(item)
    db.flush()
    db.add(SubmissionVersion(submission_id=item.id, revision=1, content=data.content, actor=ctx.actor))
    audit(db, item, ctx, 'created', 'New draft created')
    db.commit()
    return serialize_submission(db, item)


@app.get('/api/submissions/{submission_id}')
def get_submission(submission_id: int, ctx: DemoContext = Depends(demo_context),
                   db: Session = Depends(get_db)):
    return serialize_submission(db, scoped_submission(db, ctx, submission_id))


@app.patch('/api/submissions/{submission_id}')
def revise_submission(submission_id: int, data: RevisionIn,
                      ctx: DemoContext = Depends(demo_context), db: Session = Depends(get_db)):
    require_role(ctx, 'creator')
    item = scoped_submission(db, ctx, submission_id)
    if item.status not in ('draft', 'reviewed', 'changes_requested'):
        raise HTTPException(409, 'Only an editable draft can be revised; ask the reviewer for changes first')
    if version_for(db, item).content == data.content:
        raise HTTPException(409, 'The revised content is identical to the current version')
    item.revision += 1
    item.status = 'draft'
    item.last_analyzed_revision = None
    item.analysis_mode = 'not_run'
    item.ai_status = 'not_run'
    item.updated_at = utc_now()
    db.add(SubmissionVersion(submission_id=item.id, revision=item.revision,
                             content=data.content, actor=ctx.actor))
    audit(db, item, ctx, 'revised', 'New content version; previous findings require a new review')
    db.commit()
    return serialize_submission(db, item)


@app.post('/api/submissions/{submission_id}/analyze')
def analyze_submission(submission_id: int, use_ai: bool = False, ctx: DemoContext = Depends(demo_context),
                       db: Session = Depends(get_db)):
    require_role(ctx, 'creator')
    item = scoped_submission(db, ctx, submission_id)
    if item.status not in ('draft', 'reviewed', 'changes_requested'):
        raise HTTPException(409, 'This submission is currently locked for human review or approval')
    text = version_for(db, item).content
    policies = scoped_guidelines(db, ctx)
    checked = inspect_text(text, policies)
    ai_checks, ai_status = model_findings(text, policies, checked, session_id=ctx.session_id, use_ai=use_ai)
    checked += ai_checks
    db.add(AnalysisRun(submission_id=item.id, revision=item.revision, policy_digest=policy_digest(policies), snapshot=json.dumps({'findings': checked, 'ai_status': ai_status, 'sources': [serialize_guideline(g) for g in policies if g.active]})))
    db.query(Finding).filter_by(submission_id=item.id, revision=item.revision).delete()
    for f in checked:
        db.add(Finding(submission_id=item.id, revision=item.revision, **f))
    item.status = 'reviewed'
    item.last_analyzed_revision = item.revision
    item.ai_status = ai_status
    item.analysis_mode = 'rules + OpenRouter' if ai_status == 'completed' else 'rules only'
    item.updated_at = utc_now()
    audit(db, item, ctx, 'analyzed', f'{len(checked)} findings; model status: {ai_status}')
    db.commit()
    return serialize_submission(db, item)


@app.post('/api/submissions/{submission_id}/request-review')
def request_review(submission_id: int, ctx: DemoContext = Depends(demo_context),
                   db: Session = Depends(get_db)):
    require_role(ctx, 'creator')
    item = scoped_submission(db, ctx, submission_id)
    if item.status != 'reviewed' or item.last_analyzed_revision != item.revision:
        raise HTTPException(409, 'Analyze the current content revision before requesting approval')
    require_current_policies(db, ctx, item)
    item.status = 'pending_review'
    item.updated_at = utc_now()
    audit(db, item, ctx, 'sent_for_review', 'Creator requested a human decision')
    db.commit()
    return serialize_submission(db, item)


@app.post('/api/submissions/{submission_id}/decision')
def decide(submission_id: int, data: DecisionIn,
           ctx: DemoContext = Depends(demo_context), db: Session = Depends(get_db)):
    require_role(ctx, 'reviewer')
    item = scoped_submission(db, ctx, submission_id)
    if item.status != 'pending_review' or item.last_analyzed_revision != item.revision:
        raise HTTPException(409, 'The submission must be pending review with current analysis')
    if data.action == 'approve':
        require_current_policies(db, ctx, item)
        if auth.private_mode() and ctx.actor == item.creator:
            raise HTTPException(403, 'You cannot approve your own submission')
    comment = data.comment.strip()
    if data.action == 'request_changes':
        if len(comment) < 3:
            raise HTTPException(422, 'Explain what the creator should revise')
        item.status = 'changes_requested'
        action = 'changes_requested'
    else:
        high = db.query(Finding).filter_by(submission_id=item.id, revision=item.revision).filter(
            Finding.severity.in_(['critical', 'high'])).count()
        if high and (not data.override_high_risk or len(comment) < 10):
            raise HTTPException(409, 'High-risk findings require explicit override and a justification of at least 10 characters')
        item.status = 'approved'
        action = 'approved_with_override' if high else 'approved'
    item.updated_at = utc_now()
    audit(db, item, ctx, action, comment or 'Reviewed and approved')
    db.commit()
    return serialize_submission(db, item)


@app.get('/api/stats')
def stats(ctx: DemoContext = Depends(demo_context), db: Session = Depends(get_db)):
    items = db.query(Submission).filter_by(session_id=ctx.session_id).all()
    if auth.private_mode() and ctx.role == 'creator':
        items = [s for s in items if s.creator == ctx.actor]
    by_status = Counter(s.status for s in items)
    active_findings = []
    for s in items:
        active_findings.extend(db.query(Finding).filter_by(submission_id=s.id, revision=s.revision).all())
    return {'total': len(items), 'approved': by_status['approved'],
            'pending_review': by_status['pending_review'],
            'changes_requested': by_status['changes_requested'],
            'reviewed': by_status['reviewed'],
            'findings': len(active_findings),
            'needs_evidence': sum(f.evidence_status == 'needs_evidence' for f in active_findings),
            'by_severity': dict(Counter(f.severity for f in active_findings)),
            'repeat_rules': [{'code': k, 'count': v} for k, v in Counter(f.rule_code for f in active_findings).most_common(5)]}


@app.post('/api/extract')
async def extract_text(file: UploadFile = File(...), ctx: DemoContext = Depends(demo_context)):
    require_role(ctx, 'creator')
    name = (file.filename or '').lower()
    suffix = Path(name).suffix
    if suffix not in ('.pdf', '.docx', '.txt'):
        raise HTTPException(415, 'Supported files: .pdf, .docx, .txt')
    raw = await file.read(5_000_001)
    if len(raw) > 5_000_000:
        raise HTTPException(413, 'Maximum upload size is 5 MB')
    try:
        if suffix == '.txt':
            text = raw.decode('utf-8-sig')
        elif suffix == '.pdf':
            import pymupdf
            with pymupdf.open(stream=raw, filetype='pdf') as document:
                if document.page_count > 30:
                    raise HTTPException(413, 'Maximum 30 PDF pages per document')
                text = '\n'.join(page.get_text(sort=True) for page in document)
        else:
            from docx import Document
            with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                if sum(i.file_size for i in archive.infolist()) > 20_000_000 or len(archive.infolist()) > 1000:
                    raise HTTPException(413, 'Expanded document exceeds safe extraction limits')
            document = Document(io.BytesIO(raw))
            text = '\n'.join(p.text for p in document.paragraphs)
            for table in document.tables:
                text += '\n' + '\n'.join(' | '.join(c.text for c in row.cells) for row in table.rows)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(422, f'Could not extract readable text from this {suffix} document') from exc
    if not text.strip():
        raise HTTPException(422, 'No selectable text found. Scanned images/OCR are not supported.')
    return {'filename': file.filename, 'format': suffix[1:],
            'text': text[:10000], 'truncated': len(text) > 10000,
            'note': 'Only extracted text is used; the raw uploaded file is not stored.'}



def require_policy_role(ctx):
    if auth.private_mode():
        require_role(ctx, 'manager')
    elif ctx.role not in ('creator', 'manager'):
        raise HTTPException(403, 'Choose Manager to maintain sources')


def policy_digest(policies):
    data = [serialize_guideline(g) for g in policies if g.active]
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def require_current_policies(db, ctx, item):
    latest = db.query(AnalysisRun).filter_by(submission_id=item.id, revision=item.revision).order_by(AnalysisRun.id.desc()).first()
    if not latest or latest.policy_digest != policy_digest(scoped_guidelines(db, ctx)):
        raise HTTPException(409, 'Brand sources changed. Request changes if pending, then inspect again before approval.')


def record_policy(db, ctx, guide):
    db.add(PolicyEvent(session_id=ctx.session_id, code=guide.code, actor=ctx.actor,
                       snapshot=json.dumps(serialize_guideline(guide))))


class LoginIn(BaseModel):
    username: str = Field(min_length=1, max_length=90)
    password: str = Field(min_length=1, max_length=200)


@app.post('/api/auth/login')
def login(data: LoginIn):
    if not auth.private_mode():
        raise HTTPException(400, 'This deployment is a public demo')
    return auth.login(data.username, data.password)


class CommentIn(BaseModel):
    comment: str = Field(min_length=3, max_length=1000)


@app.post('/api/submissions/{submission_id}/comments')
def comment(submission_id: int, data: CommentIn, ctx: DemoContext = Depends(demo_context), db: Session = Depends(get_db)):
    item = scoped_submission(db, ctx, submission_id)
    audit(db, item, ctx, 'commented', data.comment)
    db.commit()
    return serialize_submission(db, item)


@app.get('/api/policy-history')
def policy_history(ctx: DemoContext = Depends(demo_context), db: Session = Depends(get_db)):
    return [dict(code=e.code, actor=e.actor, created_at=iso(e.created_at), source=json.loads(e.snapshot))
            for e in db.query(PolicyEvent).filter_by(session_id=ctx.session_id).order_by(PolicyEvent.id.desc()).all()]


@app.middleware('http')
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'same-origin'
    response.headers['X-Frame-Options'] = 'DENY'
    if request.url.path.startswith('/api/'):
        response.headers['Cache-Control'] = 'no-store'
    return response


# In production, a single Render/Docker web service can serve the Vite build and /api.
static_dir = Path(__file__).resolve().parents[2] / 'frontend' / 'dist'
if static_dir.is_dir():
    app.mount('/', StaticFiles(directory=str(static_dir), html=True), name='web')
