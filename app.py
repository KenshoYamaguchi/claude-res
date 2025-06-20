from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import sqlite3
import json
import os
from datetime import datetime, timedelta
from functools import wraps
import hashlib
from utils import send_email, init_database

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

CONFIG_FILE = 'config.json'

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

config = load_config()

def get_db_connection():
    conn = sqlite3.connect('coworking.db')
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        conn = get_db_connection()
        user = conn.execute('SELECT is_admin FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        conn.close()
        
        if not user or not user['is_admin']:
            flash('管理者権限が必要です。')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = get_db_connection()
        try:
            conn.execute(
                'INSERT INTO users (name, email, password_hash, is_approved) VALUES (?, ?, ?, ?)',
                (name, email, password_hash, False)
            )
            conn.commit()
            flash('会員登録申請を受け付けました。承認までお待ちください。')
            
            if config.get('email_notifications', True):
                send_email(
                    config.get('admin_email', ''),
                    '新規会員登録申請',
                    f'新しい会員登録申請があります。\n\n名前: {name}\nメール: {email}'
                )
                
        except sqlite3.IntegrityError:
            flash('このメールアドレスは既に登録されています。')
        finally:
            conn.close()
            
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE email = ? AND password_hash = ?',
            (email, password_hash)
        ).fetchone()
        conn.close()
        
        if user:
            if user['is_approved']:
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                session['is_admin'] = user['is_admin']
                return redirect(url_for('dashboard'))
            else:
                flash('アカウントが承認されていません。')
        else:
            flash('メールアドレスまたはパスワードが正しくありません。')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/reservations')
@login_required
def get_reservations():
    conn = get_db_connection()
    reservations = conn.execute('''
        SELECT r.*, u.name as user_name 
        FROM reservations r 
        JOIN users u ON r.user_id = u.id
        WHERE r.date >= date('now')
        ORDER BY r.date, r.start_time
    ''').fetchall()
    conn.close()
    
    events = []
    for reservation in reservations:
        events.append({
            'id': reservation['id'],
            'title': f"{reservation['user_name']} - {reservation['purpose']}",
            'start': f"{reservation['date']}T{reservation['start_time']}",
            'end': f"{reservation['date']}T{reservation['end_time']}",
            'color': '#007bff' if reservation['user_id'] == session['user_id'] else '#6c757d'
        })
    
    return jsonify(events)

@app.route('/api/reserve', methods=['POST'])
@login_required
def make_reservation():
    data = request.json
    date = data['date']
    start_time = data['start_time']
    end_time = data['end_time']
    purpose = data['purpose']
    
    conn = get_db_connection()
    
    existing = conn.execute('''
        SELECT * FROM reservations 
        WHERE date = ? AND (
            (start_time <= ? AND end_time > ?) OR
            (start_time < ? AND end_time >= ?) OR
            (start_time >= ? AND start_time < ?)
        )
    ''', (date, start_time, start_time, end_time, end_time, start_time, end_time)).fetchone()
    
    if existing:
        conn.close()
        return jsonify({'success': False, 'message': '選択した時間帯は既に予約されています。'})
    
    try:
        conn.execute('''
            INSERT INTO reservations (user_id, date, start_time, end_time, purpose)
            VALUES (?, ?, ?, ?, ?)
        ''', (session['user_id'], date, start_time, end_time, purpose))
        conn.commit()
        
        if config.get('email_notifications', True):
            send_email(
                config.get('admin_email', ''),
                '新しい予約',
                f'新しい予約が作成されました。\n\n日時: {date} {start_time}-{end_time}\n利用者: {session["user_name"]}\n目的: {purpose}'
            )
        
        return jsonify({'success': True, 'message': '予約が完了しました。'})
    except Exception as e:
        return jsonify({'success': False, 'message': '予約の作成に失敗しました。'})
    finally:
        conn.close()

@app.route('/admin')
@admin_required
def admin():
    conn = get_db_connection()
    pending_users = conn.execute(
        'SELECT * FROM users WHERE is_approved = 0 ORDER BY created_at DESC'
    ).fetchall()
    conn.close()
    
    return render_template('admin.html', pending_users=pending_users)

@app.route('/admin/approve_user/<int:user_id>')
@admin_required
def approve_user(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    
    if user:
        conn.execute('UPDATE users SET is_approved = 1 WHERE id = ?', (user_id,))
        conn.commit()
        
        if config.get('email_notifications', True):
            send_email(
                user['email'],
                'アカウント承認のお知らせ',
                f'{user["name"]}様\n\nアカウントが承認されました。ログインして予約をご利用ください。'
            )
        
        flash(f'{user["name"]}さんのアカウントを承認しました。')
    
    conn.close()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    init_database()
    app.run(debug=True, host='0.0.0.0', port=5000)