import pytest
from pydantic import ValidationError

from wa.config import Settings


def test_defaults_and_secrets_load(monkeypatch):
    monkeypatch.setenv("WA_S3_ACCESS_KEY", "a")
    monkeypatch.setenv("WA_S3_SECRET_KEY", "b")
    s = Settings(_env_file=None)
    assert s.s3_bucket_raw == "wa-raw"
    assert s.s3_access_key.get_secret_value() == "a"


def test_secret_is_not_printed(monkeypatch):
    monkeypatch.setenv("WA_S3_ACCESS_KEY", "a")
    monkeypatch.setenv("WA_S3_SECRET_KEY", "topsecret")
    assert "topsecret" not in repr(Settings(_env_file=None))


def test_missing_secret_fails_fast(monkeypatch):
    monkeypatch.delenv("WA_S3_ACCESS_KEY", raising=False)
    monkeypatch.delenv("WA_S3_SECRET_KEY", raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)
