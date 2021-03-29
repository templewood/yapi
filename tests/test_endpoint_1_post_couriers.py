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
    response = client.post("/couriers")

    assert response.status_code == 400
    assert response.json() == {
        "validation_error": {
            "couriers": []
        }
    }


def test_bad_request_some_digits():
    response = client.post("/couriers", data="123")

    assert response.status_code == 400
    assert response.json() == {
        "validation_error": {
            "couriers": []
        }
    }


def test_bad_request_some_chars():
    response = client.post("/couriers", data="data")

    assert response.status_code == 400
    assert response.json() == {
        "validation_error": {
            "couriers": []
        }
    }


def test_bad_request_empty_json():
    response = client.post("/couriers",
        json={},
    )

    assert response.status_code == 400
    assert response.json() == {
        "validation_error": {
            "couriers": []
        }
    }


def test_bad_request_json_with_some_random_stuff():
    response = client.post("/couriers",
        json={"foo": "bar"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "validation_error": {
            "couriers": []
        }
    }


def test_bad_request_json_with_bad_data_value():
    response = client.post("/couriers",
        json={"data": False},
    )

    assert response.status_code == 400
    assert response.json() == {
        "validation_error": {
            "couriers": []
        }
    }


def test_bad_request_json_with_empty_data_array():
    response = client.post("/couriers",
        json={"data": []},
    )

    assert response.status_code == 400
    assert response.json() == {
        "validation_error": {
            "couriers": []
        }
    }


def test_bad_request_json_with_bad_items_in_data_array():
    response = client.post("/couriers",
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
            "couriers": []
        }
    }


def test_bad_request_json_data_array_one_id_only():
    response = client.post("/couriers",
        json={
            "data": [
                {
                    "courier_id": 1
                }
            ]
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        "validation_error": {
            "couriers": [
                {
                    "id": 1
                }
            ]
        }
    }


def test_bad_request_json_data_array_wrong_id():
    response = client.post("/couriers",
        json={
            "data": [
                {
                    "courier_id": 0
                }
            ]
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        "validation_error": {
            "couriers": [
                {
                    "id": 0
                }
            ]
        }
    }


def test_bad_request_json_data_array_missing_fields():
    response = client.post("/couriers",
        json={
            "data": [
                {
                    "courier_id": 1,
                    "regions": [1, 12, 22],
                    "working_hours": ["11:35-14:05", "09:00-11:00"]
                },
                {
                    "courier_id": 2,
                    "courier_type": "foot",
                    "working_hours": ["11:35-14:05", "09:00-11:00"]
                },
                {
                    "courier_id": 3,
                    "courier_type": "foot",
                    "regions": [1, 12, 22],
                }
            ]
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        "validation_error": {
            "couriers": [
                {"id": 1},
                {"id": 2},
                {"id": 3}
            ]
        }
    }


def test_bad_request_json_data_array_extra_fields():
    response = client.post("/couriers",
        json={
            "data": [
                {
                    "courier_id": 1,
                    "courier_type": "foot",
                    "regions": [1, 12, 22],
                    "salary": 10000,
                    "working_hours": ["11:35-14:05", "09:00-11:00"]
                },
                {
                    "courier_id": 2,
                    "courier_type": "car",
                    "regions": [1, 12],
                    "foo": "bar",
                    "working_hours": ["11:35-14:05", "09:00-11:00"]
                },
                {
                    "courier_id": 3,
                    "courier_type": "bike",
                    "regions": [1, 12, 22],
                    "working_hours": ["11:35-14:05", "09:00-11:00"]
                }
            ]
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        "validation_error": {
            "couriers": [
                {"id": 1},
                {"id": 2}
            ]
        }
    }


def test_bad_request_json_data_array_all_fields_bad_values():
    response = client.post("/couriers",
        json={
            "data": [
                {
                    "courier_id": 1,
                    "courier_type": "bus",
                    "regions": [1, 12, 22],
                    "working_hours": ["11:35-14:05", "09:00-11:00"]
                },
                {
                    "courier_id": 2,
                    "courier_type": "car",
                    "regions": ["Moscow", "Tula"],
                    "working_hours": ["11:35-14:05", "09:00-11:00"]
                },
                {
                    "courier_id": 3,
                    "courier_type": "bike",
                    "regions": [1, 12, 22],
                    "working_hours": ["55:55-77:77", "09:00-11:00"]
                }
            ]
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        "validation_error": {
            "couriers": [
                {"id": 1},
                {"id": 2},
                {"id": 3}
            ]
        }
    }


def test_bad_request_json_data_array_all_good():
    response = client.post("/couriers",
        json={
            "data": [
                {
                    "courier_id": 1,
                    "courier_type": "foot",
                    "regions": [1, 12, 22],
                    "working_hours": ["11:35-14:05", "09:00-11:00"]
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


def test_bad_request_json_data_array_all_good_repeat():
    response = client.post("/couriers",
        json={
            "data": [
                {
                    "courier_id": 1,
                    "courier_type": "foot",
                    "regions": [1, 12, 22],
                    "working_hours": ["11:35-14:05", "09:00-11:00"]
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
        "couriers": []
    }
