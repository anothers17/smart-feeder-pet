import pytest
import os
from config.settings import Settings, get_settings

def test_settings_load_defaults():
    """Test that settings load default values if .env is missing."""
    # Ensure environment variables are clear
    if "MODE" in os.environ:
        del os.environ["MODE"]
    
    settings = Settings()
    assert settings.mode in ["SIMULATOR", "REAL"]
    assert hasattr(settings, "mqtt_broker")
    assert hasattr(settings, "db_host")

def test_settings_from_env(monkeypatch):
    """Test that settings correctly load from environment variables."""
    monkeypatch.setenv("MODE", "SIMULATOR")
    monkeypatch.setenv("MQTT_BROKER", "test.broker.com")
    monkeypatch.setenv("DB_PORT", "9999")
    
    settings = Settings()
    assert settings.mode == "SIMULATOR"
    assert settings.mqtt_broker == "test.broker.com"
    assert settings.db_port == 9999

def test_get_settings_singleton():
    """Test that get_settings returns a consistent instance."""
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2
