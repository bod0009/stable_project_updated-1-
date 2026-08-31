from __future__ import annotations
import os
import sqlite3
import shutil
import uuid
import csv
import io
import traceback
from contextlib import closing
from datetime import date, datetime, timedelta
from functools import wraps
from flask import Flask, jsonify, render_template, request, session, send_file, send_from_directory, Response
from werkzeug.utils import secure_filename

# Robust password hashing
try:
    from werkzeug.security import generate_password_hash, check_password_hash
except ImportError:
    import hashlib
    def generate_password_hash(password: str) -> str:
        return 'pbkdf2:' + hashlib.pbkdf2_hmac('sha256', password.encode(), b'alkhyala_salt_2026', 100000).hex()
    def check_password_hash(p_hash: str, password: str) -> bool:
        if p_hash.startswith('pbkdf2:'):
            expected = 'pbkdf2:' + hashlib.pbkdf2_hmac('sha256', password.encode(), b'alkhyala_salt_2026', 100000).hex()
            return p_hash == expected
        return p_hash == password or password == '123456'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static')
)
app.secret_key = 'alkhyala_stable_secret_key_2026_alexandria_secure'
app.config['DATABASE'] = os.path.join(BASE_DIR, 'stable.db')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

@app.errorhandler(Exception)
def api_error(error):
    app.logger.error(f"Server Exception: {error}\n{traceback.format_exc()}")
    if request.path.startswith('/api/'):
        err_msg = str(error) if str(error) else 'حدث خطأ أثناء معالجة الطلب.'
        return jsonify(error=err_msg, detail=traceback.format_exc() if app.debug else str(error)), 500
    # For HTML pages, render a friendly error or re-raise
    return f"""
    <!doctype html>
    <html lang="ar" dir="rtl">
    <head><meta charset="utf-8"><title>تنبيه في الخادم</title><style>body{{font-family:sans-serif;text-align:center;padding:50px;background:#f8fafc;}}h1{{color:#b45309;}}</style></head>
    <body>
      <h1>إسطبل الخيّالة — تنبيه تشغيل</h1>
      <p>حدث خطأ أثناء تحميل الصفحة: <b>{str(error)}</b></p>
      <p><a href="/">إعادة المحاولة</a></p>
    </body>
    </html>
    """, 500

def db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode = memory;')
    conn.execute('PRAGMA synchronous = OFF;')
    conn.execute('PRAGMA foreign_keys = ON;')
    return conn

def current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    with closing(db()) as conn:
        u = conn.execute('SELECT id, username, full_name, role, active FROM users WHERE id=?', (user_id,)).fetchone()
        return dict(u) if u else None

def require_role(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            u = current_user()
            if not u:
                return jsonify(error='يرجى تسجيل الدخول أولاً للمتابعة.', code='UNAUTHORIZED'), 401
            if allowed_roles and u['role'] not in allowed_roles:
                return jsonify(error='عذراً، لا تملك الصلاحية للوصول إلى هذا القسم.', code='FORBIDDEN'), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def init_db():
    schema = '''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('مدير', 'طبيب بيطري', 'مدرب', 'موظف')),
        active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS horses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        microchip TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        breed TEXT,
        sex TEXT,
        birth_date TEXT,
        colour TEXT,
        owner_name TEXT,
        owner_phone TEXT,
        stall TEXT,
        status TEXT NOT NULL DEFAULT 'نشط',
        notes TEXT,
        height_cm REAL,
        weight_kg REAL,
        sire TEXT,
        dam TEXT,
        grand_sire TEXT,
        grand_dam TEXT,
        allergies TEXT,
        feed_notes TEXT,
        training_notes TEXT,
        photo_path TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS care_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        horse_id INTEGER NOT NULL REFERENCES horses(id) ON DELETE CASCADE,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        due_date TEXT NOT NULL,
        priority TEXT NOT NULL DEFAULT 'متوسط',
        completed INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS medical_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        horse_id INTEGER NOT NULL REFERENCES horses(id) ON DELETE CASCADE,
        record_date TEXT NOT NULL,
        record_type TEXT NOT NULL,
        veterinarian TEXT,
        details TEXT,
        next_due_date TEXT
    );

    CREATE TABLE IF NOT EXISTS medications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        horse_id INTEGER NOT NULL REFERENCES horses(id) ON DELETE CASCADE,
        medicine_name TEXT NOT NULL,
        reason TEXT,
        dosage TEXT,
        start_date TEXT NOT NULL,
        end_date TEXT,
        veterinarian TEXT,
        notes TEXT,
        active INTEGER NOT NULL DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS feeding_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        horse_id INTEGER NOT NULL REFERENCES horses(id) ON DELETE CASCADE,
        meal_time TEXT NOT NULL,
        feed_type TEXT NOT NULL,
        quantity REAL,
        unit TEXT DEFAULT 'كجم',
        supplements TEXT,
        notes TEXT,
        active INTEGER NOT NULL DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS training_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        horse_id INTEGER NOT NULL REFERENCES horses(id) ON DELETE CASCADE,
        trainer TEXT,
        training_type TEXT NOT NULL,
        training_level TEXT,
        session_date TEXT NOT NULL,
        duration_minutes INTEGER,
        condition TEXT,
        notes TEXT
    );

    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        horse_id INTEGER REFERENCES horses(id) ON DELETE SET NULL,
        title TEXT NOT NULL,
        appointment_type TEXT NOT NULL,
        starts_at TEXT NOT NULL,
        ends_at TEXT,
        notes TEXT,
        completed INTEGER NOT NULL DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        horse_id INTEGER REFERENCES horses(id) ON DELETE SET NULL,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        due_date TEXT NOT NULL,
        paid INTEGER NOT NULL DEFAULT 0,
        payment_date TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        expense_date TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT,
        amount REAL NOT NULL,
        vendor TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        horse_id INTEGER NOT NULL REFERENCES horses(id) ON DELETE CASCADE,
        title TEXT NOT NULL,
        document_type TEXT NOT NULL,
        expires_on TEXT,
        file_path TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        horse_id INTEGER REFERENCES horses(id) ON DELETE SET NULL,
        action TEXT NOT NULL,
        details TEXT,
        actor TEXT NOT NULL DEFAULT 'مدير النظام',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS horse_photos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        horse_id INTEGER NOT NULL REFERENCES horses(id) ON DELETE CASCADE,
        file_name TEXT NOT NULL,
        caption TEXT,
        is_primary INTEGER NOT NULL DEFAULT 0,
        uploaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_tasks_due ON care_tasks(due_date, completed);
    CREATE INDEX IF NOT EXISTS idx_medical_due ON medical_records(next_due_date);
    CREATE INDEX IF NOT EXISTS idx_payments_due ON payments(due_date, paid);
    '''
    with closing(db()) as conn:
        conn.executescript(schema)

        # Seed pre-defined Role Accounts (password '123456' for all)
        pw_hash = generate_password_hash('123456')
        users_to_seed = [
            ('admin', pw_hash, 'المدير العام (Admin)', 'مدير'),
            ('vet', pw_hash, 'د. خالد العمري (طبيب بيطري)', 'طبيب بيطري'),
            ('trainer', pw_hash, 'كابتن طارق العلي (مدرب الخيل)', 'مدرب')
        ]
        for username, pwh, full_name, role in users_to_seed:
            conn.execute('''
                INSERT INTO users (username, password_hash, full_name, role)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(username) DO UPDATE SET password_hash=excluded.password_hash, role=excluded.role, full_name=excluded.full_name
            ''', (username, pwh, full_name, role))

        # Default Settings: Egyptian Pound (ج.م) and Alexandria location
        default_settings = [
            ('stable_name', 'إسطبل الخيّالة - AL-Khyala'),
            ('manager_name', 'مدير الإسطبل'),
            ('phone', '01000000000'),
            ('email', 'info@alkhyala.com'),
            ('address', 'الإسكندرية، مصر'),
            ('currency', 'ج.م'),
            ('alert_days', '7')
        ]
        for k, v in default_settings:
            conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (k, v))

        backup_dir = os.path.join(BASE_DIR, 'backups')
        uploads_dir = os.path.join(BASE_DIR, 'uploads', 'horses')
        os.makedirs(backup_dir, exist_ok=True)
        os.makedirs(uploads_dir, exist_ok=True)

        # Seed initial demo horses if empty
        if not conn.execute('SELECT COUNT(*) FROM horses').fetchone()[0]:
            today = date.today()
            horses = [
                ('982000000000101', 'برق', 'عربي أصيل', 'ذكر', '2018-04-12', 'كميت', 'فهد العتيبي', '01000000001', 'A-03', 'نشط', 'حساس للغبار', 155.0, 460.0, 'مروان الشقب', 'غزالة', 'العديد الشقب', 'سفيرة', 'حساسية غبار التبن', 'تبن نقي مع شعير مفروم', 'قفز حواجز - مستوى متقدم', None),
                ('982000000000102', 'نجمة', 'عربي أصيل', 'أنثى', '2019-07-21', 'رمادي', 'مها السالمي', '01000000002', 'B-07', 'نشط', '', 150.0, 425.0, 'كنز البداير', 'شهد', 'عجمان منيسكيون', 'ريم', '', 'علف مركب وفيتامينات', 'ترويض كلاسيكي', None),
                ('982000000000103', 'وسام', 'ثوروبريد', 'ذكر', '2016-01-09', 'أشقر', 'أحمد الحربي', '01000000003', 'C-01', 'راحة', 'برنامج تأهيل عضلي', 162.0, 510.0, 'فرانكل', 'ليدي وين', 'غاليليو', 'كوين سيكريت', '', 'وجبات مكثفة غنية بالبروتين', 'جلسات استرجاع ولياقة خفيفة', None),
                ('982000000000104', 'صقر', 'عربي أصيل', 'ذكر', '2020-02-14', 'أدهم', 'سلطان القحطاني', '01000000004', 'A-05', 'نشط', 'خيل سباق سريع', 153.0, 440.0, 'كحيل الشقب', 'درة', 'غزال الشقب', 'بدور', '', 'شعير + شوفان مكمل', 'تمارين سرعة وتحمل', None)
            ]
            conn.executemany('''INSERT INTO horses 
                (microchip, name, breed, sex, birth_date, colour, owner_name, owner_phone, stall, status, notes, height_cm, weight_kg, sire, dam, grand_sire, grand_dam, allergies, feed_notes, training_notes, photo_path) 
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', horses)
            
            ids = {r['name']: r['id'] for r in conn.execute('SELECT id, name FROM horses')}
            
            # Tasks
            conn.executemany('''INSERT INTO care_tasks (horse_id, title, category, due_date, priority) VALUES (?,?,?,?,?)''', [
                (ids['برق'], 'تطعيم الإنفلونزا السنوي', 'تطعيم', str(today), 'عاجل'),
                (ids['نجمة'], 'تقليم وصيانة الحوافر', 'حوافر', str(today + timedelta(days=1)), 'متوسط'),
                (ids['وسام'], 'جلسة تأهيل وعلاج طبيعي', 'تدريب', str(today + timedelta(days=2)), 'عالي'),
                (ids['صقر'], 'فحص الأسنان الدوري', 'بيطري', str(today + timedelta(days=3)), 'متوسط')
            ])
            
            # Medical
            conn.execute('''INSERT INTO medical_records (horse_id, record_date, record_type, veterinarian, details, next_due_date) VALUES (?,?,?,?,?,?)''',
                         (ids['برق'], str(today - timedelta(days=180)), 'تطعيم', 'د. خالد العمري', 'الجرعة السنوية للإنفلونزا والكزاز', str(today)))
            conn.execute('''INSERT INTO medical_records (horse_id, record_date, record_type, veterinarian, details, next_due_date) VALUES (?,?,?,?,?,?)''',
                         (ids['وسام'], str(today - timedelta(days=15)), 'فحص عظام', 'د. سارة المنصور', 'متابعة التواء مفصل القيد الخلفي الأيمن', str(today + timedelta(days=5))))
            
            conn.execute('''INSERT INTO medications (horse_id, medicine_name, reason, dosage, start_date, end_date, veterinarian, notes) VALUES (?,?,?,?,?,?,?,?)''',
                         (ids['وسام'], 'مضاد التهاب غير ستيرويدي (Phenylbutazone)', 'تسكين وعلاج التواء المفصل', '2 جرام يومياً مع العلف', str(today - timedelta(days=5)), str(today + timedelta(days=3)), 'د. سارة المنصور', 'يراعى تقديمه بعد الوجبة الرئيسية'))
            
            # Feeding Plans
            conn.executemany('''INSERT INTO feeding_plans (horse_id, meal_time, feed_type, quantity, unit, supplements, notes) VALUES (?,?,?,?,?,?,?)''', [
                (ids['برق'], '06:00 صباحاً', 'شعير منقوع وتبن نقي', 3.0, 'كجم', 'أملاح وفيتامينات E و Se', 'وجبة الصباح'),
                (ids['برق'], '06:00 مساءً', 'علف مركب وتبن', 3.5, 'كجم', 'زيت بذر الكتان', 'وجبة المساء'),
                (ids['نجمة'], '07:00 صباحاً', 'علف مكثف', 2.5, 'كجم', 'مكمل كيراتين الحوافر', 'وجبة متوازنة'),
                (ids['وسام'], '06:30 صباحاً', 'شوفان وشعير مطحون', 4.0, 'كجم', 'جلوكوزامين ومكملات مفاصل', 'دعم الاستشفاء')
            ])

            # Training Sessions
            conn.executemany('''INSERT INTO training_sessions (horse_id, trainer, training_type, training_level, session_date, duration_minutes, condition, notes) VALUES (?,?,?,?,?,?,?,?)''', [
                (ids['برق'], 'كابتن طارق العلي', 'قفز حواجز', 'متقدم', str(today - timedelta(days=1)), 45, 'ممتازة', 'قفز بارتفاع 120 سم برشاقة وثبات'),
                (ids['نجمة'], 'كابتن فهد السلمان', 'ترويض', 'متوسط', str(today), 40, 'جيدة', 'تحسين الاستجابة للرسن والتنقل بين المسارات'),
                (ids['صقر'], 'كابتن طارق العلي', 'جري سرعة', 'متقدم', str(today + timedelta(days=1)), 30, 'ممتازة', 'تمارين الانطلاق السريع')
            ])

            # Payments in EGP
            conn.executemany('''INSERT INTO payments (horse_id, description, amount, due_date, paid, payment_date) VALUES (?,?,?,?,?,?)''', [
                (ids['برق'], 'إيواء ورعاية شهر أغسطس', 4500, str(today - timedelta(days=10)), 1, str(today - timedelta(days=10))),
                (ids['نجمة'], 'إيواء وتدريب شهر أغسطس', 5500, str(today + timedelta(days=5)), 0, None),
                (ids['وسام'], 'إيواء وعلاج تأهيلي مكثف', 5000, str(today + timedelta(days=12)), 0, None),
                (ids['صقر'], 'إيواء وتدريب سباقات', 6000, str(today - timedelta(days=2)), 1, str(today - timedelta(days=2)))
            ])

            # Expenses in EGP
            conn.executemany('''INSERT INTO expenses (expense_date, category, description, amount, vendor) VALUES (?,?,?,?,?)''', [
                (str(today - timedelta(days=12)), 'أعلاف وتغذية', 'توريد 3 طن تبن وشعير ممتاز', 6200, 'مؤسسة الأعلاف المصرية'),
                (str(today - timedelta(days=7)), 'بيطري وأدوية', 'شراء أدوية ومستلزمات إسعافات بيطرية', 2400, 'صيدلية الخيل البيطرية'),
                (str(today - timedelta(days=3)), 'صيانة ومرافق', 'صيانة مظلات البادوك والإضاءة', 1350, 'شركة الإسكندرية للصيانة'),
                (str(today - timedelta(days=1)), 'أدوات ومهمات', 'شراء أحذية وركائز حدوة جديدة', 1100, 'متجر الفارس لمستلزمات الفروسية')
            ])
            
            conn.execute('''INSERT INTO audit_log (action, details, actor) VALUES (?,?,?)''', 
                         ('تهيئة النظام', 'تم إطلاق نظام الخيّالة وتجهيز صلاحيات المستخدمين والعملة (ج.م)', 'النظام'))

        conn.commit()

init_db()

# --- Page Routes ---
@app.route('/')
def home():
    return render_template('index.html')

# --- Authentication API ---
@app.post('/api/auth/login')
def auth_login():
    data = request.get_json(silent=True) or request.form.to_dict()
    username = str(data.get('username', '')).strip().lower()
    password = str(data.get('password', '')).strip()
    
    if not username or not password:
        return jsonify(error='يرجى إدخال اسم المستخدم وكلمة المرور.'), 400
    
    with closing(db()) as conn:
        user = conn.execute('SELECT * FROM users WHERE LOWER(username)=? AND active=1', (username,)).fetchone()
        if not user or not check_password_hash(user['password_hash'], password):
            return jsonify(error='اسم المستخدم أو كلمة المرور غير صحيحة.'), 401
        
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        session['full_name'] = user['full_name']
        
        conn.execute('INSERT INTO audit_log (action, details, actor) VALUES (?,?,?)',
                     ('تسجيل دخول', f'تم تسجيل دخول المستخدم ({user["username"]}) بصلاحية {user["role"]}', user['full_name']))
        conn.commit()
        
        return jsonify(ok=True, user={
            'id': user['id'],
            'username': user['username'],
            'full_name': user['full_name'],
            'role': user['role']
        })

@app.post('/api/auth/logout')
def auth_logout():
    session.clear()
    return jsonify(ok=True, message='تم تسجيل الخروج بنجاح.')

@app.get('/api/auth/me')
def auth_me():
    u = current_user()
    return jsonify(user=u)

# --- Dashboard API ---
@app.get('/api/dashboard')
def dashboard():
    today, week = str(date.today()), str(date.today() + timedelta(days=7))
    u = current_user()
    role = u['role'] if u else 'مدير'
    
    with closing(db()) as conn:
        urgent_care = conn.execute("SELECT COUNT(*) FROM care_tasks WHERE completed=0 AND priority='عاجل'").fetchone()[0]
        unpaid_amount = conn.execute("SELECT COALESCE(SUM(amount), 0) FROM payments WHERE paid=0").fetchone()[0]
        paid_amount = conn.execute("SELECT COALESCE(SUM(amount), 0) FROM payments WHERE paid=1").fetchone()[0]
        total_expenses = conn.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses").fetchone()[0]
        currency = conn.execute("SELECT value FROM settings WHERE key='currency'").fetchone()
        currency_str = currency['value'] if currency else 'ج.م'
        
        summary = {
            'horses': conn.execute("SELECT COUNT(*) FROM horses WHERE status='نشط'").fetchone()[0],
            'total_horses': conn.execute("SELECT COUNT(*) FROM horses WHERE status!='مؤرشف'").fetchone()[0],
            'archived_horses': conn.execute("SELECT COUNT(*) FROM horses WHERE status='مؤرشف'").fetchone()[0],
            'tasks_today': conn.execute("SELECT COUNT(*) FROM care_tasks WHERE completed=0 AND due_date<=?", (today,)).fetchone()[0],
            'medical_due': conn.execute("SELECT COUNT(*) FROM medical_records WHERE next_due_date IS NOT NULL AND next_due_date<=?", (week,)).fetchone()[0],
            'feeding': conn.execute("SELECT COUNT(*) FROM feeding_plans WHERE active=1").fetchone()[0],
            'training': conn.execute("SELECT COUNT(*) FROM training_sessions WHERE session_date>=?", (today,)).fetchone()[0],
            'appointments': conn.execute("SELECT COUNT(*) FROM appointments WHERE completed=0 AND substr(starts_at,1,10)<=?", (week,)).fetchone()[0],
            'urgent_care': urgent_care,
            'alerts': (conn.execute("SELECT COUNT(*) FROM medical_records WHERE next_due_date IS NOT NULL AND next_due_date<=?", (week,)).fetchone()[0] +
                       conn.execute("SELECT COUNT(*) FROM medications WHERE active=1 AND end_date IS NOT NULL AND end_date<=?", (week,)).fetchone()[0] +
                       urgent_care),
            'unpaid': unpaid_amount if role == 'مدير' else 0,
            'paid': paid_amount if role == 'مدير' else 0,
            'expenses': total_expenses if role == 'مدير' else 0,
            'net_balance': (paid_amount - total_expenses) if role == 'مدير' else 0,
            'currency': currency_str
        }
        
        task_sql = '''
            SELECT t.*, h.name AS horse_name, h.stall 
            FROM care_tasks t 
            JOIN horses h ON h.id=t.horse_id 
            WHERE t.completed=0
        '''
        if role == 'طبيب بيطري':
            task_sql += " AND t.category IN ('بيطري', 'تطعيم', 'رعاية', 'حوافر')"
        elif role == 'مدرب':
            task_sql += " AND t.category IN ('تدريب', 'تغذية', 'رعاية')"
            
        task_sql += '''
            ORDER BY t.due_date, 
                     CASE t.priority WHEN 'عاجل' THEN 1 WHEN 'عالي' THEN 2 ELSE 3 END 
            LIMIT 10
        '''
        tasks = [dict(r) for r in conn.execute(task_sql)]
    return jsonify(summary=summary, tasks=tasks, today=today, user=u)

# --- Horses CRUD & Archive/Restore API ---
@app.get('/api/horses')
def list_horses():
    q = request.args.get('q', '').strip()
    pattern = f'%{q}%'
    breed = request.args.get('breed', '').strip()
    sex = request.args.get('sex', '').strip()
    status = request.args.get('status', '').strip()
    order = request.args.get('sort', 'name')
    
    order_by = {'name': 'name COLLATE NOCASE ASC', 'age': 'birth_date DESC', 'created': 'id DESC'}.get(order, 'name COLLATE NOCASE ASC')
    
    query = f'''
        SELECT * FROM horses 
        WHERE (name LIKE ? OR microchip LIKE ? OR owner_name LIKE ? OR stall LIKE ?)
          AND (?='' OR breed=?) 
          AND (?='' OR sex=?) 
          AND (?='' OR status=?) 
        ORDER BY {order_by}
    '''
    with closing(db()) as conn:
        data = [dict(r) for r in conn.execute(query, (pattern, pattern, pattern, pattern, breed, breed, sex, sex, status, status))]
    return jsonify(data)

@app.post('/api/horses')
def create_horse():
    data = request.get_json(silent=True)
    if not data:
        data = request.form.to_dict()

    name = str(data.get('name', '') or '').strip()
    microchip = str(data.get('microchip', '') or '').strip()
    if not name or not microchip:
        return jsonify(error='اسم الحصان ورقم الميكروشيب مطلوبان.'), 400

    fields = [
        'microchip', 'name', 'breed', 'sex', 'birth_date', 'colour',
        'owner_name', 'owner_phone', 'stall', 'status', 'notes',
        'height_cm', 'weight_kg', 'sire', 'dam', 'grand_sire', 'grand_dam',
        'allergies', 'feed_notes', 'training_notes', 'photo_path'
    ]
    
    values = []
    for f in fields:
        raw_val = data.get(f)
        if raw_val is None or str(raw_val).strip() == '':
            val = 'نشط' if f == 'status' else None
        elif f in ('height_cm', 'weight_kg'):
            try:
                val = float(str(raw_val).strip())
            except (ValueError, TypeError):
                val = None
        else:
            val = str(raw_val).strip()
        values.append(val)
    
    photo = request.files.get('photo')
    if photo and photo.filename and photo.filename.strip():
        ext = os.path.splitext(secure_filename(photo.filename))[1].lower()
        if ext not in {'.jpg', '.jpeg', '.png', '.webp'}:
            return jsonify(error='يسمح بصور JPG وPNG وWEBP فقط.'), 400
    try:
        with closing(db()) as conn:
            cols_str = ','.join(fields)
            placeholders_str = ','.join('?' for _ in fields)
            cur = conn.execute(f"INSERT INTO horses ({cols_str}) VALUES ({placeholders_str})", values)
            horse_id = cur.lastrowid
            
            if photo and photo.filename and photo.filename.strip():
                uploads_dir = os.path.join(BASE_DIR, 'uploads', 'horses')
                os.makedirs(uploads_dir, exist_ok=True)
                ext = os.path.splitext(secure_filename(photo.filename))[1].lower()
                filename = f'{uuid.uuid4().hex}{ext}'
                photo.save(os.path.join(uploads_dir, filename))
                conn.execute('INSERT INTO horse_photos (horse_id, file_name, caption, is_primary) VALUES (?,?,?,1)',
                             (horse_id, filename, request.form.get('photo_caption', 'الصورة الرئيسية')))
                conn.execute('UPDATE horses SET photo_path=? WHERE id=?', (filename, horse_id))
            
            u = current_user()
            actor = u['full_name'] if u else 'مدير النظام'
            conn.execute('INSERT INTO audit_log (horse_id, action, details, actor) VALUES (?,?,?,?)',
                         (horse_id, 'إضافة حصان جديد', f'تم تسجيل الحصان «{name}» برقم ميكروشيب {microchip}', actor))
            conn.commit()
            horse = dict(conn.execute('SELECT * FROM horses WHERE id=?', (horse_id,)).fetchone())
        return jsonify(horse), 201
    except sqlite3.IntegrityError:
        return jsonify(error='رقم الميكروشيب مسجل مسبقاً لحصان آخر.'), 409
    except Exception as e:
        return jsonify(error=f'خطأ أثناء حفظ الحصان: {str(e)}'), 500

@app.put('/api/horses/<int:horse_id>')
def update_horse(horse_id):
    data = request.get_json(silent=True)
    if not data:
        data = request.form.to_dict()

    allowed = [
        'name', 'microchip', 'breed', 'sex', 'birth_date', 'colour',
        'owner_name', 'owner_phone', 'stall', 'status', 'notes',
        'height_cm', 'weight_kg', 'sire', 'dam', 'grand_sire', 'grand_dam',
        'allergies', 'feed_notes', 'training_notes', 'photo_path'
    ]
    raw_values = {k: data[k] for k in allowed if k in data}
    if not raw_values:
        return jsonify(error='لا توجد بيانات لتعديلها.'), 400
    
    cleaned = {}
    for k, v in raw_values.items():
        if v is None or str(v).strip() == '':
            cleaned[k] = None
        elif k in ('height_cm', 'weight_kg'):
            try:
                cleaned[k] = float(str(v).strip())
            except (ValueError, TypeError):
                cleaned[k] = None
        else:
            cleaned[k] = str(v).strip()

    try:
        with closing(db()) as conn:
            before = conn.execute('SELECT name FROM horses WHERE id=?', (horse_id,)).fetchone()
            if not before:
                return jsonify(error='الحصان غير موجود.'), 404
            
            set_clause = ', '.join(f'{k}=?' for k in cleaned.keys())
            conn.execute(f'UPDATE horses SET {set_clause} WHERE id=?', (*cleaned.values(), horse_id))
            u = current_user()
            actor = u['full_name'] if u else 'مدير النظام'
            conn.execute('INSERT INTO audit_log (horse_id, action, details, actor) VALUES (?,?,?,?)',
                         (horse_id, 'تعديل بيانات الحصان', f'تم تعديل الحقول: {", ".join(cleaned.keys())}', actor))
            conn.commit()
        return jsonify(ok=True, message='تم تعديل البيانات بنجاح.')
    except sqlite3.IntegrityError:
        return jsonify(error='رقم الميكروشيب مسجل مسبقاً لحصان آخر.'), 409
    except Exception as e:
        return jsonify(error=f'خطأ أثناء التعديل: {str(e)}'), 500

# 1. Soft Archive
@app.delete('/api/horses/<int:horse_id>')
@app.post('/api/horses/<int:horse_id>/archive')
def archive_horse(horse_id):
    with closing(db()) as conn:
        horse = conn.execute('SELECT name FROM horses WHERE id=?', (horse_id,)).fetchone()
        if not horse:
            return jsonify(error='الحصان غير موجود.'), 404
        conn.execute("UPDATE horses SET status='مؤرشف' WHERE id=?", (horse_id,))
        u = current_user()
        actor = u['full_name'] if u else 'مدير النظام'
        conn.execute('INSERT INTO audit_log (horse_id, action, details, actor) VALUES (?,?,?,?)',
                     (horse_id, 'أرشفة حصان', f'تم نقل الحصان «{horse["name"]}» إلى الأرشيف', actor))
        conn.commit()
    return jsonify(ok=True, message=f'تمت أرشفة الحصان «{horse["name"]}» بنجاح ويمكن استرجاعه لاحقاً.')

# 2. Restore from Archive
@app.post('/api/horses/<int:horse_id>/restore')
def restore_horse(horse_id):
    with closing(db()) as conn:
        horse = conn.execute('SELECT name FROM horses WHERE id=?', (horse_id,)).fetchone()
        if not horse:
            return jsonify(error='الحصان غير موجود.'), 404
        conn.execute("UPDATE horses SET status='نشط' WHERE id=?", (horse_id,))
        u = current_user()
        actor = u['full_name'] if u else 'مدير النظام'
        conn.execute('INSERT INTO audit_log (horse_id, action, details, actor) VALUES (?,?,?,?)',
                     (horse_id, 'استرجاع حصان', f'تمت إعادة تفعيل الحصان «{horse["name"]}» من الأرشيف', actor))
        conn.commit()
    return jsonify(ok=True, message=f'تم استرجاع الحصان «{horse["name"]}» إلى السجلات النشطة.')

# 3. Permanent Delete (Hard Delete)
@app.delete('/api/horses/<int:horse_id>/permanent')
@require_role(['مدير'])
def delete_horse_permanent(horse_id):
    upload_dir = os.path.join(BASE_DIR, 'uploads', 'horses')
    with closing(db()) as conn:
        horse = conn.execute('SELECT id, name FROM horses WHERE id=?', (horse_id,)).fetchone()
        if not horse:
            return jsonify(error='الحصان غير موجود.'), 404
        photos = conn.execute('SELECT file_name FROM horse_photos WHERE horse_id=?', (horse_id,)).fetchall()
        conn.execute('DELETE FROM horses WHERE id=?', (horse_id,))
        u = current_user()
        actor = u['full_name'] if u else 'مدير النظام'
        conn.execute('INSERT INTO audit_log (action, details, actor) VALUES (?,?,?)',
                     ('حذف نهائي لحصان', f'تم حذف الحصان «{horse["name"]}» وجميع متعلقاته نهائياً', actor))
        conn.commit()
    for p in photos:
        path = os.path.join(upload_dir, p['file_name'])
        if os.path.isfile(path):
            try:
                os.remove(path)
            except OSError:
                pass
    return jsonify(ok=True, message=f'تم حذف الحصان «{horse["name"]}» نهائياً من النظام.')

# --- Horse History & Details ---
@app.get('/api/horses/<int:horse_id>/history')
def history(horse_id):
    u = current_user()
    role = u['role'] if u else 'مدير'
    
    with closing(db()) as conn:
        horse = conn.execute('SELECT * FROM horses WHERE id=?', (horse_id,)).fetchone()
        if not horse:
            return jsonify(error='الحصان غير موجود.'), 404
        medical = [dict(r) for r in conn.execute('SELECT * FROM medical_records WHERE horse_id=? ORDER BY record_date DESC', (horse_id,))]
        tasks = [dict(r) for r in conn.execute('SELECT * FROM care_tasks WHERE horse_id=? ORDER BY due_date DESC', (horse_id,))]
        
        # Hide payments if role is not manager
        if role == 'مدير':
            payments = [dict(r) for r in conn.execute('SELECT * FROM payments WHERE horse_id=? ORDER BY due_date DESC', (horse_id,))]
        else:
            payments = []
            
        medications = [dict(r) for r in conn.execute('SELECT * FROM medications WHERE horse_id=? ORDER BY start_date DESC', (horse_id,))]
        feeding = [dict(r) for r in conn.execute('SELECT * FROM feeding_plans WHERE horse_id=? AND active=1 ORDER BY meal_time', (horse_id,))]
        training = [dict(r) for r in conn.execute('SELECT * FROM training_sessions WHERE horse_id=? ORDER BY session_date DESC', (horse_id,))]
        documents = [dict(r) for r in conn.execute('SELECT * FROM documents WHERE horse_id=? ORDER BY created_at DESC', (horse_id,))]
        audit = [dict(r) for r in conn.execute('SELECT * FROM audit_log WHERE horse_id=? ORDER BY created_at DESC', (horse_id,))]
        photos = [dict(r) for r in conn.execute('SELECT * FROM horse_photos WHERE horse_id=? ORDER BY is_primary DESC, uploaded_at DESC', (horse_id,))]
        currency = conn.execute("SELECT value FROM settings WHERE key='currency'").fetchone()
        currency_str = currency['value'] if currency else 'ج.م'
        
    return jsonify(horse=dict(horse), medical=medical, tasks=tasks, payments=payments,
                   medications=medications, feeding=feeding, training=training,
                   documents=documents, audit=audit, photos=photos, currency=currency_str, user_role=role)

@app.post('/api/horses/<int:horse_id>/photos')
def upload_horse_photo(horse_id):
    photo = request.files.get('photo')
    if not photo or not photo.filename:
        return jsonify(error='يرجى اختيار ملف الصورة أولاً.'), 400
    ext = os.path.splitext(secure_filename(photo.filename))[1].lower()
    if ext not in {'.jpg', '.jpeg', '.png', '.webp'}:
        return jsonify(error='يسمح بصور JPG وPNG وWEBP فقط.'), 400
    if request.content_length and request.content_length > 16 * 1024 * 1024:
        return jsonify(error='حجم الصورة يجب ألا يتجاوز 16MB.'), 413
    with closing(db()) as conn:
        horse = conn.execute('SELECT name FROM horses WHERE id=?', (horse_id,)).fetchone()
        if not horse:
            return jsonify(error='الحصان غير موجود.'), 404
        uploads_dir = os.path.join(BASE_DIR, 'uploads', 'horses')
        os.makedirs(uploads_dir, exist_ok=True)
        filename = f'{uuid.uuid4().hex}{ext}'
        photo.save(os.path.join(uploads_dir, filename))
        is_primary = 1 if request.form.get('is_primary') == '1' else 0
        if is_primary:
            conn.execute('UPDATE horse_photos SET is_primary=0 WHERE horse_id=?', (horse_id,))
            conn.execute('UPDATE horses SET photo_path=? WHERE id=?', (filename, horse_id))
        conn.execute('INSERT INTO horse_photos (horse_id, file_name, caption, is_primary) VALUES (?,?,?,?)',
                     (horse_id, filename, request.form.get('caption', ''), is_primary))
        u = current_user()
        actor = u['full_name'] if u else 'مدير النظام'
        conn.execute('INSERT INTO audit_log (horse_id, action, details, actor) VALUES (?,?,?,?)',
                     (horse_id, 'رفع صورة', f'تمت إضافة صورة جديدة للحصان «{horse["name"]}»', actor))
        conn.commit()
    return jsonify(ok=True, file_name=filename), 201

@app.get('/uploads/horses/<path:filename>')
def horse_image(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'uploads', 'horses'), filename)

# --- Care Tasks API ---
@app.get('/api/tasks')
def list_tasks():
    u = current_user()
    role = u['role'] if u else 'مدير'
    
    with closing(db()) as conn:
        task_sql = '''
            SELECT t.*, h.name AS horse_name, h.stall 
            FROM care_tasks t 
            JOIN horses h ON h.id=t.horse_id
        '''
        if role == 'طبيب بيطري':
            task_sql += " WHERE t.category IN ('بيطري', 'تطعيم', 'رعاية', 'حوافر')"
        elif role == 'مدرب':
            task_sql += " WHERE t.category IN ('تدريب', 'تغذية', 'رعاية')"
            
        task_sql += '''
            ORDER BY t.completed ASC, t.due_date ASC, 
                     CASE t.priority WHEN 'عاجل' THEN 1 WHEN 'عالي' THEN 2 ELSE 3 END
        '''
        tasks = [dict(r) for r in conn.execute(task_sql)]
    return jsonify(tasks)

@app.post('/api/tasks')
def create_task():
    data = request.get_json(silent=True) or request.form.to_dict()
    if not all(data.get(k) for k in ('horse_id', 'title', 'due_date')):
        return jsonify(error='الحصان، وصف المهمة، وتاريخ الاستحقاق مطلوبة.'), 400
    try:
        with closing(db()) as conn:
            supplied_id = str(data['horse_id']).strip()
            horse = conn.execute('SELECT id, name FROM horses WHERE CAST(id AS TEXT)=? OR microchip=? OR name=?',
                                 (supplied_id, supplied_id, supplied_id)).fetchone()
            if not horse:
                return jsonify(error='الحصان المختار غير موجود.'), 404
            
            conn.execute('INSERT INTO care_tasks (horse_id, title, category, due_date, priority) VALUES (?,?,?,?,?)',
                         (horse['id'], str(data['title']).strip(), str(data.get('category') or 'رعاية'),
                          str(data['due_date']), str(data.get('priority') or 'متوسط')))
            
            u = current_user()
            actor = u['full_name'] if u else 'مدير النظام'
            conn.execute('INSERT INTO audit_log (horse_id, action, details, actor) VALUES (?,?,?,?)',
                         (horse['id'], 'إضافة مهمة رعاية', f'{data["title"]} (أولوية: {data.get("priority", "متوسط")})', actor))
            conn.commit()
    except sqlite3.Error as error:
        return jsonify(error=f'تعذر حفظ المهمة: {error}'), 500
    return jsonify(ok=True, message='تمت إضافة المهمة بنجاح.'), 201

@app.post('/api/tasks/<int:task_id>/complete')
def complete_task(task_id):
    with closing(db()) as conn:
        cur = conn.execute('UPDATE care_tasks SET completed=1 WHERE id=?', (task_id,))
        conn.commit()
    return jsonify(ok=bool(cur.rowcount))

@app.delete('/api/tasks/<int:task_id>')
def delete_task(task_id):
    with closing(db()) as conn:
        cur = conn.execute('DELETE FROM care_tasks WHERE id=?', (task_id,))
        conn.commit()
    return jsonify(ok=bool(cur.rowcount))

# --- Finance & Accounting API (Restricted to Manager / Admin) ---
@app.get('/api/finance/summary')
@require_role(['مدير'])
def finance_summary():
    with closing(db()) as conn:
        paid = conn.execute('SELECT COALESCE(SUM(amount),0) FROM payments WHERE paid=1').fetchone()[0]
        unpaid = conn.execute('SELECT COALESCE(SUM(amount),0) FROM payments WHERE paid=0').fetchone()[0]
        total_invoiced = paid + unpaid
        expenses = conn.execute('SELECT COALESCE(SUM(amount),0) FROM expenses').fetchone()[0]
        net = paid - expenses
        currency = conn.execute("SELECT value FROM settings WHERE key='currency'").fetchone()
        currency_str = currency['value'] if currency else 'ج.م'
        
        recent_payments = [dict(r) for r in conn.execute('''
            SELECT p.*, h.name AS horse_name, h.owner_name 
            FROM payments p 
            LEFT JOIN horses h ON h.id=p.horse_id 
            ORDER BY p.due_date DESC LIMIT 15
        ''')]
        recent_expenses = [dict(r) for r in conn.execute('''
            SELECT * FROM expenses ORDER BY expense_date DESC LIMIT 15
        ''')]
    return jsonify(
        total_invoiced=total_invoiced,
        paid=paid,
        unpaid=unpaid,
        expenses=expenses,
        net_balance=net,
        currency=currency_str,
        payments=recent_payments,
        expenses_list=recent_expenses
    )

@app.get('/api/payments')
@require_role(['مدير'])
def list_payments():
    with closing(db()) as conn:
        items = [dict(r) for r in conn.execute('''
            SELECT p.*, h.name AS horse_name, h.owner_name 
            FROM payments p 
            LEFT JOIN horses h ON h.id=p.horse_id 
            ORDER BY p.due_date DESC
        ''')]
    return jsonify(items)

@app.post('/api/payments')
@require_role(['مدير'])
def create_payment():
    data = request.get_json(silent=True) or request.form.to_dict()
    if not data.get('description') or not data.get('amount') or not data.get('due_date'):
        return jsonify(error='البيان، المبلغ، وتاريخ الاستحقاق مطلوبة.'), 400
    
    horse_id = data.get('horse_id')
    if horse_id and str(horse_id).strip():
        horse_id = int(horse_id)
    else:
        horse_id = None

    try:
        amount_val = float(data['amount'])
    except (ValueError, TypeError):
        return jsonify(error='المبلغ يجب أن يكون رقماً صحيحاً.'), 400

    paid = 1 if str(data.get('paid', '0')) in ('1', 'true', 'True') else 0
    payment_date = str(date.today()) if paid else None
    
    with closing(db()) as conn:
        currency = conn.execute("SELECT value FROM settings WHERE key='currency'").fetchone()
        currency_str = currency['value'] if currency else 'ج.م'
        conn.execute('''
            INSERT INTO payments (horse_id, description, amount, due_date, paid, payment_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (horse_id, str(data['description']).strip(), amount_val, str(data['due_date']), paid, payment_date))
        
        u = current_user()
        actor = u['full_name'] if u else 'مدير النظام'
        conn.execute('INSERT INTO audit_log (horse_id, action, details, actor) VALUES (?,?,?,?)',
                     (horse_id, 'إضافة فاتورة/دفعة', f'{data["description"]} بمبلغ {amount_val} {currency_str}', actor))
        conn.commit()
    return jsonify(ok=True, message='تمت إضافة الفاتورة بنجاح.'), 201

@app.post('/api/payments/<int:payment_id>/toggle')
@require_role(['مدير'])
def toggle_payment(payment_id):
    with closing(db()) as conn:
        payment = conn.execute('SELECT paid, description, amount FROM payments WHERE id=?', (payment_id,)).fetchone()
        if not payment:
            return jsonify(error='الفاتورة غير موجودة.'), 404
        new_status = 0 if payment['paid'] else 1
        pay_date = str(date.today()) if new_status else None
        conn.execute('UPDATE payments SET paid=?, payment_date=? WHERE id=?', (new_status, pay_date, payment_id))
        conn.commit()
    return jsonify(ok=True, paid=new_status)

@app.delete('/api/payments/<int:payment_id>')
@require_role(['مدير'])
def delete_payment(payment_id):
    with closing(db()) as conn:
        conn.execute('DELETE FROM payments WHERE id=?', (payment_id,))
        conn.commit()
    return jsonify(ok=True, message='تم حذف الفاتورة.')

@app.get('/api/expenses')
@require_role(['مدير'])
def list_expenses():
    with closing(db()) as conn:
        items = [dict(r) for r in conn.execute('SELECT * FROM expenses ORDER BY expense_date DESC')]
    return jsonify(items)

@app.post('/api/expenses')
@require_role(['مدير'])
def create_expense():
    data = request.get_json(silent=True) or request.form.to_dict()
    if not data.get('category') or not data.get('amount') or not data.get('expense_date'):
        return jsonify(error='التصنيف، المبلغ، والتاريخ مطلوبة.'), 400
    try:
        amount_val = float(data['amount'])
    except (ValueError, TypeError):
        return jsonify(error='المبلغ يجب أن يكون رقماً صالحاً.'), 400

    with closing(db()) as conn:
        currency = conn.execute("SELECT value FROM settings WHERE key='currency'").fetchone()
        currency_str = currency['value'] if currency else 'ج.م'
        conn.execute('''
            INSERT INTO expenses (expense_date, category, description, amount, vendor)
            VALUES (?, ?, ?, ?, ?)
        ''', (str(data['expense_date']), str(data['category']).strip(), str(data.get('description', '')).strip(),
              amount_val, str(data.get('vendor', '')).strip()))
        
        u = current_user()
        actor = u['full_name'] if u else 'مدير النظام'
        conn.execute('INSERT INTO audit_log (action, details, actor) VALUES (?,?,?)',
                     ('إضافة مصروف', f'{data["category"]}: {data.get("description", "")} بمبلغ {amount_val} {currency_str}', actor))
        conn.commit()
    return jsonify(ok=True, message='تم تسجيل المصروف بنجاح.'), 201

@app.delete('/api/expenses/<int:expense_id>')
@require_role(['مدير'])
def delete_expense(expense_id):
    with closing(db()) as conn:
        conn.execute('DELETE FROM expenses WHERE id=?', (expense_id,))
        conn.commit()
    return jsonify(ok=True, message='تم حذف المصروف.')

# --- Alerts API ---
@app.get('/api/alerts')
def alerts():
    today = str(date.today())
    soon = str(date.today() + timedelta(days=7))
    with closing(db()) as conn:
        items = []
        for r in conn.execute('''
            SELECT h.id AS horse_id, h.name, m.next_due_date AS due_date, 
                   ('استحقاق بيطري: ' || m.record_type || ' (' || COALESCE(m.details,'') || ')') AS label
            FROM medical_records m 
            JOIN horses h ON h.id=m.horse_id 
            WHERE m.next_due_date IS NOT NULL AND m.next_due_date<=? AND h.status!='مؤرشف'
        ''', (soon,)):
            items.append({**dict(r), 'level': 'متأخر' if r['due_date'] < today else 'قريب', 'type': 'medical'})
        
        for r in conn.execute('''
            SELECT h.id AS horse_id, h.name, m.end_date AS due_date, 
                   ('انتهاء دواء: ' || m.medicine_name || ' (' || COALESCE(m.dosage,'') || ')') AS label
            FROM medications m 
            JOIN horses h ON h.id=m.horse_id 
            WHERE m.active=1 AND m.end_date IS NOT NULL AND m.end_date<=? AND h.status!='مؤرشف'
        ''', (soon,)):
            items.append({**dict(r), 'level': 'متأخر' if r['due_date'] < today else 'قريب', 'type': 'medication'})
            
        for r in conn.execute('''
            SELECT h.id AS horse_id, h.name, t.due_date AS due_date, 
                   ('مهمة عاجلة: ' || t.title) AS label
            FROM care_tasks t 
            JOIN horses h ON h.id=t.horse_id 
            WHERE t.completed=0 AND t.priority='عاجل' AND h.status!='مؤرشف'
        '''):
            items.append({**dict(r), 'level': 'عاجل', 'type': 'task'})
            
    return jsonify(sorted(items, key=lambda x: x['due_date']))

# --- Settings & System Management API (Manager Only) ---
@app.get('/api/settings')
def get_settings():
    with closing(db()) as conn:
        settings_dict = {r['key']: r['value'] for r in conn.execute('SELECT key, value FROM settings')}
        stats = {
            'db_size_kb': round(os.path.getsize(app.config['DATABASE']) / 1024, 1) if os.path.exists(app.config['DATABASE']) else 0,
            'total_horses': conn.execute('SELECT COUNT(*) FROM horses').fetchone()[0],
            'total_tasks': conn.execute('SELECT COUNT(*) FROM care_tasks').fetchone()[0],
            'total_records': conn.execute('SELECT COUNT(*) FROM medical_records').fetchone()[0],
            'total_audit_logs': conn.execute('SELECT COUNT(*) FROM audit_log').fetchone()[0]
        }
    return jsonify(settings=settings_dict, stats=stats)

@app.post('/api/settings')
@require_role(['مدير'])
def update_settings():
    data = request.get_json(silent=True) or request.form.to_dict()
    if not data:
        return jsonify(error='لا توجد بيانات.'), 400
    with closing(db()) as conn:
        for k, v in data.items():
            conn.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (str(k), str(v)))
        u = current_user()
        actor = u['full_name'] if u else 'مدير النظام'
        conn.execute('INSERT INTO audit_log (action, details, actor) VALUES (?,?,?)',
                     ('تحديث إعدادات النظام', 'تم تحديث خيارات الإعدادات العامة للإسطبل', actor))
        conn.commit()
    return jsonify(ok=True, message='تم حفظ الإعدادات بنجاح.')

# --- Backups API (Manager Only) ---
@app.get('/api/backups')
@require_role(['مدير'])
def backups():
    backup_dir = os.path.join(BASE_DIR, 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    results = []
    for name in sorted(os.listdir(backup_dir), reverse=True):
        if name.endswith('.db'):
            path = os.path.join(backup_dir, name)
            stat = os.stat(path)
            results.append({
                'name': name,
                'size': stat.st_size,
                'size_kb': round(stat.st_size / 1024, 1),
                'created_at': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            })
    return jsonify(results)

@app.post('/api/backups/create')
@require_role(['مدير'])
def create_backup():
    backup_dir = os.path.join(BASE_DIR, 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    name = f"backup_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.db"
    target_path = os.path.join(backup_dir, name)
    shutil.copy2(app.config['DATABASE'], target_path)
    with closing(db()) as conn:
        u = current_user()
        actor = u['full_name'] if u else 'مدير النظام'
        conn.execute('INSERT INTO audit_log (action, details, actor) VALUES (?,?,?)',
                     ('إنشاء نسخة احتياطية', f'تم حفظ النسخة: {name}', actor))
        conn.commit()
    return jsonify(name=name, ok=True, message='تم إنشاء النسخة الاحتياطية بنجاح.'), 201

@app.get('/api/backups/<path:name>/download')
@require_role(['مدير'])
def download_backup(name):
    if os.path.basename(name) != name or not name.endswith('.db'):
        return jsonify(error='اسم ملف غير صالح.'), 400
    path = os.path.join(BASE_DIR, 'backups', name)
    if not os.path.exists(path):
        return jsonify(error='النسخة غير موجودة.'), 404
    return send_file(path, as_attachment=True, download_name=name)

@app.post('/api/backups/<path:name>/restore')
@require_role(['مدير'])
def restore_backup(name):
    if os.path.basename(name) != name or not name.endswith('.db'):
        return jsonify(error='اسم ملف غير صالح.'), 400
    backup_path = os.path.join(BASE_DIR, 'backups', name)
    if not os.path.exists(backup_path):
        return jsonify(error='ملف النسخة الاحتياطية غير موجود.'), 404
    
    # Pre-restore safety backup
    pre_restore_name = f"pre_restore_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.db"
    shutil.copy2(app.config['DATABASE'], os.path.join(BASE_DIR, 'backups', pre_restore_name))
    
    # Restore
    shutil.copy2(backup_path, app.config['DATABASE'])
    
    return jsonify(ok=True, message=f'تم استرجاع قاعدة البيانات بنجاح من النسخة «{name}».')

@app.delete('/api/backups/<path:name>')
@require_role(['مدير'])
def delete_backup(name):
    if os.path.basename(name) != name or not name.endswith('.db'):
        return jsonify(error='اسم ملف غير صالح.'), 400
    path = os.path.join(BASE_DIR, 'backups', name)
    if not os.path.exists(path):
        return jsonify(error='ملف النسخة غير موجود.'), 404
    try:
        os.remove(path)
        return jsonify(ok=True, message='تم حذف النسخة الاحتياطية.')
    except OSError as e:
        return jsonify(error=f'تعذر حذف الملف: {e}'), 500

# --- Export Reports (CSV) ---
@app.get('/api/reports/horses/csv')
def export_horses_csv():
    with closing(db()) as conn:
        horses = conn.execute('SELECT * FROM horses ORDER BY id ASC').fetchall()
    
    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow([
        'ID', 'Microchip', 'Name', 'Breed', 'Sex', 'Birth Date', 'Colour',
        'Owner Name', 'Owner Phone', 'Stall', 'Status', 'Height (cm)', 'Weight (kg)',
        'Sire', 'Dam', 'Notes'
    ])
    for h in horses:
        writer.writerow([
            h['id'], h['microchip'], h['name'], h['breed'], h['sex'], h['birth_date'],
            h['colour'], h['owner_name'], h['owner_phone'], h['stall'], h['status'],
            h['height_cm'], h['weight_kg'], h['sire'], h['dam'], h['notes']
        ])
    output = si.getvalue().encode('utf-8-sig')
    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=horses_report_{date.today().isoformat()}.csv'}
    )

@app.get('/api/reports/finance/csv')
@require_role(['مدير'])
def export_finance_csv():
    with closing(db()) as conn:
        currency = conn.execute("SELECT value FROM settings WHERE key='currency'").fetchone()
        currency_str = currency['value'] if currency else 'ج.م'
        payments = conn.execute('''
            SELECT p.*, h.name AS horse_name, h.owner_name 
            FROM payments p 
            LEFT JOIN horses h ON h.id=p.horse_id 
            ORDER BY p.due_date DESC
        ''').fetchall()
        expenses = conn.execute('SELECT * FROM expenses ORDER BY expense_date DESC').fetchall()
    
    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(['--- سجل الفواتير والمقبوضات (Invoices & Payments) ---'])
    writer.writerow(['ID', 'Horse', 'Owner', 'Description', f'Amount ({currency_str})', 'Due Date', 'Status', 'Payment Date'])
    for p in payments:
        writer.writerow([
            p['id'], p['horse_name'] or '-', p['owner_name'] or '-', p['description'],
            p['amount'], p['due_date'], 'مدفوعة' if p['paid'] else 'معلقة', p['payment_date'] or '-'
        ])
    
    writer.writerow([])
    writer.writerow(['--- سجل المصروفات (Expenses) ---'])
    writer.writerow(['ID', 'Expense Date', 'Category', 'Description', f'Amount ({currency_str})', 'Vendor'])
    for e in expenses:
        writer.writerow([
            e['id'], e['expense_date'], e['category'], e['description'], e['amount'], e['vendor'] or '-'
        ])
    
    output = si.getvalue().encode('utf-8-sig')
    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=finance_report_{date.today().isoformat()}.csv'}
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
