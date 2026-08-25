import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app


@pytest.fixture
def client(tmp_path):
    db_path = tmp_path / "test_skilllink.db"
    os.environ["SKILLLINK_DB"] = str(db_path)
    client = TestClient(app, follow_redirects=False)
    with client:
        yield client
    os.environ.pop("SKILLLINK_DB", None)
