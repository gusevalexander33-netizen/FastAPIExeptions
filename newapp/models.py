from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    password = Column(String(100), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    is_superuser = Column(Boolean, default=False)
    username = Column(String(150), unique=True, index=True, nullable=False)
    email = Column(String(254), unique=True, index=True, nullable=False)
    first_name = Column(String(150), nullable=True)
    last_name = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    is_staff = Column(Boolean, default=False)
    date_joined = Column(DateTime(timezone=True), server_default=func.now())
    bio = Column(Text, nullable=True)

    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="author")

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

class Category(Base):
        __tablename__ = 'categories'

        id = Column(Integer, primary_key=True, index=True, nullable=False)
        name = Column(String(100), unique=True, index=True, nullable=False)
        slug = Column(String(100), unique=True, index=True, nullable=False)
        description = Column(Text, nullable=True)
        created_at = Column(DateTime(timezone=True), server_default=func.now())

        posts = relationship("Post", back_populates="category")

        def __repr__(self):
            return f"<Category(name='{self.name}'"

class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), unique=True, index=True, nullable=False)
    slug = Column(String(200), unique=True, index=True, nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    status = Column(String(20), default='draft')
    view_count = Column(Integer, default=0)
    published_at = Column(DateTime(timezone=True), nullable=True)

    author = relationship("User", back_populates="posts")
    category = relationship("Category", back_populates="posts")
    comments = relationship("Comment", back_populates="posts")
    tags = relationship("Tag", back_populates="posts")

    def __repr__(self):
        return f"<Post(title='{self.title}', slug='{self.slug}')>"

class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    parent_post_id = Column(Integer, ForeignKey('posts.id'), nullable=True)
    is_approved = Column(Boolean, default=True)

    author = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")
    replies = relationship("Comment", backref="parent", remote_side="comments")

    def __repr__(self):
        return f"<Comment(content='{self.content}', author_id='{self.author_id}')>"

class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)

    def __repr__(self):
        return f"<Tag(name='{self.name}')>"

