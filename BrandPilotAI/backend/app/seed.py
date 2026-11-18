"""Only fictitious LumaLeaf brand facts. Safe for a public demonstration."""
from sqlalchemy.orm import Session
from .models import Brand, Guideline

SEED = [
    ('FACT-01', 'fact', 'approved_fact', 'Recycled plastic content',
     'LumaLeaf reusable bottles are made with 60% post-consumer recycled plastic.', None, None, None, 'info'),
    ('FACT-02', 'fact', 'approved_fact', 'Product warranty',
     'LumaLeaf bottles include a 12-month limited manufacturing warranty.', None, None, None, 'info'),
    ('FACT-03', 'fact', 'approved_fact', 'Bottle capacity',
     'The standard LumaLeaf bottle holds 750 mL.', None, None, None, 'info'),
    ('CLAIMS-01', 'policy', 'claims', 'Evidence required for absolute claims',
     'Absolute, comparative, guarantee or environmental benefit claims must be supported by explicitly approved brand evidence. Lack of evidence is not proof that a claim is false.', None, None, None, 'high'),
    ('POL-01', 'rule', 'claims', 'Do not claim plastic-free packaging',
     'The phrase "100% plastic-free" contradicts the documented use of recycled plastic.',
     '100% plastic-free', 'made with 60% post-consumer recycled plastic', 'FACT-01', 'critical'),
    ('POL-02', 'rule', 'claims', 'Avoid impossible environmental guarantees',
     'A claim to save the planet is not supported by any approved LumaLeaf evidence.',
     'guaranteed to save the planet', 'designed with everyday reuse in mind', None, 'high'),
    ('POL-03', 'rule', 'claims', 'Avoid unsupported superlatives',
     'Statements such as "best in the world" need substantiation before publication.',
     'best in the world', 'designed for everyday reuse', None, 'high'),
    ('POL-04', 'rule', 'terminology', 'Use exact brand capitalization',
     'The correct brand spelling is LumaLeaf, with a capital L in Leaf.',
     'lumaleaf', 'LumaLeaf', None, 'medium'),
    ('POL-05', 'rule', 'accessibility', 'Meaningful call-to-action text',
     'A link or call to action should explain its destination instead of saying "click here".',
     'click here', 'Explore the LumaLeaf collection', None, 'low'),
    ('POL-06', 'rule', 'claims', 'No lifetime warranty claims',
     'A lifetime warranty conflicts with the approved 12-month limited warranty.',
     'lifetime warranty', '12-month limited manufacturing warranty', 'FACT-02', 'critical'),
    ('POL-07', 'rule', 'claims', 'Use approved bottle capacity',
     'The standard bottle capacity is 750 mL, not 1,000 mL.',
     '1,000 mL', '750 mL', 'FACT-03', 'high'),
    ('POL-08', 'rule', 'claims', 'Biodegradability requires evidence',
     'The brand has not approved a claim that its bottle is completely biodegradable.',
     'completely biodegradable', 'made with 60% post-consumer recycled plastic', None, 'high'),
    ('TONE-01', 'policy', 'tone', 'Friendly, clear brand voice',
     'LumaLeaf writing should sound confident and approachable, without excessive ALL CAPS or pressure tactics.',
     None, None, None, 'low'),
]

def seed_database(db: Session):
    brand = db.query(Brand).filter_by(slug='lumaleaf').first()
    if not brand:
        brand = Brand(slug='lumaleaf', name='LumaLeaf',
                      description='Fictional reusable bottle brand used exclusively for the BrandPilot AI demo.')
        db.add(brand)
        db.flush()
    existing = {g.code for g in db.query(Guideline).filter(Guideline.brand_id == brand.id).all()}
    for code, kind, category, title, body, trigger, suggestion, linked_fact_code, severity in SEED:
        if code not in existing:
            db.add(Guideline(brand_id=brand.id, session_id=None, code=code, kind=kind,
                             category=category, title=title, body=body, trigger=trigger,
                             suggestion=suggestion, linked_fact_code=linked_fact_code,
                             severity=severity, active=True))
    db.commit()
    return brand
