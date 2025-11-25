import os
import json

def test_config_post_merge_preserves_api_keys(client, tmp_path, monkeypatch):
    # Prepare existing config with api_keys
    cfg_path = tmp_path / 'config.json'
    existing = {
        'api_keys': {
            'kimi': 'old_kimi_key',
            'google_gemini': 'old_gemini_key',
            'baidu_map': 'old_map_key'
        },
        'some_setting': True
    }
    cfg_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding='utf-8')
    monkeypatch.setenv('FLASK_CONFIG_PATH', str(cfg_path))

    # Post new config (without touching api_keys)
    resp = client.post('/api/config', json={'new_setting': 123})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get('success') is True
    assert data.get('version') == '1.1'

    # Read back
    final = json.loads(cfg_path.read_text(encoding='utf-8'))
    assert final['api_keys']['kimi'] == 'old_kimi_key'
    assert final['api_keys']['google_gemini'] == 'old_gemini_key'
    assert final['api_keys']['baidu_map'] == 'old_map_key'
    assert final['new_setting'] == 123
    assert final['some_setting'] is True