"""Offline tests for OpenRouter: never send a live API request in the test suite."""
import json as jsonlib
from unittest.mock import Mock

from app import ai
from app.models import Guideline


def policies():
    return [
        Guideline(code='FACT-01', kind='fact', category='approved_fact', title='Recycled plastic',
                  body='Contains 60% post-consumer recycled plastic.', active=True),
        Guideline(code='CLAIMS-01', kind='policy', category='claims', title='Claim evidence',
                  body='Claims require approved evidence.', active=True),
        Guideline(code='TONE-01', kind='policy', category='tone', title='Friendly voice',
                  body='Avoid exaggerated language.', active=True),
    ]


def reset_limit(monkeypatch):
    monkeypatch.setattr(ai, '_USAGE_DAY', '')
    monkeypatch.setattr(ai, '_USAGE_TOTAL', 0)
    monkeypatch.setattr(ai, '_USAGE_SESSIONS', {})


def test_key_not_compulsory(monkeypatch):
    monkeypatch.delenv('OPENROUTER_API_KEY', raising=False)
    checks, status = ai.model_findings('Guaranteed something amazing!', policies(), [], session_id='one')
    assert checks == [] and status == 'not_configured'
    assert not ai.is_configured()


def test_ai_opt_out_never_contacts_provider(monkeypatch):
    monkeypatch.setenv('OPENROUTER_API_KEY', 'test-only-key')
    monkeypatch.setattr(ai.httpx, 'post', lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError('Network called')))
    assert ai.model_findings('This is a marketing claim.', policies(), [], use_ai=False)[1] == 'skipped_by_user'


def test_quoted_source_validation_and_authorization_header(monkeypatch):
    reset_limit(monkeypatch)
    monkeypatch.setenv('OPENROUTER_API_KEY', 'test-only-key')
    monkeypatch.setenv('OPENROUTER_MODEL', 'openrouter/free')
    seen = {}

    def fake_post(url, *, json, headers, **kwargs):
        payload = json
        seen.update({'url': url, 'payload': payload, 'headers': headers})
        out = {'findings': [
            {'excerpt':'world’s best', 'source_code':'CLAIMS-01', 'evidence_status':'needs_evidence',
             'severity':'high','explanation':'No brand evidence supports the superlative.',
             'suggestion':'designed for everyday use'},
            {'excerpt':'world’s best', 'source_code':'MADE-UP-99', 'evidence_status':'guideline',
             'severity':'high','explanation':'Invalid source.','suggestion':'never trust this'},
            {'excerpt':'nonexistent exact quote', 'source_code':'FACT-01',
             'evidence_status':'contradicted','severity':'high',
             'explanation':'not in copy','suggestion':'avoid'},
        ]}
        response = Mock(status_code=200)
        response.json.return_value = {'choices':[{'message':{'content':'```json\n' + jsonlib.dumps(out) + '\n```'}}]}
        return response

    monkeypatch.setattr(ai.httpx, 'post', fake_post)
    found, status = ai.model_findings('Our bottle is the world’s best.', policies(), [], session_id='some-session')
    assert status == 'completed'
    assert len(found) == 1
    assert found[0]['source_code'] == 'CLAIMS-01'
    assert found[0]['source_excerpt'] == 'Claims require approved evidence.'
    assert seen['url'] == 'https://openrouter.ai/api/v1/chat/completions'
    assert seen['payload']['model'] == 'openrouter/free'
    assert seen['headers']['Authorization'] == 'Bearer test-only-key'
    assert 'test-only-key' not in str(found)


def test_provider_rate_limit_and_local_quota(monkeypatch):
    reset_limit(monkeypatch)
    monkeypatch.setenv('OPENROUTER_API_KEY', 'test-only-key')
    monkeypatch.setenv('AI_DEMO_SESSION_LIMIT', '1')
    monkeypatch.setenv('AI_DEMO_DAILY_LIMIT', '2')
    response = Mock(status_code=429)
    monkeypatch.setattr(ai.httpx, 'post', lambda *args, **kwargs: response)
    assert ai.model_findings('Some marketing content', policies(), [], session_id='session-A')[1] == 'rate_limited_rules_only'
    assert ai.model_findings('Some marketing content', policies(), [], session_id='session-A')[1] == 'demo_limit_rules_only'
    assert ai.model_findings('Some marketing content', policies(), [], session_id='session-B')[1] == 'rate_limited_rules_only'
    assert ai.model_findings('Some marketing content', policies(), [], session_id='session-C')[1] == 'demo_limit_rules_only'


def test_review_endpoint_explicit_rules_only(client, monkeypatch):
    monkeypatch.setenv('OPENROUTER_API_KEY', 'unused-key')
    monkeypatch.setattr(ai.httpx, 'post', lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError('Network called')))
    resp = client.post('/api/submissions', json={'title':'Launch','channel':'social',
                  'content':'Our bottle is 100% plastic-free and guaranteed to save the planet.'})
    sid = resp.json()['id']
    checked = client.post(f'/api/submissions/{sid}/analyze?use_ai=false')
    assert checked.status_code == 200
    assert checked.json()['ai_status'] == 'skipped_by_user'
    assert checked.json()['analysis_mode'] == 'rules only'
    assert any(x['source_code']=='FACT-01' for x in checked.json()['findings'])
