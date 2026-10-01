"""
================================================
# models.py
================================================
"""
from datetime import date  # библиотека для времени
from pathlib import Path # для бд
import sqlite3 # бд
from typing import List, Optional # список?

# Путь к файлу базы данных
DB_FILE = Path(__file__).with_name("library.db")


# класс - книга
class Book:
    def __init__(self, id: int, title: str, author: str, date_of_release: date, 
                 status: str, reader_id: Optional[int] = None, 
                 date_of_return: Optional[date] = None):
        self.id = id
        self.title = title
        self.author = author
        self.date_of_release = date_of_release # дата издания (20.12.2024)
        self.status = status # "Available", "Taken", "Expired"
        self.reader_id = reader_id # ID читателя, если книга выдана
        self.date_of_return = date_of_return # Дата, до которой нужно вернуть

# класс - читатель
class Reader:
    def __init__(self, id: int, full_name: str):
        self.id = id
        self.full_name = full_name

# класс для истории выдачи
class IssueLog:
    def __init__(self, id: int, book_id: int, reader_id: int, 
                 issue_date: date, return_date: Optional[date] = None):
        self.id = id
        self.book_id = book_id
        self.reader_id = reader_id
        self.issue_date = issue_date # Когда взяли
        self.return_date = return_date # Когда вернули (заполняется при возврате)
