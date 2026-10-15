from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# ---------- Книги ----------


class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200, examples=["Война и мир"])
    author: str = Field(min_length=1, max_length=200, examples=["Лев Толстой"])
    year: int | None = Field(default=None, ge=1000, le=2100, examples=[1869])
    total_copies: int = Field(default=1, ge=1, le=100, examples=[2])


class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    author: str | None = Field(default=None, min_length=1, max_length=200)
    year: int | None = Field(default=None, ge=1000, le=2100)


class BookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # разрешает строить схему из ORM-объекта

    id: int
    title: str
    author: str
    year: int | None
    total_copies: int
    available_copies: int


# ---------- Читатели ----------

PHONE_PATTERN = r"^\+?\d{10,15}$" 


class ReaderCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200, examples=["Иван Петров"])
    email: EmailStr = Field(examples=["ivan@mail.ru"])
    phone: str | None = Field(default=None, pattern=PHONE_PATTERN, examples=["+79991234567"])


class ReaderUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=200)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, pattern=PHONE_PATTERN)


class ReaderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    phone: str | None


# ---------- Выдачи ----------


class LoanCreate(BaseModel):
    book_id: int = Field(gt=0)
    reader_id: int = Field(gt=0)


class LoanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    book_id: int
    reader_id: int
    issue_date: date
    due_date: date
    return_date: date | None
