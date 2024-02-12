import os

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from main import app
from app import get_db


DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(
    DATABASE_URL,
    poolclass = StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

client = TestClient(app)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

def setup() -> None:
    # create the tables in the test database
    # metadata.create_all(bind=engine)
    pass


def teardown() -> None:
    # Drop the tables in the test database 
    # CAUTION: if test database if different
    # metadata.drop_all(bind=engine)
    pass


def test_invite(client):
    login_response = client.post(
        "/login",
        data={"username": "bagdad@gmail.com", "password": "bagdad"}
    )
    
    # Check if login was successful and get the token
    assert login_response.status_code == 200
    token = login_response.json()['access_token']
    
    # Prepare invitation data
    invitation_data = {
        "full_name": "Sakib Al Hasan",
        "email": "sakb@gmail.com",
        "organization": "ABC",
        "organizational_role": "user",
        "role": "user"
    }

    # Send invitation using the '/invite' endpoint with the authorization token
    response = client.post(
        "/invitation/invite",
        json=invitation_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    # Check if the invitation was successfully sent
    assert response.status_code == 200
    assert response.json() == {"message": "Invitation sent successfully"}
