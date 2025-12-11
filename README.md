# BOOK SHOP REPOSITORY
---

This repository contains the Flask web application files for the online book store.<br>

---

Functional:
- catalog of books filtered by genre;
- search for books by title/author;
- user authentication (registration, login, phone verification);
- shopping cart;
- making orders with a choice of delivery method;
- book reviews (with rating);
- the user's order history.

---

Files:<br>

├── app.py                  # Entry point, Flask setup<br>
├── config.py             # Application Settings<br>
├── database.py            # Configuring SQLAlchemy<br>
├── models.py             # ORM‑models (User, Book)<br>
├── routes.py             # Route handlers<br>
├── import_books.py      # Importing books from JSON to a database<br>
├── requirements.txt       # Dependencies<br>
├── .env                  # Environment variables<br>
├── templates/            # HTML‑templates<br>
│   ├── base.html<br>
│   ├── home.html<br>
│   ├── book_detail.html<br>
│   ├── cart.html<br>
│   ├── checkout.html<br>
│   ├── login.html<br>
│   ├── register.html<br>
│   ├── verify_phone.html<br>
│   ├── orders.html<br>
│   ├── search_results.html<br>
│   ├── genre_catalog.html<br>
│   └── add_review.html<br>
└── templates/json/<br>
    └── books.json        # Data for importing books<br>
<br>

Main routes:
- /
- /catalog/genre/<genre_name>
- /search/
- /book/<id>
- /book/<id>/add-review
- /cart
- /add-to-cart/<id>
- /remove-from-cart/<id>
- /checkout
- /orders
- /login
- /register
- /verify-phone/<id>
- /logout

---

Requirements:<br>
- Python 3.9+;
- PostgreSQL (or another database supported by SQLAlchemy);
- pip for installing dependencies;

---

Installation and launch:
- Copy the repository
- - git clone [URL](https://github.com/Ana0715/book_shop)
- - cd book_shop
- Create a virtual environment
- - python -m venv venv
- - source venv/bin/activate # Linux/macOS
- - venv\Scripts\activate    # Windows
- Install dependencies
- - pip install -r requirements.txt
- Set up environment variables
- - Create a file .env in the root of the project:
- - - DATABASE_URL=postgresql://<user>:<password>@localhost:5432/<base name>
- - - SECRET_KEY=<random_stringe_note_32_characters>
- - - APP_PORT=5000
- - - DEBUG=True
- - For SQLite:
- - - DATABASE_URL=sqlite:///book_shop.db
- Configuring the database
- - For PostgreSQL:
- - Install PostgreSQL.
- - Create a database:
- - - CREATE DATABASE book_shop_db;
- - - CREATE USER book_user WITH ENCRYPTED PASSWORD 'your_password';
- - - GRANT ALL PRIVILEGES ON DATABASE book_shop_db TO book_user;
- - Specify in .env:
- - - DATABASE_URL=postgresql://book_user:your_password@localhost:5432/book_shop_db
- - For SQLite (default):
- - The database is created automatically in the root of the project as book_shop.db.
- Initialize the database
- - python import_books.py
- - This script will create tables in the database, downloads books from templates/json/books.json.
- Launch the application:
- - python app.py
- Open it in a browser:
- - http://localhost:5000
