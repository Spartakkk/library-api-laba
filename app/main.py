from fastapi import FastAPI

from app.routers import books, loans, readers

app = FastAPI(
    title="Библиотека API",
    description="Учёт книг, читателей и выдачи книг",
)

app.include_router(books.router)
app.include_router(readers.router)
app.include_router(loans.router)
