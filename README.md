## **Title**: Movie Listing API using FastAPI  
**Subtitle**: Featuring Secure and Public Endpoints


### **Project Overview**

#### Introduction
The goal of this capstone project is to develop a **Movie Listing API using FastAPI**. The API allows users to perform various actions related to movie listings, such as viewing listed movies, rating them, and adding comments. The application is secured using JWT (JSON Web Tokens), ensuring that only the user who listed a movie can edit or delete it. Additionally, the API is designed to provide both public and authenticated endpoints, offering flexibility and security. 

#### Goals and Purpose
- **User Interaction:** Enable users to interact with movie listings by adding, viewing, and editing movies.
- **Secure Operations:** Protect user-specific operations, such as editing and deleting movies, with JWT-based authentication.
- **Data Integrity:** Maintain the integrity of movie data through secure user-specific interactions and validations.
- **Scalability and Performance:** Ensure the API is scalable and performs efficiently even as the number of users and movies grows.

#### Tech Stack
- **Python:** The primary server-side programming language.
- **FastAPI:** The web framework used to build the API, known for its speed and ease of use.
- **SQLAlchemy:** ORM used for database interactions.
- **PostgreSQL:** The relational database used for storing movie and user data.
- **Render:** Cloud hosting platform used to deploy and manage the application.

#### Key Features
- **User Authentication:**
  - User registration and login.
  - JWT token generation for secure authentication.
  
- **Movie Listing:**
  - View movies (public access).
  - Add movies (authenticated access).
  - Edit and delete movies (restricted to the user who listed them).
  - List all movies with pagination support.

- **Movie Rating:**
  - Rate a movie (authenticated access).
  - Retrieve ratings for a specific movie (public access).
  - Calculate and display the average rating for a movie.

- **Comments:**
  - Add comments to a movie (authenticated access).
  - View comments on a movie (public access).
  - Add nested replies to existing comments (authenticated access).

- **Error Handling and Logging:**
  - Robust error handling with appropriate HTTP status codes.
  - Logging for monitoring application behavior and debugging.

---

###  **Installation and Setup**

#### Prerequisites
Before setting up the project, ensure you have the following software and tools installed on your local machine:
- **Python 3.12.3**
- **Visual Studio Code (VSCode)** or any other preferred code editor
- **Git** for version control

#### Installation Steps
Follow these steps to set up the project on your local machine:

1. **Clone the Repository**:
   Open your terminal or command prompt and run the following command to clone the project repository:
   ```bash
   git clone <https://github.com/Toluskydc/movie_listing_api>
   ```

2. **Create a Virtual Environment**:
   Navigate to the cloned repository directory and create a virtual environment by running:
   ```bash
   python3 -m venv <env-name>
   ```
   Replace `<env-name>` with your preferred name for the virtual environment.

3. **Activate the Virtual Environment**:
   - On **Windows**:
     ```bash
     <env-name>\Scripts\activate.bat
     ```
     Alternatively, you can use:
     ```bash
     .\<env-name>\Scripts\Activate
     ```
   - On **macOS/Linux**:
     ```bash
     source <env-name>/bin/activate
     ```

4. **Install Dependencies**:
   Once the virtual environment is activated, install the required dependencies by running:
   ```bash
   pip install -r requirements.txt
   ```
   This command will install all the necessary packages listed in the `requirements.txt` file.

5. **Set Up Environment Variables**:
   Create a `.env` file in the root directory of your project. This file will store all the necessary environment variables, including:
   - **DATABASE_URL**: The URL for your PostgreSQL database.
   - **SECRET_KEY**: A secret key for JWT token generation.
   - **ALGORITHM**: The algorithm used for JWT (typically "HS256").
   - **ACCESS_TOKEN_EXPIRE_MINUTES**: The number of minutes until the access token expires.

   Example `.env` file:
   ```env
   DATABASE_URL=your_database_url
   SECRET_KEY=your_secret_key
   ALGORITHM=your_algorithm
   ACCESS_TOKEN_EXPIRE_MINUTES=your_minutes
   ```

#### Optional:
- **Configure VSCode**:
  If you are using VSCode, you may want to install relevant extensions like Python, Pylance, and others to enhance your development experience.

- **Database Setup**:
  Ensure your PostgreSQL database is running and accessible. You may need to create a database for the project before starting.

---

### **API Documentation**

#### **Swagger/OpenAPI Access**
- **How API Documentation is Generated**: FastAPI automatically generates an interactive API documentation using OpenAPI and Swagger. This is a built-in feature of FastAPI that doesn't require additional setup. When you define your API routes using FastAPI, it automatically documents them with the necessary request/response formats, parameters, and descriptions based on your code.
  
- **Accessing the Documentation**: 
  1. **Activate the Environment**: Make sure you have your virtual environment activated.
  2. **Run the Application**: Navigate to the movie directory and run the following command:
     ```
     uvicorn movie_app.main:app --reload
     ```
  3. **Open Swagger UI**: Once the application is running, open your browser and go to `http://localhost:8000/docs#/` to access the interactive Swagger UI. This page allows you to explore and test your API endpoints directly from the browser.
  4. **Open Redoc**: Alternatively, you can visit `http://localhost:8000/redoc` for a different style of API documentation provided by ReDoc.

#### **Endpoint Descriptions**

##### **User Endpoints**
- **Signup** (`POST /signup`): Allows a new user to register by providing a username, email, and password. The password is hashed before being stored in the database.
- **Login** (`POST /login`): Authenticates a user using their username and password, returning a JWT token upon successful login.
- **Update Profile** (`PUT /users/me`): Enables the currently authenticated user to update their profile information.

##### **Movie Endpoints**
- **List Movies** (`GET /movies/`): Retrieves a paginated list of movies with optional `offset` and `limit` query parameters.
- **Get Movie by ID** (`GET /movie/{movie_id}`): Fetches details of a specific movie by its ID.
- **List User's Movies** (`GET /movies/user`): Retrieves a list of movies created by the currently authenticated user.
- **Create Movie** (`POST /new_movies`): Allows an authenticated user to create a new movie entry.
- **Update Movie** (`PUT /movie_update/{movie_id}`): Enables an authenticated user to update a movie they created, identified by its ID.
- **Delete Movie** (`DELETE /movie_delete/{movie_id}`): Allows an authenticated user to delete a movie they created.

##### **Comment Endpoints**
- **Add Comment** (`POST /movies/{movie_id}/comments/`): Enables an authenticated user to add a comment to a specific movie.
- **Get Comments** (`GET /movies/{movie_id}/comments/`): Retrieves a paginated list of comments for a specific movie.
- **Add Reply to Comment** (`POST /comments/{parent_comment_id}/replies/`): Allows an authenticated user to add a reply to an existing comment.
- **Delete Comment** (`DELETE /comments/{comment_id}/`): Enables an authenticated user to delete their own comment.

##### **Rating Endpoints**
- **Add Rating** (`POST /movies/{movie_id}/ratings/`): Allows an authenticated user to rate a movie.
- **Get Ratings** (`GET /movies/{movie_id}/ratings/`): Retrieves a list of ratings for a specific movie.
- **Get Average Rating** (`GET /movies/{movie_id}/ratings/average`): Fetches the average rating for a specific movie.

#### **Request and Response Examples**
- **Signup** (`POST /signup`):
  - **Request**:
    ```json
    {
      "username": "string",
      "first_name": "string",
      "last_name": "string",
      "phone_number": "string",
      "email": "user@example.com",
      "password": "string"
    }
    ```
  - **Response**:
    ```json
    {
      "username": "string",
      "first_name": "string",
      "last_name": "string",
      "phone_number": "string",
      "email": "user@example.com",
      "id": 0
    }
    ```

- **Login** (`POST /login`):
  - **Request**: The login form requires a username and password. The user clicks on the "Authorize" button with a lock icon to submit their credentials.

- **Update Profile** (`PUT /users/me`):
  - **Request**:
    ```json
    {
      "username": "string",
      "first_name": "string",
      "last_name": "string",
      "phone_number": "string",
      "email": "user@example.com"
    }
    ```
  - **Response**:
    ```json
    {
      "username": "string",
      "first_name": "string",
      "last_name": "string",
      "phone_number": "string",
      "email": "user@example.com",
      "id": 0
    }
    ```


---

##### **Movie Endpoints**
- **List Movies** (`GET /movies/`):
  - **Request**: Parameters `offset` and `limit`
  - **Response**:
    ```json
    {
      "message": "success",
      "data": [
        {
          "title": "Queen of girls",
          "release_date": "2021-05-24",
          "created_at": "2024-08-14T20:16:31.070301",
          "updated_at": "2024-08-14T20:17:39.759250",
          "id": 3,
          "description": "Drama",
          "user_id": 1
        }
      ]
    }
    ```

- **Get Movie by ID** (`GET /movies/{movie_id}`):
  - **Request**: Path parameter `movie_id`
  - **Response**:
    ```json
    {
      "title": "Queen of girls",
      "description": "Drama",
      "release_date": "2021-05-24",
      "id": 3,
      "user_id": 1,
      "comments": [
        {
          "comment_text": "Very interesting!",
          "id": 4,
          "movie_id": 3,
          "user_id": 2,
          "parent_comment_id": null,
          "replies": []
        }
      ],
      "ratings": [
        {
          "rating": 9,
          "id": 4,
          "movie_id": 3,
          "user_id": 2
        },
        {
          "rating": 7,
          "id": 5,
          "movie_id": 3,
          "user_id": 1
        }
      ],
      "average_rating": 8,
      "created_at": "2024-08-14T20:16:31.070301",
      "updated_at": "2024-08-14T20:17:39.759250"
    }
    ```

- **List User's Movies** (`GET /movies/user`):
  - **Request**: Parameters `offset` and `limit`
  - **Response**:
    ```json
    {
      "message": "success",
      "data": [
        {
          "title": "Queen of girls",
          "release_date": "2021-05-24",
          "created_at": "2024-08-14T20:16:31.070301",
          "updated_at": "2024-08-14T20:17:39.759250",
          "id": 3,
          "description": "Drama",
          "user_id": 1
        },
        {
          "title": "King of boys",
          "release_date": "2018-04-24",
          "created_at": "2024-08-11T20:16:31.070301",
          "updated_at": "2024-08-11T20:17:39.759250",
          "id": 4,
          "description": "Drama",
          "user_id": 1
        }
      ]
    }
    ```

- **Create Movie** (`POST /new_movies`):
  - **Request**:
    ```json
    {
      "title": "string",
      "description": "string",
      "release_date": "2024-08-15"
    }
    ```
  - **Response**:
    ```json
    {
      "title": "string",
      "description": "string",
      "release_date": "2024-08-15",
      "id": 0,
      "created_at": "2024-08-15T12:23:15.522Z"
    }
    ```

- **Update Movie** (`PUT /movie_update/{movie_id}`):
  - **Request**:
    ```json
    {
      "title": "string",
      "description": "string",
      "release_date": "2024-08-15"
    }
    ```
  - **Response**:
    ```json
    {
      "title": "string",
      "description": "string",
      "release_date": "2024-08-15",
      "id": 0,
      "updated_at": "2024-08-15T12:25:10.164Z"
    }
    ```

- **Delete Movie** (`DELETE /movie_delete/{movie_id}`):
  - **Request**: Path parameter `movie_id`

##### **Comment Endpoints**
- **Add Comment** (`POST /movies/{movie_id}/comments/`):
  - **Request**:
    ```json
    {
      "comment_text": "string"
    }
    ```
  - **Response**:
    ```json
    {
      "comment_text": "string",
      "id": 0,
      "movie_id": 0,
      "user_id": 0,
      "parent_comment_id": 0,
      "replies": []
    }
    ```

- **Get Comments** (`GET /movies/{movie_id}/comments/`):
  - **Request**: Parameters `movie_id`, `skip`, and `limit`
  - **Response**:
    ```json
    [
      {
        "comment_text": "string",
        "id": 0,
        "movie_id": 0,
        "user_id": 0,
        "parent_comment_id": 0,
        "replies": []
      }
    ]
    ```

- **Add Reply to Comment** (`POST /comments/{parent_comment_id}/replies/`):
  - **Request**:
    ```json
    {
      "comment_text": "string"
    }
    ```
  - **Response**:
    ```json
    {
      "comment_text": "string",
      "id": 0,
      "movie_id": 0,
      "user_id": 0,
      "parent_comment_id": 0,
      "replies": []
    }
    ```

- **Delete Comment** (`DELETE /comments/{comment_id}/`):
  - **Request**: Path parameter `comment_id`

##### **Rating Endpoints**
- **Add Rating** (`POST /movies/{movie_id}/ratings/`):
  - **Request**:
    ```json
    {
      "rating": 0
    }
    ```
  - **Response**:
    ```json
    {
      "rating": 0,
      "id": 0,
      "movie_id": 0,
      "user_id": 0
    }
    ```

- **Get Ratings** (`GET /movies/{movie_id}/ratings/`):
  - **Request**: Parameters `movie_id`, `skip`, and `limit`
  - **Response**:
    ```json
    [
      {
        "rating": 0,
        "id": 0,
        "movie_id": 0,
        "user_id": 0
      }
    ]
    ```

- **Get Average Rating** (`GET /movies/{movie_id}/ratings/average`):
  - **Request**: Path parameter `movie_id`
  - **Response**:
    ```json
    {
      "average_rating": 0
    }
    ```

---

### **Testing**

#### **How to Run Tests**

To ensure your application is functioning correctly, you can run the test suite using pytest. Follow these steps:

1. **Activate the Virtual Environment**: Make sure your virtual environment is activated. This ensures that pytest runs with the correct dependencies.

2. **Navigate to the Project Directory**: Go to the directory where your test files are located.

3. **Run Tests**: Execute the following command to run all test cases:

    ```bash
    pytest
    ```

   This command will discover and execute all the test functions defined in your test files. Ensure your test database or any required test setup is properly configured.

#### **Sample Test Cases**

Below are some sample test cases to verify different aspects of your application:

##### **Signup Endpoint Test**

**Objective**: Verify that the signup endpoint correctly handles various types of user input and returns the appropriate status codes and responses.

```python
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
        assert all('msg' in error for error in errors)
        assert all('loc' in error for error in errors)
    else:
        response_json = response.json()
        assert response_json.get("username") == username
        assert response_json.get("first_name") == first_name
        assert response_json.get("last_name") == last_name
        assert response_json.get("phone_number") == phone_number
        assert response_json.get("email") == email
```

**Explanation**: This test checks if the signup process handles various valid and invalid inputs correctly. It verifies the response status and checks if validation errors are appropriately returned.

##### **Update Movie**

**Objective**: Ensure that the movie update functionality works as expected, handling different scenarios such as successful updates and invalid inputs.

```python
@pytest.mark.parametrize("payload, expected_status", [
    ({"title": "Updated Title", "description": "Updated description", "release_date": "2024-08-01"}, 200),
    ({"title": "Updated Title"}, 200),  # Ensure title is provided for successful update
    ({"title": ""}, 422),  # Expect validation error for empty title
    ({"title": "Updated Title"}, 404),  # Assuming movie ID 9999 does not exist
])
def test_update_movie(payload, expected_status, setup_movie_update_database_with_user, client: TestClient):
    user = setup_movie_update_database_with_user["user"]
    movie = setup_movie_update_database_with_user["movie"]

    token = get_auth_token(client, user.username, "testpassword")
    url = f"/movie_update/{movie.id if expected_status != 404 else '9999'}"

    response = client.put(url, json=payload, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == expected_status
```

**Explanation**: This test verifies that the movie update endpoint handles different scenarios correctly. It checks both successful updates and cases where the movie ID might be invalid or the input data might be incomplete.

##### **Get Average Rating**

**Objective**: Test the functionality for calculating and retrieving the average rating for a movie.

```python
def setup_test_data(db_session):
    db_session.query(models.Rating).delete()
    db_session.query(models.Movie).delete()
    db_session.query(models.User).delete()
    db_session.commit()

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

    movie_id = int(uuid.uuid4().int & (1<<31)-1)
    movie = models.Movie(
        id=movie_id,
        title="Test Movie",
        description="A test movie",
        release_date=date(2024, 7, 23),
        user_id=user.id
    )
    db_session.add(movie)
    db_session.commit()

    ratings = [
        models.Rating(rating=5, movie_id=movie_id, user_id=user.id),
        models.Rating(rating=7, movie_id=movie_id, user_id=user.id),
        models.Rating(rating=8, movie_id=movie_id, user_id=user.id)
    ]
    db_session.add_all(ratings)
    db_session.commit()

    return movie_id
```

**Explanation**: This setup function creates a test user, a test movie, and some ratings for the movie. It ensures the test database is clean and populated with relevant data before running the test.

---

### **Deployment**

#### **Deployment Instructions**

To deploy your FastAPI-based Movie Listing API to Render, follow these steps:

1. **Create a Render Account**:
   - Sign up for a free Render account at [Render's website](https://render.com/).

2. **Prepare Your Project**:
   - Ensure your project is set up with a `requirements.txt` or `pyproject.toml` file for dependencies.
   - Ensure your project has a `Procfile` for specifying how to run your FastAPI app. Here’s an example `Procfile`:
     ```
     web: uvicorn movie_app.main:app --host 0.0.0.0 --port 10000
     ```
   - Ensure you have a `runtime.txt` file if you want to specify the Python version (e.g., `python-3.10`).

3. **Push Your Code to a Git Repository**:
   - Render deploys your application directly from a Git repository. Push your code to GitHub, GitLab, or Bitbucket.

4. **Create a New Web Service on Render**:
   - Log in to your Render dashboard.
   - Click on “New” and select “Web Service”.
   - Connect your GitHub, GitLab, or Bitbucket account and select the repository with your project.
   - Configure the build and deploy settings:
     - **Branch**: Select the branch you want to deploy (e.g., `main`).
     - **Build Command**: Leave this blank if you don’t need to run any specific build commands. For Python projects, Render will use `pip` to install dependencies.
     - **Start Command**: Use the command from your `Procfile` (`web: uvicorn movie_app.main:app --host 0.0.0.0 --port 10000`).
   - Click “Create Web Service” to start the deployment process.

5. **Monitor Deployment**:
   - Render will automatically build and deploy your application. You can monitor the build and deployment status on the Render dashboard.

6. **Access Your Application**:
   - Once the deployment is complete, Render will provide you with a URL where your application is live.

#### **Environment Configuration**

To configure environment variables on Render:

1. **Navigate to Your Service**:
   - Go to your Render dashboard and select the service you deployed.

2. **Access Environment Variables**:
   - Click on the “Environment” tab.

3. **Add Environment Variables**:
   - Click “Add Environment Variable”.
   - Enter the variable name and value. For example:
     - `DATABASE_URL` = `postgresql://user:password@hostname:port/dbname`
     - `SECRET_KEY` = `your_jwt_secret_key`
     - `DEBUG` = `false`
     - `ALGORITHM` = `your_algorithm_key`
     - `ACCESS_TOKEN_EXPIRE_MINUTES` = `any_minutes_you_want`
   - Click “Save” to add the environment variables.

4. **Apply Changes**:
   - Render will automatically restart your service with the new environment variables.

5. **Verify Configuration**:
   - Ensure that your application is correctly picking up the environment variables and running as expected.



### **Logging and Monitoring**

#### Logging Setup

This project uses [Papertrail](https://papertrailapp.com/) for centralized logging. Papertrail is a service that aggregates logs from various sources, making it easier to monitor and troubleshoot issues. Here’s how logging is configured in this project:

- **Logging Configuration**: The logging is set up using Python's `logging` module. Logs are sent to Papertrail using the `SysLogHandler`. The relevant configuration is defined in the `logger.py` file.

  ```python
  import logging
  import logging.handlers

   PAPERTRAIL_HOST = 'your_papertrail_host'
   PAPERTRAIL_PORT = your_papertrail_port

  handler = logging.handlers.SysLogHandler(address=(PAPERTRAIL_HOST, PAPERTRAIL_PORT))

  logging.basicConfig(
      level=logging.DEBUG,
      format="%(asctime)s %(levelname)s %(name)s %(message)s",
      handlers=[handler]
  )

  def get_logger(name):
      logger = logging.getLogger(name)
      return logger
  ```

  - **Log Level**: Set to `DEBUG` to capture detailed log information.
  - **Format**: Logs include timestamp, log level, logger name, and message.
  - **Handlers**: Configured to send logs to Papertrail.

- **Viewing Logs**: To view logs, sign in to your Papertrail account and navigate to the log stream for this project. You can filter and search logs based on various criteria, including log level and time range.

#### Error Handling and Sentry Integration

Errors are logged to provide visibility into issues that occur during the execution of the application. Here’s how errors are handled and logged:

- **Logging Errors**: Errors are logged using different log levels depending on the severity:
  - **`ERROR`**: Used for critical issues that may affect the application’s functionality. These are logged when exceptions are caught or when operations fail.
  - **`WARNING`**: Used for non-critical issues that might require attention, such as failed lookups or validation errors.

  Example of logging an error in the `create_user` function:
  ```python
  def create_user(db: session, user: schema.UserCreate, hashed_password: str):
      logger.debug("Creating user with username: %s", user.username)
      try:
          db_user = models.User(
              username=user.username,
              first_name=user.first_name,
              last_name=user.last_name,
              phone_number=user.phone_number,
              email=user.email,
              hashed_password=hashed_password
          )
          db.add(db_user)
          db.commit()
          db.refresh(db_user)
          logger.info("User created successfully with username: %s", user.username)
          return db_user
      except ValueError as e:
          logger.error("Error creating user with username: %s. Error: %s", user.username, str(e))
          raise ValueError(str(e))
  ```

- **Exception Handling**: When exceptions occur, they are logged with the `ERROR` level, and in many cases, the exception is re-raised to be handled by higher-level error handlers or middleware. This ensures that errors are recorded and can be traced back for debugging.

  Example of handling and logging an exception in the `delete_movie` function:
  ```python
  def delete_movie(db: session, movie_id: int, user_id: int):
      logger.debug("Attempting to delete movie with ID: %d for user ID: %d", movie_id, user_id)
      movie = get_movie(db, movie_id, user_id=user_id)
      if not movie:
          logger.warning("Movie with ID: %d not found for user ID: %d", movie_id, user_id)
          return None
      
      try:
          db.delete(movie)
          db.commit()
          logger.info("Movie with ID: %d successfully deleted", movie_id)
          return movie
      except Exception as e:
          logger.error("Error deleting movie with ID: %d for user ID: %d. Error: %s", movie_id, user_id, str(e))
          raise
  ```

Sentry provides error tracking and monitoring to help you identify and fix issues in real-time. Here’s how you can integrate Sentry with your FastAPI application:

1. **Configuration**:
   Install the Sentry SDK and configure it in your `main.py`:

   ```python
   import sentry_sdk
   from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

   sentry_sdk.init(
       dsn="your_sentry_dsn",
       traces_sample_rate=1.0  # Adjust this for performance monitoring
   )

   app.add_middleware(SentryAsgiMiddleware)
   ```

2. **Handling Errors**:
   Sentry automatically captures unhandled exceptions. For manual error reporting, use the Sentry SDK in your code:

   ```python
   import sentry_sdk

   def some_function():
       try:
           # Your code
           pass
       except Exception as e:
           sentry_sdk.capture_exception(e)
           raise
   ```

   You can also add custom error handling in your FastAPI application:

   ```python
   from fastapi import Request, HTTPException
   from fastapi.responses import JSONResponse

   @app.exception_handler(HTTPException)
   async def http_exception_handler(request: Request, exc: HTTPException):
       # Log error
       logger.error(f"HTTP Exception: {exc.detail}")
       # Report to Sentry
       sentry_sdk.capture_exception(exc)
       return JSONResponse(
           status_code=exc.status_code,
           content={"detail": exc.detail},
       )
   ```

3. **Monitoring and Alerts**:
   Log in to your Sentry account to view error reports and performance data. You can configure alerts to notify you when specific types of errors occur.

#### **Example**

Here’s an example of logging and error handling in a CRUD operation:

```python
from fastapi import HTTPException
from movie_app.logger import get_logger
import sentry_sdk

logger = get_logger(__name__)

def some_crud_operation():
    try:
        # Perform some database operation
        pass
    except Exception as e:
        logger.error("An error occurred during CRUD operation: %s", str(e))
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
```

**Note**: Replace `your_papertrail_host`, `your_papertrail_port`, and `your_sentry_dsn` with your actual Papertrail and Sentry credentials. Avoid sharing sensitive information publicly.




## Detailed Usage

### Authentication

1. **Sign Up**
   - **Endpoint:** `POST /signup`
   - **Description:** Register a new user by providing a username, email, and password. The user will be added to the database with a hashed password.
   - **Request Body:**
     ```json
     {
       "username": "string",
       "email": "string",
       "password": "string"
     }
     ```
   - **Response:** Returns the created user object with a unique ID.

2. **Login**: 
   - Click the **Authorize** button (a green and white button with a lock icon) located on the right side of the API documentation interface. 
   - A prompt will appear asking for your `username` and `password`. 
   - If the credentials are incorrect, you will receive an `Unauthorized` error.
   - Once logged in successfully, you will receive a bearer token that grants access to the full range of API features.

### Usage for Authenticated Users

Authenticated users can perform the following actions:

1. **Update Profile**
   - **Endpoint:** `PUT /users/me`
   - **Description:** Update the current user's profile information.
   - **Request Body:**
     ```json
     {
       "username": "string",
       "email": "string",
       "password": "string"
     }
     ```
   - **Response:** Returns the updated user information.

2. **Create Movie**
   - **Endpoint:** `POST /new_movies`
   - **Description:** Create a new movie entry. Only accessible to authenticated users.
   - **Request Body:**
     ```json
     {
       "title": "string",
       "description": "string",
       "release_date": "YYYY-MM-DD"
     }
     ```
   - **Response:** Returns the created movie object with its ID.

3. **Get Movie by ID**
   - **Endpoint:** `GET /movie/{movie_id}`
   - **Description:** Retrieve details of a specific movie by its ID.
   - **Response:** Returns the movie details including comments, ratings, and average rating.

4. **Get Movies for User**
   - **Endpoint:** `GET /movies/user`
   - **Description:** Retrieve movies created by the authenticated user.
   - **Response:** Returns a list of movies created by the user.

5. **Update Movie**
   - **Endpoint:** `PUT /movie_update/{movie_id}`
   - **Description:** Update details of a movie created by the authenticated user.
   - **Request Body:**
     ```json
     {
       "title": "string",
       "description": "string",
       "release_date": "YYYY-MM-DD"
     }
     ```
   - **Response:** Returns the updated movie details.

6. **Delete Movie**
   - **Endpoint:** `DELETE /movie_delete/{movie_id}`
   - **Description:** Delete a movie created by the authenticated user.
   - **Response:** Returns a success message.

7. **Add Comment**
   - **Endpoint:** `POST /movies/{movie_id}/comments/`
   - **Description:** Add a comment to a specific movie.
   - **Request Body:**
     ```json
     {
       "coment": "string"
     }
     ```
   - **Response:** Returns the added comment.

8. **Add Nested Comment**
   - **Endpoint:** `POST /comments/{parent_comment_id}/replies/`
   - **Description:** Add a nested comment in response to an existing comment.
   - **Request Body:**
     ```json
     {
       "coment": "string"
     }
     ```
   - **Response:** Returns the added nested comment.

9. **Get Comments**
   - **Endpoint:** `GET /movies/{movie_id}/comments/`
   - **Description:** Retrieve all comments (both parent and nested) for a specific movie.
   - **Response:** Returns a list of comments.

10. **Add Rating**
    - **Endpoint:** `POST /movies/{movie_id}/ratings/`
    - **Description:** Add a rating to a specific movie.
    - **Request Body:**
      ```json
      {
        "rating": 1-10
      }
      ```
    - **Response:** Returns the added rating.

11. **Get Ratings**
    - **Endpoint:** `GET /movies/{movie_id}/ratings/`
    - **Description:** Retrieve all ratings for a specific movie.
    - **Response:** Returns a list of ratings.

12. **Get Average Rating**
    - **Endpoint:** `GET /movies/{movie_id}/ratings/average`
    - **Description:** Retrieve the average rating for a specific movie.
    - **Response:** Returns the average rating.

### Usage for Unauthenticated Users

Unauthenticated users have limited access:

1. **Get All Movies**
   - **Endpoint:** `GET /movies/`
   - **Description:** Retrieve a list of all movies with pagination support (offset and limit).
   - **Response:** Returns a list of movies.

2. **Get Movie by ID**
   - **Endpoint:** `GET /movie/{movie_id}`
   - **Description:** Retrieve details of a specific movie, including comments, ratings, and average rating.
   - **Response:** Returns the movie details.

3. **Get Comments**
   - **Endpoint:** `GET /movies/{movie_id}/comments/`
   - **Description:** Retrieve all comments (both parent and nested) for a specific movie.
   - **Response:** Returns a list of comments.

4. **Get Ratings**
   - **Endpoint:** `GET /movies/{movie_id}/ratings/`
   - **Description:** Retrieve all ratings for a specific movie.
   - **Response:** Returns a list of ratings.

5. **Get Average Rating**
   - **Endpoint:** `GET /movies/{movie_id}/ratings/average`
   - **Description:** Retrieve the average rating for a specific movie.
   - **Response:** Returns the average rating.

### Error Handling

- **Unauthorized Access:** If an unauthenticated user attempts to access features requiring authentication, a `401 Unauthorized` error will be returned.
- **Forbidden Access:** If an authenticated user attempts to access or modify resources they do not own, a `403 Forbidden` error will be returned.
- **Not Found:** If a requested resource (e.g., movie, comment) is not found, a `404 Not Found` error will be returned.
- **Validation Errors:** If there are validation issues with the input data, a `422 Unprocessable Entity` error will be returned.
- **Internal Server Error:** In case of unexpected server issues, a `500 Internal Server Error` will be returned.




---
### **Contributing**

I welcome contributions to the Movie Listing API project! Here’s how you can get involved:

#### **Contribution Guidelines**

1. **Fork the Repository**
   - Start by forking the repository to your own GitHub account. This allows you to make changes in your own copy without affecting the original project.

2. **Clone Your Fork**
   - Clone your forked repository to your local machine:
     ```bash
     git clone https://github.com/Toluskydc/movie_listing_api.git
     ```

3. **Create a New Branch**
   - Create a new branch for your changes:
     ```bash
     git checkout -b feature/your-feature-name
     ```

4. **Follow Code Style**
   - Ensure that your code follows the project's coding style. I used [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code style.
   - You can use tools like [flake8](https://flake8.pycqa.org/) to check for style issues.

5. **Write Tests**
   - Add or update tests to cover your changes. I used [pytest](https://docs.pytest.org/en/stable/) for testing.
   - Run tests to ensure everything is working correctly:
     ```bash
     pytest
     ```

6. **Update Documentation**
   - Update the README or other documentation files if your changes affect the API usage or functionality.

7. **Commit Your Changes**
   - Commit your changes with a descriptive message:
     ```bash
     git add .
     git commit -m "Add a detailed message about your changes"
     ```

8. **Push Your Changes**
   - Push your changes to your forked repository:
     ```bash
     git push origin feature/your-feature-name
     ```

9. **Create a Pull Request**
   - Go to the original repository and create a pull request from your forked repository’s branch.
   - Provide a clear description of your changes and why they are being made.

10. **Review Process**
    - Your pull request will be reviewed by the project and would provide feedback or request changes before it can be merged.

#### **Code of Conduct**

Please follow our [Code of Conduct](./CODE_OF_CONDUCT.md) to ensure a welcoming and inclusive environment for all contributors.

#### **Additional Resources**

- For more details on contributing, refer to the [GitHub Documentation](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/about-pull-requests).
- If you have any questions or need help, feel free to open an issue or contact the maintainers.

Thank you for contributing to the Movie Listing API project!

---



### **License**

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

### **Contact Information**

If you have any questions, feedback, or need assistance, feel free to reach out to me:

- **Author**: TOLUWANI OMOSUYI
- **GitHub Profile**: [https://github.com/Toluskydc](https://github.com/Toluskydc)
- **Email**: [booktolusky@gmail.com](mailto:booktolusky@gmail.com)
- **Repository**: [https://github.com/Toluskydc/movie_listing_api](https://github.com/Toluskydc/movie_listing_api)

You can also open an issue or submit a pull request on the repository if you have any suggestions or contributions.
