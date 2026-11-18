"""End-to-end API integration tests: no external AI credentials required."""

BAD = 'Our LumaLeaf bottle is 100% plastic-free, best in the world, and guaranteed to save the planet. Click here!'
GOOD = ('Meet LumaLeaf: a reusable 750 mL bottle made with 60% post-consumer recycled plastic. '
        'Includes a 12-month limited manufacturing warranty. Explore our range.')


def create(client, content=BAD):
    r = client.post('/api/submissions', json={'title': 'Campaign launch', 'channel': 'social', 'content': content})
    assert r.status_code == 201, r.text
    return r.json()['id']


def reviewer():
    return {'X-Demo-Role': 'reviewer', 'X-Demo-Actor': 'Demo Reviewer'}


def test_health_and_brand_seed(client):
    assert client.get('/api/health').json()['status'] == 'ok'
    codes = {g['code'] for g in client.get('/api/guidelines').json()}
    assert {'FACT-01', 'CLAIMS-01', 'POL-01'} <= codes


def test_conflict_has_real_approved_source(client):
    sid = create(client)
    r = client.post(f'/api/submissions/{sid}/analyze')
    assert r.status_code == 200, r.text
    result = r.json()
    conflict = next(x for x in result['findings'] if x['rule_code'] == 'POL-01')
    assert conflict['evidence_status'] == 'contradicted'
    assert conflict['source_code'] == 'FACT-01'
    assert '60%' in conflict['source_excerpt']
    assert conflict['origin'] == 'rules'


def test_unsupported_claim_is_needs_evidence_not_false(client):
    sid = create(client, 'Our bottles are 100% carbon-neutral, guaranteed to change the world.')
    result = client.post(f'/api/submissions/{sid}/analyze').json()
    assert any(f['evidence_status'] == 'needs_evidence' for f in result['findings'])
    assert all(f['source_code'] for f in result['findings'])


def test_compliant_copy_can_be_approved_with_a_separate_reviewer(client):
    sid = create(client, GOOD)
    analyzed = client.post(f'/api/submissions/{sid}/analyze')
    assert analyzed.status_code == 200
    assert analyzed.json()['high_risk_count'] == 0
    assert client.post(f'/api/submissions/{sid}/request-review').status_code == 200
    assert client.post(f'/api/submissions/{sid}/decision', json={'action':'approve'}, headers=reviewer()).status_code == 200
    stored = client.get(f'/api/submissions/{sid}').json()
    assert stored['status'] == 'approved'
    assert any(e['action'] == 'approved' and e['actor'] == 'Demo Reviewer' for e in stored['audit_events'])


def test_creator_cannot_approve(client):
    sid = create(client, GOOD)
    client.post(f'/api/submissions/{sid}/analyze')
    client.post(f'/api/submissions/{sid}/request-review')
    r = client.post(f'/api/submissions/{sid}/decision', json={'action':'approve'})
    assert r.status_code == 403


def test_high_risk_requires_override_and_justification(client):
    sid = create(client)
    client.post(f'/api/submissions/{sid}/analyze')
    client.post(f'/api/submissions/{sid}/request-review')
    assert client.post(f'/api/submissions/{sid}/decision', json={'action':'approve'}, headers=reviewer()).status_code == 409
    r = client.post(f'/api/submissions/{sid}/decision', headers=reviewer(), json={
        'action':'approve', 'override_high_risk': True,
        'comment':'Approval granted after manual review of claim evidence.'})
    assert r.status_code == 200
    assert r.json()['status'] == 'approved'


def test_changes_request_revision_and_stale_analysis(client):
    sid = create(client)
    client.post(f'/api/submissions/{sid}/analyze')
    client.post(f'/api/submissions/{sid}/request-review')
    req = client.post(f'/api/submissions/{sid}/decision', headers=reviewer(), json={
        'action': 'request_changes', 'comment': 'Please correct claims before release'})
    assert req.status_code == 200
    changed = client.patch(f'/api/submissions/{sid}', json={'content': GOOD})
    assert changed.status_code == 200
    assert changed.json()['revision'] == 2
    assert client.post(f'/api/submissions/{sid}/request-review').status_code == 409
    assert client.post(f'/api/submissions/{sid}/analyze').status_code == 200
    assert client.post(f'/api/submissions/{sid}/request-review').status_code == 200
    assert client.post(f'/api/submissions/{sid}/decision', headers=reviewer(), json={'action':'approve'}).status_code == 200
    result = client.get(f'/api/submissions/{sid}').json()
    assert len(result['versions']) == 2
    assert any(e['action'] == 'revised' for e in result['audit_events'])


def test_demo_sessions_are_separated_for_regular_queries(client):
    sid = create(client)
    assert client.get(f'/api/submissions/{sid}', headers={'X-Demo-Session':'different-session-999'}).status_code == 404
    assert client.get('/api/submissions', headers={'X-Demo-Session':'different-session-999'}).json() == []


def test_custom_rule_is_session_scoped_and_checked(client):
    r = client.post('/api/guidelines', json={
        'kind':'rule','title':'Avoid urgency pressure','category':'tone',
        'body':'Do not use high-pressure words in friendly brand communication.',
        'trigger':'BUY RIGHT NOW','suggestion':'Explore the collection','severity':'medium'})
    assert r.status_code == 201, r.text
    code = r.json()['code']
    sid = create(client, 'BUY RIGHT NOW: a new LumaLeaf bottle has arrived.')
    res = client.post(f'/api/submissions/{sid}/analyze').json()
    assert any(f['rule_code'] == code for f in res['findings'])
    other = client.get('/api/guidelines', headers={'X-Demo-Session':'different-session-999'}).json()
    assert code not in {g['code'] for g in other}


def test_txt_import_and_unsupported_extension(client):
    result = client.post('/api/extract', files={'file': ('sample.txt', b'LumaLeaf sample content', 'text/plain')})
    assert result.status_code == 200
    assert 'LumaLeaf' in result.json()['text']
    result = client.post('/api/extract', files={'file': ('bad.exe', b'bad', 'application/octet-stream')})
    assert result.status_code == 415


def test_pdf_and_docx_import(client):
    import io
    import pymupdf
    from docx import Document

    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((70, 70), 'LumaLeaf PDF imported content')
    pdf_bytes = doc.tobytes()
    doc.close()
    result = client.post('/api/extract', files={'file': ('sample.pdf', pdf_bytes, 'application/pdf')})
    assert result.status_code == 200, result.text
    assert 'LumaLeaf' in result.json()['text']

    word = Document()
    word.add_paragraph('LumaLeaf DOCX imported content')
    stream = io.BytesIO()
    word.save(stream)
    result = client.post('/api/extract', files={'file': (
        'sample.docx', stream.getvalue(),
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document')})
    assert result.status_code == 200, result.text
    assert 'LumaLeaf' in result.json()['text']
