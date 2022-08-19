from sqlite3 import DatabaseError
from fastapi import Depends, FastAPI
from sqlalchemy import create_engine, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
import os
import schemas

app = FastAPI()

# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:root@localhost:5432/ecs"

DB_ENDPOINT = os.getenv("endpoint")
DB_USERNAME = os.getenv("username")
DB_PASSWORD = os.getenv("password")

# SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
    #   postgresql://<username>:<password>@<db_endpoint>:5432/ecs

SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_ENDPOINT}:5432/ecs"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Book(Base):
    __tablename__ = "Books"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    author = Column(String)

Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/books/{book_name}")
def read_item(book_name: str, db: Session = Depends(get_db)):
    return db.query(Book).filter(Book.name == book_name).first()


@app.post("/books", response_model=schemas.Book)
def place_item(book: schemas.Book, db: Session = Depends(get_db)):
    db_book = Book(name=book.name, author=book.author)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@app.get("/")
def hello_world():
    return "Hello, World!"
    