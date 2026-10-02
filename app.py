"""
================================================
# app.py
================================================
"""
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

# Глобальные переменные интерфейса, чтобы main.py мог получить к ним доступ
table = None
status_label = None
reader_combobox = None
db = None
readers_cache = {} # Хранилище пар { "Имя (ID: 1)": 1 } для быстрой фильтрации ID


def load_books():
    # Обновляет таблицу книг на экране, получая свежие данные из базы
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


def load_readers():
    # Загружает читателей из базы и заполняет выпадающий список
    global readers_cache
    try:
        readers = db.get_all_readers()
    except sqlite3.Error as error:
        messagebox.showerror("Ошибка базы данных", f"Не удалось загрузить читателей:\n{error}")
        return

    dropdown_values = []
    readers_cache = {}

    for r_id, name in readers:
        display_text = f"{name} (ID: {r_id})"
        dropdown_values.append(display_text)
        readers_cache[display_text] = r_id

    reader_combobox['values'] = dropdown_values
    if dropdown_values:
        reader_combobox.current(0)


def action_take_book():
    # Обработчик кнопки взять книгу
    selected_book = table.selection()
    if not selected_book:
        messagebox.showwarning("Внимание", "Пожалуйста, выберите книгу из списка!")
        return

    selected_reader_text = reader_combobox.get()
    if not selected_reader_text:
        messagebox.showwarning("Внимание", "Нет доступных читателей!")
        return

    reader_id = readers_cache.get(selected_reader_text)

    book_values = table.item(selected_book)["values"]
    book_id = book_values[0]
    book_title = book_values[1]

    success = db.take_book(book_id=book_id, reader_id=reader_id)
    if success:
        messagebox.showinfo("Успех", f"Книга '{book_title}' успешно выдана читателю {selected_reader_text}!")
        load_books()
    else:
        messagebox.showerror("Ошибка", "Не удалось выдать книгу. Возможно, она уже занята.")


def action_return_book():
    # Обработчик кнопки вернуть книгу
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
    # Создает окно интерфейса
    global table, status_label, reader_combobox, db
    db = db_manager

    root = tk.Tk()
    root.title("Система учета библиотеки")
    root.geometry("950x520")

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

    reader_frame = ttk.LabelFrame(root, text=" Выдача книги читателю ")
    reader_frame.pack(fill="x", padx=20, pady=10)

    ttk.Label(reader_frame, text="Выберите читателя:").pack(side="left", padx=10, pady=10)
    
    reader_combobox = ttk.Combobox(reader_frame, state="readonly", width=40)
    reader_combobox.pack(side="left", padx=10, pady=10)

    controls = ttk.Frame(root)
    controls.pack(fill="x", padx=20, pady=14)

    ttk.Button(controls, text="🔄 Обновить список", command=load_books).pack(side="left", padx=5)
    ttk.Button(controls, text="📖 Выдать выбранную книгу", command=action_take_book).pack(side="left", padx=5)
    ttk.Button(controls, text="📥 Вернуть книгу", command=action_return_book).pack(side="left", padx=5)

    status_label = ttk.Label(controls, text="")
    status_label.pack(side="right")

    load_books()
    load_readers()
    return root
