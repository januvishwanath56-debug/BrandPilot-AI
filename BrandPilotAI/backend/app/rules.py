"""Transparent deterministic checks. No text is sent to an external provider here."""
import re
from .models import Guideline

ABSOLUTE_PATTERNS = [
    re.compile(r'\b100\s*%\s+(?:carbon[- ]neutral|eco[- ]friendly|organic|recyclable|sustainable)\b', re.I),
    re.compile(r'\bzero[- ]emissions\b', re.I),
    re.compile(r'\bguaranteed\s+(?!to save the planet)[a-z][\w -]{3,60}', re.I),
    re.compile(r'\b(?:number\s*one|#1)\s+(?:in the world|on earth)\b', re.I),
]

def inspect_text(text: str, guidelines: list[Guideline]) -> list[dict]:
    active = [g for g in guidelines if g.active]
    by_code = {g.code: g for g in active}
    findings: list[dict] = []
    occupied: list[tuple[int, int]] = []

    for rule in active:
        if rule.kind != 'rule' or not rule.trigger:
            continue
        for match in re.finditer(re.escape(rule.trigger), text, re.IGNORECASE):
            quote = match.group(0)
            if rule.code == 'POL-04' and quote == 'LumaLeaf':
                continue
            source = by_code.get(rule.linked_fact_code) if rule.linked_fact_code else None
            source = source or rule
            status = 'contradicted' if rule.linked_fact_code and source.code == rule.linked_fact_code else (
                'needs_evidence' if rule.category == 'claims' else 'guideline'
            )
            findings.append({
                'rule_code': rule.code,
                'issue_type': 'claim_conflict' if status == 'contradicted' else rule.category,
                'severity': rule.severity,
                'excerpt': quote,
                'explanation': rule.body,
                'suggestion': rule.suggestion or quote,
                'source_code': source.code,
                'source_title': source.title,
                'source_excerpt': source.body,
                'evidence_status': status,
                'origin': 'rules',
            })
            occupied.append(match.span())

    claim_policy = by_code.get('CLAIMS-01')
    if claim_policy:
        for pattern in ABSOLUTE_PATTERNS:
            for match in pattern.finditer(text):
                if any(match.start() < end and match.end() > start for start, end in occupied):
                    continue
                quote = match.group(0)
                findings.append({
                    'rule_code': claim_policy.code,
                    'issue_type': 'claims',
                    'severity': 'high',
                    'excerpt': quote,
                    'explanation': 'No approved evidence for this absolute claim was identified in the demo knowledge base. It needs human verification; this is not a finding that the claim is false.',
                    'suggestion': 'Replace the absolute wording with a specific approved product fact.',
                    'source_code': claim_policy.code,
                    'source_title': claim_policy.title,
                    'source_excerpt': claim_policy.body,
                    'evidence_status': 'needs_evidence',
                    'origin': 'rules',
                })
                occupied.append(match.span())

    letters = [c for c in text if c.isalpha()]
    tone = by_code.get('TONE-01')
    if tone and len(letters) >= 50 and sum(c.isupper() for c in letters) / len(letters) > .75:
        findings.append({
            'rule_code': tone.code, 'issue_type': 'tone', 'severity': 'low',
            'excerpt': text[:90],
            'explanation': 'Most of this message is capitalized, which can feel aggressive and conflicts with the friendly brand voice.',
            'suggestion': 'Use normal sentence capitalization.',
            'source_code': tone.code, 'source_title': tone.title,
            'source_excerpt': tone.body, 'evidence_status': 'guideline', 'origin': 'rules',
        })
    return findings[:30]
