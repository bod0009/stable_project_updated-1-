import sqlite3
import os
import shutil
import hashlib
from datetime import date, timedelta

def hash_pw(pw):
    return 'pbkdf2:' + hashlib.pbkdf2_hmac('sha256', pw.encode(), b'alkhyala_salt_2026', 100000).hex()

db_path = '/working_dir/c_90c07f132c73da6f/stable_project/stable.db'
if os.path.exists(db_path):
    os.remove(db_path)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
conn.execute('PRAGMA journal_mode = memory;')
conn.execute('PRAGMA synchronous = OFF;')
conn.execute('PRAGMA foreign_keys = ON;')

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
'''

conn.executescript(schema)

# Pre-seeded users with password 123456
pw = hash_pw('123456')
users = [
    ('admin', pw, 'المدير العام (Admin)', 'مدير'),
    ('vet', pw, 'د. خالد العمري (طبيب بيطري)', 'طبيب بيطري'),
    ('trainer', pw, 'كابتن طارق العلي (مدرب الخيل)', 'مدرب')
]
conn.executemany('''
    INSERT INTO users (username, password_hash, full_name, role)
    VALUES (?, ?, ?, ?)
''', users)

# Default settings (Alexandria, Egypt, EGP)
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
    conn.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (k, v))

# Seed demo horses
horses = [
    ('982000000000101', 'برق', 'عربي أصيل', 'ذكر', '2018-04-12', 'كميت', 'فهد العتيبي', '01000000001', 'A-03', 'نشط', 'حساس للغبار', 155.0, 460.0, 'مروان الشقب', 'غزالة', 'العديد الشقب', 'سفيرة', 'حساسية غبار التبن', 'تبن نقي مع شعير مفروم', 'قفز حواجز - مستوى متقدم', None),
    ('982000000000102', 'نجمة', 'عربي أصيل', 'أنثى', '2019-07-21', 'رمادي', 'مها السالمي', '01000000002', 'B-07', 'نشط', '', 150.0, 425.0, 'كنز البداير', 'شهد', 'عجمان منيسكيون', 'ريم', '', 'علف مركب وفيتامينات', 'ترويض كلاسيكي', None),
    ('982000000000103', 'وسام', 'ثوروبريد', 'ذكر', '2016-01-09', 'أشقر', 'أحمد الحربي', '01000000003', 'C-01', 'راحة', 'برنامج تأهيل عضلي', 162.0, 510.0, 'فرانكل', 'ليدي وين', 'غاليليو', 'كوين سيكريت', '', 'وجبات مكثفة غنية بالبروتين', 'جلسات استرجاع ولياقة خفيفة', None),
    ('982000000000104', 'صقر', 'عربي أصيل', 'ذكر', '2020-02-14', 'أدهم', 'سلطان القحطاني', '01000000004', 'A-05', 'نشط', 'خيل سباق سريع', 153.0, 440.0, 'كحيل الشقب', 'درة', 'غزال الشقب', 'بدور', '', 'شعير + شوفان مكمل', 'تمارين سرعة وتحمل', None)
]
conn.executemany('''INSERT OR IGNORE INTO horses 
    (microchip, name, breed, sex, birth_date, colour, owner_name, owner_phone, stall, status, notes, height_cm, weight_kg, sire, dam, grand_sire, grand_dam, allergies, feed_notes, training_notes, photo_path) 
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', horses)

ids = {r['name']: r['id'] for r in conn.execute('SELECT id, name FROM horses')}

today = date.today()

# Tasks
conn.executemany('''INSERT INTO care_tasks (horse_id, title, category, due_date, priority) VALUES (?,?,?,?,?)''', [
    (ids['برق'], 'تطعيم الإنفلونزا السنوي', 'تطعيم', str(today), 'عاجل'),
    (ids['نجمة'], 'تقليم وصيانة الحوافر', 'حوافر', str(today + timedelta(days=1)), 'متوسط'),
    (ids['وسام'], 'جلسة تأهيل وعلاج طبيعي', 'تدريب', str(today + timedelta(days=2)), 'عالي'),
    (ids['صقر'], 'فحص الأسنان الدوري', 'بيطري', str(today + timedelta(days=3)), 'متوسط')
])

# Medical & Medications
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

conn.execute('INSERT INTO audit_log (action, details, actor) VALUES (?,?,?)',
             ('تهيئة النظام', 'تم إطلاق نظام الخيّالة وضبط الصلاحيات والعملة بالجنيه المصري (ج.م)', 'النظام'))

conn.commit()
conn.close()

# Create initial backup snapshot
backup_dir = '/working_dir/c_90c07f132c73da6f/stable_project/backups'
os.makedirs(backup_dir, exist_ok=True)
backup_path = f'{backup_dir}/backup_{today.isoformat()}_initial.db'
shutil.copy2(db_path, backup_path)

print("Database initialized with users and settings successfully!")
