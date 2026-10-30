
import boto3
from botocore.client import BaseClient
from botocore.config import Config

from wa.config import get_settings


def s3_client() -> BaseClient:
    s = get_settings()
    return boto3.client(
        "s3",
        endpoint_url=s.s3_endpoint,
        aws_access_key_id=s.s3_access_key.get_secret_value(),
        aws_secret_access_key=s.s3_secret_key.get_secret_value(),
        region_name="us-east-1",  # SeaweedFS ignores it; boto3 requires one
        config=Config(
            s3={"addressing_style": "path"},
            retries={"max_attempts": 3, "mode": "standard"},
        ),
    )


def ensure_buckets(client: BaseClient | None = None) -> list[str]:
    """Create the raw and mart buckets if missing. Safe to run repeatedly."""
    client = client or s3_client()
    s = get_settings()
    existing = {b["Name"] for b in client.list_buckets()["Buckets"]}
    created = []
    for name in (s.s3_bucket_raw, s.s3_bucket_mart):
        if name not in existing:
            client.create_bucket(Bucket=name)
            created.append(name)
    return created