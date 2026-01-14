from flask import Flask, request, render_template, redirect, session
from database import init_db_sync
from database.models import Car
import asyncio
import uuid
import os
from dotenv import load_dotenv
from functools import wraps 


load_dotenv()
ADMIN_PASS = os.getenv("ADMIN_PASS")
SECRET_KEY = os.getenv("SECRET_KEY")

init_db_sync()
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
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Админ-панель</title>
            <style>
                body { font-family: Arial; padding: 20px; }
                a { display: block; padding: 10px; margin: 5px; background: #02818a; color: white; text-decoration: none; border-radius: 5px; }
                a:hover { background: #026b6b; }
            </style>
        </head>
        <body>
            <h1>Админка</h1>
            <a href="/addc4r">Добавить машину</a>
            <a href="/rmc4r"> Удалить машину</a>
            <a href="/"> На главную</a>
            <a href="/list">К списку машин</a>

        </body>
        </html>
        '''
    
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'n4paro1':
            session['is_admin'] = True
        return redirect('/admin')
    
    return render_template('admin.html')


#end of deepseek

@app.route("/list")
def list_cars():
    async def get_cars():
        qs = Car.all()

        if brand := request.args.get("brand"):
            qs = qs.filter(brand__icontains=brand)

        if min_price := request.args.get("price_min"):
            qs = qs.filter(price__gte=int(min_price))

        if max_price := request.args.get("price_max"):
            qs = qs.filter(price__lte=int(max_price))

        return await qs

    cars = asyncio.run(get_cars())
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

        async def _create():
            car = await Car.create(brand = brand, model = model, price = price, photo = photo_path)
            return car
        
        asyncio.run(Car.create(brand=brand, model=model, price=price, photo = photo_path))
        return render_template("success.html")
    return render_template("add_car.html")


@app.route("/rmc4r", methods = ["GET", "POST"])
@admin_required
def rmc4r():
    if request.method == "POST":
        car_id = request.form["car_id"]
        async def _del(cid):
            await Car.filter(id=cid).delete()

        asyncio.run(_del(car_id))
        return render_template("success.html")

    return render_template("delete_car.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)