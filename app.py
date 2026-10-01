"""
================================================
# app.py
================================================
"""
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

# Переменные для хранения интерфейса, чтобы main.py мог получить к ним доступ
table = None
status_label = None
db = None

def load_books():
    """Обновляет таблицу книг на экране, получая свежие данные из базы."""
    for item in table.get_children():
        table.delete(item)

    try:
        rows = db.get_all_books()
    except sqlite3.Error as error:
        messagebox.showerror("Ошибка базы данных", f"Не удалось загрузить данные:\n{error}")
        return

    for row in rows:
        display_row = list(row)
        if display_row[5] is None: # Если читатель NULL
            display_row[5] = "—"
        if display_row[6] is None: # Если дата возврата NULL
            display_row[6] = "—"
            
        table.insert("", tk.END, values=display_row)

    status_label.config(text=f"Всего книг в библиотеке: {len(rows)}")


def action_take_book():
    """Обработчик кнопки 'Выдать книгу'."""
    selected = table.selection()
    if not selected:
        messagebox.showwarning("Внимание", "Пожалуйста, выберите книгу из списка!")
        return

    book_values = table.item(selected)["values"]
    book_id = book_values[0]
    book_title = book_values[1]

    # !!!
    # Заглушка: выдаем первому читателю
    reader_id = 1  
    # !!!

    success = db.take_book(book_id=book_id, reader_id=reader_id)
    if success:
        messagebox.showinfo("Успех", f"Книга '{book_title}' успешно выдана Иванову И.!")
        load_books()
    else:
        messagebox.showerror("Ошибка", "Не удалось выдать книгу. Возможно, она уже занята.")


def action_return_book():
    # Обработчик кнопки 'Вернуть книгу'
    selected = table.selection()
    if not selected:
        messagebox.showwarning("Внимание", "Пожалуйста, выберите книгу для возврата!")
        return

    book_values = table.item(selected)["values"]
    book_id = book_values[0]
    book_title = book_values[1]

    success = db.return_book(book_id=book_id)
    if success:
        messagebox.showinfo("Успех", f"Книга '{book_title}' возвращена в библиотеку.")
        load_books()
    else:
        messagebox.showerror("Ошибка", "Эта книга и так находится в библиотеке!")


def create_app(db_manager):
    # Функция инициализации и сборки окна интерфейса
    global table, status_label, db
    db = db_manager # Привязываем менеджер бд к логике кнопок

    root = tk.Tk()
    root.title("Система учета библиотеки")
    root.geometry("950x450")

    title = ttk.Label(root, text="Управление книжным фондом", font=("Arial", 18, "bold"))
    title.pack(pady=(18, 10))

    columns = ("id", "title", "author", "year", "status", "reader", "deadline")
    table = ttk.Treeview(root, columns=columns, show="headings", height=12)

    headings = ("ID", "Название книги", "Автор", "Год", "Статус", "Кто взял", "Вернуть до")
    widths = (50, 200, 150, 80, 100, 180, 120)

    for column, heading, width in zip(columns, headings, widths):
        table.heading(column, text=heading)
        table.column(column, width=width, anchor="center")

    table.pack(fill="both", expand=True, padx=20)

    controls = ttk.Frame(root)
    controls.pack(fill="x", padx=20, pady=14)

    ttk.Button(controls, text="🔄 Обновить список", command=load_books).pack(side="left", padx=5)
    ttk.Button(controls, text="📖 Выдать книгу (ID:1)", command=action_take_book).pack(side="left", padx=5)
    ttk.Button(controls, text="📥 Вернуть книгу", command=action_return_book).pack(side="left", padx=5)

    status_label = ttk.Label(controls, text="")
    status_label.pack(side="right")

    load_books() # Загружаем данные при старте
    return root # для main.py
