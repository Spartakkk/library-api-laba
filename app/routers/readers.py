from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import rules
from app.database import get_db
from app.models import Reader
from app.schemas import ReaderCreate, ReaderOut, ReaderUpdate

router = APIRouter(prefix="/readers", tags=["Читатели"])


def get_reader_or_404(db: Session, reader_id: int):
    reader = db.get(Reader, reader_id)
    if reader is None:
        raise HTTPException(status_code=404, detail="Читатель не найден")
    return reader


def check_email_is_free(db: Session, email: str, reader_id: int | None = None):
    other = db.scalar(select(Reader).where(Reader.email == email))
    if other is not None and other.id != reader_id:
        raise HTTPException(status_code=409, detail="Читатель с таким email уже существует")


@router.get("", response_model=list[ReaderOut])
def list_readers(db: Session = Depends(get_db)):
    return db.scalars(select(Reader).order_by(Reader.id)).all()


@router.get("/{reader_id}", response_model=ReaderOut)
def get_reader(reader_id: int, db: Session = Depends(get_db)):
    return get_reader_or_404(db, reader_id)


@router.post("", response_model=ReaderOut, status_code=201)
def create_reader(data: ReaderCreate, db: Session = Depends(get_db)):
    check_email_is_free(db, data.email)
    reader = Reader(**data.model_dump())
    db.add(reader)
    db.commit()
    db.refresh(reader)
    return reader


@router.patch("/{reader_id}", response_model=ReaderOut)
def update_reader(reader_id: int, data: ReaderUpdate, db: Session = Depends(get_db)):
    reader = get_reader_or_404(db, reader_id)
    if data.email is not None:
        check_email_is_free(db, data.email, reader_id)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(reader, field, value)
    db.commit()
    db.refresh(reader)
    return reader


@router.delete("/{reader_id}", status_code=204)
def delete_reader(reader_id: int, db: Session = Depends(get_db)):
    reader = get_reader_or_404(db, reader_id)
    active_loans = sum(1 for loan in reader.loans if loan.return_date is None)
    rules.check_no_active_loans(active_loans)
    db.delete(reader)
    db.commit()
