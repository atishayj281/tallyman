"""Write SeaweedFS's s3.json from .env so secrets never live in git."""

import json
from pathlib import Path

from wa.config import get_settings

OUT = Path("infra/seaweedfs/s3.json")


def main() -> None:
    s = get_settings()
    cfg = {
        "identities": [
            {
                "name": "tallyman",
                "credentials": [
                    {
                        "accessKey": s.s3_access_key.get_secret_value(),
                        "secretKey": s.s3_secret_key.get_secret_value(),
                    }
                ],
                "actions": ["Admin", "Read", "Write", "List", "Tagging"],
            }
        ]
    }
    OUT.write_text(json.dumps(cfg, indent=2))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
