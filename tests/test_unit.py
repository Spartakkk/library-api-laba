from datetime import date

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app import rules
from app.config import LOAN_DAYS, MAX_ACTIVE_LOANS
from app.schemas import BookCreate, ReaderCreate


def test_book_available_when_copies_left():
    rules.check_book_available(1)


def test_book_not_available_when_no_copies():
    with pytest.raises(HTTPException) as error:
        rules.check_book_available(0)
    assert error.value.status_code == 409


def test_reader_below_limit_can_borrow():
    rules.check_reader_limit(MAX_ACTIVE_LOANS - 1)


def test_reader_at_limit_cannot_borrow():
    with pytest.raises(HTTPException) as error:
        rules.check_reader_limit(MAX_ACTIVE_LOANS)
    assert error.value.status_code == 409


def test_book_cannot_be_returned_twice():
    rules.check_not_returned(None)
    with pytest.raises(HTTPException):
        rules.check_not_returned(date(2026, 10, 1))


def test_cannot_delete_with_active_loans():
    rules.check_no_active_loans(0)
    with pytest.raises(HTTPException):
        rules.check_no_active_loans(1)


def test_due_date_is_issue_date_plus_loan_days():
    issue_date = date(2026, 10, 1)
    due_date = rules.calc_due_date(issue_date)
    assert (due_date - issue_date).days == LOAN_DAYS


def test_book_schema_rejects_zero_copies():
    with pytest.raises(ValidationError):
        BookCreate(title="Книга", author="Автор", total_copies=0)


def test_reader_schema_rejects_bad_email():
    with pytest.raises(ValidationError):
        ReaderCreate(name="Иван", email="not-an-email")
