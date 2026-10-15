from datetime import date

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    author: Mapped[str] = mapped_column(String(200))
    year: Mapped[int | None]
    total_copies: Mapped[int]  
    available_copies: Mapped[int]

    loans: Mapped[list["Loan"]] = relationship(back_populates="book", cascade="all, delete-orphan")


class Reader(Base):
    __tablename__ = "readers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(200), unique=True)
    phone: Mapped[str | None] = mapped_column(String(20)) 

    loans: Mapped[list["Loan"]] = relationship(back_populates="reader", cascade="all, delete-orphan")


class Loan(Base):
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))
    reader_id: Mapped[int] = mapped_column(ForeignKey("readers.id"))
    issue_date: Mapped[date]  # когда выдали
    due_date: Mapped[date]  # когда нужно вернуть
    return_date: Mapped[date | None]  # когда вернули (None — книга ещё у читателя)

    book: Mapped[Book] = relationship(back_populates="loans")
    reader: Mapped[Reader] = relationship(back_populates="loans")
