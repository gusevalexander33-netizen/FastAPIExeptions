from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn

import models, schemas
from database import engine, get_db
from repositories import (
    UserRepository, PostRepository, CommentRepository,
    CategoryRepository, TagRepository
)
from exeptions.base import AppException
from exeptions.infrastructure import DatabaseException
from exeptions.domain import *
from exeption_handlers import (
    app_exception_handler,
    database_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)


def run_migrations():
    try:
        from alembic.config import Config
        from alembic import command
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
    except:
        pass


run_migrations()

app = FastAPI(title="FastAPI Blog API", version="1.0.0")

# Регистрируем обработчики ошибок
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(DatabaseException, database_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

def get_user_repo(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_post_repo(db: Session = Depends(get_db)) -> PostRepository:
    return PostRepository(db)

def get_comment_repo(db: Session = Depends(get_db)) -> CommentRepository:
    return CommentRepository(db)

def get_category_repo(db: Session = Depends(get_db)) -> CategoryRepository:
    return CategoryRepository(db)

def get_tag_repo(db: Session = Depends(get_db)) -> TagRepository:
    return TagRepository(db)

@app.get("/api/users/", response_model=List[schemas.UserResponse], tags=["Users"])
def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(None),
    user_repo: UserRepository = Depends(get_user_repo)
):
    if search:
        return user_repo.search_users(search)
    return user_repo.get_all(skip=skip, limit=limit)


@app.get("/api/users/{user_id}/", response_model=schemas.UserResponse, tags=["Users"])
def get_user(user_id: int, user_repo: UserRepository = Depends(get_user_repo)):
    return user_repo.get_by_id(user_id)


@app.post("/api/users/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED, tags=["Users"])
def create_user(user: schemas.UserCreate, user_repo: UserRepository = Depends(get_user_repo)):
    return user_repo.create(user.model_dump())


@app.put("/api/users/{user_id}/", response_model=schemas.UserResponse, tags=["Users"])
def update_user(user_id: int, user_update: schemas.UserUpdate, user_repo: UserRepository = Depends(get_user_repo)):
    return user_repo.update(user_id, user_update.model_dump(exclude_unset=True))


@app.delete("/api/users/{user_id}/", status_code=status.HTTP_204_NO_CONTENT, tags=["Users"])
def delete_user(user_id: int, user_repo: UserRepository = Depends(get_user_repo)):
    user_repo.delete(user_id)
    return None

@app.get("/api/posts/", response_model=List[schemas.PostResponse], tags=["Posts"])
def get_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    author_id: Optional[int] = Query(None),
    category_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
post_repo: PostRepository = Depends(get_post_repo)
):
    if search:
        return post_repo.search_posts(search)
    if author_id:
        return post_repo.get_user_posts(author_id, skip=skip, limit=limit)
    if category_id:
        return post_repo.get_category_posts(category_id, skip=skip, limit=limit)
    if status_filter == "published":
        return post_repo.get_published_posts(skip=skip, limit=limit)
    if status_filter == "draft":
        return post_repo.get_draft_posts(skip=skip, limit=limit)
    return post_repo.get_all(skip=skip, limit=limit)


@app.get("/api/posts/{post_id}/", response_model=schemas.PostResponse, tags=["Posts"])
def get_post(post_id: int, post_repo: PostRepository = Depends(get_post_repo)):
    post = post_repo.get_by_id(post_id)
    post_repo.increment_views(post_id)
    return post


@app.post("/api/posts/", response_model=schemas.PostResponse, status_code=status.HTTP_201_CREATED, tags=["Posts"])
def create_post(
    post: schemas.PostCreate,
    post_repo: PostRepository = Depends(get_post_repo),
    user_repo: UserRepository = Depends(get_user_repo)
):
    if not user_repo.exists(post.author_id):
        raise UserNotFoundException(user_id=post.author_id)
    return post_repo.create(post.model_dump())


@app.put("/api/posts/{post_id}/", response_model=schemas.PostResponse, tags=["Posts"])
def update_post(post_id: int, post_update: schemas.PostUpdate, post_repo: PostRepository = Depends(get_post_repo)):
    return post_repo.update(post_id, post_update.model_dump(exclude_unset=True))


@app.delete("/api/posts/{post_id}/", status_code=status.HTTP_204_NO_CONTENT, tags=["Posts"])
def delete_post(post_id: int, post_repo: PostRepository = Depends(get_post_repo)):
    post_repo.delete(post_id)
    return None

@app.get("/api/posts/{post_id}/comments/", response_model=List[schemas.CommentResponse], tags=["Comments"])
def get_post_comments(post_id: int, comment_repo: CommentRepository = Depends(get_comment_repo)):
    return comment_repo.get_post_comments(post_id)


@app.post("/api/comments/", response_model=schemas.CommentResponse, status_code=status.HTTP_201_CREATED, tags=["Comments"])
def create_comment(
    comment: schemas.CommentCreate,
    comment_repo: CommentRepository = Depends(get_comment_repo),
    post_repo: PostRepository = Depends(get_post_repo),
    user_repo: UserRepository = Depends(get_user_repo)
):
    if not user_repo.exists(comment.author_id):
        raise UserNotFoundException(user_id=comment.author_id)
    if not post_repo.exists(comment.post_id):
        raise PostNotFoundException(post_id=comment.post_id)
    return comment_repo.create(comment.model_dump())


@app.delete("/api/comments/{comment_id}/", status_code=status.HTTP_204_NO_CONTENT, tags=["Comments"])
def delete_comment(comment_id: int, comment_repo: CommentRepository = Depends(get_comment_repo)):
    comment_repo.delete(comment_id)
    return None

@app.get("/api/categories/", response_model=List[schemas.CategoryResponse], tags=["Categories"])
def get_categories(category_repo: CategoryRepository = Depends(get_category_repo)):
    return category_repo.get_all()

@app.get("/api/tags/", response_model=List[schemas.TagResponse], tags=["Tags"])
def get_tags(tag_repo: TagRepository = Depends(get_tag_repo)):
    return tag_repo.get_all()

@app.get("/api/health/", tags=["System"])
def health_check():
    return {"status": "healthy"}