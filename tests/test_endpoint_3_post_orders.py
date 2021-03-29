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
    metadata.create_all(engine)


def test_bad_request_empty_body():
    response = client.post("/orders")

    assert response.status_code == 400
    assert response.json() == {
        "validation_error": {
            "orders": []
        }
    }


def test_bad_request_some_digits():
    response = client.post("/orders", data="123")

    assert response.status_code == 400
    assert response.json() == {
        "validation_error": {
            "orders": []
        }
    }


def test_bad_request_some_chars():
    response = client.post("/orders", data="data")

    assert response.status_code == 400
    assert response.json() == {
        "validation_error": {
            "orders": []
        }
    }


def test_bad_request_empty_json():
    response = client.post("/orders",
        json={},
    )

    assert response.status_code == 400
    assert response.json() == {
        "validation_error": {
            "orders": []
        }
    }


def test_bad_request_json_with_some_random_stuff():
    response = client.post("/orders",
        json={"foo": "bar"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "validation_error": {
            "orders": []
        }
    }


def test_bad_request_json_with_bad_data_value():
    response = client.post("/orders",
        json={"data": False},
    )

    assert response.status_code == 400
    assert response.json() == {
        "validation_error": {
            "orders": []
        }
    }


def test_bad_request_json_with_empty_data_array():
    response = client.post("/orders",
        json={"data": []},
    )

    assert response.status_code == 400
    assert response.json() == {
        "validation_error": {
            "orders": []
        }
    }


def test_bad_request_json_with_bad_items_in_data_array():
    response = client.post("/orders",
        json={
            "data": [
                {
                    "abc": 1
                },
                {
                    "def": True
                }
            ]
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "validation_error": {
            "orders": []
        }
    }


def test_bad_request_json_data_array_one_id_only():
    response = client.post("/orders",
        json={
            "data": [
                {
                    "order_id": 1
                }
            ]
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        "validation_error": {
            "orders": [
                {
                    "id": 1
                }
            ]
        }
    }


def test_bad_request_json_data_array_wrong_id():
    response = client.post("/orders",
        json={
            "data": [
                {
                    "order_id": 0
                }
            ]
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        "validation_error": {
            "orders": [
                {
                    "id": 0
                }
            ]
        }
    }


def test_bad_request_json_data_array_missing_fields():
    response = client.post("/orders",
        json={
            "data": [
                {
                    "order_id": 1,
                    "region": 12,
                    "delivery_hours": ["09:00-18:00"]
                },
                {
                    "order_id": 2,
                    "weight": 15,
                    "delivery_hours": ["09:00-18:00"]
                },
                {
                    "order_id": 3,
                    "weight": 0.01,
                    "region": 22,
                }
            ]
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        "validation_error": {
            "orders": [
                {"id": 1},
                {"id": 2},
                {"id": 3}
            ]
        }
    }


def test_bad_request_json_data_array_extra_fields():
    response = client.post("/orders",
        json={
            "data": [
                {
                    "order_id": 1,
                    "weight": 0.23,
                    "region": 12,
                    "color": "green",
                    "delivery_hours": ["09:00-18:00"]
                },
                {
                    "order_id": 2,
                    "weight": 15,
                    "region": 12,
                    "quantity": 125,
                    "delivery_hours": ["09:00-18:00"]
                },
                {
                    "order_id": 3,
                    "weight": 0.01,
                    "region": 22,
                    "delivery_hours": ["09:00-18:00"]
                }
            ]
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        "validation_error": {
            "orders": [
                {"id": 1},
                {"id": 2}
            ]
        }
    }


def test_bad_request_json_data_array_all_fields_bad_values():
    response = client.post("/orders",
        json={
            "data": [
                {
                    "order_id": 1,
                    "weight": 100.23,
                    "region": 12,
                    "delivery_hours": ["09:00-18:00"]
                },
                {
                    "order_id": 2,
                    "weight": 15,
                    "region": "Moscow",
                    "delivery_hours": ["09:00-18:00"]
                },
                {
                    "order_id": 3,
                    "weight": 0.01,
                    "region": 22,
                    "delivery_hours": ["19:77-28:00"]
                }
            ]
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        "validation_error": {
            "orders": [
                {"id": 1},
                {"id": 2},
                {"id": 3}
            ]
        }
    }


def test_bad_request_json_data_array_all_fields_all_good():
    response = client.post("/orders",
        json={
            "data": [
                {
                    "order_id": 1,
                    "weight": 0.23,
                    "region": 12,
                    "delivery_hours": ["09:00-18:00"]
                },
                {
                    "order_id": 2,
                    "weight": 15,
                    "region": 1,
                    "delivery_hours": ["09:00-18:00"]
                },
                {
                    "order_id": 3,
                    "weight": 0.01,
                    "region": 22,
                    "delivery_hours": ["09:00-12:00", "16:00-21:30"]
                }
            ]
        },
    )
    assert response.status_code == 201
    assert response.json() == {
        "orders": [
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


def test_bad_request_json_data_array_all_fields_all_good_repeat():
    response = client.post("/orders",
        json={
            "data": [
                {
                    "order_id": 1,
                    "weight": 0.23,
                    "region": 12,
                    "delivery_hours": ["09:00-18:00"]
                },
                {
                    "order_id": 2,
                    "weight": 15,
                    "region": 1,
                    "delivery_hours": ["09:00-18:00"]
                },
                {
                    "order_id": 3,
                    "weight": 0.01,
                    "region": 22,
                    "delivery_hours": ["09:00-12:00", "16:00-21:30"]
                }
            ]
        },
    )
    assert response.status_code == 201
    assert response.json() == {
        "orders": []
    }
