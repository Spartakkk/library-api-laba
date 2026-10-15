"""Эндпоинты для выдач книг: /loans"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import rules
from app.database import get_db
from app.models import Book, Loan, Reader
from app.schemas import LoanCreate, LoanOut

router = APIRouter(prefix="/loans", tags=["Выдачи"])


def get_loan_or_404(db: Session, loan_id: int):
    loan = db.get(Loan, loan_id)
    if loan is None:
        raise HTTPException(status_code=404, detail="Выдача не найдена")
    return loan


@router.get("", response_model=list[LoanOut])
def list_loans(reader_id: int | None = None, active: bool | None = None, db: Session = Depends(get_db)):
    query = select(Loan).order_by(Loan.id)
    if reader_id is not None:
        query = query.where(Loan.reader_id == reader_id)
    if active is True:
        query = query.where(Loan.return_date.is_(None))
    if active is False:
        query = query.where(Loan.return_date.is_not(None))
    return db.scalars(query).all()


@router.get("/{loan_id}", response_model=LoanOut)
def get_loan(loan_id: int, db: Session = Depends(get_db)):
    return get_loan_or_404(db, loan_id)


@router.post("", response_model=LoanOut, status_code=201)
def issue_book(data: LoanCreate, db: Session = Depends(get_db)):
    book = db.get(Book, data.book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    reader = db.get(Reader, data.reader_id)
    if reader is None:
        raise HTTPException(status_code=404, detail="Читатель не найден")

    # Проверяем бизнес-правила
    active_loans = sum(1 for loan in reader.loans if loan.return_date is None)
    rules.check_reader_limit(active_loans)
    rules.check_book_available(book.available_copies)

    today = date.today()
    loan = Loan(book=book, reader=reader, issue_date=today, due_date=rules.calc_due_date(today))
    book.available_copies -= 1  # один экземпляр ушёл с полки
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


@router.post("/{loan_id}/return", response_model=LoanOut)
def return_book(loan_id: int, db: Session = Depends(get_db)):
    loan = get_loan_or_404(db, loan_id)
    rules.check_not_returned(loan.return_date)

    loan.return_date = date.today()
    loan.book.available_copies += 1  # экземпляр вернулся на полку
    db.commit()
    db.refresh(loan)
    return loan
