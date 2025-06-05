import os
import sys
import pytest

# Ensure the application module can be imported from the repository root
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import app


def test_index_route():
    client = app.app.test_client()
    response = client.get('/')
    assert response.status_code == 200
