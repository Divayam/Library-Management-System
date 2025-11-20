"""
FastAPI server exposing backend services as REST endpoints.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from backend import services  # noqa: E402

app = FastAPI(title="Library Management API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BookPayload(BaseModel):
    title: str
    author: str
    isbn: str | None = None
    total_copies: int


class StudentPayload(BaseModel):
    name: str
    email: str


class BorrowPayload(BaseModel):
    student_id: int
    book_id: int


class ReturnPayload(BaseModel):
    record_id: int


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@app.get("/books")
def list_books() -> List[dict]:
    return services.get_books()


@app.post("/books", status_code=201)
def create_book(payload: BookPayload) -> dict:
    try:
        return services.add_book(
            payload.title, payload.author, payload.isbn, payload.total_copies
        )
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/students")
def list_students() -> List[dict]:
    return services.get_students()


@app.post("/students", status_code=201)
def create_student(payload: StudentPayload) -> dict:
    try:
        return services.add_student(payload.name, payload.email)
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/borrow", status_code=201)
def borrow_book(payload: BorrowPayload) -> dict:
    result = services.borrow_book(payload.student_id, payload.book_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@app.post("/return")
def return_book(payload: ReturnPayload) -> dict:
    result = services.return_book(payload.record_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@app.get("/borrow-records")
def list_borrow_records(status: str | None = None) -> List[dict]:
    return services.list_borrow_records(status=status)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)

