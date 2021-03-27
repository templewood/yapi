import sys
sys.path.append("../app")

from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


def test_endpoint_1_post_couriers_bad_request_empty_body():
    response = client.post("/couriers")

    assert response.status_code == 400
    assert response.json() == {
        "validation_error": {
            "couriers": []
        }
    }


def test_endpoint_1_post_couriers_bad_request_some_digits():
    response = client.post("/couriers", data="123")

    assert response.status_code == 400
    assert response.json() == {
        "validation_error": {
            "couriers": []
        }
    }


def test_endpoint_1_post_couriers_bad_request_some_chars():
    response = client.post("/couriers", data="data")

    assert response.status_code == 400
    assert response.json() == {
        "validation_error": {
            "couriers": []
        }
    }


def test_endpoint_1_post_couriers_bad_request_empty_json():
    response = client.post("/couriers",
        json={},
    )

    assert response.status_code == 400
    assert response.json() == {
        "validation_error": {
            "couriers": []
        }
    }


def test_endpoint_1_post_couriers_bad_request_json_with_some_random_stuff():
    response = client.post("/couriers",
        json={"foo": "bar"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "validation_error": {
            "couriers": []
        }
    }


def test_endpoint_1_post_couriers_bad_request_json_with_bad_data_value():
    response = client.post("/couriers",
        json={"data": False},
    )

    assert response.status_code == 400
    assert response.json() == {
        "validation_error": {
            "couriers": []
        }
    }


def test_endpoint_1_post_couriers_bad_request_json_with_empty_data_array():
    response = client.post("/couriers",
        json={"data": []},
    )

    assert response.status_code == 400
    assert response.json() == {
        "validation_error": {
            "couriers": []
        }
    }


def test_endpoint_1_post_couriers_bad_request_json_with_bad_items_in_data_array():
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


# def test_post_good_couriers():
#     response = client.post(
#         "/couriers",
#         json={
#             "data": [
#                 {
#                     "courier_id": 1,
#                     "courier_type": "foot",
#                     "regions": [1, 12, 22],
#                     "working_hours": ["11:35-14:05", "09:00-11:00"]
#                 },
#                 {
#                     "courier_id": 2,
#                     "courier_type": "bike",
#                     "regions": [22],
#                     "working_hours": ["09:00-18:00"]
#                 },
#                 {
#                     "courier_id": 3,
#                     "courier_type": "car",
#                     "regions": [12, 22, 23, 33],
#                     "working_hours": []
#                 }
#             ]
#         },
#     )
#     assert response.status_code == 201
#     assert response.json() == {
#         "couriers": [
#             {
#                 "id": 1
#             },
#             {
#                 "id": 2
#             },
#             {
#                 "id": 3
#             }
#         ]
#     }

# def test_post_bad_courier1():
#     response = client.post(
#         "/couriers",
#         json={
#             "data": [
#                 {
#                     "courier_id": 1
#                 }
#             ]
#         },
#     )
#     assert response.status_code == 400
#     assert response.json() == {
#         "validation_error": {
#             "couriers": [
#                 {
#                     "id": 1
#                 }
#             ]
#         }
#     }

# def test_post_bad_courier2():
#     response = client.post(
#         "/couriers",
#         json={ },
#     )
#     assert response.status_code == 400
#     assert response.json() == {
#         "validation_error": {
#             "couriers": []
#         }
#     }
