import sys
sys.path.append("../app")

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_post_good_couriers():
    response = client.post(
        "/couriers",
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

def test_post_bad_courier1():
    response = client.post(
        "/couriers",
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

def test_post_bad_courier2():
    response = client.post(
        "/couriers",
        json={ },
    )
    assert response.status_code == 400
    assert response.json() == {
        "validation_error": {
            "couriers": []
        }
    }
