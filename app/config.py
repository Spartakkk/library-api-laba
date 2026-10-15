import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://library:library@localhost:5432/library")

MAX_ACTIVE_LOANS = int(os.getenv("MAX_ACTIVE_LOANS", "3"))

LOAN_DAYS = int(os.getenv("LOAN_DAYS", "14"))
