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

Files:
.
├── app.py                  # Entry point, Flask setup
├── config.py             # Application Settings
├── database.py            # Configuring SQLAlchemy
├── models.py             # ORM‑models (User, Book)
├── routes.py             # Route handlers
├── import_books.py      # Importing books from JSON to a database
├── requirements.txt       # Dependencies
├── .env                  # Environment variables
├── templates/            # HTML‑templates
│   ├── base.html
│   ├── home.html
│   ├── book_detail.html
│   ├── cart.html
│   ├── checkout.html
│   ├── login.html
│   ├── register.html
│   ├── verify_phone.html
│   ├── orders.html
│   ├── search_results.html
│   ├── genre_catalog.html
│   └── add_review.html
└── templates/json/
    └── books.json        # Data for importing books
<br>

---


