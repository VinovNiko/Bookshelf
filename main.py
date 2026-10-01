"""
================================================
# main.py
================================================
"""
from manager import LibraryDBManager
from app import create_app


if __name__ == "__main__":
    db_manager = LibraryDBManager()
    root = create_app(db_manager)
    root.mainloop()
