import uuid

import pytest

from wa.config import get_settings
from wa.storage import ensure_buckets, s3_client

pytestmark = pytest.mark.integration


def test_put_then_get_object():
    ensure_buckets()
    client = s3_client()
    bucket = get_settings().s3_bucket_raw
    key = f"smoke/{uuid.uuid4()}.txt"
    body = b"hello from wa-02"

    client.put_object(Bucket=bucket, Key=key, Body=body)
    got = client.get_object(Bucket=bucket, Key=key)["Body"].read()
    client.delete_object(Bucket=bucket, Key=key)

    assert got == body