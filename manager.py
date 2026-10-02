"""
================================================
# manager.py
================================================
"""
from datetime import date, timedelta # библиотека для времени, и разницы времени
from pathlib import Path # для бд
import sqlite3 # бд
from typing import List, Optional # список?


DB_FILE = Path(__file__).with_name("library.db")

# Менеджер библиотеки для SQLite
class LibraryDBManager:
    
    def __init__(self, db_path: Path = DB_FILE):
        self.db_path = db_path
        self._init_db()
        self._seed_data()

    def _init_db(self):
        # Создает таблицы в базе данных, если их еще нет
        with sqlite3.connect(self.db_path) as conn:
            # Таблица читателей
            conn.execute("""
                CREATE TABLE IF NOT EXISTS readers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL
                )
            """)
            # Таблица книг (статус, id читателя и дата возврата хранятся тут, так как книга в одном экземпляре)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    date_of_release INTEGER NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Available',
                    reader_id INTEGER REFERENCES readers(id) ON DELETE SET NULL,
                    date_of_return TEXT
                )
            """)
            # Таблица истории выдачи
            conn.execute("""
                CREATE TABLE IF NOT EXISTS issue_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
                    reader_id INTEGER NOT NULL REFERENCES readers(id) ON DELETE CASCADE,
                    issue_date TEXT NOT NULL,
                    return_date TEXT
                )
            """)

    def _seed_data(self):
        # Заполняет базу первичными данными для теста, если она пуста
        with sqlite3.connect(self.db_path) as conn:
            # Проверяем книги
            if conn.execute("SELECT COUNT(*) FROM books").fetchone()[0] == 0:
                conn.executemany(
                    "INSERT INTO books (title, author, date_of_release) VALUES (?, ?, ?)",
                    [
                        ("Гарри Поттер", "Дж. К. Роулинг", 1997),
                        ("1984", "Джордж Оруэлл", 1949),
                        ("Мастер и Маргарита", "Михаил Булгаков", 1967)
                    ]
                )
            # Проверяем читателей
            if conn.execute("SELECT COUNT(*) FROM readers").fetchone()[0] == 0:
                conn.executemany(
                    "INSERT INTO readers (full_name) VALUES (?)",
                    [
                        ("Иван Иванов",),
                        ("Светлана Петрова",)
                    ]
                )

    # Операции с Книгами
    # добавить
    def add_book(self, title: str, author: str, date_of_release: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO books (title, author, date_of_release) VALUES (?, ?, ?)",
                (title, author, date_of_release)
            )

    # получить названия
    def get_all_books(self) -> List[tuple]:
        """Возвращает список всех книг для вывода в таблицу Tkinter."""
        with sqlite3.connect(self.db_path) as conn:
            # Получаем книги вместе с именами читателей (если книга выдана)
            return conn.execute("""
                SELECT b.id, b.title, b.author, b.date_of_release, b.status, r.full_name, b.date_of_return
                FROM books b
                LEFT JOIN readers r ON b.reader_id = r.id
                ORDER BY b.id
            """).fetchall()

    # Логика выдачи и возврата 
    # взять
    def take_book(self, book_id: int, reader_id: int, days_to_keep: int = 14) -> bool:
        """Выдать книгу читателю."""
        return_date_str = (date.today() + timedelta(days=days_to_keep)).isoformat()
        today_str = date.today().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            # Проверяем, доступна ли книга
            status = conn.execute("SELECT status FROM books WHERE id = ?", (book_id,)).fetchone()
            if not status or status[0] != "Available":
                return False
            
            # Обновляем статус книги
            conn.execute("""
                UPDATE books 
                SET status = 'Taken', reader_id = ?, date_of_return = ? 
                WHERE id = ?
            """, (reader_id, return_date_str, book_id))
            
            # Записываем в историю
            conn.execute("""
                INSERT INTO issue_logs (book_id, reader_id, issue_date) 
                VALUES (?, ?, ?)
            """, (book_id, reader_id, today_str))
            return True

    # вернуть
    def return_book(self, book_id: int) -> bool:
        today_str = date.today().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            # Проверяем, выдана ли книга
            status = conn.execute("SELECT status FROM books WHERE id = ?", (book_id,)).fetchone()
            if not status or status[0] != "Taken":
                return False
            
            # Обновляем (ставим дату возврата)
            conn.execute("""
                UPDATE issue_logs 
                SET return_date = ? 
                WHERE book_id = ? AND return_date IS NULL
            """, (today_str, book_id))
            
            # Сбрасываем поля в таблице книг
            conn.execute("""
                UPDATE books 
                SET status = 'Available', reader_id = NULL, date_of_return = NULL 
                WHERE id = ?
            """, (book_id,))
            return True

    # вывести всех читателей
    def get_all_readers(self) -> List[tuple]:
        # Получает список всех зарегистрированных читателей (id, full_name)
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute("SELECT id, full_name FROM readers ORDER BY full_name").fetchall()
