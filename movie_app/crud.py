from sqlalchemy.orm import session
from movie_app import models
from movie_app import schema
from sqlalchemy import func
from movie_app.models import Rating
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import joinedload



from movie_app.logger import get_logger

logger = get_logger(__name__)


# User's CRUD


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


def get_user_by_username(db: session, username: str):
    logger.debug("Attempting to retrieve user by username: %s", username)
    try:
        user = db.query(models.User).filter(models.User.username == username).first()
        if user:
            logger.info("User retrieved successfully by username: %s", username)
        else:
            logger.warning("No user found with username: %s", username)
        return user
    except Exception as e:
        logger.error("Error retrieving user by username: %s. Error: %s", username, str(e))
        raise


def get_user_by_email(db: session, email: str):
    logger.debug("Attempting to retrieve user by email: %s", email)
    try:
        user = db.query(models.User).filter(models.User.email == email).first()
        if user:
            logger.info("User retrieved successfully by email: %s", email)
        else:
            logger.warning("No user found with email: %s", email)
        return user
    except Exception as e:
        logger.error("Error retrieving user by email: %s. Error: %s", email, str(e))
        raise


def update_user(db: session, user_id: int, user_update: schema.UserUpdate):
    logger.debug("Attempting to update user with ID: %d", user_id)
    # Get the user to update
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not db_user:
        logger.warning("User with ID %d not found for update", user_id)
        return None

    # Update the fields if they are provided
    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(db_user, key, value)
    
    # Set the updated_at field
    db_user.updated_at = datetime.utcnow()

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info("User with ID %d updated successfully", user_id)
    return db_user



# Movies CRUD

def get_movie(db: session, id: int, user_id: int = None):
    logger.debug("Querying movie with ID: %d and user ID: %s", id, user_id)
    query = db.query(models.Movie).filter(models.Movie.id == id)
    if user_id:
        query = query.filter(models.Movie.user_id == user_id)
    movie = query.first()
    if movie:
        logger.info("Movie with ID %d found", id)
        # Load comments and their replies
        movie.comments = load_comments_with_replies(db, movie.id)
    return movie

def load_comments_with_replies(db: session, movie_id: int):
    logger.debug("Loading comments with replies for movie ID: %d", movie_id)
    # Load comments
    comments = db.query(models.Comment).filter(models.Comment.movie_id == movie_id, models.Comment.parent_comment_id.is_(None)).all()
    # Load replies recursively
    def load_replies(comment):
        replies = db.query(models.Comment).filter(models.Comment.parent_comment_id == comment.id).all()
        for reply in replies:
            reply.replies = load_replies(reply)
        return replies
    for comment in comments:
        comment.replies = load_replies(comment)
        logger.info("Loaded %d comments and their replies for movie ID %d", len(comments), movie_id)
    return comments


def get_movie_by_title(db: session, title: str):
    return db.query(models.Movie).filter(models.Movie.title == title).first()


def get_movies(db: session, offset: int = 0, limit: int = 10):
    logger.debug("Querying movies with offset: %d and limit: %d", offset, limit)
    movies = db.query(models.Movie).offset(offset).limit(limit).all()
    logger.info("Retrieved %d movies with offset: %d and limit: %d", len(movies), offset, limit)
    return movies


def get_movie_for_user(db: session, user_id: int = None, offset: int = 0, limit: int = 10):
    logger.debug("Querying movies for user ID: %d with offset: %d and limit: %d", user_id, offset, limit)
    movies = db.query(models.Movie).filter(models.Movie.user_id == user_id).offset(offset).limit(limit).all()
    logger.info("Retrieved %d movies for user ID: %d", len(movies), user_id)
    return movies


def create_movie(db: session, movie: schema.MovieCreate, user_id: int = None):
    logger.debug("Inserting new movie with title: %s for user ID: %d", movie.title, user_id)
    db_movie = models.Movie(
        **movie.dict(),
        user_id= user_id,
        created_at = datetime.utcnow()
    )
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    logger.info("Movie with ID: %d and title: %s successfully created", db_movie.id, db_movie.title)
    return db_movie


def update_movie(db: session, movie_id: int, payload: schema.MovieUpdate, user_id: int= None):
    logger.debug("Querying for movie with ID: %d and User ID: %d", movie_id, user_id)
    print(f"Querying for movie with ID: {movie_id} and User ID: {user_id}")
    movie = db.query(models.Movie).filter(
        models.Movie.id == movie_id,
        models.Movie.user_id == user_id
    ).first()
    print(f"Movie found: {movie}")

    if not movie:
        logger.warning("Movie with ID: %d not found for user ID: %d", movie_id, user_id)
        print(f"Movie with ID {movie_id} not found for user ID {user_id}")  # Debug print
        return None

    for key, value in payload.dict(exclude_unset=True).items():
        setattr(movie, key, value)
    
    db.commit()
    db.refresh(movie)
    logger.info("Movie with ID: %d successfully updated with new details: %s", movie.id, movie)
    print(f"Updated movie details: {movie}")  # Debug print
    return movie


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



# Comments CRUD

def create_comment(db: session, comment: schema.CommentCreate, user_id: int, movie_id: int):
    logger.debug("Starting comment creation: movie_id=%d, user_id=%d", movie_id, user_id)
    print(f"Starting comment creation: movie_id={movie_id}, user_id={user_id}")
    
    movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    logger.debug("Movie found in CRUD: %s", movie)
    print(f"Movie found in CRUD: {movie}")
    
    if not movie:
        logger.warning("Movie with ID: %d not found for user ID: %d when creating comment", movie_id, user_id)
        raise ValueError("Movie not found")
    
    db_comment = models.Comment(
        comment_text=comment.comment_text,
        movie_id=movie_id,
        user_id=user_id,
    )
    
    try:
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        logger.info("Comment successfully created for movie_id=%d, user_id=%d", movie_id, user_id)
        return db_comment
    except Exception as e:
        logger.error("Error creating comment for movie_id=%d, user_id=%d. Error: %s", movie_id, user_id, str(e))
        raise





def create_nested_comment(db: session, comment: schema.CommentCreate, parent_comment_id: int, user_id: int):
    logger.debug("Starting creation of nested comment for parent_comment_id: %d by user_id: %d", parent_comment_id, user_id)
    # Fetch the parent comment
    parent_comment = db.query(models.Comment).filter(models.Comment.id == parent_comment_id).first()
    if not parent_comment:
        logger.warning("Parent comment with ID %d does not exist", parent_comment_id)
        raise ValueError("Parent comment does not exist")
    
    db_comment = models.Comment(
        comment_text = comment.comment_text,
        movie_id= parent_comment.movie_id,
        user_id= user_id,
        parent_comment_id= parent_comment_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)

    logger.info("Nested comment created wuth iD %d for parent_comment_id %d by user_id %d", db_comment.id, parent_comment_id, user_id)
    return db_comment


def get_comments(db: session, movie_id: int, skip: int = 0, limit: int = 10):
    logger.debug("Fetching comments for movie_id=%d with skip=%d and limit=%d", movie_id, skip, limit)
    # Check if the movie exists
    movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not movie:
        logger.warning("Movie with ID: %d not found when fetching comments", movie_id)
        raise HTTPException(status_code=404, detail="Movie not found")
    
    # Query for comments with joinedload for replies
    comments = db.query(models.Comment).options(joinedload(models.Comment.replies)).filter(
        models.Comment.movie_id == movie_id,
        models.Comment.parent_comment_id == None
    ).offset(skip).limit(limit).all()
    
    if not comments:
        logger.info("No comments found for movie_id=%d", movie_id)
    else:
        logger.info("Retrieved %d comments for movie_id=%d", len(comments), movie_id)
    
    return comments


def get_comment(db: session, comment_id: int):
    return db.query(models.Comment).filter(models.Comment.id == comment_id).first()

def delete_comment(db: session, comment_id: int):
    db_comment = get_comment(db, comment_id)
    logger.debug("Fetched comment for deletion: %s", db_comment)
    print("Fetched Comment for Deletion:", db_comment)
    if db_comment:
        db.delete(db_comment)
        db.commit()
        logger.info("Comment with ID %d deleted from the database", comment_id)
    else:
        logger.warning("Attempted to delete comment_id: %d, but it was not found", comment_id)
    return None



# Ratings
def create_rating(db: session, rating: schema.RatingCreate, movie_id: int, user_id: int):
    logger.debug("Creating rating for movie_id: %d by user_id: %d", movie_id, user_id)
    db_rating = models.Rating(
        rating=rating.rating,
        movie_id=movie_id,
        user_id=user_id
    )
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    logger.info("Rating created for movie_id: %d by user_id: %d", movie_id, user_id)
    return db_rating

def get_ratings(db: session, movie_id: int, skip: int = 0, limit: int = 10):
    logger.debug("Starting retrieval of ratings for movie_id: %d with skip: %d and limit: %d", movie_id, skip, limit)
    try:
        ratings = db.query(models.Rating).filter(models.Rating.movie_id == movie_id).offset(skip).limit(limit).all()
        logger.info("Successfully retrieved %d ratings for movie_id: %d", len(ratings), movie_id)
        return ratings
    except Exception as e:
        logger.error("Failed to retrieve ratings for movie_id: %d due to server error: %s", movie_id, str(e))
        raise


def get_average_rating(db: session, movie_id: int):
    logger.debug("Calculating average rating for movie_id: %d", movie_id)
    average_rating = db.query(func.avg(Rating.rating)).filter(Rating.movie_id == movie_id).scalar()
    logger.info("Calculated average rating for movie_id: %d is %.2f", movie_id, average_rating if average_rating else 0.0)
    return average_rating