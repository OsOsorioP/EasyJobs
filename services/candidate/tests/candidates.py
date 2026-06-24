def test_create_candidate_requires_auth(client):
    response = client.post("/api/v1/candidates", json={"name": "Ana", "email": "ana@test.com"})
    assert response.status_code == 401

def test_create_candidate_rejects_candidate_role(client, candidate_token):
    headers = {"Authorization": f"Bearer {candidate_token}"}
    response = client.post(
        "/api/v1/candidates",
        json={"name": "Ana", "email": "ana@test.com"},
        headers=headers,
    )
    assert response.status_code == 403

def test_create_candidate_as_recruiter_succeeds(client, auth_headers):
    response = client.post(
        "/api/v1/candidates",
        json={"name": "Ana Torres", "email": "ana@test.com", "skills": "Python, FastAPI"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Ana Torres"
    assert body["email"] == "ana@test.com"
    assert "id" in body

def test_create_candidate_duplicate_email_returns_409(client, auth_headers):
    payload = {"name": "Ana Torres", "email": "ana@test.com"}
    first = client.post("/api/v1/candidates", json=payload, headers=auth_headers)
    assert first.status_code == 201

    second = client.post("/api/v1/candidates", json=payload, headers=auth_headers)
    assert second.status_code == 409

def test_create_candidate_invalid_email_returns_422(client, auth_headers):
    response = client.post(
        "/api/v1/candidates",
        json={"name": "Ana", "email": "no-es-un-email"},
        headers=auth_headers,
    )
    assert response.status_code == 422

def test_list_candidates_requires_auth(client):
    response = client.get("/api/v1/candidates")
    assert response.status_code == 401

def test_list_candidates_with_any_authenticated_role(client, auth_headers, candidate_token):
    client.post(
        "/api/v1/candidates",
        json={"name": "Ana", "email": "ana@test.com"},
        headers=auth_headers,
    )

    candidate_headers = {"Authorization": f"Bearer {candidate_token}"}
    response = client.get("/api/v1/candidates", headers=candidate_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_get_candidate_not_found(client, auth_headers):
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/v1/candidates/{fake_id}", headers=auth_headers)
    assert response.status_code == 404

def test_get_candidate_success(client, auth_headers):
    created = client.post(
        "/api/v1/candidates",
        json={"name": "Ana", "email": "ana@test.com"},
        headers=auth_headers,
    ).json()

    response = client.get(f"/api/v1/candidates/{created['id']}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "ana@test.com"

def test_update_candidate_as_recruiter(client, auth_headers):
    created = client.post(
        "/api/v1/candidates",
        json={"name": "Ana", "email": "ana@test.com"},
        headers=auth_headers,
    ).json()

    response = client.put(
        f"/api/v1/candidates/{created['id']}",
        json={"name": "Ana Maria", "email": "ana@test.com"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Ana Maria"

def test_patch_candidate_partial_update(client, auth_headers):
    created = client.post(
        "/api/v1/candidates",
        json={"name": "Ana", "email": "ana@test.com", "skills": "Python"},
        headers=auth_headers,
    ).json()

    response = client.patch(
        f"/api/v1/candidates/{created['id']}",
        json={"skills": "Python, Docker"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["skills"] == "Python, Docker"
    assert body["name"] == "Ana"  # no se modificó

def test_delete_candidate_rejects_recruiter_role(client, auth_headers):
    created = client.post(
        "/api/v1/candidates",
        json={"name": "Ana", "email": "ana@test.com"},
        headers=auth_headers,
    ).json()

    response = client.delete(f"/api/v1/candidates/{created['id']}", headers=auth_headers)
    assert response.status_code == 403

def test_delete_candidate_as_admin_succeeds(client, auth_headers, admin_token):
    created = client.post(
        "/api/v1/candidates",
        json={"name": "Ana", "email": "ana@test.com"},
        headers=auth_headers,
    ).json()

    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.delete(f"/api/v1/candidates/{created['id']}", headers=admin_headers)
    assert response.status_code == 204

    follow_up = client.get(f"/api/v1/candidates/{created['id']}", headers=auth_headers)
    assert follow_up.status_code == 404

def test_update_candidate_duplicate_email_returns_409(client, auth_headers):
    client.post(
        "/api/v1/candidates",
        json={"name": "Carlos", "email": "carlos@test.com"},
        headers=auth_headers,
    )
    second = client.post(
        "/api/v1/candidates",
        json={"name": "Ana", "email": "ana@test.com"},
        headers=auth_headers,
    ).json()

    response = client.put(
        f"/api/v1/candidates/{second['id']}",
        json={"name": "Ana", "email": "carlos@test.com"},
        headers=auth_headers,
    )
    assert response.status_code == 409

def test_update_candidate_not_found(client, auth_headers):
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.put(
        f"/api/v1/candidates/{fake_id}",
        json={"name": "Ana", "email": "ana@test.com"},
        headers=auth_headers,
    )
    assert response.status_code == 404

def test_patch_candidate_not_found(client, auth_headers):
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.patch(
        f"/api/v1/candidates/{fake_id}",
        json={"skills": "Go"},
        headers=auth_headers,
    )
    assert response.status_code == 404

def test_delete_candidate_not_found(client, admin_token):
    fake_id = "00000000-0000-0000-0000-000000000000"
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.delete(f"/api/v1/candidates/{fake_id}", headers=headers)
    assert response.status_code == 404

def test_update_candidate_rejects_candidate_role(client, auth_headers, candidate_token):
    created = client.post(
        "/api/v1/candidates",
        json={"name": "Ana", "email": "ana@test.com"},
        headers=auth_headers,
    ).json()

    headers = {"Authorization": f"Bearer {candidate_token}"}
    response = client.put(
        f"/api/v1/candidates/{created['id']}",
        json={"name": "Ana M", "email": "ana@test.com"},
        headers=headers,
    )
    assert response.status_code == 403

def test_delete_candidate_rejects_candidate_role(client, auth_headers, candidate_token):
    created = client.post(
        "/api/v1/candidates",
        json={"name": "Ana", "email": "ana@test.com"},
        headers=auth_headers,
    ).json()

    headers = {"Authorization": f"Bearer {candidate_token}"}
    response = client.delete(f"/api/v1/candidates/{created['id']}", headers=headers)
    assert response.status_code == 403

def test_invalid_jwt_token_returns_401(client):
    headers = {"Authorization": "Bearer token.malformado.aqui"}
    response = client.get("/api/v1/candidates", headers=headers)
    assert response.status_code == 401