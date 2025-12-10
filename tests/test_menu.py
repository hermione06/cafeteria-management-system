import json

def test_menu_list(client):
    res = client.get("/menu/")
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)


def test_menu_create(client):
    data = {
        "name": "Test Dish",
        "price": "5.50",
        "category": "Snacks",
        "description": "Sample",
        "stock": "10"
    }

    res = client.post("/menu/", data=data)
    assert res.status_code == 201
    body = res.get_json()
    assert body["name"] == "Test Dish"
    assert body["price"] == 5.50
    assert body["stock"] == 10


def test_menu_update(client):
    # First create an item
    res = client.post("/menu/", data={
        "name": "Update Dish",
        "price": "2.00",
        "category": "Drinks"
    })
    item_id = res.get_json()["id"]

    # Update it
    update = {"price": 4.00, "stock": 5}
    res2 = client.put(f"/menu/{item_id}", json=update)
    assert res2.status_code == 200

    updated = res2.get_json()
    assert updated["price"] == 4.00
    assert updated["stock"] == 5


def test_menu_delete(client):
    # Create item
    res = client.post("/menu/", data={
        "name": "Delete Dish",
        "price": "3.20",
        "category": "Meals"
    })
    item_id = res.get_json()["id"]

    # Delete
    res2 = client.delete(f"/menu/{item_id}")
    assert res2.status_code == 200
