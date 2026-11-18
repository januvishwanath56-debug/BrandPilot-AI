import { useEffect, useMemo, useState } from 'react';
import {
  Activity, AlertCircle, AlertTriangle, ArrowDownToLine, ArrowRight, ArrowUpRight,
  BadgeCheck, BookOpen, Check, CheckCircle2, ChevronRight, CircleDot,
  ClipboardCheck, Clock3, Copy, FileCheck2, FileSearch2, FileText, FlaskConical,
  FolderOpen, History, Layers3, LockKeyhole, Menu, PenLine, Plus,
  RotateCcw, Search, Send, Shield, ShieldCheck, Sparkles, Upload,
  UserRoundCheck, WandSparkles, X, XCircle,
} from 'lucide-react';

const SAMPLE_BAD = 'Our LumaLeaf bottle is 100% plastic-free, best in the world, and guaranteed to save the planet. Click here to buy yours today!';
const SAMPLE_GOOD = 'Meet LumaLeaf: a reusable 750 mL bottle made with 60% post-consumer recycled plastic. Includes a 12-month limited manufacturing warranty. Explore our collection today.';
const API_ROOT = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');
const SESSION_KEY = 'brandpilot_demo_session_v1';
function demoSession() {
  try {
    let id = localStorage.getItem(SESSION_KEY);
    if (!id) {
      id = globalThis.crypto?.randomUUID?.() || `demo-${Math.random().toString(36).slice(2)}-site`;
      localStorage.setItem(SESSION_KEY, id);
    }
    return id;
  } catch { return globalThis.crypto.randomUUID(); }
}
const SESSION_ID = demoSession();
const ITEMS = [
  { id: 'desk', name: 'Review desk', icon: FileSearch2, number: '01' },
  { id: 'queue', name: 'Approval gate', icon: ClipboardCheck, number: '02' },
  { id: 'library', name: 'Brand library', icon: BookOpen, number: '03' },
  { id: 'history', name: 'Decision trail', icon: History, number: '04' },
];
const STATUS = {
  draft: 'Draft', reviewed: 'Analyzed', pending_review: 'Pending approval',
  changes_requested: 'Changes requested', approved: 'Approved',
};
const DATE = v => v ? new Date(v).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' }) : '—';
const HUMAN = v => ({ claims: 'Evidence & claims', claim_conflict: 'Factual conflict', terminology: 'Brand language', accessibility: 'Accessibility', tone: 'Tone of voice', approved_fact: 'Approved fact' }[v] || v || 'Policy');

function Tag({ tone = 'quiet', children }) { return <span className={`tag tag-${tone}`}>{children}</span>; }
function StatusTag({ status }) {
  const tones = { approved: 'green', pending_review: 'blue', changes_requested: 'red', reviewed: 'amber', draft: 'quiet' };
  return <Tag tone={tones[status] || 'quiet'}>{STATUS[status] || status}</Tag>;
}
function BlockLabel({ children, end }) {
  return <div className="section-label"><span>{children}</span>{end && <span className="section-label-end">{end}</span>}</div>;
}
function HighlightedCopy({ copy, findings }) {
  const ranges = [];
  const low = copy.toLowerCase();
  for (const finding of findings) {
    const quote = finding.excerpt?.toLowerCase();
    if (!quote) continue;
    let from = 0;
    while (from < low.length) {
      const start = low.indexOf(quote, from);
      if (start === -1) break;
      const end = start + quote.length;
      if (!ranges.some(r => start < r.end && end > r.start)) ranges.push({ start, end, finding });
      from = end;
    }
  }
  ranges.sort((a, b) => a.start - b.start);
  let cursor = 0;
  const pieces = [];
  for (const part of ranges) {
    pieces.push(<span key={`text-${cursor}`}>{copy.slice(cursor, part.start)}</span>);
    pieces.push(<mark className={`highlight ${part.finding.evidence_status === 'contradicted' ? 'highlight-critical' : ''}`} key={`mark-${part.start}`} title={`${part.finding.source_code}: ${part.finding.explanation}`}>{copy.slice(part.start, part.end)}</mark>);
    cursor = part.end;
  }
  pieces.push(<span key="tail">{copy.slice(cursor)}</span>);
  return <div className="marked-copy">{pieces}</div>;
}
function ProgressRail({ current }) {
  const status = current?.status;
  const stage = !status || status === 'draft' ? 0 : status === 'reviewed' || status === 'changes_requested' ? 1 : status === 'pending_review' ? 2 : 3;
  return <div className="progress-rail">
    {['DRAFT','INSPECTED','HUMAN REVIEW','APPROVED'].map((step, i) => <div key={step} className={`rail-step ${i <= stage ? 'on' : ''} ${i === stage ? 'here' : ''}`}><span className="rail-dot">{i < stage ? <Check size={10}/> : String(i + 1).padStart(2,'0')}</span><span>{step}</span></div>)}
  </div>;
}
function SummaryScore({ current, dirty }) {
  const issueCount = current?.finding_count || 0;
  const highCount = current?.high_risk_count || 0;
  const analyzed = current && current.last_analyzed_revision === current.revision && !dirty;
  if(current?.status === 'approved') return <div className="gate-state clear"><div className="gate-art"><BadgeCheck size={32}/></div><span className="micro-label">RELEASE GATE / APPROVED</span><h3>Signed off by a human.</h3><p>Revision {current.revision} is locked. The recorded decision and source snapshots remain in the decision trail.</p></div>;
  if(current?.status === 'pending_review') return <div className="gate-state neutral"><div className="gate-art"><Clock3 size={32}/></div><span className="micro-label">RELEASE GATE / PENDING</span><h3>Waiting for human judgment.</h3><p>The submitted revision is locked until a reviewer records a decision.</p></div>;
  if (!analyzed) return <div className="gate-state neutral"><div className="gate-art"><FileSearch2 size={32}/></div><span className="micro-label">RELEASE GATE / WAITING</span><h3>Nothing is cleared until it's checked.</h3><p>Inspect your copy against LumaLeaf’s approved facts and brand policies.</p></div>;
  return <div className={`gate-state ${highCount ? 'blocked' : 'clear'}`}><div className="gate-art">{highCount ? <AlertTriangle size={32}/> : <ShieldCheck size={32}/>}</div><span className="micro-label">RELEASE GATE / {highCount ? 'ATTENTION REQUIRED' : 'READY FOR REVIEW'}</span><h3>{highCount ? `${highCount} high-risk ${highCount === 1 ? 'issue' : 'issues'}` : issueCount ? 'Review the suggestions.' : 'No known issues found.'}</h3><p>{highCount ? 'Revise the copy or document a reviewer override. This is not an automatic rejection.' : 'Automated review is advisory. Only a human can approve the final content.'}</p></div>;
}

export default function App() {
  const [page, setPage] = useState('desk');
  const [identity, setIdentity] = useState(null);
  const [loginForm, setLoginForm] = useState({username:'', password:''});
  const [commentText, setCommentText] = useState('');
  const [role, setRole] = useState('creator');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [drafts, setDrafts] = useState([]);
  const [guidelines, setGuidelines] = useState([]);
  const [stats, setStats] = useState(null);
  const [config, setConfig] = useState({});
  const [current, setCurrent] = useState(null);
  const [title, setTitle] = useState('Autumn product launch');
  const [channel, setChannel] = useState('social');
  const [content, setContent] = useState(SAMPLE_BAD);
  const [useAI, setUseAI] = useState(false);
  const [busy, setBusy] = useState('');
  const [alert, setAlert] = useState(null);
  const [decisionNote, setDecisionNote] = useState('');
  const [override, setOverride] = useState(false);
  const [showAdd, setShowAdd] = useState(false);
  const [ruleFilter, setRuleFilter] = useState('all');
  const [search, setSearch] = useState('');
  const [ruleForm, setRuleForm] = useState({ kind:'rule', category:'claims', title:'', body:'', trigger:'', suggestion:'', severity:'medium' });
  const notify = (message, tone = 'good') => setAlert({ message, tone });

  async function api(path, { method = 'GET', body = null, asReviewer = false } = {}) {
    const headers = {
      'X-Demo-Session': SESSION_ID,
      'X-Demo-Role': asReviewer ? 'reviewer' : role,
      'X-Demo-Actor': asReviewer || role === 'reviewer' ? 'Demo Reviewer' : role === 'manager' ? 'Demo Manager' : 'Demo Creator',
    };
    if (identity?.token) headers.Authorization = `Bearer ${identity.token}`;
    if (body !== null && !(body instanceof FormData)) headers['Content-Type'] = 'application/json';
    let response;
    try {
      response = await fetch(`${API_ROOT}${path}`, { method, headers, body: body instanceof FormData ? body : body == null ? undefined : JSON.stringify(body) });
    } catch { throw new Error('The review service is unreachable. Start FastAPI or check that your deployment is awake.'); }
    if (!response.ok) {
      const details = await response.json().catch(() => null);
      throw new Error(typeof details?.detail === 'string' ? details.detail : `Request failed (${response.status}).`);
    }
    return response.json();
  }
  async function refresh() {
    try {
      const c = await api('/api/config');
      setConfig(c);
      if(c.auth_required && !identity) return c;
      const [d, g, s] = await Promise.all([api('/api/submissions'), api('/api/guidelines'), api('/api/stats')]);
      setDrafts(d); setGuidelines(g); setStats(s); setConfig(c);
      return c;
    } catch (e) { notify(e.message, 'bad'); return null; }
  }
  useEffect(() => { refresh(); }, [identity]);
  useEffect(() => {
    if(!showAdd) return;
    const previous = document.activeElement;
    const dialog = document.querySelector('.modal');
    const focusable = () => [...dialog.querySelectorAll('button,input,select,textarea')].filter(e=>!e.disabled);
    focusable()[0]?.focus();
    const key = e => {
      if(e.key === 'Escape') setShowAdd(false);
      if(e.key === 'Tab') { const list=focusable(); const index=list.indexOf(document.activeElement); if(e.shiftKey && index<=0) {e.preventDefault();list.at(-1)?.focus();} else if(!e.shiftKey && index===list.length-1) {e.preventDefault();list[0]?.focus();} }
    };
    document.addEventListener('keydown', key);
    return () => {document.removeEventListener('keydown',key);previous?.focus();};
  }, [showAdd]);
  const dirty = Boolean(current) && (content !== current.content || title !== current.title || channel !== current.channel);
  const analyzed = Boolean(current) && current.last_analyzed_revision === current.revision && current.status !== 'draft' && !dirty;
  const canSubmit = Boolean(current) && role === 'creator' && current.status === 'reviewed' && analyzed;
  const pending = drafts.filter(d => d.status === 'pending_review');
  const issueCount = current?.finding_count || 0;
  const highCount = current?.high_risk_count || 0;
  const activeGuides = guidelines.filter(g => g.active).length;
  const visibleGuides = useMemo(() => guidelines.filter(g => (ruleFilter === 'all' || g.kind === ruleFilter) && `${g.code} ${g.title} ${g.body}`.toLowerCase().includes(search.toLowerCase())), [guidelines, ruleFilter, search]);
  const activePage = ITEMS.find(p => p.id === page) || ITEMS[0];

  function choosePage(next) { setPage(next); setSidebarOpen(false); }
  function changeRole(next) {
    if(config.auth_required) return;
    setRole(next); setDecisionNote(''); setOverride(false);
    choosePage(next === 'reviewer' ? 'queue' : next === 'manager' ? 'library' : 'desk');
    notify(`Viewing as ${next.charAt(0).toUpperCase()+next.slice(1)}. Demo personas are not authenticated accounts.`, 'info');
  }
  function loadSample(clean = false) {
    setCurrent(null);
    setTitle(clean ? 'Everyday essentials campaign' : 'Autumn product launch');
    setChannel('social'); setContent(clean ? SAMPLE_GOOD : SAMPLE_BAD); choosePage('desk');
    notify(clean ? 'Approved-facts sample loaded. Run a check to verify it.' : 'Risky example loaded. Inspect the claims to see evidence-backed findings.', 'info');
  }
  async function loadDraft(id, destination) {
    setBusy('load');
    try {
      const d = await api(`/api/submissions/${id}`);
      setCurrent(d); setTitle(d.title); setChannel(d.channel); setContent(d.content);
      setDecisionNote(''); setOverride(false);
      if (destination) choosePage(destination);
    } catch (e) { notify(e.message, 'bad'); }
    finally { setBusy(''); }
  }
  async function analyze(fromSample = null) {
    if (role !== 'creator') return notify('Switch to the Creator persona to inspect content.', 'bad');
    const source = fromSample || { title, channel, content };
    if (source.title.trim().length < 3 || source.content.trim().length < 8) return notify('Enter a title and at least eight characters of copy.', 'bad');
    setBusy('analyze');
    try {
      let d = fromSample ? null : current;
      if (!d || source.title !== d.title || source.channel !== d.channel) {
        d = await api('/api/submissions', { method:'POST', body:{ title:source.title.trim(), channel:source.channel, content:source.content }});
      } else if (source.content !== d.content) {
        d = await api(`/api/submissions/${d.id}`, { method:'PATCH', body:{ content:source.content }});
      }
      const checked = await api(`/api/submissions/${d.id}/analyze?use_ai=${Boolean(useAI && config.ai_configured)}`, { method:'POST' });
      setCurrent(checked); setContent(checked.content); setTitle(checked.title); setChannel(checked.channel);
      await refresh(); choosePage('desk');
      notify(`${checked.finding_count} evidence-linked finding${checked.finding_count === 1 ? '' : 's'} recorded for revision ${checked.revision}.`, checked.finding_count ? 'info' : 'good');
    } catch (e) { notify(e.message, 'bad'); }
    finally { setBusy(''); }
  }
  function fix(f) {
    if (role !== 'creator' || !current || current.status === 'pending_review' || current.status === 'approved') return;
    const i = content.toLowerCase().indexOf(f.excerpt.toLowerCase());
    if (i < 0) return notify('This text has changed. Run the review again to refresh suggestions.', 'bad');
    setContent(content.slice(0, i) + f.suggestion + content.slice(i + f.excerpt.length));
    notify('Suggested wording placed in the editor. Inspect and re-run the analysis.', 'info');
  }
  async function submitForReview() {
    if (!canSubmit) return;
    setBusy('submit');
    try {
      setCurrent(await api(`/api/submissions/${current.id}/request-review`, { method:'POST' }));
      await refresh(); notify('Submitted to human review. Switch to Reviewer to decide.');
    } catch (e) { notify(e.message, 'bad'); }
    finally { setBusy(''); }
  }
  async function decision(action) {
    if (!['reviewer','manager'].includes(role) || !current) return;
    setBusy('decide');
    try {
      setCurrent(await api(`/api/submissions/${current.id}/decision`, { method:'POST', body:{ action, comment:decisionNote, override_high_risk:override } }));
      setDecisionNote(''); setOverride(false); await refresh();
      notify(action === 'approve' ? 'The human approval is recorded in the saved decision trail.' : 'Revision requested and saved to the decision trail.');
    } catch (e) { notify(e.message, 'bad'); }
    finally { setBusy(''); }
  }
  async function importFile(file) {
    if (!file) return;
    if (file.size > 5_000_000) return notify('Maximum document size is 5 MB.', 'bad');
    setBusy('import');
    try {
      const form = new FormData(); form.append('file', file);
      const result = await api('/api/extract', { method:'POST', body:form });
      setCurrent(null); setTitle((file.name.replace(/\.[^.]+$/, '') || 'Imported document').slice(0,130));
      setChannel('document'); setContent(result.text); choosePage('desk');
      notify(`Extracted ${result.format.toUpperCase()} text${result.truncated ? ' (truncated to 10,000 characters)' : ''}.`);
    } catch (e) { notify(e.message, 'bad'); }
    finally { setBusy(''); }
  }
  async function addGuideline(e) {
    e.preventDefault(); setBusy('guide');
    try {
      await api('/api/guidelines', { method:'POST', body:{ ...ruleForm,
        trigger:ruleForm.kind === 'fact' ? null : ruleForm.trigger,
        suggestion:ruleForm.kind === 'fact' ? null : ruleForm.suggestion } });
      setShowAdd(false); setRuleForm({ kind:'rule', category:'claims', title:'', body:'', trigger:'', suggestion:'', severity:'medium' });
      await refresh(); if(current) await loadDraft(current.id); notify('Brand guidance added. Future scans will reference the new source.');
    } catch (e) { notify(e.message, 'bad'); }
    finally { setBusy(''); }
  }
  async function toggleGuideline(g) {
    setBusy('guide');
    try {
      await api(`/api/guidelines/${g.id}`, { method:'PATCH', body:{active:!g.active} });
      await refresh(); if(current) await loadDraft(current.id); notify(g.active ? 'Custom rule paused.' : 'Custom rule restored.');
    } catch (e) { notify(e.message, 'bad'); }
    finally { setBusy(''); }
  }
  function exportReport() {
    if (!current || !analyzed) return;
    const data = {
      product:'BrandPilot AI', demo:true, brand:'LumaLeaf',
      exported_at:new Date().toISOString(), submission:current,
      notice:'Advisory analysis of a fictional brand; not a legal or compliance certification.',
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], {type:'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = `brandpilot-review-${current.id}-v${current.revision}.json`;
    a.click(); URL.revokeObjectURL(url);
  }
  async function signIn(e) {
    e.preventDefault();setBusy('login');
    try {const result=await api('/api/auth/login',{method:'POST',body:loginForm});setIdentity(result);setRole(result.role);setLoginForm({username:'',password:''});setAlert(null);}
    catch(e){notify(e.message,'bad');} finally{setBusy('');}
  }
  async function postComment(){
    setBusy('comment');try{setCurrent(await api(`/api/submissions/${current.id}/comments`,{method:'POST',body:{comment:commentText}}));setCommentText('');notify('Comment recorded.');}catch(e){notify(e.message,'bad');}finally{setBusy('');}
  }
  function exportApproved(){
    const url=URL.createObjectURL(new Blob([current.content],{type:'text/plain'}));const a=document.createElement('a');a.href=url;a.download=`approved-${current.id}-v${current.revision}.txt`;a.click();URL.revokeObjectURL(url);
  }
  if(config.auth_required && !identity) return <main className="login-page"><form className="modal" onSubmit={signIn}><BlockLabel>BRANDPILOT / PRIVATE PILOT</BlockLabel><h1>Proof before publish.</h1><p>Sign in with an account provisioned by your workspace owner.</p><label className="field"><span>USERNAME</span><input required autoComplete="username" value={loginForm.username} onChange={e=>setLoginForm({...loginForm,username:e.target.value})}/></label><label className="field"><span>PASSWORD</span><input required type="password" autoComplete="current-password" value={loginForm.password} onChange={e=>setLoginForm({...loginForm,password:e.target.value})}/></label>{alert && <p role="alert">{alert.message}</p>}<button className="button btn-ink" disabled={Boolean(busy)}>Sign in</button></form></main>;
  const originalVersion = current?.versions?.length > 1 ? current.versions.find(v => v.revision === 1) : null;

  return <div className="shell"><a className="skip-link" href="#main-content">Skip to workspace</a>
    <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
      <div className="brand-wrap"><div className="monogram">b<span>•</span></div><div className="brand-word">brandpilot<span className="brand-word-dot">.</span><small>THE CONTENT GOVERNANCE DESK</small></div></div>
      <div className="workspace"><div className="workspace-emblem">L<span>✳</span></div><div><strong>LumaLeaf</strong><small>Fictional brand workspace</small></div><ChevronRight size={14}/></div>
      <div className="nav-heading">THE WORKSPACE <span>2026 / R2</span></div>
      <nav aria-label="Workspace navigation">{ITEMS.map(item => { const Icon = item.icon; return <button aria-label={item.name} aria-current={page === item.id ? "page" : undefined} key={item.id} onClick={() => choosePage(item.id)} className={`nav-link ${page === item.id ? 'active' : ''}`}><Icon size={18}/><span>{item.name}</span><small>{item.id === 'queue' && pending.length ? pending.length : item.number}</small></button>; })}</nav>
      <div className="sidebar-bottom"><div className="sidebar-feature"><div className="sidebar-feature-top"><CircleDot size={15}/> THE BRAND PROMISE</div><p>Every claim has a source. Every decision has a human.</p><div className="sidebar-lines"><span/><span/><span/></div></div><div className="sidebar-credit">CREATED BY <strong>JANU V</strong><br/>CODEZEN INDIA / ROUND 02</div></div>
    </aside>

    <div className="content-shell">
      <header className="topbar"><div className="topbar-left"><button className="mobile-menu" aria-label="Toggle navigation" onClick={() => setSidebarOpen(v=>!v)}><Menu size={21}/></button><span className="topbar-slash">B / P</span><span className="topbar-divider"/> <span>{activePage.name}</span><span className="topbar-muted">/ Governance workspace</span></div><div className="topbar-right"><span className="session-indicator"><span className="signal-dot"/> LIVE SANDBOX</span><div className="role-picker" hidden={config.auth_required}><button onClick={() => changeRole('creator')} className={role === 'creator' ? 'active' : ''}>Creator</button><button onClick={() => changeRole('reviewer')} className={role === 'reviewer' ? 'active' : ''}>Reviewer</button><button onClick={() => changeRole('manager')} className={role === 'manager' ? 'active' : ''}>Manager</button></div>{identity && <button className="text-button" onClick={()=>{setIdentity(null);setCurrent(null);setDrafts([]);}}>Sign out ({identity.actor})</button>}<div className="initials" title="Selectable demo persona—not a real account">{role === 'creator' ? 'CR' : 'RV'}</div></div></header>
      <main className="main" id="main-content">
        <div className="hero">
          <div className="hero-copy"><div className="hero-index">BRAND INTELLIGENCE SYSTEM <span className="hero-sep">◆</span> 2026 EDITION</div><h1>{page === 'desk' ? <>Nothing goes live <em>without proof.</em></> : page === 'queue' ? <>The final word is <em>human.</em></> : page === 'library' ? <>One brand. <em>One source of truth.</em></> : <>Every decision <em>leaves a trail.</em></>}</h1><p>{page === 'desk' ? 'A pre-publication workspace that checks your content against approved facts, shows the evidence, and puts people in control.' : page === 'queue' ? 'Review the source evidence, request a rewrite, or make a documented approval decision.' : page === 'library' ? 'Define the facts and editorial rules the brand reviewer is allowed to trust.' : 'Follow the complete journey of a draft, from its first scan to the final review.'}</p><div className="hero-chips"><span>01 / SOURCE-TRACED</span><span>02 / HUMAN-LED</span><span>03 / AUDITABLE</span></div></div>
          <div className="hero-aside"><div className="hero-aside-top"><span>RELEASE STATUS</span><Shield size={19}/></div><SummaryScore current={current} dirty={dirty}/><div className="hero-foot"><span><span className="hero-foot-dot"/> SYSTEM READY</span><span>INTERNAL DEMO / NOT FOR PRODUCTION</span></div></div>
        </div>
        <div className="demo-line"><FlaskConical size={17}/><span><b>{config.auth_required ? 'Private pilot workspace.' : 'Live product sandbox.'}</b> LumaLeaf is fictional. {config.auth_required ? 'Permissions use your signed-in account.' : 'Selectable personas are not real authentication. Use only fictional, non-sensitive material.'} Findings are advisory, not compliance certification. {config.ai_configured ? 'Optional OpenRouter analysis is available.' : 'The verified rule engine runs without an AI key.'}</span></div>

        <div className="page-heading"><div><BlockLabel end={`MODULE ${activePage.number} / 04`}>PUBLISHING CONTROL</BlockLabel><h2>{page === 'desk' ? 'The review desk' : page === 'queue' ? 'The approval gate' : page === 'library' ? 'The source library' : 'The decision trail'}</h2></div><div className="heading-actions">{page === 'desk' && <><button className="button btn-outline" onClick={() => loadSample(false)}><RotateCcw size={15}/> Load sample</button><button className="button btn-link" onClick={() => analyze({title:'Autumn product launch', channel:'social', content:SAMPLE_BAD})} disabled={Boolean(busy) || role !== 'creator'}><Sparkles size={16}/> One-click demo <ArrowUpRight size={14}/></button></>}{page === 'library' && (role === 'manager' || (!config.auth_required && role === 'creator')) && <button className="button btn-ink" onClick={() => setShowAdd(true)}><Plus size={15}/> Add a source</button>}</div></div>

        {page === 'desk' && <>
          <div className="metric-row"><div className="metric"><div><span>01 — DRAFTS REVIEWED</span><FileText size={15}/></div><strong>{stats?.total ?? '—'}</strong><small>Content records in this session</small></div><div className="metric"><div><span>02 — OPEN APPROVALS</span><Clock3 size={15}/></div><strong>{stats?.pending_review ?? '—'}</strong><small>Awaiting a human decision</small></div><div className="metric"><div><span>03 — APPROVED RELEASES</span><BadgeCheck size={15}/></div><strong>{stats?.approved ?? '—'}</strong><small>Approved in this session</small></div><div className="metric metric-accent"><div><span>04 — KNOWLEDGE SOURCES</span><BookOpen size={15}/></div><strong>{activeGuides}</strong><small>Active rules, facts & policies</small></div></div>
          <div className="desk-grid">
            <section className="module-card editor-card"><div className="card-cap"><div><span className="cap-number">01</span><div><h3>Prepare the copy</h3><p>Write, paste, or import your material.</p></div></div><Tag>{current ? `REVISION ${current.revision}` : 'NEW DRAFT'}</Tag></div>
              <div className="editor-inside"><div className="editor-fields"><label className="field"><span>CAMPAIGN TITLE</span><input disabled={Boolean(current)} value={title} maxLength={130} onChange={e=>setTitle(e.target.value)} placeholder="Campaign name"/></label><label className="field"><span>CHANNEL</span><select disabled={Boolean(current)} value={channel} onChange={e=>setChannel(e.target.value)}><option value="social">Social post</option><option value="advertisement">Advertisement</option><option value="email">Email campaign</option><option value="document">Document</option></select></label></div>
              <label className="field editor-area"><span>SUBMITTED CONTENT <span className="field-end">{content.length.toLocaleString()} / 10,000</span></span><textarea disabled={role !== 'creator' || ['approved','pending_review'].includes(current?.status)} rows={9} maxLength={10000} value={content} onChange={e=>setContent(e.target.value)} spellCheck placeholder="Paste the copy you want to publish..."/></label>
              <div className="editor-options"><span>TRY A CAMPAIGN</span><button onClick={()=>loadSample(false)}>⚑ With violations</button><button onClick={()=>loadSample(true)}>✓ Approved facts</button><label className="file-button"><Upload size={14}/> Import file<input type="file" accept=".pdf,.docx,.txt" onChange={e=>{importFile(e.target.files?.[0]);e.target.value='';}}/></label></div>
              <div className="ai-switch-row"><div className="ai-switch-copy"><Sparkles size={18}/><div><strong>OpenRouter AI advisory</strong><span>{config.ai_configured ? `${config.ai_model || 'Free model'} · sends submitted copy to an external model` : 'Not configured · reliable local rules still work'}</span></div></div><label className="switch" title="AI requests use a shared free quota"><input type="checkbox" checked={useAI && Boolean(config.ai_configured)} aria-label="Enable external OpenRouter analysis" disabled={!config.ai_configured} onChange={e=>setUseAI(e.target.checked)}/><span/></label></div>
              <div className="editor-bottom"><span>{dirty ? <><CircleDot size={14}/> Unsaved changes need a new scan</> : <><ShieldCheck size={14}/> Facts & rules checked locally</>}</span><button className="button btn-ink" disabled={Boolean(busy) || role !== 'creator' || current?.status === 'approved' || current?.status === 'pending_review'} onClick={()=>analyze()}><Sparkles size={17}/>{busy === 'analyze' ? 'Inspecting…' : 'Inspect the copy'} <ArrowRight size={16}/></button></div></div>
            </section>
            <section className="module-card scan-card"><div className="card-cap"><div><span className="cap-number">02</span><div><h3>The evidence report</h3><p>Findings are tied to stored policy sources.</p></div></div>{analyzed && <Tag tone={highCount ? 'red' : issueCount ? 'amber' : 'green'}>{issueCount} {issueCount === 1 ? 'ISSUE' : 'ISSUES'}</Tag>}</div>
              {!analyzed ? <div className="blank-report"><div className="report-paper"><div className="paper-tab">BRAND / SCAN / 001</div><span className="paper-line p-long"/><span className="paper-line p-medium"/><span className="paper-line p-long"/><span className="paper-highlight"/><span className="paper-line p-short"/><span className="paper-stamp"><FileSearch2 size={31}/></span></div><h3>{dirty ? 'Re-inspection required' : 'Your evidence report starts here.'}</h3><p>{dirty ? 'The editor contains unreviewed changes. Run the scan again to link findings to the latest version.' : 'Paste content and inspect it. We will show exactly what needs attention, why, and which approved source it relates to.'}</p><div className="blank-steps">CONTENT <ArrowRight size={12}/> EVIDENCE <ArrowRight size={12}/> HUMAN</div></div> : <div className="report-content"><div className="report-status"><div className={`report-status-icon ${highCount ? 'warn' : 'pass'}`}>{highCount ? <AlertTriangle size={22}/> : <CheckCircle2 size={22}/>}</div><div><b>{highCount ? 'Hold for claim review' : issueCount ? 'Suggestions found' : 'Ready for human review'}</b><p>{highCount ? 'High-severity findings need correction or explicit approval override.' : issueCount ? 'These findings are advisory; inspect the evidence before publishing.' : 'No known policy violations were found. This is not a legal certification.'}</p></div></div>
              <div className="scan-metadata"><span>REV {current.revision} / {current.channel.toUpperCase()}</span><span>{current.ai_status === 'completed' ? 'OPENROUTER + RULES' : current.ai_status === 'not_configured' ? 'RULES / NO KEY' : current.ai_status === 'skipped_by_user' ? 'RULES / AI SKIPPED' : current.ai_status?.includes('rules_only') ? 'RULES / AI UNAVAILABLE' : 'RULES ONLY'}</span></div>
              <div className="marked-area"><div className="marked-area-head"><span>ANNOTATED COPY</span><span><CircleDot size={12}/> {issueCount} FLAGGED</span></div><HighlightedCopy copy={current.content} findings={current.findings}/></div>
              <div className="findings-heading"><h4>Findings & supporting evidence</h4><button className="text-button" onClick={exportReport}><ArrowDownToLine size={14}/> Export JSON</button></div>
              {issueCount === 0 && <div className="clean-note"><CheckCircle2 size={18}/><div><b>Clear against known rules</b><p>Approved facts in the source library were not contradicted by recognized patterns. Human review is still required.</p></div></div>}
              <div className="issue-list">{current.findings?.map((f,i)=><article className="issue" key={f.id}><div className="issue-top"><span className="issue-index">{String(i+1).padStart(2,'0')}</span><Tag tone={f.severity === 'critical' ? 'red' : f.severity === 'high' ? 'amber' : 'quiet'}>{f.severity}</Tag><span className="issue-type">{HUMAN(f.issue_type)}</span></div><h4>“{f.excerpt}”</h4><p className="issue-description">{f.explanation}</p><div className="evidence-card"><div><BookOpen size={14}/> <strong>THE SOURCE</strong><code>{f.source_code}</code></div><p><b>{f.source_title}</b> — {f.source_excerpt}</p><small>Source snapshot {f.source_version} · {f.evidence_status.replaceAll('_',' ')} · {f.origin === 'llm' ? 'AI advisory' : 'deterministic check'}</small></div><div className="suggestion"><div className="suggestion-label"><WandSparkles size={15}/> RECOMMENDED LANGUAGE</div><p>{f.suggestion}</p><button hidden={['CLAIMS-01','TONE-01'].includes(f.rule_code)} onClick={()=>fix(f)} disabled={role !== 'creator' || current.status === 'pending_review' || current.status === 'approved'}><PenLine size={13}/> Insert into editor <ArrowRight size={14}/></button></div></article>)}</div>
              <div className="submit-strip"><div><ShieldCheck size={17}/><span><b>Human approval required</b><small>Never automatically publish reviewed content</small></span></div><button className="button btn-orange" disabled={!canSubmit || Boolean(busy)} onClick={submitForReview}><Send size={15}/> Request approval</button></div>
            </div>}
            </section>
          </div>
          <div className="bottom-grid"><section className="module-card"><div className="card-cap"><div><span className="cap-number">03</span><div><h3>Recent campaigns</h3><p>Every content revision is preserved.</p></div></div><Tag>{drafts.length} TOTAL</Tag></div><div className="recent-list">{drafts.length ? drafts.slice(0,5).map(d=><button key={d.id} className="recent-row" onClick={()=>loadDraft(d.id,'desk')}><div className="recent-index">{String(d.id).padStart(2,'0')}</div><div className="recent-name"><b>{d.title}</b><small>{d.channel.toUpperCase()} / REV {d.revision} / {DATE(d.updated_at)}</small></div><StatusTag status={d.status}/><ArrowRight size={15}/></button>) : <p className="empty-small">No campaigns yet. One-click demo creates your first record.</p>}</div></section><section className="how-card"><BlockLabel>HOW IT WORKS</BlockLabel><h3>From first word to final sign-off.</h3><div className="how-steps"><span><b>01</b> Inspect the campaign <ArrowRight size={14}/></span><span><b>02</b> Correct & recheck <ArrowRight size={14}/></span><span><b>03</b> Request human sign-off <ArrowRight size={14}/></span></div><button onClick={()=>choosePage('queue')}>Explore the approval workflow <ArrowUpRight size={16}/></button></section></div>
        </>}

        {page === 'queue' && <div className="queue-grid"><section className="module-card"><div className="card-cap"><div><span className="cap-number">01</span><div><h3>Awaiting a decision</h3><p>Select an item to inspect before approving.</p></div></div><Tag tone="amber">{pending.length} OPEN</Tag></div>{pending.length ? <div className="queue-list">{pending.map(d=><button key={d.id} className={`queue-row ${current?.id === d.id ? 'selected' : ''}`} onClick={()=>loadDraft(d.id)}><div className="queue-row-icon"><FileText size={19}/></div><div><b>{d.title}</b><small>{d.channel.toUpperCase()} · REV {d.revision} · {d.finding_count} ISSUES</small></div><ChevronRight size={17}/></button>)}</div> : <div className="empty-queue"><FileCheck2 size={36}/><h3>Nothing to sign off yet.</h3><p>Create a draft in Review desk, run a scan, and select Request approval.</p><button className="button btn-ink" onClick={()=>{changeRole('creator');choosePage('desk');}}>Go to review desk <ArrowRight size={15}/></button></div>}</section>
          <section className="module-card decision-card"><div className="card-cap"><div><span className="cap-number">02</span><div><h3>Human judgment</h3><p>Decisions and overrides are recorded.</p></div></div><UserRoundCheck size={22}/></div>{current?.status !== 'pending_review' ? <div className="empty-queue"><ShieldCheck size={39}/><h3>Select a pending campaign.</h3><p>The exact copy, evidence, and review controls will appear here.</p></div> : <div className="decision-inside"><div className="decision-title"><h3>{current.title}</h3><StatusTag status={current.status}/></div><div className="decision-meta">SUBMITTED BY {current.creator.toUpperCase()} · REVISION {current.revision}</div><div className="decision-copy"><HighlightedCopy copy={current.content} findings={current.findings}/></div><div className="decision-findings"><BlockLabel>FLAGGED EVIDENCE</BlockLabel>{current.findings.length ? current.findings.map(f=><div key={f.id} className="decision-finding"><Tag tone={f.severity === 'critical' ? 'red' : 'amber'}>{f.severity}</Tag><div><b>{f.excerpt}</b><p>{f.explanation}</p><small>SOURCE / {f.source_code} — {f.source_title}</small><p>{f.source_excerpt}</p></div></div>) : <p className="no-issues"><CheckCircle2 size={15}/> No known violations identified.</p>}</div>{!['reviewer','manager'].includes(role) ? <div className="reviewer-nudge"><Shield size={17}/> Switch to the Reviewer demo persona to decide.<button onClick={()=>changeRole('reviewer')}>Switch persona <ArrowRight size={14}/></button></div> : <div className="decision-form"><label className="field"><span>REVIEWER COMMENT</span><textarea rows={3} value={decisionNote} onChange={e=>setDecisionNote(e.target.value)} placeholder="Explain the decision or required revisions..."/></label>{highCount > 0 && <label className="override"><input type="checkbox" checked={override} onChange={e=>setOverride(e.target.checked)}/><span>I am explicitly overriding {highCount} high-risk finding(s). Approval requires a justification of at least ten characters.</span></label>}<div className="decision-buttons"><button className="button btn-outline" onClick={()=>decision('request_changes')} disabled={Boolean(busy)}><RotateCcw size={15}/> Request changes</button><button className="button btn-ink" onClick={()=>decision('approve')} disabled={Boolean(busy)}><Check size={15}/> Record approval</button></div></div>}</div>}</section></div>}

        {page === 'library' && <><div className="library-banner"><div className="library-emblem">L<span>✳</span></div><div><span>APPROVED KNOWLEDGE / BRAND 001</span><h3>LumaLeaf brand system</h3><p>These sources—not model guesses—are the starting point for every brand decision.</p></div><Tag tone="green">{activeGuides} ACTIVE SOURCES</Tag></div><div className="library-controls"><div className="search-field"><Search size={17}/><input aria-label="Search brand sources" value={search} onChange={e=>setSearch(e.target.value)} placeholder="Search by source ID, fact or rule..."/></div><div className="filter-tabs">{[['all','All sources'],['fact','Facts'],['rule','Rules'],['policy','Policies']].map(([v,label])=><button className={ruleFilter === v ? 'active' : ''} key={v} onClick={()=>setRuleFilter(v)}>{label}</button>)}</div></div><div className="library-grid">{visibleGuides.map(g=><article className={`library-card ${!g.active ? 'paused' : ''}`} key={g.id}><div className="library-card-top"><span>{g.kind === 'fact' ? 'APPROVED FACT' : g.kind === 'policy' ? 'GOVERNANCE POLICY' : 'AUTOMATIC CHECK'}</span><code>{g.code}</code></div><div className="library-card-icon">{g.kind === 'fact' ? <BadgeCheck size={20}/> : g.kind === 'rule' ? <FileSearch2 size={20}/> : <Shield size={20}/>}</div><h3>{g.title}</h3><p>{g.body}</p>{g.trigger && <div className="trigger"><span>TRIGGER PHRASE</span><b>“{g.trigger}”</b></div>}<div className="library-card-footer"><span>{HUMAN(g.category)} · {g.severity}</span>{g.is_custom ? <button disabled={!['creator','manager'].includes(role) || Boolean(busy)} onClick={()=>toggleGuideline(g)}>{g.active ? 'Pause source' : 'Enable source'}</button> : <span><LockKeyhole size={12}/> DEMO STANDARD</span>}</div></article>)}</div>{!visibleGuides.length && <div className="empty-queue"><Search size={30}/><h3>No matching sources.</h3><p>Try a different search or filter.</p></div>}</>}

        {page === 'history' && <div className="history-grid"><section className="module-card"><div className="card-cap"><div><span className="cap-number">01</span><div><h3>Campaign archive</h3><p>Saved content cannot disappear on a refresh with persistent storage.</p></div></div><Tag>{drafts.length} RECORDS</Tag></div>{drafts.length ? <div className="queue-list">{drafts.map(d=><button className={`queue-row ${current?.id === d.id ? 'selected' : ''}`} key={d.id} onClick={()=>loadDraft(d.id)}><div className="queue-row-icon"><FileText size={18}/></div><div><b>{d.title}</b><small>REV {d.revision} · {DATE(d.updated_at)}</small></div><StatusTag status={d.status}/></button>)}</div> : <p className="empty-small">Inspect a campaign to begin the audit history.</p>}</section><section className="module-card"><div className="card-cap"><div><span className="cap-number">02</span><div><h3>The audit timeline</h3><p>Actor, role, revision, and decision notes.</p></div></div><History size={21}/></div>{!current ? <div className="empty-queue"><Clock3 size={37}/><h3>Select an archived campaign.</h3><p>Every recorded decision is displayed newest first.</p></div> : <div className="timeline"><div className="timeline-summary"><b>{current.title}</b><StatusTag status={current.status}/></div>{current.audit_events?.map((ev,i)=><div key={ev.id} className="timeline-entry"><span className="timeline-node">{String(i+1).padStart(2,'0')}</span><div><strong>{ev.action.replaceAll('_',' ')}</strong><p>{ev.note}</p><small>{ev.actor} / {ev.role} / REV {ev.revision} / {DATE(ev.created_at)}</small></div></div>)}<div className="comment-box"><label className="field"><span>ADD A COLLABORATION NOTE</span><textarea value={commentText} maxLength={1000} rows={2} onChange={e=>setCommentText(e.target.value)} /></label><button className="button btn-outline" disabled={Boolean(busy)||commentText.trim().length<3} onClick={postComment}>Record comment</button></div><BlockLabel>VERSION ARCHIVE</BlockLabel>{current.versions?.map(v=><details key={v.revision} className="version"><summary>REVISION {v.revision} <span>{DATE(v.created_at)}</span></summary><p>{v.content}</p></details>)}{current.analysis_history?.map(run=><details className="version" key={run.id}><summary>INSPECTION {run.id} / REV {run.revision}<span>{run.ai_status}</span></summary>{run.findings.map((f,i)=><p key={i}><b>{f.source_code}</b> · {f.excerpt}<br/>{f.source_excerpt}</p>)}{!run.findings.length && <p>No known issues detected in this inspection.</p>}</details>)}{current.status === 'approved' && <button className="button btn-ink" onClick={exportApproved}><ArrowDownToLine size={15}/> Export approved copy</button>}{originalVersion && <div className="version-context"><History size={16}/> Original wording remains accessible for comparison with the latest revision.</div>}</div>}</section></div>}

        {stats && <section className="insights-strip" aria-label="Governance insights"><div><span className="micro-label">POLICY RADAR</span><h3>What keeps coming back?</h3><p>Current-revision findings across this workspace. These are counts, not an accuracy score.</p></div><div><b>{stats.needs_evidence || 0}</b><span>claims need evidence</span></div><ul>{stats.repeat_rules?.length ? stats.repeat_rules.map(r=><li key={r.code}><code>{r.code}</code><span>{r.count} finding{r.count!==1?'s':''}</span></li>) : <li>No repeated findings yet.</li>}</ul></section>}
        <footer><div><span className="footer-icon">b.</span> BRANDPILOT AI <span className="footer-soft">/ Proof before publish.</span></div><div>BY JANU V · OXFORD COLLEGE OF ENGINEERING · 2026</div></footer>
      </main>
    </div>
    {showAdd && <div className="overlay" onMouseDown={e=>{if(e.target===e.currentTarget)setShowAdd(false);}}><div className="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title"><div className="modal-top"><div><BlockLabel>NEW KNOWLEDGE SOURCE</BlockLabel><h2 id="modal-title">Add to the brand library</h2><p>Sources added here belong to this workspace. AI reviews send active sources to OpenRouter only when enabled.</p></div><button aria-label="Close" className="close-modal" onClick={()=>setShowAdd(false)}><X size={19}/></button></div><form onSubmit={addGuideline}><div className="modal-fields"><label className="field"><span>SOURCE TYPE</span><select value={ruleForm.kind} onChange={e=>setRuleForm({...ruleForm,kind:e.target.value})}><option value="rule">Phrase-based checking rule</option><option value="fact">Approved product fact</option></select></label><label className="field"><span>CATEGORY</span><select value={ruleForm.category} onChange={e=>setRuleForm({...ruleForm,category:e.target.value})}><option value="claims">Claims</option><option value="terminology">Terminology</option><option value="tone">Tone</option><option value="accessibility">Accessibility</option><option value="approved_fact">Approved fact</option></select></label></div><label className="field"><span>SOURCE TITLE</span><input required minLength={3} maxLength={130} value={ruleForm.title} onChange={e=>setRuleForm({...ruleForm,title:e.target.value})} placeholder="e.g. Avoid exaggerated savings claims"/></label><label className="field"><span>APPROVED EVIDENCE OR POLICY</span><textarea required rows={3} minLength={8} maxLength={1500} value={ruleForm.body} onChange={e=>setRuleForm({...ruleForm,body:e.target.value})} placeholder="Write a precise brand guideline or product fact"/></label>{ruleForm.kind === 'rule' && <><label className="field"><span>EXACT PHRASE TO FLAG</span><input required maxLength={180} value={ruleForm.trigger} onChange={e=>setRuleForm({...ruleForm,trigger:e.target.value})} placeholder="e.g. best in the galaxy"/></label><label className="field"><span>SUGGESTED REPLACEMENT</span><input maxLength={300} value={ruleForm.suggestion} onChange={e=>setRuleForm({...ruleForm,suggestion:e.target.value})} placeholder="e.g. designed for everyday reuse"/></label><label className="field"><span>SEVERITY</span><select value={ruleForm.severity} onChange={e=>setRuleForm({...ruleForm,severity:e.target.value})}><option value="critical">Critical</option><option value="high">High</option><option value="medium">Medium</option><option value="low">Low</option></select></label></>}<div className="modal-footer"><button type="button" className="button btn-outline" onClick={()=>setShowAdd(false)}>Cancel</button><button type="submit" disabled={Boolean(busy)} className="button btn-ink"><Plus size={15}/> Save source</button></div></form></div></div>}
    {alert && <div className={`toast toast-${alert.tone}`} role="status"><span>{alert.tone==='bad'?<AlertCircle size={18}/>:alert.tone==='info'?<Sparkles size={18}/>:<CheckCircle2 size={18}/>}</span><p>{alert.message}</p><button aria-label="Dismiss notice" onClick={()=>setAlert(null)}><X size={17}/></button></div>}
  </div>;
}
