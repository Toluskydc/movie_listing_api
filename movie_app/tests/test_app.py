import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from datetime import date
import uuid

from movie_app.database import Base, get_db
from movie_app.main import app
from movie_app.auth import get_current_user, create_access_token
import movie_app.models as models
from movie_app.models import Base, User, Movie, Rating
from movie_app.auth import pwd_context
from movie_app.database import SessionLocal


SQLALCHEMY_DATABASE_URL = "sqlite:///"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}, 
    poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



# Override the get_db dependency to use the test database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Mocking current_user dependency
def mock_get_current_user():
    return models.User(id=1, username="testuser", first_name="Test", last_name="User", email="testuser@example.com", phone_number="+12345678901", hashed_password="hashed")

app.dependency_overrides[get_current_user] = mock_get_current_user

Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c



@pytest.fixture(scope="function")
def setup_database():
    Base.metadata.create_all(bind=engine)

    # Cleanup data before each test
    with TestingSessionLocal() as db_session:
        db_session.query(models.Movie).delete()
        db_session.query(models.User).delete()
        db_session.commit()

    yield
    Base.metadata.drop_all(bind=engine)



@pytest.fixture(scope="module")
def setup_database_with_user():
    Base.metadata.create_all(bind=engine)
    client = TestClient(app)
    client.post("/signup", json={
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "+12345678901",
        "email": "testuser@example.com",
        "password": "testpassword"
    })
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def setup_movie_data(client, setup_database):
    # Add specific movie data for get_movie_by_id tests
    with TestingSessionLocal() as db_session:
        # Adding movie data with correct date format
        movie = models.Movie(
            id=51, 
            title="Test Movie", 
            description="A test movie", 
            release_date=date(2024, 7, 23),  # Use date object here
            user_id=87
        )
        db_session.add(movie)
        db_session.commit()

    yield client



def hash_password(password: str) -> str:
    return pwd_context.hash(password)

@pytest.fixture(scope="function")
def setup_user_and_movies(setup_database):
    db = TestingSessionLocal()
    try:
        # Create a user with hashed password
        hashed_password = hash_password("testpassword")
        user = models.User(
            username="testuser",
            hashed_password=hashed_password,
            first_name="Test",
            last_name="User",
            phone_number="+12345678901",
            email="testuser@example.com"
        )
        db.add(user)
        db.commit()

        # Create movies for the user
        movie = models.Movie(
            id=1,
            title="User's Movie",
            description="A movie created by the user",
            release_date=date(2024, 7, 24),  # Use date object here
            user_id=user.id
        )
        db.add(movie)
        db.commit()

        # Create another user and movie
        other_user = models.User(
            username="otheruser",
            hashed_password=hash_password("otherpassword"),
            first_name="Other",
            last_name="User",
            phone_number="+12345678901",
            email="otheruser@example.com"
        )
        db.add(other_user)
        db.commit()
        
        other_movie = models.Movie(
            id=2,
            title="Other User's Movie",
            description="A movie created by another user",
            release_date=date(2024, 7, 25),  # Use date object here
            user_id=other_user.id
        )
        db.add(other_movie)
        db.commit()

    finally:
        db.close()
    return user

    


@pytest.fixture(scope="module")
def setup_movie_database_with_user():
    # Create the database schema
    Base.metadata.create_all(bind=engine)
    
    # Create a test user
    with TestingSessionLocal() as db_session:
        hashed_password = hash_password("testpassword")
        user = models.User(
            username="testuser",
            hashed_password=hashed_password,
            first_name="Test",
            last_name="User",
            phone_number="+12345678901",
            email="testuser@example.com"
        )
        db_session.add(user)
        db_session.commit()

    yield
    Base.metadata.drop_all(bind=engine)


def get_auth_token(client: TestClient, username: str, password: str):
    response = client.post("/token", data={"username": username, "password": password})
    return response.json().get("access_token")


@pytest.fixture(scope="function")
def verify_movie_data():
    with TestingSessionLocal() as db_session:
        movie = db_session.query(models.Movie).filter_by(id=2).first()
        print(f"Directly fetched movie: {movie}")


@pytest.fixture(scope="function")
def setup_movie_update_database_with_user(client: TestClient):
    Base.metadata.create_all(bind=engine)
    with TestingSessionLocal() as db_session:
        # Ensure user ID 1 exists; create it if not
        user = db_session.query(models.User).filter_by(id=1).first()
        if user is None:
            hashed_password = hash_password("testpassword")
            user = models.User(
                id=1,  # Set user ID to 1
                username="testuser",
                hashed_password=hashed_password,
                first_name="Test",
                last_name="User",
                phone_number="+12345678901",
                email="testuser@example.com"
            )
            db_session.add(user)
            db_session.commit()
            db_session.refresh(user)
        
        movie = models.Movie(
            title="Original Title",
            description="Original description",
            release_date=date(2024, 7, 24),
            user_id=user.id
        )
        db_session.add(movie)
        db_session.commit()
        db_session.refresh(movie)

        # Debug print to verify movie data
        movie_data = db_session.query(models.Movie).filter_by(id=movie.id).first()
        print(f"Setup Movie ID: {movie.id}")
        print(f"Directly fetched movie: {movie_data}")

        yield {"user": user, "movie": movie}

    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def setup_movie_delete_database_with_user(client: TestClient):
    Base.metadata.create_all(bind=engine)
    with TestingSessionLocal() as db_session:
        user = db_session.query(models.User).filter_by(id=1).first()
        if user is None:
            hashed_password = hash_password("testpassword")
            user = models.User(
                id=1,
                username="testuser",
                hashed_password=hashed_password,
                first_name="Test",
                last_name="User",
                phone_number="+12345678901",
                email="testuser@example.com"
            )
            db_session.add(user)
            db_session.commit()
            db_session.refresh(user)

        movie = models.Movie(
            title="Movie to Delete",
            description="Description of the movie",
            release_date=date(2024, 8, 1),
            user_id=user.id
        )
        db_session.add(movie)
        db_session.commit()
        db_session.refresh(movie)

        # Adding a movie for a different user
        other_user = models.User(
            id=2,
            username="otheruser",
            hashed_password=hashed_password,
            first_name="Other",
            last_name="User",
            phone_number="+09876543210",
            email="otheruser@example.com"
        )
        db_session.add(other_user)
        db_session.commit()

        other_movie = models.Movie(
            title="Other Movie",
            description="Description of another movie",
            release_date=date(2024, 8, 2),
            user_id=other_user.id
        )
        db_session.add(other_movie)
        db_session.commit()

        yield {"user": user, "movie": movie, "other_movie": other_movie}

    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def setup_user_and_movies_cooment():
    with TestingSessionLocal() as db_session:
        # Create a user with a unique ID
        hashed_password = hash_password("testpassword")
        user = models.User(
            username="testuser",
            hashed_password=hashed_password,
            first_name="Test",
            last_name="User",
            phone_number="+12345678901",
            email="testuser@example.com"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Create a movie with a unique ID
        movie = models.Movie(
            id=int(uuid.uuid4().int & (1<<31)-1),  # Use a unique integer ID
            title="User's Movie",
            description="A movie created by the user",
            release_date=date(2024, 7, 24),
            user_id=user.id
        )
        db_session.add(movie)
        db_session.commit()

        yield user, movie

        # Cleanup after test
        db_session.query(models.Movie).filter_by(user_id=user.id).delete()
        db_session.query(models.User).filter_by(id=user.id).delete()
        db_session.commit()

@pytest.fixture(scope="function")
def setup_movie_with_parent_comment(client: TestClient, setup_user_and_movies_cooment):
    user, movie = setup_user_and_movies_cooment
    movie_id = movie.id

    with TestingSessionLocal() as db_session:
        # Add a parent comment
        parent_comment = models.Comment(
            comment_text="This is a parent comment",
            movie_id=movie_id,
            user_id=user.id,
            parent_comment_id=None
        )
        db_session.add(parent_comment)
        db_session.commit()
        db_session.refresh(parent_comment)
        parent_comment_id = parent_comment.id

    yield movie_id, parent_comment_id

    # Cleanup after test
    with TestingSessionLocal() as db_session:
        db_session.query(models.Comment).filter_by(movie_id=movie_id).delete()
        db_session.commit()


@pytest.fixture(scope="function")
def setup_comments_with_nested(client: TestClient, setup_user_and_movies_cooment):
    user, movie = setup_user_and_movies_cooment

    with TestingSessionLocal() as db_session:
        # Create a parent comment
        parent_comment = models.Comment(
            comment_text="Parent comment",
            movie_id=movie.id,
            user_id=user.id,
            parent_comment_id=None
        )
        db_session.add(parent_comment)
        db_session.commit()
        db_session.refresh(parent_comment)

        # Create nested comments
        nested_comment1 = models.Comment(
            comment_text="Nested comment 1",
            movie_id=movie.id,
            user_id=user.id,
            parent_comment_id=parent_comment.id
        )
        nested_comment2 = models.Comment(
            comment_text="Nested comment 2",
            movie_id=movie.id,
            user_id=user.id,
            parent_comment_id=parent_comment.id
        )
        db_session.add(nested_comment1)
        db_session.add(nested_comment2)
        db_session.commit()

        # Yield parent comment ID and nested comment IDs
        yield parent_comment.id, nested_comment1.id, nested_comment2.id

        # Cleanup after the test
        db_session.query(models.Comment).filter(models.Comment.parent_comment_id == parent_comment.id).delete()
        db_session.query(models.Comment).filter(models.Comment.id == parent_comment.id).delete()
        db_session.commit()



@pytest.fixture
def token(client: TestClient):
    # Authenticate a test user and get the token
    response = client.post("/login", data={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    return response.json().get("access_token")







# User testings

# /signup endpoint test
@pytest.mark.parametrize(
    "username, password, first_name, last_name, phone_number, email, expected_status",
    [
        ("testuser1", "testpassword", "Test", "User", "+12345678901", "testuser1@example.com", 200),  # Valid data
        ("testuser2", "testpassword", "Test", "User", "12345678901", "testuser2@example.com", 200),  # Valid data without '+'
        ("testuser3", "testpassword", "Test", "User", "7544", "testuser3@example.com", 422),  # Incomplete phone number
        ("testuser4", "testpassword", "Test", "User", "789P", "testuser4@example.com", 422),  # Incorrect phone number
        ("testuser5", "testpassword", "Test", "User", "+12345678901", "correctemail@example.com", 200),  # Valid data with correct email
        ("testuser6", "testpassword", "Test", "User", "+12345678901", "incorrectemail", 422)  # Incorrect email
    ]
)
def test_signup(client: TestClient, username, password, first_name, last_name, phone_number, email, expected_status):
    response = client.post("/signup", json={
        "username": username,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "phone_number": phone_number,
        "email": email
    })
    
    assert response.status_code == expected_status
    
    if expected_status == 422:
        response_json = response.json()
        assert 'detail' in response_json
        errors = response_json['detail']
        assert len(errors) > 0
        # Check if there is at least one error message
        assert all('msg' in error for error in errors)
        assert all('loc' in error for error in errors)
    else:
        response_json = response.json()
        assert response_json.get("username") == username
        assert response_json.get("first_name") == first_name
        assert response_json.get("last_name") == last_name
        assert response_json.get("phone_number") == phone_number
        assert response_json.get("email") == email

    

# /login endpoint test
@pytest.mark.parametrize(
    "username, password, expected_status, expected_detail",
    [
        ("testuser", "testpassword", 200, None),  # Successful login
        ("wronguser", "testpassword", 401, "Incorrect username or password"),  # Incorrect username
        ("testuser", "wrongpassword", 401, "Incorrect username or password"),  # Incorrect password
    ]
)
def test_login(client: TestClient, setup_database_with_user, username: str, password: str, expected_status: int, expected_detail: str):
    response = client.post("/login", data={"username": username, "password": password})
    assert response.status_code == expected_status
    if expected_detail:
        assert response.json() == {"detail": expected_detail}
    else:
        assert "access_token" in response.json()



# /update endpoint test
@pytest.mark.parametrize("update_data, expected_status_code", [
    ({"email": "newemail@example.com"}, 200),  # Valid email update
    ({"email": "invalidemail"}, 422),          # Invalid email format
    ({"phone_number": "+12345678901"}, 200),   # Valid phone number update
    ({"phone_number": "1234"}, 422),           # Invalid phone number format
    ({"email": "newemail@example.com", "phone_number": "+12345678901"}, 200),  # Valid update
    ({"email": "newemail@example.com", "phone_number": "1234"}, 422),  # Invalid phone number format
])
def test_update_profile(update_data, expected_status_code, client, token):
    response = client.put(
        "/users/me",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == expected_status_code




# Movies testings


# get all movies
@pytest.mark.parametrize(
    "offset, limit, expected_status_code",
    [
        (0, 10, 200),   # valid offset and limit
        (0, 0, 200),    # limit of 0 should return an empty list with status 200
        (1, 10, 200),   # valid offset and limit with offset > 0
        (1000, 10, 200) # large offset value to test edge cases
    ]
)
def test_get_movies(offset, limit, expected_status_code, client):
    response = client.get(f"/movies/?offset={offset}&limit={limit}")
    assert response.status_code == expected_status_code
    if expected_status_code == 200:
        assert "message" in response.json()
        assert "data" in response.json()
        assert isinstance(response.json()["data"], list)



# get movie by ID
@pytest.mark.parametrize("movie_id", [51, 84])
def test_get_movie_by_id(setup_movie_data, movie_id):
    response = setup_movie_data.get(f"/movie/{movie_id}")

    if movie_id == 51:
        # Expected to find the movie
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == movie_id
        assert data["title"] == "Test Movie"
        assert data["description"] == "A test movie"
        assert data["release_date"] == "2024-07-23"
        assert data["user_id"] == 87
        assert data["comments"] == []
        assert data["ratings"] == []
    else:
        # Expected to not find the movie
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Movie not found!"



# get movies for a specific user
@pytest.mark.parametrize("username, password", [("testuser", "testpassword")])
def test_get_movie_for_user(client: TestClient, setup_user_and_movies, username, password):
    # Simulate token creation
    token = create_access_token(data={"sub": username})
    
    # Access the movies endpoint with authentication
    response = client.get("/movies/user", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"
    data = response.json()
    assert "data" in data
    




# create a new movie
@pytest.mark.parametrize("username, password", [("testuser", "testpassword")])
def test_create_movie(client, setup_movie_database_with_user, username, password):
    # Simulate login and get token
    response = client.post("/login", data={"username": username, "password": password})
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Create a movie
    movie_data = {"title": "Test Movie", "description": "Test description", "release_date": "2024-07-24"}
    response = client.post("/new_movies", json=movie_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Movie"
    assert data["description"] == "Test description"
    assert data["release_date"] == "2024-07-24"



# update a movie
@pytest.mark.parametrize("payload, expected_status", [
    ({"title": "Updated Title", "description": "Updated description", "release_date": "2024-08-01"}, 200),
    ({"title": "Updated Title"}, 200),  # Ensure title is provided for successful update
    ({"title": ""}, 422),  # Expect validation error for empty title
    ({"title": "Updated Title"}, 404),  # Assuming movie ID 9999 does not exist
])
def test_update_movie(payload, expected_status, setup_movie_update_database_with_user, client: TestClient):
    user = setup_movie_update_database_with_user["user"]
    movie = setup_movie_update_database_with_user["movie"]

    # Ensure the token and URL are consistent
    token = get_auth_token(client, user.username, "testpassword")
    url = f"/movie_update/{movie.id if expected_status != 404 else '9999'}"

    print(f"Testing with Movie ID: {movie.id}")  # Debug print
    print(f"Request URL: {url}")  # Debug print

    response = client.put(url, json=payload, headers={"Authorization": f"Bearer {token}"})

    print(f"Response status: {response.status_code}")  # Debug print
    print(f"Response body: {response.json()}")  # Debug print

    assert response.status_code == expected_status



# delete movie
@pytest.mark.parametrize("movie_id, expected_status, expected_response", [
    (1, 200, {
        "message": "success",
        "data": {
            "id": 1,
            "title": "Movie to Delete",
            "description": "Description of the movie",
            "release_date": "2024-08-01",
            "user_id": 1
        }
    }), 
    (9999, 404, {"detail": "Movie not found"}),
    (2, 404, {"detail": "Movie not found"})  # Movie exists but not owned by user
])
def test_delete_movie(movie_id, expected_status, expected_response, setup_movie_delete_database_with_user, client: TestClient):
    user = setup_movie_delete_database_with_user["user"]
    token = get_auth_token(client, user.username, "testpassword")
    
    url = f"/movie_delete/{movie_id}"
    response = client.delete(url, headers={"Authorization": f"Bearer {token}"})
    
    print(f"Actual response: {response.json()}")  # Debug print
    assert response.status_code == expected_status
    assert response.json() == expected_response




# Comments Testing

# Add comments
@pytest.mark.parametrize("comment_data, expected_status, expected_response", [
    ({"comment_text": "Great movie!"}, 200, None),  # Expected response for successful comment creation
    ({"comment_text": "Great movie!"}, 404, {"detail": "Movie not found"}),  # Case when movie is not found
    ({}, 422, {"detail": [{"type": "missing", "loc": ["body", "comment_text"], "msg": "Field required", "input": {}}]})  # Case when comment_text is missing
])
def test_add_comment(comment_data, expected_status, expected_response, client: TestClient):
    # Ensure tables are created
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    # Create a unique username for each test
    unique_username = f"testuser_{uuid.uuid4().hex[:6]}"
    hashed_password = pwd_context.hash("testpassword")
    user = User(username=unique_username, first_name="Test", last_name="User", email=f"{unique_username}@example.com", phone_number="+12345678901", hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)

    # Determine whether to create a movie or not based on the expected status
    if expected_status != 404:
        # Create movie only if we're not testing the "movie not found" scenario
        movie = Movie(title="Test Movie", description="Test Description", release_date=date(2023, 1, 1), user_id=user.id)
        db.add(movie)
        db.commit()
        db.refresh(movie)
        movie_id = movie.id
    else:
        # Use a non-existent movie ID to trigger the 404
        movie_id = 9999

    # Generate token for the user
    token = create_access_token(data={"sub": user.username})

    # Test the add comment endpoint with the provided parameters
    response = client.post(f"/movies/{movie_id}/comments/", json=comment_data, headers={"Authorization": f"Bearer {token}"})

    # Check for expected status and response
    assert response.status_code == expected_status
    if expected_response:
        assert response.json() == expected_response

    db.close()

# Get comments
@pytest.mark.parametrize("movie_id, skip, limit, expected_status, expected_response", [
    (1, 0, 10, 200, [{"id": 1, "comment_text": "Great movie!", "movie_id": 1, "user_id": 1, "parent_comment_id": None, "replies": []}]),
    (1, 0, 1, 200, [{"id": 1, "comment_text": "Great movie!", "movie_id": 1, "user_id": 1, "parent_comment_id": None, "replies": []}]),
    (1, 1, 10, 200, []),  # Assuming only 1 comment exists and we skip it
    (999, 0, 10, 404, {"detail": "Movie not found"}),  # Invalid movie_id
])
def test_get_comments(movie_id, skip, limit, expected_status, expected_response, client: TestClient):
    response = client.get(f"/movies/{movie_id}/comments/?skip={skip}&limit={limit}")
    
    assert response.status_code == expected_status
    
    if expected_status == 200:
        assert response.json() == expected_response
    else:
        assert response.json() == expected_response


# Add nested comments
def test_add_nested_comment(client: TestClient, setup_movie_with_parent_comment):
    movie_id, parent_comment_id = setup_movie_with_parent_comment

    # Add a nested comment
    response = client.post(f"/comments/{parent_comment_id}/replies/", json={
        "comment_text": "This is a nested comment"
    })
    assert response.status_code == 200

    nested_comment = response.json()
    assert nested_comment["parent_comment_id"] == parent_comment_id
    assert nested_comment["comment_text"] == "This is a nested comment"

    # Verify the nested comment is added
    with TestingSessionLocal() as db_session:
        added_comment = db_session.query(models.Comment).filter_by(id=nested_comment["id"]).first()
        assert added_comment is not None
        assert added_comment.parent_comment_id == parent_comment_id

# Delete comments and nessted comment not authorized
def test_delete_comment_not_authorized(client: TestClient, setup_comments_with_nested):
    parent_comment_id, _, _ = setup_comments_with_nested

    # Create and authenticate a different user
    response = client.post("/signup", json={
        "username": "otheruser",
        "first_name": "Other",
        "last_name": "User",
        "phone_number": "+1234567890",
        "email": "otheruser@example.com",
        "password": "otherpassword"
    })
    assert response.status_code == 200

    # Attempt to obtain a token for the new user
    token_response = get_auth_token(client, "otheruser", "otherpassword")
    if token_response is None:
        print("Failed to obtain token for 'otheruser'.")
    else:
        print("Token Response Status Code:", token_response.status_code)
        print("Token Response JSON:", token_response.json())
        new_user_token = token_response.json().get("access_token")

        # Perform the delete request as the different user
        response = client.delete(f"/comments/{parent_comment_id}/", headers={"Authorization": f"Bearer {new_user_token}"})

        # Print response for debugging
        print("Response Status Code:", response.status_code)
        print("Response JSON:", response.json())

        assert response.status_code == 403



# Ratings Testing

# Add ratings
def setup_test_data(db_session):
    # Clean up any existing data
    db_session.query(Rating).delete()
    db_session.query(Movie).delete()
    db_session.query(User).delete()
    db_session.commit()

    # Create user with unique ID
    hashed_password = hash_password("testpassword")
    user = User(
        id=1,  # Ensure this ID is used consistently
        username="testuser",
        hashed_password=hashed_password,
        first_name="Test",
        last_name="User",
        phone_number="+12345678901",
        email="testuser@example.com"
    )
    db_session.add(user)
    db_session.commit()

    # Create movie with unique ID
    movie_id = int(uuid.uuid4().int & (1<<31)-1)  # Use a unique integer ID
    movie = Movie(
        id=movie_id,
        title="Test Movie",
        description="A test movie",
        release_date=date(2024, 7, 23),
        user_id=user.id
    )
    db_session.add(movie)
    db_session.commit()

    return user, movie_id

@pytest.mark.parametrize("rating, expected_status_code", [(5, 200), (0, 422), (11, 422)])
def test_add_rating(rating, expected_status_code):
    client = TestClient(app)

    # Setup test data
    with TestingSessionLocal() as db_session:
        movie_id = setup_test_data(db_session)

        # Obtain auth token
        token = get_auth_token(client, "testuser", "testpassword")

    # Test adding rating
    response = client.post(
        f"/movies/{movie_id}/ratings/",
        headers={"Authorization": f"Bearer {token}"},
        json={"rating": rating}
    )

    # Debug print response
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.json()}")

    # Check response status code
    assert response.status_code == expected_status_code

    if response.status_code == 200:
        # Check response content
        data = response.json()
        assert data["rating"] == rating
        assert data["movie_id"] == movie_id
        assert data["user_id"] == 1  # Check the user ID directly

    elif response.status_code == 422:
        # Check if response content indicates validation error
        data = response.json()
        assert "detail" in data

    # Clean up database
    with TestingSessionLocal() as db_session:
        db_session.query(models.Rating).delete()
        db_session.query(models.Movie).delete()
        db_session.query(models.User).delete()
        db_session.commit()

# Get ratings
def setup_test_data(db_session):
    # Clean up any existing data
    db_session.query(Rating).delete()
    db_session.query(Movie).delete()
    db_session.query(User).delete()
    db_session.commit()

    # Create user with unique ID
    hashed_password = hash_password("testpassword")
    user = User(
        id=1,  # Ensure this ID is used consistently
        username="testuser",
        hashed_password=hashed_password,
        first_name="Test",
        last_name="User",
        phone_number="+12345678901",
        email="testuser@example.com"
    )
    db_session.add(user)
    db_session.commit()  # Commit to ensure the user is saved and has an ID

    # Create movie with unique ID
    movie_id = int(uuid.uuid4().int & (1<<31)-1)  # Use a unique integer ID
    movie = Movie(
        id=movie_id,
        title="Test Movie",
        description="A test movie",
        release_date=date(2024, 7, 23),
        user_id=user.id
    )
    db_session.add(movie)
    db_session.commit()  # Commit to ensure the movie is saved

    # Add ratings
    ratings = [
        Rating(rating=5, movie_id=movie_id, user_id=user.id),
        Rating(rating=7, movie_id=movie_id, user_id=user.id),
        Rating(rating=8, movie_id=movie_id, user_id=user.id) 
    ]
    db_session.add_all(ratings)
    db_session.commit()  # Commit to ensure the ratings are saved

    return user, movie_id

@pytest.mark.parametrize("expected_ratings, skip, limit", [
    ([5, 7, 8], 0, 10),  # Expecting all ratings
    ([5], 0, 1),         # Expecting only the first rating
    ([7, 8], 1, 10),     # Expecting ratings starting from the second
])
def test_get_ratings(expected_ratings, skip, limit):
    client = TestClient(app)

    # Setup test data
    with TestingSessionLocal() as db_session:
        movie_id = setup_test_data(db_session)

    # Test fetching ratings
    response = client.get(
        f"/movies/{movie_id}/ratings/",
        params={"skip": skip, "limit": limit}
    )

    # Debug print response
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.json()}")

    # Check response status code
    assert response.status_code == 200
    data = response.json()

    # Check response content
    ratings = [rating['rating'] for rating in data]
    assert ratings == expected_ratings

    # Clean up database
    with TestingSessionLocal() as db_session:
        db_session.query(models.Rating).delete()
        db_session.query(models.Movie).delete()
        db_session.query(models.User).delete()
        db_session.commit()


# Get average rating
def setup_test_data(db_session):
    # Clean up any existing data
    db_session.query(models.Rating).delete()
    db_session.query(models.Movie).delete()
    db_session.query(models.User).delete()
    db_session.commit()

    # Create user with unique ID
    hashed_password = hash_password("testpassword")
    user = models.User(
        id=1,  # Ensure this ID is used consistently
        username="testuser",
        hashed_password=hashed_password,
        first_name="Test",
        last_name="User",
        phone_number="+12345678901",
        email="testuser@example.com"
    )
    db_session.add(user)
    db_session.commit()

    # Create movie with unique ID
    movie_id = int(uuid.uuid4().int & (1<<31)-1)  # Use a unique integer ID
    movie = models.Movie(
        id=movie_id,
        title="Test Movie",
        description="A test movie",
        release_date=date(2024, 7, 23),
        user_id=user.id
    )
    db_session.add(movie)
    db_session.commit()

    # Add ratings
    ratings = [
        models.Rating(rating=5, movie_id=movie_id, user_id=user.id),
        models.Rating(rating=7, movie_id=movie_id, user_id=user.id),
        models.Rating(rating=8, movie_id=movie_id, user_id=user.id)
    ]
    db_session.add_all(ratings)
    db_session.commit()

    return movie_id






