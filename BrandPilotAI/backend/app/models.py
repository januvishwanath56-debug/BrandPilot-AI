"""Relational models; findings are tied to the exact version reviewed."""
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

def utc_now():
    return datetime.now(timezone.utc)

class Brand(Base):
    __tablename__ = 'brands'
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text)

class Guideline(Base):
    __tablename__ = 'guidelines'
    id: Mapped[int] = mapped_column(primary_key=True)
    brand_id: Mapped[int] = mapped_column(ForeignKey('brands.id'), index=True)
    session_id: Mapped[str | None] = mapped_column(String(90), nullable=True, index=True)
    code: Mapped[str] = mapped_column(String(45), unique=True, index=True)
    kind: Mapped[str] = mapped_column(String(25))  # fact, rule, or policy
    category: Mapped[str] = mapped_column(String(35))
    title: Mapped[str] = mapped_column(String(130))
    body: Mapped[str] = mapped_column(Text)
    trigger: Mapped[str | None] = mapped_column(String(180), nullable=True)
    suggestion: Mapped[str | None] = mapped_column(String(300), nullable=True)
    linked_fact_code: Mapped[str | None] = mapped_column(String(45), nullable=True)
    severity: Mapped[str] = mapped_column(String(15), default='medium')
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

class Submission(Base):
    __tablename__ = 'submissions'
    id: Mapped[int] = mapped_column(primary_key=True)
    brand_id: Mapped[int] = mapped_column(ForeignKey('brands.id'))
    session_id: Mapped[str] = mapped_column(String(90), index=True)
    creator: Mapped[str] = mapped_column(String(90))
    title: Mapped[str] = mapped_column(String(130))
    channel: Mapped[str] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(30), default='draft', index=True)
    revision: Mapped[int] = mapped_column(Integer, default=1)
    last_analyzed_revision: Mapped[int | None] = mapped_column(Integer, nullable=True)
    analysis_mode: Mapped[str] = mapped_column(String(35), default='not_run')
    ai_status: Mapped[str] = mapped_column(String(45), default='not_run')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

class SubmissionVersion(Base):
    __tablename__ = 'submission_versions'
    __table_args__ = (UniqueConstraint('submission_id', 'revision'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey('submissions.id'), index=True)
    revision: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)
    actor: Mapped[str] = mapped_column(String(90))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

class Finding(Base):
    __tablename__ = 'findings'
    id: Mapped[int] = mapped_column(primary_key=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey('submissions.id'), index=True)
    revision: Mapped[int] = mapped_column(Integer)
    rule_code: Mapped[str] = mapped_column(String(45))
    issue_type: Mapped[str] = mapped_column(String(35))
    severity: Mapped[str] = mapped_column(String(15))
    excerpt: Mapped[str] = mapped_column(String(400))
    explanation: Mapped[str] = mapped_column(Text)
    suggestion: Mapped[str] = mapped_column(String(500))
    source_code: Mapped[str] = mapped_column(String(45))
    source_title: Mapped[str] = mapped_column(String(130))
    source_excerpt: Mapped[str] = mapped_column(Text)
    evidence_status: Mapped[str] = mapped_column(String(35))
    origin: Mapped[str] = mapped_column(String(25), default='rules')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

class AuditEvent(Base):
    __tablename__ = 'audit_events'
    id: Mapped[int] = mapped_column(primary_key=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey('submissions.id'), index=True)
    revision: Mapped[int] = mapped_column(Integer)
    actor: Mapped[str] = mapped_column(String(90))
    role: Mapped[str] = mapped_column(String(20))
    action: Mapped[str] = mapped_column(String(35))
    note: Mapped[str] = mapped_column(Text, default='')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class AnalysisRun(Base):
    __tablename__ = 'analysis_runs'
    id: Mapped[int] = mapped_column(primary_key=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey('submissions.id'), index=True)
    revision: Mapped[int] = mapped_column(Integer)
    policy_digest: Mapped[str] = mapped_column(String(64))
    snapshot: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class PolicyEvent(Base):
    __tablename__ = 'policy_events'
    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[str] = mapped_column(String(90), index=True)
    code: Mapped[str] = mapped_column(String(45))
    actor: Mapped[str] = mapped_column(String(90))
    snapshot: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
