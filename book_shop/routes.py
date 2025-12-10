from flask import Blueprint, flash, redirect, render_template, url_for, request
from flask_login import current_user, login_required, login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import Email, EqualTo, InputRequired, Length
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from db.database import session_scope
from db.models import User, Book, Review, CartItem, OrderItem, Order
from werkzeug.security import generate_password_hash, check_password_hash

main_blueprint = Blueprint("main", __name__)


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField(
        "Password", validators=[InputRequired(), Length(min=8, max=36)]
    )


class RegistrationForm(FlaskForm):
    username = StringField("Имя", validators=[InputRequired(), Length(max=100, min=4)])
    phone = StringField("Номер телефона", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Пароль", validators=[InputRequired(), Length(min=8, max=36)])
    confirm_password = PasswordField("Повторите пароль", validators=[InputRequired(), EqualTo("password")])


@main_blueprint.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        with session_scope() as session:
            user = session.query(User).filter((User.email == form.email.data) | (User.phone == form.phone.data)).first()
            if user:
                flash("User with this email or phone already exists!", 'danger')
                return render_template("register.html", form=form)

            user = User(
                username=form.username.data,
                email=form.email.data,
                phone=form.phone.data,
                password_hash=generate_password_hash(form.password.data),
                is_verified=False
            )
            session.add(user)
            session.commit()

            flash("SMS с кодом подтверждения отправлено на ваш телефон!", 'info')
            return redirect(url_for("main.verify_phone", user_id=user.id))
    
    elif form.errors:
        flash(form.errors, category='danger')

    return render_template("register.html", form=form)


@main_blueprint.route("/verify-phone/<int:user_id>", methods=["GET", "POST"])
def verify_phone(user_id):
    with session_scope() as session:
        user = session.query(User).get(user_id)
        if not user:
            return "Пользователь не найден", 404

    if request.method == "POST":
        with session_scope() as session:
            user = session.query(User).get(user_id)
            user.is_verified = True
            session.commit()
        flash("Телефон подтверждён! Теперь вы можете войти.", "success")
        return redirect(url_for("main.login"))

    return render_template("verify_phone.html", user_id=user_id)


@main_blueprint.route("/")
def main_route():
    with session_scope() as session:
        top_books = session.query(Book).order_by(func.random()).limit(3).all()
        
        for book in top_books:
            session.expunge(book)

        genres = (session.query(Book.genre).distinct().order_by(Book.genre).all())
        genres = [genre[0] for genre in genres]

    if current_user.is_authenticated:
        user_data = {
            'is_authenticated': True,
            'name': current_user.username,
            'show_logout': True
        }
    else:
        user_data = {
            'is_authenticated': False,
            'name': 'Гость',
            'show_login': True,
            'show_register': True
        }

    return render_template(
        "home.html",
        user_data=user_data,
        top_books=top_books,
        genres=genres
    )


@main_blueprint.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        with session_scope() as session:
            user = session.query(User).filter_by(email=form.email.data).first()
            if user and check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                return redirect(url_for('main.main_route'))
        flash('Login failed', 'danger')
    return render_template('login.html', form=form)


@main_blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.login'))


@main_blueprint.route("/book/<int:book_id>")
def book_detail(book_id):
    with session_scope() as session:
        book = session.query(Book).get(book_id)
        if not book:
            return "Книга не найдена", 404
        reviews = session.query(Review).filter_by(book_id=book_id).all()
        session.expunge(book)
        for review in reviews:
            session.expunge(review)
    return render_template("book_detail.html", book=book, reviews=reviews)



@main_blueprint.route("/catalog/genre/<genre_name>")
def catalog_by_genre(genre_name):
    with session_scope() as session:
        books = session.query(Book).filter_by(genre=genre_name).all()
        for book in books:
            session.expunge(book)
    return render_template("genre_catalog.html", books=books, genre=genre_name)


@main_blueprint.route("/search/")
def search():
    q = request.args.get("q", "").strip().capitalize()
    with session_scope() as session:
        if q:
            books = (
                session.query(Book).filter((Book.title.contains(q)) | (Book.author.contains(q))).all())
            for book in books:
                session.expunge(book)
        else:
            books = []
    return render_template("search_results.html", books=books, query=q)


@main_blueprint.route('/book/<int:book_id>/add-review', methods=['GET', 'POST'])
@login_required
def add_review(book_id):
    with session_scope() as session:
        book = session.query(Book)\
            .options(joinedload(Book.reviews))\
            .get(book_id)
        
        if not book:
            return "Книга не найдена", 404

        if request.method == 'POST':
            try:
                text = request.form.get('text', '').strip()
                rating_str = request.form.get('rating')

                if not text:
                    flash('Текст отзыва обязателен', 'error')
                    return render_template('add_review.html', book=book)

                if not rating_str or not rating_str.isdigit():
                    flash('Оценка должна быть числом от 1 до 5', 'error')
                    return render_template('add_review.html', book=book)

                rating = int(rating_str)
                if rating < 1 or rating > 5:
                    flash('Оценка должна быть от 1 до 5', 'error')
                    return render_template('add_review.html', book=book)

                review = Review(
                    text=text,
                    rating=rating,
                    book_id=book.id,
                    user_id=current_user.id
                )
                session.add(review)
                session.commit()

                flash('Отзыв успешно добавлен!', 'success')
                return redirect(url_for('main.book_detail', book_id=book.id))

            except Exception as e:
                session.rollback()
                flash(f'Ошибка при сохранении отзыва: {str(e)}', 'error')
                return render_template('add_review.html', book=book)

        return render_template('add_review.html', book=book)



@main_blueprint.route("/cart")
@login_required
def cart():
    with session_scope() as session:
        cart_items = session.query(CartItem).filter_by(user_id=current_user.id).all()
        total_price = sum(item.book.price * item.quantity for item in cart_items)
        
        for item in cart_items:
            session.expunge(item.book)
            session.expunge(item)

    return render_template(
        "cart.html",
        cart_items=cart_items,
        total_price=total_price,
    )

@main_blueprint.route("/add-to-cart/<int:book_id>", methods=["POST"])
@login_required
def add_to_cart(book_id):
    with session_scope() as session:
        book = session.query(Book).get(book_id)
        if not book:
            flash("Книга не найдена", "danger")
            return redirect(url_for("main.main_route"))

        cart_item = session.query(CartItem).filter_by(
            user_id=current_user.id,
            book_id=book_id
        ).first()

        if cart_item:
            cart_item.quantity += 1
        else:
            cart_item = CartItem(user_id=current_user.id, book_id=book_id)
            session.add(cart_item)

        session.commit()
        flash(f"Книга '{book.title}' добавлена в корзину", "success")

    return redirect(url_for("main.book_detail", book_id=book_id))

@main_blueprint.route("/remove-from-cart/<int:item_id>", methods=["POST"])
@login_required
def remove_from_cart(item_id):
    with session_scope() as session:
        cart_item = session.query(CartItem).get(item_id)
        if not cart_item or cart_item.user_id != current_user.id:
            flash("Элемент корзины не найден", "danger")
            return redirect(url_for("main.cart"))


        session.delete(cart_item)
        session.commit()
        flash("Книга удалена из корзины", "info")

    return redirect(url_for("main.cart"))


@main_blueprint.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    with session_scope() as session:
        cart_items = session.query(CartItem).filter_by(user_id=current_user.id).all()
        if not cart_items:
            flash("Корзина пуста", "warning")
            return redirect(url_for("main.cart"))

        total_price = sum(item.book.price * item.quantity for item in cart_items)

        if request.method == "POST":
            delivery_type = request.form.get("delivery_type")
            address = request.form.get("address") if delivery_type == "доставка" else None
            confirm = request.form.get("confirm")

            if not confirm:
                flash("Необходимо подтвердить заказ", "danger")
                return render_template(
                    "checkout.html",
                    cart_items=cart_items,
                    total_price=total_price
                )

            order = Order(
                user_id=current_user.id,
                delivery_type=delivery_type,
                address=address,
                total_price=total_price
            )
            session.add(order)
            session.commit()

            for item in cart_items:
                order_item = OrderItem(
                    order_id=order.id,
                    book_id=item.book_id,
                    quantity=item.quantity,
                    price=item.book.price
                )
                session.add(order_item)
                session.delete(item)

            session.commit()
            flash("Заказ оформлен! Спасибо за покупку.", "success")
            return redirect(url_for("main.main_route"))


        return render_template(
            "checkout.html",
            cart_items=cart_items,
            total_price=total_price
        )

@main_blueprint.route("/orders")
@login_required
def orders():
    with session_scope() as session:
        orders = (
            session.query(Order)
            .filter_by(user_id=current_user.id)
            .options(joinedload(Order.items).joinedload(OrderItem.book)            )
            .order_by(Order.created_at.desc())
            .all()
        )
        
        for order in orders:
            session.expunge(order)
            for item in order.items:
                session.expunge(item.book)

    return render_template("orders.html", orders=orders)
