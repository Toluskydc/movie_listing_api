from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from movie_app.auth import authenticate_user, create_access_token, get_current_user
from movie_app import crud, schema, models
from movie_app.database import engine, Base, get_db
from typing import List
from movie_app.auth import pwd_context
from sqlalchemy.exc import DataError
from fastapi.responses import JSONResponse
from pydantic import ValidationError



import sentry_sdk

from movie_app.logger import get_logger

logger = get_logger(__name__)


sentry_sdk.init(
    dsn="https://1313ea9c5f985d00926b066b2fbace17@o4507780871618560.ingest.us.sentry.io/4507780873388032",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)

Base.metadata.create_all(bind=engine)

app = FastAPI()



# User's Routes

@app.post("/signup", response_model=schema.User)
def signup(user: schema.UserCreate, db: Session = Depends(get_db)):
    logger.info("Signup process started for username: %s", user.username)
    try:
        db_user_by_username = crud.get_user_by_username(db, username=user.username)
        db_user_by_email = crud.get_user_by_email(db, email=user.email)
        
        if db_user_by_username:
            logger.warning("Signup failed: Username already registered - %s", user.username)
            raise HTTPException(status_code=400, detail="Username already registered!")
        
        if db_user_by_email:
            logger.warning("Signup failed: Email already exist - %s", user.email)
            raise HTTPException(status_code=400, detail="Email already registered!")

        # Hash password and create user
        hashed_password = pwd_context.hash(user.password)
        logger.info("User created successfully: %s", user.username)
        return crud.create_user(db=db, user=user, hashed_password=hashed_password)
    except ValidationError as e:
        logger.error("Validation error during signup: %s", e.errors())
        return JSONResponse(status_code=422, content={"detail": e.errors()})
    except ValueError as e:
        logger.error("Value error during signup: %s", str(e))
        return JSONResponse(status_code=422, content={"detail": str(e)})



@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logger.debug("Login attempt for username: %s", form_data.username)
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.warning("Failed login attempt for username: %s", form_data.username)
        raise HTTPException(
            status_code=401, 
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token = create_access_token(data={"sub": user.username})
    logger.info("Successful login for username: %s", form_data.username)
    return {"access_token": access_token, "token_type": "bearer"}



@app.put("/users/me", response_model=schema.User)
def update_profile(user_update: schema.UserUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.debug("Profile update attempt for user ID: %d", current_user.id)
    try:
        # Update the profile for the current authenticated user
        updated_user = crud.update_user(db, user_id=current_user.id, user_update=user_update)
        logger.info("Profile successfully updated for user ID: %d", current_user.id)
        return updated_user
    except ValidationError as e:
        # Return a 422 status code for validation errors from schema
        logger.error("Validation error during profile update for user ID %d: %s", current_user.id, e.errors())
        raise HTTPException(status_code=422, detail=e.errors())
    except ValueError as e:
        logger.error("Value error during profile update for user ID %d: %s", current_user.id, str(e))
        # Return a 400 status code for other invalid data errors
        raise HTTPException(status_code=400, detail=str(e))

# --------------------------------------------------------------------------


# Movies Routes


@app.get('/movies/')
def get_movies(db: Session = Depends(get_db), offset: int = 0, limit: int = 10):
    logger.debug("Request to get movies with offset: %d and limit: %d", offset, limit)
    movies = crud.get_movies(db, offset=offset, limit=limit)
    logger.info("Successfully retrieved %d movies with offset: %d and limit: %d", len(movies), offset, limit)
    return {"message": "success", "data": movies}

@app.get("/movie/{movie_id}",  response_model=schema.Movie)
def get_movie_by_id(movie_id: str, db: Session = Depends(get_db)):
    logger.debug("Request to get movie by ID: %s", movie_id)
    movie = crud.get_movie(db, movie_id)
    if not movie:
        logger.warning("Movie with ID %s not found", movie_id)
        raise HTTPException(status_code=404, detail="Movie not found!")
    # Calculate the average rating and add it to the movie object
    average_rating = crud.get_average_rating(db, movie_id)
    movie.average_rating = average_rating
    logger.info("Successfully retrieved movie with ID: %s", movie_id)
    return movie

@app.get("/movies/user")
def get_movie_for_user(db: Session = Depends(get_db), user: schema.User = Depends(get_current_user), offset: int =0, limit: int =10):
    logger.debug("Request to get movies for user ID: %d with offset: %d and limit: %d", user.id, offset, limit)
    movies = crud.get_movie_for_user(
        db,
        user_id=user.id,
        offset=offset,
        limit=limit
    )
    logger.info("Successfully retrieved %d movies for user ID: %d", len(movies), user.id)
    return {"message": "success", "data": movies}

@app.post('/new_movies', response_model=schema.MovieCreateResponse)
def create_movie(payload: schema.MovieCreate, user: schema.User = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.debug("Request to create a new movie with title: %s by user ID: %d", payload.title, user.id)
    try:
        movie = crud.create_movie(db, payload, user_id=user.id)
        logger.info("Successfully created movie with ID: %d and title: %s", movie.id, movie.title)
        return schema.MovieCreateResponse(
            id=movie.id,
            title=movie.title,
            description=movie.description,
            release_date=movie.release_date,
            created_at=movie.created_at
        )
    except DataError as e:
        logger.error("Unexpected error while creating movie with title: %s by user ID: %d. Error: %s", payload.title, user.id, str(e))
        raise HTTPException(status_code=400, detail="Invalid input data")

@app.put('/movie_update/{movie_id}', response_model=schema.MovieUpdateResponse)
def update_movie(
    movie_id: int,
    payload: schema.MovieUpdate,
    user: schema.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logger.debug("Request to update movie with ID: %d by user ID: %d", movie_id, user.id)
    print(f"Received request to update movie with ID: {movie_id}")
    print(f"Current user ID: {user.id}")
    
    movie = db.query(models.Movie).filter(models.Movie.id == movie_id, models.Movie.user_id == user.id).first()
    print(f"Movie found: {movie}")

    if not movie:
        print(f"Movie with ID {movie_id} not found for user ID {user.id}")
        logger.warning("Movie with ID: %d not found for user ID: %d", movie_id, user.id)
        raise HTTPException(status_code=404, detail="Movie not found")
    
    movie.title = payload.title or movie.title
    movie.description = payload.description or movie.description
    movie.release_date = payload.release_date or movie.release_date

    try:
        db.commit()
        logger.info("Movie with ID: %d successfully updated by user ID: %d", movie.id, user.id)
    except Exception as e:
        logger.error("Error updating movie with ID: %d by user ID: %d. Error: %s", movie.id, user.id, str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")
    return schema.MovieUpdateResponse(
        id=movie.id,
        title=movie.title,
        description=movie.description,
        release_date=movie.release_date,
        updated_at=movie.updated_at
    )

@app.delete('/movie_delete/{movie_id}', response_model=schema.MovieDeleteResponse)
def delete_movie(movie_id: int, user: schema.User = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.debug("Request to delete movie with ID: %d by user ID: %d", movie_id, user.id)
    deleted_movie = crud.delete_movie(db, movie_id, user.id)
    if not deleted_movie:
        logger.warning("Movie with ID: %d not found for user ID: %d", movie_id, user.id)
        raise HTTPException(status_code=404, detail="Movie not found")
    logger.info("Successfully deleted movie with ID: %d by user ID: %d", movie_id, user.id)
    return {"message": "success", "data": deleted_movie}





# Comment Routes

@app.post("/movies/{movie_id}/comments/", response_model=schema.Comment)
def add_comment(
    movie_id: int, 
    comment: schema.CommentCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    logger.debug("Received request to add comment for movie_id: %d by user_id: %d", movie_id, current_user.id)
    print(f"Received movie_id: {movie_id}")
    
    movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    logger.debug("Movie found: %s", movie)
    print(f"Movie found: {movie}")
    if not movie:
        logger.warning("Movie with ID: %d not found when adding comment", movie_id)
        raise HTTPException(status_code=404, detail="Movie not found")
    
    try:
        comment = crud.create_comment(db=db, comment=comment, movie_id=movie_id, user_id=current_user.id)
        logger.info("Comment successfully added to movie_id: %d by user_id: %d", movie_id, current_user.id)
        return comment
    except ValueError as e:
        logger.error("Failed to add comment to movie_id: %d by user_id: %d. Error: %s", movie_id, current_user.id, str(e))
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/movies/{movie_id}/comments/", response_model=List[schema.Comment])
def get_comments(movie_id: int, db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    logger.debug("Received request to get comments for movie_id: %d with skip: %d and limit: %d", movie_id, skip, limit)
    comments = crud.get_comments(db=db, movie_id=movie_id, skip=skip, limit=limit)
    
    if not comments:
        logger.info("No comments found for movie_id: %d", movie_id)
    else:
        logger.info("Retrieved %d comments for movie_id: %d", len(comments), movie_id)
    
    return comments

@app.post("/comments/{parent_comment_id}/replies/", response_model=schema.Comment)
def add_nested_comment(parent_comment_id: int, comment: schema.CommentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    logger.debug ("Received request to add a nested comment to parent_comment_id: %d by user_id: %d", parent_comment_id, current_user.id)
    try:
        nested_comment = crud.create_nested_comment(db=db, comment=comment, parent_comment_id=parent_comment_id, user_id=current_user.id)
        logger.info("Nested comment with ID %d successfully added to parent_comment_id: %d by user_id: %d", nested_comment.id, parent_comment_id, current_user.id)
        return nested_comment 
    except ValueError as e:
        logger.error("Failed to add nested comment: %s", str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.delete("/comments/{comment_id}/")
def delete_comment(comment_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    logger.debug("Received request to delete comment_id: %d by user_id: %d", comment_id, current_user.id)
    comment = crud.get_comment(db, comment_id)
    logger.debug("Fetched comment: %s", comment)
    print("Fetched Comment:", comment)
    if not comment:
        logger.warning("Comment with ID %d not found for deletion by user_id: %d", comment_id, current_user.id)
        raise HTTPException(status_code=404, detail="Comment not found")
    
    print("Current User ID:", current_user.id)
    print("Comment User ID:", comment.user_id)
    if comment.user_id != current_user.id:
        logger.warning("User_id: %d attempted to delete comment_id: %d but it is not authorized", current_user.id, comment_id)
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    
    crud.delete_comment(db=db, comment_id=comment_id)
    logger.info("Comment with ID %d successfully deleted by user_id: %d", comment_id, current_user.id)
    return {"message": "success"}








# Rating Routes


@app.post("/movies/{movie_id}/ratings/", response_model=schema.Rating)
def add_rating(movie_id: int, rating: schema.RatingCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    logger.debug("Received request to add a rating to movie_id: %d by user_id: %d", movie_id, current_user.id)
    # Check if the movie exists
    movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not movie:
        logger.warning("Movie with ID %d not found for rating by user_id: %d", movie_id, current_user.id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

    # Create and return the rating
    rating_response = crud.create_rating(db=db, rating=rating, movie_id=movie_id, user_id=current_user.id)
    logger.info("Rating added to movie_id: %d by user_id: %d", movie_id, current_user.id)
    return rating_response

@app.get("/movies/{movie_id}/ratings/", response_model=List[schema.Rating])
def get_ratings(movie_id: int, db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    logger.debug("Received request to retrieve ratings for movie_id: %d", movie_id)
    ratings = crud.get_ratings(db=db, movie_id=movie_id, skip=skip, limit=limit)
    logger.info("Successfully retrieved %d ratings for movie_id: %d", len(ratings), movie_id)
    return ratings

@app.get("/movies/{movie_id}/ratings/average", response_model=schema.AverageRating)
def get_average_rating(movie_id: int, db: Session = Depends(get_db)):
    logger.debug("Received request to retrieve average rating for movie_id: %d", movie_id)

    average_rating = crud.get_average_rating(db=db, movie_id=movie_id)

    if average_rating is None:
        average_rating = 0.0
    logger.info("Successfully retrieved average rating for movie_id: %d, average: %d.2f", movie_id, average_rating)
    return schema.AverageRating(average_rating=average_rating)