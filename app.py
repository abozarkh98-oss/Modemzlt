from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import psutil
import datetime

app = Flask(__name__)
app.secret_key = 'zlt_x28_super_secret_key'

# لیست کامل بسته‌های اولیه همراه با پشتیبانی از تخفیف
packages = [
    # یکروزه
    {"id": 1, "category": "یکروزه", "name": "یکروزه ۱ گیگابایت", "price": 15000, "discount": 0},
    {"id": 2, "category": "یکروزه", "name": "یکروزه ۲ گیگابایت", "price": 20000, "discount": 0},
    {"id": 3, "category": "یکروزه", "name": "یکروزه ۳ گیگابایت", "price": 30000, "discount": 0},
    {"id": 4, "category": "یکروزه", "name": "یکروزه ۵ گیگابایت", "price": 45000, "discount": 10},
    {"id": 5, "category": "یکروزه", "name": "یکروزه ۱۰ گیگابایت", "price": 85000, "discount": 10},
    {"id": 6, "category": "یکروزه", "name": "نامحدود یکروزه [۲ تا ۹ صبح]", "price": 50000, "discount": 0},
    
    # هفتگی
    {"id": 7, "category": "هفتگی", "name": "هفتگی ۳ گیگابایت", "price": 30000, "discount": 0},
    {"id": 8, "category": "هفتگی", "name": "هفتگی ۵ گیگابایت", "price": 50000, "discount": 0},
    {"id": 9, "category": "هفتگی", "name": "هفتگی ۷ گیگابایت", "price": 70000, "discount": 0},
    {"id": 10, "category": "هفتگی", "name": "هفتگی ۹ گیگابایت", "price": 90000, "discount": 0},
    {"id": 11, "category": "هفتگی", "name": "هفتگی ۱۲ گیگابایت", "price": 140000, "discount": 0},
    
    # ماهانه
    {"id": 12, "category": "ماهانه", "name": "ماهانه ۳ گیگابایت", "price": 30000, "discount": 0},
    {"id": 13, "category": "ماهانه", "name": "ماهانه ۵ گیگابایت", "price": 65000, "discount": 0},
    {"id": 14, "category": "ماهانه", "name": "ماهانه ۱۰ گیگابایت", "price": 130000, "discount": 0},
    {"id": 15, "category": "ماهانه", "name": "ماهانه ۵۰ گیگابایت", "price": 600000, "discount": 0},
    {"id": 16, "category": "ماهانه", "name": "ماهانه ۱۰۰ گیگابایت", "price": 1100000, "discount": 16},
    {"id": 17, "category": "ماهانه", "name": "نامحدود ۲ تا ۹ صبح یکماهه", "price": 120000, "discount": 0},
]

orders = []
announcement = {"text": "", "expires_at": None}

@app.route('/')
def index():
    return render_template('index.html')

# API دریافت بسته‌ها برای صفحه اصلی
@app.route('/api/packages', methods=['GET'])
def get_packages():
    return jsonify(packages)

# API اضافه کردن بسته جدید
@app.route('/api/packages/add', methods=['POST'])
def add_package():
    data = request.json
    new_id = max([p['id'] for p in packages], default=0) + 1
    new_pkg = {
        "id": new_id,
        "category": data.get('category', 'سایر'),
        "name": data.get('name'),
        "price": int(data.get('price', 0)),
        "discount": int(data.get('discount', 0))
    }
    packages.append(new_pkg)
    return jsonify({"success": True})

# API ویرایش بسته
@app.route('/api/packages/edit', methods=['POST'])
def edit_package():
    data = request.json
    pkg_id = int(data.get('id'))
    for p in packages:
        if p['id'] == pkg_id:
            p['name'] = data.get('name', p['name'])
            p['category'] = data.get('category', p['category'])
            p['price'] = int(data.get('price', p['price']))
            p['discount'] = int(data.get('discount', p['discount']))
            return jsonify({"success": True})
    return jsonify({"success": False, "message": "بسته یافت نشد"})

# API حذف بسته
@app.route('/api/packages/delete', methods=['POST'])
def delete_package():
    data = request.json
    pkg_id = int(data.get('id'))
    global packages
    packages = [p for p in packages if p['id'] != pkg_id]
    return jsonify({"success": True})

# API ثبت سفارش
@app.route('/api/order', methods=['POST'])
def create_order():
    data = request.json
    order = {
        "id": len(orders) + 1,
        "username": data.get('username'),
        "phone": data.get('phone'),
        "package": data.get('package'),
        "price": data.get('price'),
        "status": "pending"
    }
    orders.append(order)
    return jsonify({"success": True})

@app.route('/api/orders', methods=['GET'])
def get_orders():
    return jsonify(orders)

@app.route('/api/order/status', methods=['POST'])
def update_order_status():
    data = request.json
    for o in orders:
        if o['id'] == data['id']:
            o['status'] = data['status']
            break
    return jsonify({"success": True})

@app.route('/api/stats')
def get_stats():
    return jsonify({
        'cpu': psutil.cpu_percent(),
        'ram': psutil.virtual_memory().percent
    })

@app.route('/api/announcement', methods=['GET', 'POST'])
def handle_announcement():
    global announcement
    if request.method == 'POST':
        data = request.json
        text = data.get('text')
        hours = float(data.get('hours', 0))
        expires = datetime.datetime.now() + datetime.timedelta(hours=hours)
        announcement = {"text": text, "expires_at": expires}
        return jsonify({"success": True})
    
    is_active = announcement['expires_at'] and datetime.datetime.now() < announcement['expires_at']
    return jsonify({
        "active": is_active,
        "text": announcement['text'] if is_active else ""
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
