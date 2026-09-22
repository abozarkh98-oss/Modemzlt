import os
from flask import Flask, render_template_string, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'super_secret_rgb_key'

# دیتابیس نمونه در حافظه (می‌توانید کاربران و سفارش‌ها را مدیریت کنید)
# نام کاربری ادمین پیش‌فرض: admin | رمز عبور: admin123
users_db = {
    "admin": {"password": "admin123", "role": "admin"}
}

orders_db = []

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>فروشگاه آنلاین RGB</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Tahoma', 'Segoe UI', sans-serif;
        }
        body {
            background-color: #0d0d13;
            color: #ffffff;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        
        /* افکت افقی RGB Header */
        header {
            width: 100%;
            padding: 20px;
            text-align: center;
            background: rgba(20, 20, 30, 0.8);
            border-bottom: 3px solid;
            border-image: linear-gradient(90deg, #ff0055, #00e5ff, #7600ff, #ff0055) 1;
            animation: rgb-border 4s linear infinite;
            box-shadow: 0 0 15px rgba(0, 229, 255, 0.3);
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 40px;
        }

        @keyframes rgb-border {
            0% { filter: hue-rotate(0deg); }
            100% { filter: hue-rotate(360deg); }
        }

        .logo {
            font-size: 24px;
            font-weight: bold;
            color: #00e5ff;
            text-shadow: 0 0 10px #00e5ff;
        }

        nav a {
            color: #fff;
            text-decoration: none;
            margin: 0 10px;
            padding: 8px 16px;
            border-radius: 5px;
            border: 1px solid transparent;
            transition: 0.3s;
        }

        nav a:hover {
            border-color: #ff0055;
            box-shadow: 0 0 10px #ff0055;
            color: #ff0055;
        }

        .container {
            width: 90%;
            max-width: 1000px;
            margin: 40px auto;
            background: #161622;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 0 20px rgba(118, 0, 255, 0.2);
            border: 1px solid #2a2a3d;
        }

        .rgb-card {
            background: #1c1c2b;
            border: 2px solid #2a2a40;
            border-radius: 10px;
            padding: 20px;
            margin: 15px 0;
            transition: 0.3s;
        }

        .rgb-card:hover {
            border-color: #00e5ff;
            box-shadow: 0 0 15px rgba(0, 229, 255, 0.4);
        }

        .btn {
            background: linear-gradient(45deg, #ff0055, #7600ff);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            text-decoration: none;
            display: inline-block;
            transition: 0.3s;
            box-shadow: 0 0 10px rgba(255, 0, 85, 0.4);
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 0 20px rgba(255, 0, 85, 0.8);
        }

        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 12px;
            margin: 10px 0 20px 0;
            background: #0d0d13;
            border: 1px solid #333;
            color: white;
            border-radius: 6px;
        }

        input[type="text"]:focus, input[type="password"]:focus {
            outline: none;
            border-color: #00e5ff;
            box-shadow: 0 0 8px #00e5ff;
        }

        .alert {
            padding: 10px;
            background: #ff005522;
            border: 1px solid #ff0055;
            color: #ff0055;
            border-radius: 6px;
            margin-bottom: 20px;
        }
        
        .success {
            padding: 10px;
            background: #00e5ff22;
            border: 1px solid #00e5ff;
            color: #00e5ff;
            border-radius: 6px;
            margin-bottom: 20px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }

        th, td {
            padding: 12px;
            text-align: right;
            border-bottom: 1px solid #2a2a3d;
        }

        th {
            color: #00e5ff;
        }
    </style>
</head>
<body>

    <header>
        <div class="logo">فروشگاه RGB</div>
        <nav>
            <a href="/">صفحه اصلی</a>
            {% if session.get('user') %}
                <span>خوش آمدید، {{ session['user'] }}</span>
                {% if session.get('role') == 'admin' %}
                    <a href="/admin" style="border-color: #00e5ff;">مدیریت</a>
                {% endif %}
                <a href="/logout">خروج</a>
            {% else %}
                <a href="/login">ورود کاربر</a>
                <a href="/admin/login">ورود مدیریت</a>
            {% endif %}
        </nav>
    </header>

    <div class="container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="{{ 'success' if category == 'success' else 'alert' }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        {% if page == 'home' %}
            <h2>محصولات ویژه</h2>
            <div class="rgb-card">
                <h3>محصول RGB آنلاین</h3>
                <p>قیمت: ۱۰۰,۰۰۰ تومان</p>
                <br>
                {% if session.get('user') %}
                    <form action="/order" method="POST">
                        <button type="submit" class="btn">ثبت سفارش</button>
                    </form>
                {% else %}
                    <p style="color: #ff0055; margin-bottom: 10px;">برای ثبت سفارش باید قبل از خرید وارد حساب کاربری خود شوید.</p>
                    <a href="/login" class="btn">ورود به حساب جهت خرید</a>
                {% endif %}
            </div>

        {% elif page == 'login' %}
            <h2>ورود به حساب کاربری</h2>
            <form method="POST" action="/login">
                <label>نام کاربری:</label>
                <input type="text" name="username" required>
                <label>رمز عبور:</label>
                <input type="password" name="password" required>
                <button type="submit" class="btn">ورود</button>
            </form>

        {% elif page == 'admin_login' %}
            <h2>ورود به پنل مدیریت</h2>
            <form method="POST" action="/admin/login">
                <label>نام کاربری مدیر:</label>
                <input type="text" name="username" required>
                <label>رمز عبور مدیر:</label>
                <input type="password" name="password" required>
                <button type="submit" class="btn">ورود به پنل مدیریت</button>
            </form>

        {% elif page == 'admin' %}
            <h2>پنل مدیریت ادمین</h2>
            <div class="rgb-card">
                <h3>ساخت کاربر جدید (توسط ادمین)</h3>
                <form method="POST" action="/admin/create_user">
                    <label>نام کاربری جدید:</label>
                    <input type="text" name="new_username" required>
                    <label>رمز عبور:</label>
                    <input type="password" name="new_password" required>
                    <button type="submit" class="btn">ایجاد کاربر</button>
                </form>
            </div>

            <div class="rgb-card">
                <h3>لیست کاربران تعریف‌شده</h3>
                <ul>
                    {% for u in users %}
                        <li>{{ u }} (نقش: {{ users[u]['role'] }})</li>
                    {% endfor %}
                </ul>
            </div>

            <div class="rgb-card">
                <h3>لیست سفارشات ثبت شده</h3>
                {% if orders %}
                    <table>
                        <tr>
                            <th>کاربر</th>
                            <th>محصول</th>
                        </tr>
                        {% for order in orders %}
                            <tr>
                                <td>{{ order.user }}</td>
                                <td>{{ order.item }}</td>
                            </tr>
                        {% endfor %}
                    </table>
                {% else %}
                    <p>هیچ سفارشی ثبت نشده است.</p>
                {% endif %}
            </div>
        {% endif %}
    </div>

</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, page='home')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # بررسی صحت حساب تعریف شده توسط ادمین
        if username in users_db and users_db[username]['password'] == password:
            session['user'] = username
            session['role'] = users_db[username]['role']
            flash('با موفقیت وارد شدید.', 'success')
            return redirect(url_for('home'))
        else:
            flash('نام کاربری یا رمز عبور اشتباه است (حساب باید توسط ادمین ساخته شده باشد).', 'error')
            
    return render_template_string(HTML_TEMPLATE, page='login')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users_db and users_db[username]['password'] == password and users_db[username]['role'] == 'admin':
            session['user'] = username
            session['role'] = 'admin'
            flash('ورود موفق به پنل مدیریت.', 'success')
            return redirect(url_for('admin_panel'))
        else:
            flash('اطلاعات مدیریت نادرست است.', 'error')
            
    return render_template_string(HTML_TEMPLATE, page='admin_login')

@app.route('/admin')
def admin_panel():
    if session.get('role') != 'admin':
        flash('دسترسی غیرمجاز. لطفا ابتدا وارد حساب ادمین شوید.', 'error')
        return redirect(url_for('admin_login'))
    return render_template_string(HTML_TEMPLATE, page='admin', users=users_db, orders=orders_db)

@app.route('/admin/create_user', methods=['POST'])
def create_user():
    if session.get('role') != 'admin':
        return redirect(url_for('home'))
    
    new_username = request.form.get('new_username')
    new_password = request.form.get('new_password')
    
    if new_username in users_db:
        flash('این نام کاربری قبلاً وجود دارد.', 'error')
    else:
        users_db[new_username] = {"password": new_password, "role": "user"}
        flash(f'کاربر {new_username} با موفقیت ساخته شد.', 'success')
        
    return redirect(url_for('admin_panel'))

@app.route('/order', methods=['POST'])
def order():
    if not session.get('user'):
        flash('قبل از خرید باید وارد حساب کاربری خود شوید.', 'error')
        return redirect(url_for('login'))
    
    orders_db.append({"user": session['user'], "item": "محصول RGB آنلاین"})
    flash('سفارش شما با موفقیت ثبت شد!', 'success')
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    flash('از حساب کاربری خارج شدید.', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    # تنظیم پورت روی 8080 جهت ناسازگاری نداشتن با اینترنت ایران در Railway
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
