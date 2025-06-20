import sqlite3
import smtplib
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def load_config():
    if os.path.exists('config.json'):
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def send_email(to_email, subject, body):
    config = load_config()
    
    if not config.get('email_notifications', False):
        print(f"Email notification disabled: {subject}")
        return True
    
    try:
        smtp_host = config.get('smtp_host', '')
        smtp_port = config.get('smtp_port', 587)
        smtp_username = config.get('smtp_username', '')
        smtp_password = config.get('smtp_password', '')
        
        if not all([smtp_host, smtp_username, smtp_password, to_email]):
            print("Email configuration incomplete")
            return False
        
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        text = msg.as_string()
        server.sendmail(smtp_username, to_email, text)
        server.quit()
        
        print(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False

def init_database():
    conn = sqlite3.connect('coworking.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_approved BOOLEAN DEFAULT 0,
            is_admin BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date DATE NOT NULL,
            start_time TIME NOT NULL,
            end_time TIME NOT NULL,
            purpose TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        SELECT COUNT(*) FROM users WHERE is_admin = 1
    ''')
    admin_count = cursor.fetchone()[0]
    
    if admin_count == 0:
        import hashlib
        admin_password = 'admin123'
        admin_password_hash = hashlib.sha256(admin_password.encode()).hexdigest()
        
        cursor.execute('''
            INSERT INTO users (name, email, password_hash, is_approved, is_admin)
            VALUES (?, ?, ?, ?, ?)
        ''', ('Administrator', 'admin@example.com', admin_password_hash, True, True))
        
        print("Default admin user created:")
        print("Email: admin@example.com")
        print("Password: admin123")
        print("Please change the password after first login!")
    
    conn.commit()
    conn.close()
    print("Database initialized successfully")

def validate_reservation_time(date, start_time, end_time):
    config = load_config()
    rules = config.get('reservation_rules', {})
    
    operating_hours = rules.get('operating_hours', {'start': '09:00', 'end': '18:00'})
    
    if start_time < operating_hours['start'] or end_time > operating_hours['end']:
        return False, "営業時間外です"
    
    start_dt = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
    end_dt = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M")
    
    duration_hours = (end_dt - start_dt).total_seconds() / 3600
    
    min_hours = rules.get('min_booking_hours', 1)
    max_hours = rules.get('max_hours_per_day', 8)
    
    if duration_hours < min_hours:
        return False, f"最低{min_hours}時間以上の予約が必要です"
    
    if duration_hours > max_hours:
        return False, f"1日の最大予約時間は{max_hours}時間です"
    
    return True, "OK"

def get_available_slots(date):
    config = load_config()
    rules = config.get('reservation_rules', {})
    operating_hours = rules.get('operating_hours', {'start': '09:00', 'end': '18:00'})
    
    conn = sqlite3.connect('coworking.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT start_time, end_time FROM reservations 
        WHERE date = ? 
        ORDER BY start_time
    ''', (date,))
    
    reserved_slots = cursor.fetchall()
    conn.close()
    
    available_slots = []
    current_time = operating_hours['start']
    
    for start, end in reserved_slots:
        if current_time < start:
            available_slots.append((current_time, start))
        current_time = max(current_time, end)
    
    if current_time < operating_hours['end']:
        available_slots.append((current_time, operating_hours['end']))
    
    return available_slots