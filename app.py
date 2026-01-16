from flask import Flask, request, render_template, redirect, session
from database.db import init_db, db
from database.models import Car
import uuid
import os
from dotenv import load_dotenv
from functools import wraps 


load_dotenv()
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")
SECRET_KEY = os.getenv("SECRET_KEY")

app = Flask(__name__)
app.secret_key = SECRET_KEY


@app.route("/")
def home():
    return render_template("home.html")

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            return redirect('/admin')
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # Если уже авторизован - показываем админ-панель
    if session.get('is_admin'):
        return render_template('admin_panel.html')
    
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASS:
            session['is_admin'] = True
        return redirect('/admin')
    
    return render_template('admin.html')


@app.route("/list")
def list_cars():
    qs = Car.query

    if brand := request.args.get("brand"):
        qs = qs.filter(Car.brand.ilike(f"%{brand}%"))

    if min_price := request.args.get("price_min"):
        qs = qs.filter(Car.price >= int(min_price))

    if max_price := request.args.get("price_max"):
        qs = qs.filter(Car.price <= int(max_price))

    cars = qs.all()
    return render_template("list_of_cars.html", cars=cars)

@app.route("/addc4r", methods=["GET", "POST"])
@admin_required
def addc4r():
    if request.method == "POST":
        brand = request.form["brand"]
        model = request.form["model"]
        price = request.form["price"]
        photo = request.files["photo"]

        ext = photo.filename.rsplit(".", 1)[1]
        filename = f"{uuid.uuid4()}.{ext}"
        path = os.path.join("static/uploads", filename)
        photo.save(path)
        photo_path = f"uploads/{filename}"

        car = Car(
            brand=brand,
            model=model,
            price=int(price),
            photo=photo_path
        )
        db.session.add(car)
        db.session.commit()
        return render_template("success.html")
    return render_template("add_car.html")


@app.route("/rmc4r", methods=["GET", "POST"])
@admin_required
def rmc4r():
    if request.method == "POST":
        car_id = request.form["car_id"]
        Car.query.filter_by(id=car_id).delete()
        db.session.commit()
        return render_template("success.html")
    return render_template("delete_car.html")

if __name__ == "__main__":
    init_db(app)
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)