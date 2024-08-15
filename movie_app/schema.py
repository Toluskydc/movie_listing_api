from pydantic import BaseModel, EmailStr, field_validator
from pydantic.types import StringConstraints
from typing import Optional, List, Annotated
from datetime import date, datetime
import re



## User Schema

PHONE_NUMBER_PATTERN = re.compile(r'^\+?[1-9]\d{9,14}$')

class UserBase(BaseModel):
    username: str
    first_name: str
    last_name: str
    phone_number: str
    email: EmailStr

    @field_validator('first_name', 'last_name', 'username', mode='before')
    def validate_non_empty(cls, value, info):
        if not value or value.strip() == "":
            raise ValueError(f"{info.field_name} cannot be empty or null")
        return value

    @field_validator("phone_number", mode="before")
    def validate_phone_number(cls, value):
        value = value.strip()  # Remove any leading or trailing whitespace
        if not PHONE_NUMBER_PATTERN.match(value):
            raise ValueError('Invalid phone number format. Use E.164 format.')
        return value


class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None

class User(UserBase): 
    id: int

    class Config:
        from_attributes = True





## Movie Schema
class MovieListingBase(BaseModel):
    title: str
    description: Optional[str] = None
    release_date: Optional[date] = None


class MovieListing(MovieListingBase):
    id: int
    user_id: int

    class config:
        from_attributes = True


class MovieCreate(MovieListingBase):
    title: Annotated[str, StringConstraints(min_length=1)]  # Ensures title is not empty
    description: Optional[str] = None
    release_date: Optional[date] = None

class MovieUpdate(MovieListingBase):
    title: Annotated[str, StringConstraints(min_length=1)]  # Ensures title is not empty
    description: Optional[str] = None
    release_date: Optional[date] = None

class Movie(MovieListing):
    comments: List['Comment'] = []
    ratings: List['Rating'] = []
    average_rating: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MovieCreateResponse(MovieListingBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class MovieUpdateResponse(MovieListingBase):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True

class MovieDeleteResponse(BaseModel):
    message: str
    data: MovieListing





## Comment Schema
class CommentBase(BaseModel):
    comment_text: Annotated[str, StringConstraints(min_length=2)]
  

class CommentCreate(CommentBase):
    # parent_comment_id: Optional[int] = None
    pass


class Comment(CommentBase):
    id: int
    comment_text: str
    movie_id: int
    user_id: int
    parent_comment_id: Optional[int] = None
    replies: List['Comment'] = []

    class Config:
        from_attributes = True




## Rating Schema
class RatingBase(BaseModel):
    rating: int

    @field_validator('rating', mode='before')
    def check_rating(cls, value):
        if value < 1 or value > 10:
            raise ValueError('Rating must be between 1 and 10')
        return value

class RatingCreate(RatingBase):
    pass

class Rating(RatingBase):
    id: int
    movie_id: int
    user_id: int

    class Config:
        form_attributes = True


class AverageRating(BaseModel):
    average_rating: float

    class Config:
        from_attributes = True