import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'super_secret_rgb_key_change_in_production'

# دیتابیس در حافظه
# حساب ادمین پیش‌فرض: نام کاربری admin | رمز عبور admin123
users_db = {
    "admin": {"password": "admin123", "role": "admin"}
}

orders_db = []

@app.route('/')
def home():
    return render_template('index.html', page='home')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # تنها کاربرانی می‌توانند وارد شوند که ادمین قبلاً تعریف کرده است
        if username in users_db and users_db[username]['password'] == password:
            session['user'] = username
            session['role'] = users_db[username]['role']
            flash('با موفقیت وارد شدید.', 'success')
            return redirect(url_for('home'))
        else:
            flash('نام کاربری یا رمز عبور اشتباه است (حساب باید توسط ادمین ساخته شده باشد).', 'error')
            
    return render_template('index.html', page='login')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users_db and users_db[username]['password'] == password and users_db[username]['role'] == 'admin':
            session['user'] = username
            session['role'] = 'admin'
            flash('خوش آمدید، وارد پنل مدیریت شدید.', 'success')
            return redirect(url_for('admin_panel'))
        else:
            flash('اطلاعات مدیریت نادرست است.', 'error')
            
    return render_template('index.html', page='admin_login')

@app.route('/admin')
def admin_panel():
    if session.get('role') != 'admin':
        flash('دسترسی غیرمجاز! لطفاً ابتدا وارد حساب مدیریت شوید.', 'error')
        return redirect(url_for('admin_login'))
    return render_template('index.html', page='admin', users=users_db, orders=orders_db)

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
        flash(f'کاربر {new_username} با موفقیت ساخت شد.', 'success')
        
    return redirect(url_for('admin_panel'))

@app.route('/order', methods=['POST'])
def order():
    if not session.get('user'):
        flash('قبل از خرید باید وارد حساب کاربری خود شوید.', 'error')
        return redirect(url_for('login'))
    
    orders_db.append({"user": session['user'], "item": "محصول ویژه RGB"})
    flash('سفارش شما با موفقیت ثبت شد!', 'success')
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    flash('از حساب کاربری خارج شدید.', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    # پورت پیش‌فرض روی 8080 جهت سازگاری کامل با اینترنت ایران در Railway
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
