from app.config import MAX_ACTIVE_LOANS

def create_book(client, copies=1):
    response = client.post(
        "/books",
        json={"title": "Война и мир", "author": "Лев Толстой", "year": 1869, "total_copies": copies},
    )
    assert response.status_code == 201
    return response.json()


def create_reader(client, email="ivan@mail.ru"):
    response = client.post("/readers", json={"name": "Иван Петров", "email": email})
    assert response.status_code == 201
    return response.json()


def issue_book(client, book_id, reader_id):
    return client.post("/loans", json={"book_id": book_id, "reader_id": reader_id})


def test_book_crud(client):
    book = create_book(client)
    assert book["available_copies"] == 1

    response = client.get(f"/books/{book['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == "Война и мир"

    response = client.patch(f"/books/{book['id']}", json={"year": 1870})
    assert response.status_code == 200
    assert response.json()["year"] == 1870

    assert client.delete(f"/books/{book['id']}").status_code == 204
    assert client.get(f"/books/{book['id']}").status_code == 404


def test_issue_and_return_book(client):
    book = create_book(client, copies=1)
    reader = create_reader(client)

    response = issue_book(client, book["id"], reader["id"])
    assert response.status_code == 201
    loan = response.json()
    assert client.get(f"/books/{book['id']}").json()["available_copies"] == 0

    response = client.post(f"/loans/{loan['id']}/return")
    assert response.status_code == 200
    assert response.json()["return_date"] is not None
    assert client.get(f"/books/{book['id']}").json()["available_copies"] == 1

    assert client.post(f"/loans/{loan['id']}/return").status_code == 409


def test_cannot_issue_book_without_free_copies(client):
    book = create_book(client, copies=1)
    first = create_reader(client, "first@mail.ru")
    second = create_reader(client, "second@mail.ru")

    assert issue_book(client, book["id"], first["id"]).status_code == 201
    response = issue_book(client, book["id"], second["id"])
    assert response.status_code == 409
    assert response.json()["detail"] == "Нет свободных экземпляров книги"


def test_reader_loan_limit(client):
    book = create_book(client, copies=MAX_ACTIVE_LOANS + 1)
    reader = create_reader(client)

    for _ in range(MAX_ACTIVE_LOANS):
        assert issue_book(client, book["id"], reader["id"]).status_code == 201
    assert issue_book(client, book["id"], reader["id"]).status_code == 409


def test_cannot_delete_reader_with_active_loan(client):
    book = create_book(client)
    reader = create_reader(client)
    loan = issue_book(client, book["id"], reader["id"]).json()

    assert client.delete(f"/readers/{reader['id']}").status_code == 409

    client.post(f"/loans/{loan['id']}/return")
    assert client.delete(f"/readers/{reader['id']}").status_code == 204


def test_errors(client):
    assert client.post("/books", json={"title": "", "author": "X"}).status_code == 422
    assert client.post("/readers", json={"name": "Иван", "email": "bad"}).status_code == 422
    assert client.get("/books/999").status_code == 404
    assert issue_book(client, 999, 999).status_code == 404

    create_reader(client, "same@mail.ru")
    response = client.post("/readers", json={"name": "Другой", "email": "same@mail.ru"})
    assert response.status_code == 409
