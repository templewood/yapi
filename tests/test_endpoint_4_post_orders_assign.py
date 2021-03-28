import sys
sys.path.append("../app")

import pytest

from fastapi.testclient import TestClient
from main import app


client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def clean_db():
    from config import settings
    from db.schema import metadata
    from sqlalchemy import create_engine
    engine = create_engine(settings.database_url)
    metadata.drop_all(engine)
    metadata.create_all(engine)
    yield
    metadata.drop_all(engine)


def test_post_couriers_good():
    response = client.post("/couriers",
        json={
            "data": [
                {
                    "courier_id": 1,
                    "courier_type": "foot",
                    "regions": [1, 12, 22],
                    "working_hours": ["16:35-22:05", "09:00-11:00"]
                },
                {
                    "courier_id": 2,
                    "courier_type": "bike",
                    "regions": [22],
                    "working_hours": ["09:00-18:00"]
                },
                {
                    "courier_id": 3,
                    "courier_type": "car",
                    "regions": [12, 22, 23, 33],
                    "working_hours": []
                }
            ]
        },
    )
    assert response.status_code == 201
    assert response.json() == {
        "couriers": [
            {
                "id": 1
            },
            {
                "id": 2
            },
            {
                "id": 3
            }
        ]
    }


def test_post_orders_good():
    response = client.post("/orders",
        json={
            "data": [
                {
                    "order_id": 10,
                    "weight": 0.23,
                    "region": 12,
                    "delivery_hours": ["09:00-23:00"]
                },
                {
                    "order_id": 11,
                    "weight": 15,
                    "region": 1,
                    "delivery_hours": ["09:00-23:00"]
                },
                {
                    "order_id": 12,
                    "weight": 0.01,
                    "region": 22,
                    "delivery_hours": ["09:00-12:00", "22:00-23:30"]
                }
            ]
        },
    )
    assert response.status_code == 201
    assert response.json() == {
        "orders": [
            {
                "id": 10
            },
            {
                "id": 11
            },
            {
                "id": 12
            }
        ]
    }
