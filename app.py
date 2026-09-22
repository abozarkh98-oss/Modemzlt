import os
import sqlite3
from flask import Flask, render_template, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "zlt_x28_super_secret_key_2026")
DB_NAME = "database.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # جدول کاربران
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            total_gb REAL DEFAULT 0,
            used_gb REAL DEFAULT 0,
            days_left INTEGER DEFAULT 0,
            admin_msg TEXT DEFAULT '',
            is_admin INTEGER DEFAULT 0
        )
    ''')
    
    # جدول بسته‌ها
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS packages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            data_gb REAL NOT NULL,
            price_toman INTEGER NOT NULL,
            tag TEXT,
            desc TEXT
        )
    ''')
    
    # جدول سفارشات
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            package_name TEXT NOT NULL,
            price_toman INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # ایجاد کاربر ارشد مدیریت پیش‌فرض (admin / admin123)
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (username, password, is_admin) VALUES (?, ?, 1)",
            ("admin", generate_password_hash("admin123"))
        )

    # ایجاد کاربر تست (user1 / 1234)
    cursor.execute("SELECT * FROM users WHERE username = 'user1'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (username, password, total_gb, used_gb, days_left, admin_msg) VALUES (?, ?, 50.0, 18.4, 14, ?)",
            ("user1", generate_password_hash("1234"), "به پنل مدیریت مودم ZLT X28 خوش آمدید.")
        )

    # افزودن بسته‌های اولیه در صورت خالی بودن جدول
    cursor.execute("SELECT COUNT(*) as count FROM packages")
    if cursor.fetchone()['count'] == 0:
        default_pkgs = [
            ("بسته ۱ روزه", "daily", 1, 15000, "اقتصادی", "بسته اقتصادی روزانه مناسب کارهای سبک و پیام‌رسان‌ها"),
            ("بسته ۱ روزه", "daily", 2, 20000, "پرفروش", "سرعت فوق‌العاده مناسب وب‌گردی و شبکه‌های اجتماعی"),
            ("بسته ۱ روزه", "daily", 3, 30000, "استاندارد", "حجم مطلوب برای استفاده یک روزه پرسرعت"),
            ("بسته ۱ روزه ویژه", "daily", 5, 45000, "تخفیف‌دار 10%", "همراه با ۱۰٪ تخفیف ویژه مصرف روزانه بالا"),
            
            ("بسته ۷ روزه استاندارد", "weekly", 5, 50000, "اقتصادی", "مقرون‌به‌صرفه برای یک هفته کار و مرور وب"),
            ("بسته ۷ روزه پرطرفدار", "weekly", 7, 70000, "پرفروش", "مناسب برای استریم متوسط و استفاده روزمره هفتگی"),
            ("بسته ۷ روزه حرفه‌ای", "weekly", 9, 90000, "پیشنهاد ما", "حجم مناسب برای بالاترین سرعت و مصرف هفتگی سنگین"),
            
            ("بسته ۳۰ روزه استاندارد", "monthly", 5, 65000, "اقتصادی", "بسته پایه ماهانه برای اتصال دائمی و سبک"),
            ("بسته ۳۰ روزه متوسط", "monthly", 10, 130000, "متوسط", "مناسب برای کاربران کم‌مصرف در بازه یک ماهه"),
            ("بسته ۳۰ روزه سنگین", "monthly", 50, 600000, "پرفروش", "حجم بالا برای ترافیک کاری، اداری و دانلود مداوم"),
            ("بسته شبانه ماهانه VIP", "monthly", 100, 120000, "شبانه VIP", "مخصوص دانلودهای سنگین در ساعات شبانه (ساعت ۲ الی ۹ صبح)")
        ]
        cursor.executemany(
            "INSERT INTO packages (name, category, data_gb, price_toman, tag, desc) VALUES (?, ?, ?, ?, ?, ?)",
            default_pkgs
        )

    conn.commit()
    conn.close()

init_db()

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/packages', methods=['GET'])
def get_packages():
    conn = get_db()
    pkgs = conn.execute("SELECT * FROM packages").fetchall()
    conn.close()
    return jsonify([dict(p) for p in pkgs])

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')

    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()

    if user and check_password_hash(user['password'], password):
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['is_admin'] = user['is_admin']
        return jsonify({"success": True, "username": user['username'], "is_admin": bool(user['is_admin'])})
    
    return jsonify({"success": False, "message": "نام کاربری یا رمز عبور اشتباه است."}), 401

@app.route('/api/user/status', methods=['GET'])
def user_status():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "احراز هویت نشده‌اید."}), 401

    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    orders = conn.execute("SELECT * FROM orders WHERE username = ? ORDER BY id DESC", (user['username'],)).fetchall()
    conn.close()

    total = user['total_gb']
    used = user['used_gb']
    remaining = max(0.0, total - used)
    percent = round((used / total * 100), 1) if total > 0 else 100

    return jsonify({
        "success": True,
        "username": user['username'],
        "total": total,
        "used": used,
        "remaining": round(remaining, 1),
        "percent": percent,
        "days_left": user['days_left'],
        "admin_msg": user['admin_msg'],
        "orders": [dict(o) for o in orders]
    })

@app.route('/api/buy', methods=['POST'])
def buy_package():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "لطفا ابتدا وارد شوید."}), 401

    data = request.json or {}
    pkg_id = data.get('package_id')

    conn = get_db()
    pkg = conn.execute("SELECT * FROM packages WHERE id = ?", (pkg_id,)).fetchone()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()

    if not pkg or not user:
        conn.close()
        return jsonify({"success": False, "message": "بسته یا کاربر یافت نشد."}), 404

    # بروزرسانی حجم کاربر
    new_total = user['total_gb'] + pkg['data_gb']
    conn.execute("UPDATE users SET total_gb = ? WHERE id = ?", (new_total, user['id']))
    
    # ثبت سفارش
    conn.execute(
        "INSERT INTO orders (username, package_name, price_toman) VALUES (?, ?, ?)",
        (user['username'], pkg['name'] + f" ({pkg['data_gb']}GB)", pkg['price_toman'])
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": f"بسته {pkg['name']} با موفقیت خریداری شد."})

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True})

# --- Admin APIs ---

@app.route('/api/admin/users', methods=['GET', 'POST', 'PUT', 'DELETE'])
def admin_users():
    if not session.get('is_admin'):
        return jsonify({"success": False, "message": "دسترسی غیرمجاز."}), 403

    conn = get_db()

    if request.method == 'GET':
        users = conn.execute("SELECT id, username, total_gb, used_gb, days_left, admin_msg, is_admin FROM users").fetchall()
        conn.close()
        return jsonify([dict(u) for u in users])

    elif request.method == 'POST' or request.method == 'PUT':
        data = request.json or {}
        username = data.get('username')
        password = data.get('password')
        total_gb = float(data.get('total_gb', 0))
        used_gb = float(data.get('used_gb', 0))
        days_left = int(data.get('days_left', 0))
        admin_msg = data.get('admin_msg', '')

        existing = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        if existing:
            query = "UPDATE users SET total_gb=?, used_gb=?, days_left=?, admin_msg=?"
            params = [total_gb, used_gb, days_left, admin_msg]
            if password:
                query += ", password=?"
                params.append(generate_password_hash(password))
            query += " WHERE username=?"
            params.append(username)
            conn.execute(query, params)
        else:
            hashed = generate_password_hash(password or '1234')
            conn.execute(
                "INSERT INTO users (username, password, total_gb, used_gb, days_left, admin_msg) VALUES (?, ?, ?, ?, ?, ?)",
                (username, hashed, total_gb, used_gb, days_left, admin_msg)
            )

        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "اطلاعات کاربر ذخیره شد."})

    elif request.method == 'DELETE':
        data = request.json or {}
        username = data.get('username')
        conn.execute("DELETE FROM users WHERE username = ? AND is_admin = 0", (username,))
        conn.commit()
        conn.close()
        return jsonify({"success": True})

@app.route('/api/admin/packages', methods=['POST', 'DELETE'])
def admin_packages():
    if not session.get('is_admin'):
        return jsonify({"success": False, "message": "دسترسی غیرمجاز."}), 403

    conn = get_db()
    data = request.json or {}

    if request.method == 'POST':
        conn.execute(
            "INSERT INTO packages (name, category, data_gb, price_toman, tag, desc) VALUES (?, ?, ?, ?, ?, ?)",
            (data['name'], data['category'], float(data['data_gb']), int(data['price_toman']), data.get('tag', 'جدید'), data.get('desc', ''))
        )
        conn.commit()
        conn.close()
        return jsonify({"success": True})

    elif request.method == 'DELETE':
        conn.execute("DELETE FROM packages WHERE id = ?", (data.get('id'),))
        conn.commit()
        conn.close()
        return jsonify({"success": True})

@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    if not session.get('is_admin'):
        return jsonify({"success": False, "message": "دسترسی غیرمجاز."}), 403

    conn = get_db()
    user_count = conn.execute("SELECT COUNT(*) as c FROM users WHERE is_admin = 0").fetchone()['c']
    orders = conn.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
    total_revenue = sum(o['price_toman'] for o in orders)
    conn.close()

    return jsonify({
        "user_count": user_count,
        "order_count": len(orders),
        "total_revenue": total_revenue,
        "orders": [dict(o) for o in orders]
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
