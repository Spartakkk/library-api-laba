from datetime import date, timedelta

from fastapi import HTTPException

from app.config import LOAN_DAYS, MAX_ACTIVE_LOANS

def check_book_available(available_copies: int):
    if available_copies < 1:
        raise HTTPException(status_code=409, detail="Нет свободных экземпляров книги")


def check_reader_limit(active_loans: int):
    if active_loans >= MAX_ACTIVE_LOANS:
        raise HTTPException(
            status_code=409,
            detail=f"Читатель не может взять больше {MAX_ACTIVE_LOANS} книг одновременно",
        )

def check_not_returned(return_date: date | None):
    if return_date is not None:
        raise HTTPException(status_code=409, detail="Эта книга уже возвращена")


def check_no_active_loans(active_loans: int):
    if active_loans > 0:
        raise HTTPException(status_code=409, detail="Нельзя удалить: есть невозвращённые книги")


def calc_due_date(issue_date: date):
    return issue_date + timedelta(days=LOAN_DAYS)
