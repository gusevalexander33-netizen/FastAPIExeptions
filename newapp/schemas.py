from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional
from datetime import datetime
import re

def validate_username(v: str) -> str:
    if not v or not v.strip():
        raise ValueError('Username не может быть пустым')
    if len(v) < 3:
        raise ValueError('Username должен быть не менее 3 символов')
    if len(v) > 150:
        raise ValueError('Username должен быть не более 150 символов')
    if not re.match(r'^[a-zA-Z0-9_@.+-]+$', v):
        raise ValueError('Username содержит недопустимые символы')
    return v.strip().lower()


def validate_password(v: str) -> str:
    if len(v) < 8:
        raise ValueError('Пароль должен быть не менее 8 символов')
    if not re.search(r'[A-Z]', v):
        raise ValueError('Пароль должен содержать заглавную букву')
    if not re.search(r'[a-z]', v):
        raise ValueError('Пароль должен содержать строчную букву')
    if not re.search(r'\d', v):
        raise ValueError('Пароль должен содержать цифру')
    return v


def validate_slug(v: str) -> str:
    if not v or not v.strip():
        raise ValueError('Slug не может быть пустым')
    if not re.match(r'^[a-z0-9-]+$', v):
        raise ValueError('Slug может содержать только латинские буквы, цифры и дефис')
    if '--' in v:
        raise ValueError('Slug не может содержать двойной дефис')
    return v.lower()


def validate_title(v: str) -> str:
    if not v or not v.strip():
        raise ValueError('Заголовок не может быть пустым')
    if len(v) < 5:
        raise ValueError('Заголовок должен быть не менее 5 символов')
    if len(v) > 200:
        raise ValueError('Заголовок должен быть не более 200 символов')
    return v.strip()


def validate_content(v: str) -> str:
    if not v or not v.strip():
        raise ValueError('Содержимое не может быть пустым')
    if len(v) < 10:
        raise ValueError('Содержимое должно быть не менее 10 символов')
    return v.strip()


def validate_status(v: str) -> str:
    allowed = ["draft", "published", "archived"]
    if v not in allowed:
        raise ValueError(f'Статус должен быть одним из: {", ".join(allowed)}')
    return v

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=150)
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, max_length=150)
    last_name: Optional[str] = Field(None, max_length=150)

    @validator('username')
    def validate_username_field(cls, v):
        return validate_username(v)

    @validator('first_name', 'last_name')
    def validate_name_fields(cls, v):
        if v is not None and v.strip() == '':
            raise ValueError('Имя/фамилия не могут быть пустой строкой')
        return v


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    email: EmailStr

    @validator('password')
    def validate_password_field(cls, v):
        return validate_password(v)


class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=150)
    last_name: Optional[str] = Field(None, max_length=150)
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

    @validator('first_name', 'last_name')
    def validate_name_fields(cls, v):
        if v is not None and v.strip() == '':
            raise ValueError('Имя/фамилия не могут быть пустой строкой')
        return v


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_staff: bool
    date_joined: datetime

    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    slug: str
    description: Optional[str] = Field(None, max_length=500)

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Название категории не может быть пустым')
        return v.strip()

    @validator('slug')
    def validate_slug_field(cls, v):
        return validate_slug(v)


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PostBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    slug: str
    content: str = Field(..., min_length=10)
    category_id: Optional[int] = Field(None, gt=0)
    status: str = Field("draft")

    @validator('title')
    def validate_title_field(cls, v):
        return validate_title(v)

    @validator('slug')
    def validate_slug_field(cls, v):
        return validate_slug(v)

    @validator('content')
    def validate_content_field(cls, v):
        return validate_content(v)

    @validator('status')
    def validate_status_field(cls, v):
        return validate_status(v)


class PostCreate(PostBase):
    author_id: int = Field(..., gt=0)


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    content: Optional[str] = Field(None, min_length=10)
    status: Optional[str] = None
    category_id: Optional[int] = Field(None, gt=0)

    @validator('title')
    def validate_title_field(cls, v):
        return validate_title(v) if v else v

    @validator('content')
    def validate_content_field(cls, v):
        return validate_content(v) if v else v

    @validator('status')
    def validate_status_field(cls, v):
        return validate_status(v) if v else v


class PostResponse(PostBase):
    id: int
    author_id: int
    views_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    post_id: int = Field(..., gt=0)
    parent_id: Optional[int] = Field(None, gt=0)

    @validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('Комментарий не может быть пустым')
        return v.strip()


class CommentCreate(CommentBase):
    author_id: int = Field(..., gt=0)


class CommentResponse(CommentBase):
    id: int
    author_id: int
    is_approved: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    slug: str

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Название тега не может быть пустым')
        return v.strip().lower()

    @validator('slug')
    def validate_slug_field(cls, v):
        return validate_slug(v)


class TagCreate(TagBase):
    pass


class TagResponse(TagBase):
    id: int

    class Config:
        from_attributes = True