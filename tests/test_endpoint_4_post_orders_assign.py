import sys
sys.path.append("../app")

from datetime import datetime
from time import sleep
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
                    "working_hours": ["16:35-23:45", "09:00-11:00"]
                },
                {
                    "courier_id": 2,
                    "courier_type": "bike",
                    "regions": [22],
                    "working_hours": ["07:00-09:00"]
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
                },
                {
                    "order_id": 13,
                    "weight": 0.21,
                    "region": 1,
                    "delivery_hours": ["23:48-23:58"]
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
            },
            {
                "id": 13
            }
        ]
    }


def test_bad_post_assign_orders_to_nonexistent_courier():
    response = client.post("/orders/assign",
        json={
            "courier_id": 123456789
        }
    )
    assert response.status_code == 400


def test_empty_post_assign_orders_to_nonworking_courier():
    response = client.post("/orders/assign",
        json={
            "courier_id": 3
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "orders": []
    }


def test_good_post_assign_orders_to_working_courier():
    response = client.post("/orders/assign",
        json={
            "courier_id": 1
        }
    )
    assert response.status_code == 200
    assert response.json().get('orders') == [
        {
            "id": 10
        },
        {
            "id": 12
        }
    ]


def test_good_post_assign_orders_to_working_courier_again():
    response = client.post("/orders/assign",
        json={
            "courier_id": 1
        }
    )
    assert response.status_code == 200
    assert response.json().get('orders') == [
        {
            "id": 10
        },
        {
            "id": 12
        }
    ]


def test_good_post_complete_one_order():
    sleep(0.5)
    response = client.post("/orders/complete",
        json={
            "courier_id": 1,
            "order_id": 10,
            "complete_time": datetime.now().isoformat(timespec='milliseconds')[:-1] + 'Z'
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "order_id": 10
    }


def test_good_post_one_more_assign_request():
    response = client.post("/orders/assign",
        json={
            "courier_id": 1
        }
    )
    assert response.status_code == 200
    assert response.json().get('orders') == [
        {
            "id": 12
        }
    ]


def test_good_post_complete_the_last_order():
    sleep(0.5)
    response = client.post("/orders/complete",
        json={
            "courier_id": 1,
            "order_id": 12,
            "complete_time": datetime.now().isoformat(timespec='milliseconds')[:-1] + 'Z'
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "order_id": 12
    }


def test_good_get_courier_info_upon_order_completion():
    response = client.get("/couriers/1")
    assert response.status_code == 200
    assert response.json() == {
        "courier_id": 1,
        "courier_type": "foot",
        "regions": [
            1,
            12,
            22
        ],
        "working_hours": [
            "16:35-23:45",
            "09:00-11:00"
        ],
        "earnings": 1000
    }
