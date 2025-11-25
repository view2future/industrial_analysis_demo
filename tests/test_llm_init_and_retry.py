import os
import time
import pytest

from src.ai.llm_generator import LLMReportGenerator


def test_kimi_init_with_config_key(monkeypatch):
    def fake_load_config(_):
        return {'api_keys': {'kimi': 'dummy_key'}}
    monkeypatch.setattr(LLMReportGenerator, '_load_config', fake_load_config)
    gen = LLMReportGenerator(llm_service='kimi')
    assert gen.model_name
    assert gen.max_tokens > 0


def test_kimi_init_missing_key_raises(monkeypatch):
    def fake_load_config(_):
        return {'api_keys': {}}
    monkeypatch.setattr(LLMReportGenerator, '_load_config', fake_load_config)
    with pytest.raises(ValueError):
        LLMReportGenerator(llm_service='kimi')


def test_gemini_init_with_config_key(monkeypatch):
    def fake_load_config(_):
        return {'api_keys': {'google_gemini': 'dummy_key'}}
    monkeypatch.setattr(LLMReportGenerator, '_load_config', fake_load_config)
    gen = LLMReportGenerator(llm_service='gemini')
    assert gen.model_name


def test_key_rotation_reinit(monkeypatch):
    def fake_load_config(_):
        return {'api_keys': {'kimi': 'key1'}}
    monkeypatch.setattr(LLMReportGenerator, '_load_config', fake_load_config)
    gen = LLMReportGenerator(llm_service='kimi')
    # Change env key
    monkeypatch.setenv('KIMI_API_KEY', 'key2')
    # Trigger rotation check via retry wrapper
    try:
        gen._check_key_rotation_and_reinit('kimi')
    except Exception:
        pass
    assert gen.api_key == 'key2'