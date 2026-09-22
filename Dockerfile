FROM python:3.10-slim

WORKDIR /app

# کپی فایل وابستگی‌ها و نصب آن‌ها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# کپی تمامی کدهای پروژه
COPY . .

# باز کردن پورت 8080
EXPOSE 8080

# اجرا به وسیله Gunicorn روی پورت 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
