"""
Data access layer for the Library Management System.
"""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional

from postgrest import APIError

from .db import get_client


def _handle_response(response) -> List[Dict[str, Any]]:
    error = getattr(response, "error", None)
    if error:
        raise APIError(error)
    data = getattr(response, "data", None)
    if data is None:
        return []
    return data


def _single(table: str, column: str, value: Any) -> Optional[Dict[str, Any]]:
    client = get_client()
    response = (
        client.table(table)
        .select("*")
        .eq(column, value)
        .limit(1)
        .execute()
    )
    data = _handle_response(response)
    return data[0] if data else None


# ------------------------- BOOK SERVICES ------------------------- #
def get_book(book_id: int) -> Optional[Dict[str, Any]]:
    return _single("books", "id", book_id)


def get_books() -> List[Dict[str, Any]]:
    client = get_client()
    response = client.table("books").select("*").order("title").execute()
    return _handle_response(response)


def add_book(title: str, author: str, isbn: Optional[str], total_copies: int) -> Dict[str, Any]:
    if total_copies < 1:
        raise ValueError("Total copies must be at least 1.")

    payload = {
        "title": title,
        "author": author,
        "isbn": isbn,
        "total_copies": total_copies,
        "available_copies": total_copies,
    }
    client = get_client()
    response = client.table("books").insert(payload).execute()
    data = _handle_response(response)
    return data[0] if data else {}


def update_book(book_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    client = get_client()
    response = client.table("books").update(data).eq("id", book_id).execute()
    updated = _handle_response(response)
    return updated[0] if updated else {}


# ------------------------ STUDENT SERVICES ----------------------- #
def get_student(student_id: int) -> Optional[Dict[str, Any]]:
    return _single("students", "id", student_id)


def get_students() -> List[Dict[str, Any]]:
    client = get_client()
    response = client.table("students").select("*").order("name").execute()
    return _handle_response(response)


def add_student(name: str, email: str) -> Dict[str, Any]:
    payload = {"name": name, "email": email}
    client = get_client()
    response = client.table("students").insert(payload).execute()
    data = _handle_response(response)
    return data[0] if data else {}


# --------------------- BORROW RECORD SERVICES -------------------- #
def get_borrow_record(record_id: int) -> Optional[Dict[str, Any]]:
    return _single("borrow_records", "id", record_id)


def list_borrow_records(status: Optional[str] = None) -> List[Dict[str, Any]]:
    client = get_client()
    query = client.table("borrow_records").select("*").order("borrow_date", desc=True)
    if status:
        query = query.eq("status", status)
    response = query.execute()
    return _handle_response(response)


def borrow_book(student_id: int, book_id: int) -> Dict[str, Any]:
    client = get_client()

    student = get_student(student_id)
    if not student:
        return {"success": False, "error": "Student does not exist."}

    book = get_book(book_id)
    if not book:
        return {"success": False, "error": "Book does not exist."}

    available = book.get("available_copies", 0)
    if available <= 0:
        return {"success": False, "error": "No copies available."}

    response = (
        client.table("borrow_records")
        .insert(
            {
                "student_id": student_id,
                "book_id": book_id,
                "borrow_date": str(date.today()),
                "status": "borrowed",
            }
        )
        .execute()
    )
    try:
        _handle_response(response)
    except APIError as exc:
        return {"success": False, "error": str(exc)}

    new_available = max(available - 1, 0)
    client.table("books").update({"available_copies": new_available}).eq("id", book_id).execute()

    return {"success": True, "message": "Book borrowed successfully."}


def return_book(record_id: int) -> Dict[str, Any]:
    client = get_client()

    record = get_borrow_record(record_id)
    if not record:
        return {"success": False, "error": "Record not found."}

    if record.get("status") == "returned":
        return {"success": False, "error": "Book already returned."}

    book = get_book(record["book_id"])
    if not book:
        return {"success": False, "error": "Book does not exist."}

    client.table("borrow_records").update(
        {
            "return_date": str(date.today()),
            "status": "returned",
        }
    ).eq("id", record_id).execute()

    total = book.get("total_copies", 0)
    available = book.get("available_copies", 0)
    new_available = min(available + 1, total if total else available + 1)
    client.table("books").update({"available_copies": new_available}).eq("id", book["id"]).execute()

    return {"success": True, "message": "Book returned successfully."}

