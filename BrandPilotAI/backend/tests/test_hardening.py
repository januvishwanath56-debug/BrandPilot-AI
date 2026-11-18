import json
from unittest.mock import Mock
from app import ai, auth
from test_workflow import create, GOOD, reviewer
from test_openrouter import policies, reset_limit


def test_policy_change_blocks_stale_approval(client):
    sid = create(client, GOOD)
    client.post(f'/api/submissions/{sid}/analyze')
    client.post(f'/api/submissions/{sid}/request-review')
    client.post('/api/guidelines', json={'kind':'rule','title':'New rule','body':'This phrase now needs review.', 'trigger':'reusable'})
    assert client.post(f'/api/submissions/{sid}/decision',headers=reviewer(),json={'action':'approve'}).status_code == 409
    assert client.post(f'/api/submissions/{sid}/decision',headers=reviewer(),json={'action':'request_changes','comment':'Recheck new policy'}).status_code == 200
    assert client.post(f'/api/submissions/{sid}/analyze').status_code == 200
    assert client.post(f'/api/submissions/{sid}/request-review').status_code == 200
    assert client.post(f'/api/submissions/{sid}/decision',headers=reviewer(),json={'action':'approve'}).status_code == 200


def test_inspection_history_survives_reanalysis(client):
    sid = create(client)
    client.post(f'/api/submissions/{sid}/analyze')
    result = client.post(f'/api/submissions/{sid}/analyze').json()
    assert len(result['analysis_history']) == 2
    assert result['analysis_history'][0]['sources']
    assert result['findings'][0]['source_version']


def test_whitespace_and_null_rejected(client):
    assert client.post('/api/submissions',json={'title':'   ','content':'         ','channel':'social'}).status_code == 422
    g = client.post('/api/guidelines',json={'kind':'fact','title':'Valid title','body':'An approved source fact.'}).json()
    assert client.patch(f"/api/guidelines/{g['id']}",json={'body':None}).status_code == 422
    assert client.get('/api/guidelines').status_code == 200


def test_comments_and_policy_audit(client):
    sid = create(client)
    result = client.post(f'/api/submissions/{sid}/comments',json={'comment':'Please verify this fact.'}).json()
    assert result['audit_events'][0]['action'] == 'commented'
    assert result['audit_events'][0]['created_at'].endswith('+00:00')
    client.post('/api/guidelines',json={'kind':'fact','title':'New fact','body':'New source approved for testing.'})
    assert len(client.get('/api/policy-history').json()) == 1


def test_default_analysis_does_not_send_to_provider(client, monkeypatch):
    monkeypatch.setenv('OPENROUTER_API_KEY','test-key')
    monkeypatch.setattr(ai.httpx,'post',lambda *a,**k: (_ for _ in ()).throw(AssertionError('Unexpected external call')))
    sid = create(client)
    assert client.post(f'/api/submissions/{sid}/analyze').json()['ai_status'] == 'skipped_by_user'


def test_malformed_model_payload_falls_back(monkeypatch):
    monkeypatch.setenv('OPENROUTER_API_KEY','test-key')
    for payload in ([], {'choices':['wrong']}, {'choices':[{'message':{'content':'nonsense'}}]}, {'choices':[{'message':{'content':'{"wrong":[]}'}}]}):
        reset_limit(monkeypatch)
        response=Mock(status_code=200)
        response.json.return_value=payload
        monkeypatch.setattr(ai.httpx,'post',lambda *a,**k: response)
        assert ai.model_findings('Example submitted copy.',policies(),[])[1] == 'invalid_model_response'


def test_nonfree_model_blocked(monkeypatch):
    monkeypatch.setenv('OPENROUTER_API_KEY','test-key')
    monkeypatch.setenv('OPENROUTER_MODEL','paid/model')
    assert ai.model_findings('Some content',policies(),[])[1] == 'nonfree_model_blocked_rules_only'


def test_private_roles_cannot_be_forged(client, monkeypatch):
    monkeypatch.setenv('AUTH_MODE','private')
    monkeypatch.setenv('AUTH_SECRET','test-secret-that-is-at-least-32-characters')
    users={name:{'role':role,'password_hash':auth.password_hash('test-password')} for name,role in [('alice','creator'),('bob','reviewer'),('maya','manager'),('eve','creator')]}
    monkeypatch.setenv('AUTH_USERS_JSON',json.dumps(users))
    assert client.get('/api/submissions').status_code == 401
    assert client.post('/api/auth/login',json={'username':'alice','password':'wrong'}).status_code == 401
    def headers(name):
        r=client.post('/api/auth/login',json={'username':name,'password':'test-password'})
        assert r.status_code == 200,r.text
        return {'Authorization':'Bearer '+r.json()['token']}
    alice,bob,maya,eve = [headers(n) for n in users]
    r=client.post('/api/submissions',headers=alice,json={'title':'Private campaign','channel':'social','content':GOOD})
    sid=r.json()['id']
    assert client.get(f'/api/submissions/{sid}',headers=eve).status_code == 404
    assert client.get('/api/submissions',headers=eve).json() == []
    assert client.post('/api/guidelines',headers=alice,json={'kind':'fact','title':'Bad access','body':'Not authorised source'}).status_code == 403
    assert client.post('/api/guidelines',headers=maya,json={'kind':'fact','title':'Manager fact','body':'An approved source for testing'}).status_code == 201
    client.post(f'/api/submissions/{sid}/analyze',headers=alice)
    client.post(f'/api/submissions/{sid}/request-review',headers=alice)
    assert client.post(f'/api/submissions/{sid}/decision',headers={**alice,'X-Demo-Role':'reviewer'},json={'action':'approve'}).status_code == 403
    assert client.post(f'/api/submissions/{sid}/decision',headers=bob,json={'action':'approve'}).status_code == 200
    forged={**alice,'Authorization':alice['Authorization']+'x'}
    assert client.get('/api/submissions',headers=forged).status_code == 401
