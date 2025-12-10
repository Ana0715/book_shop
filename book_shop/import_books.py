import json
import os
from db.database import SessionLocal, init_db
from db.models import Book, Base

def load_books_from_json(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def import_books():
    init_db()

    json_path = os.path.join('templates', 'json', 'books.json')
    books_data = load_books_from_json(json_path)

    session = SessionLocal()

    try:
        for book in books_data:
            book_instance = Book(
                id = book['id'],
                title = book['title'],
                author = book['author'],
                price = book['price'],
                genre = book['genre'],
                cover = book.get('cover', None),
                description = book.get('description', None),
                rating = book.get('rating', None),
                year = book.get('year', None)
            )
            session.add(book_instance)
        
        session.commit()
        print(f"Успешно добавлено {len(books_data)} книг.")
    
    except Exception as e:
        session.rollback()
        print(f"Ошибка при импорте: {e}")
    finally:
        session.close()

if __name__ == '__main__':
    import_books()
