import os
import sys
import tempfile
import sqlite3
import unittest
import csv
import io
import shutil
from datetime import date, datetime, timedelta

class StableDatabaseAndLogicTest(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute('PRAGMA journal_mode = memory;')
        self.conn.execute('PRAGMA synchronous = OFF;')
        self.conn.execute('PRAGMA foreign_keys = ON;')
        self.init_schema()

    def tearDown(self):
        self.conn.close()
        os.close(self.db_fd)
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def init_schema(self):
        schema = '''
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

        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            horse_id INTEGER REFERENCES horses(id) ON DELETE SET NULL,
            action TEXT NOT NULL,
            details TEXT,
            actor TEXT NOT NULL DEFAULT 'مدير النظام',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        '''
        self.conn.executescript(schema)
        self.conn.commit()

    def test_horse_creation_and_uniqueness(self):
        # Insert horse
        self.conn.execute('''
            INSERT INTO horses (microchip, name, breed, sex, birth_date, colour, owner_name, stall, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('982000000000001', 'برق', 'عربي أصيل', 'ذكر', '2019-01-01', 'أشقر', 'فهد العتيبي', 'A-01', 'نشط'))
        self.conn.commit()

        row = self.conn.execute('SELECT * FROM horses WHERE microchip=?', ('982000000000001',)).fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row['name'], 'برق')

        # Test UNIQUE constraint on microchip
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute('''
                INSERT INTO horses (microchip, name) VALUES (?, ?)
            ''', ('982000000000001', 'صقر'))
            self.conn.commit()

    def test_foreign_key_cascade_deletion(self):
        cur = self.conn.execute('''
            INSERT INTO horses (microchip, name) VALUES (?, ?)
        ''', ('982000000000002', 'نجمة'))
        horse_id = cur.lastrowid

        self.conn.execute('''
            INSERT INTO care_tasks (horse_id, title, category, due_date) VALUES (?, ?, ?, ?)
        ''', (horse_id, 'تقليم حوافر', 'حوافر', str(date.today())))
        self.conn.execute('''
            INSERT INTO medical_records (horse_id, record_date, record_type, details) VALUES (?, ?, ?, ?)
        ''', (horse_id, str(date.today()), 'تطعيم', 'جرعة سنوية'))
        self.conn.execute('''
            INSERT INTO feeding_plans (horse_id, meal_time, feed_type, quantity) VALUES (?, ?, ?, ?)
        ''', (horse_id, '07:00 ص', 'شعير', 3.0))
        self.conn.commit()

        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM care_tasks WHERE horse_id=?', (horse_id,)).fetchone()[0], 1)
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM medical_records WHERE horse_id=?', (horse_id,)).fetchone()[0], 1)

        # Delete horse permanently
        self.conn.execute('DELETE FROM horses WHERE id=?', (horse_id,))
        self.conn.commit()

        # Verify cascading deletion
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM care_tasks WHERE horse_id=?', (horse_id,)).fetchone()[0], 0)
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM medical_records WHERE horse_id=?', (horse_id,)).fetchone()[0], 0)
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM feeding_plans WHERE horse_id=?', (horse_id,)).fetchone()[0], 0)

    def test_horse_archive_and_restore(self):
        cur = self.conn.execute('''
            INSERT INTO horses (microchip, name, status) VALUES (?, ?, 'نشط')
        ''', ('982000000000003', 'وسام'))
        h_id = cur.lastrowid
        self.conn.commit()

        # Archive
        self.conn.execute("UPDATE horses SET status='مؤرشف' WHERE id=?", (h_id,))
        self.conn.commit()
        status_archived = self.conn.execute("SELECT status FROM horses WHERE id=?", (h_id,)).fetchone()[0]
        self.assertEqual(status_archived, 'مؤرشف')

        # Restore
        self.conn.execute("UPDATE horses SET status='نشط' WHERE id=?", (h_id,))
        self.conn.commit()
        status_restored = self.conn.execute("SELECT status FROM horses WHERE id=?", (h_id,)).fetchone()[0]
        self.assertEqual(status_restored, 'نشط')

    def test_finance_calculations_and_ledger(self):
        # Insert payments
        self.conn.execute("INSERT INTO payments (description, amount, due_date, paid) VALUES (?, ?, ?, ?)", ('إيواء شهر 1', 3000, '2026-08-01', 1))
        self.conn.execute("INSERT INTO payments (description, amount, due_date, paid) VALUES (?, ?, ?, ?)", ('تدريب خاص', 2000, '2026-08-05', 1))
        self.conn.execute("INSERT INTO payments (description, amount, due_date, paid) VALUES (?, ?, ?, ?)", ('إيواء شهر 2', 1500, '2026-08-10', 0))

        # Insert expenses
        self.conn.execute("INSERT INTO expenses (expense_date, category, description, amount, vendor) VALUES (?, ?, ?, ?, ?)", ('2026-08-02', 'أعلاف', 'تبن وشعير', 1200, 'المؤسسة'))
        self.conn.execute("INSERT INTO expenses (expense_date, category, description, amount, vendor) VALUES (?, ?, ?, ?, ?)", ('2026-08-04', 'بيطري', 'أدوية', 800, 'البيطري'))
        self.conn.commit()

        paid = self.conn.execute('SELECT COALESCE(SUM(amount), 0) FROM payments WHERE paid=1').fetchone()[0]
        unpaid = self.conn.execute('SELECT COALESCE(SUM(amount), 0) FROM payments WHERE paid=0').fetchone()[0]
        total_invoiced = paid + unpaid
        expenses = self.conn.execute('SELECT COALESCE(SUM(amount), 0) FROM expenses').fetchone()[0]
        net_balance = paid - expenses

        self.assertEqual(paid, 5000)
        self.assertEqual(unpaid, 1500)
        self.assertEqual(total_invoiced, 6500)
        self.assertEqual(expenses, 2000)
        self.assertEqual(net_balance, 3000)

        # Toggle payment status
        pay_id = self.conn.execute("SELECT id FROM payments WHERE description='إيواء شهر 2'").fetchone()[0]
        self.conn.execute("UPDATE payments SET paid=1, payment_date=? WHERE id=?", (str(date.today()), pay_id))
        self.conn.commit()

        updated_paid = self.conn.execute('SELECT COALESCE(SUM(amount), 0) FROM payments WHERE paid=1').fetchone()[0]
        self.assertEqual(updated_paid, 6500)

    def test_alert_logic(self):
        today = date.today()
        soon = today + timedelta(days=7)

        cur = self.conn.execute("INSERT INTO horses (microchip, name, status) VALUES (?, ?, 'نشط')", ('982000000000004', 'صقر'))
        h_id = cur.lastrowid

        self.conn.execute("INSERT INTO medical_records (horse_id, record_date, record_type, next_due_date) VALUES (?, ?, ?, ?)",
                          (h_id, str(today - timedelta(days=180)), 'تطعيم', str(today - timedelta(days=2))))
        self.conn.execute("INSERT INTO medications (horse_id, medicine_name, start_date, end_date, active) VALUES (?, ?, ?, ?, 1)",
                          (h_id, 'مضاد حيوي', str(today - timedelta(days=4)), str(today + timedelta(days=3))))
        self.conn.execute("INSERT INTO care_tasks (horse_id, title, category, due_date, priority, completed) VALUES (?, ?, ?, ?, 'عاجل', 0)",
                          (h_id, 'علاج حافر طارئ', 'رعاية', str(today)))
        self.conn.commit()

        med_alerts = self.conn.execute('SELECT next_due_date FROM medical_records WHERE next_due_date <= ?', (str(soon),)).fetchall()
        self.assertEqual(len(med_alerts), 1)

        medication_alerts = self.conn.execute('SELECT end_date FROM medications WHERE active=1 AND end_date <= ?', (str(soon),)).fetchall()
        self.assertEqual(len(medication_alerts), 1)

        urgent_tasks = self.conn.execute("SELECT COUNT(*) FROM care_tasks WHERE completed=0 AND priority='عاجل'").fetchone()[0]
        self.assertEqual(urgent_tasks, 1)

    def test_database_backup_and_recovery_file_copy(self):
        self.conn.execute("INSERT INTO settings (key, value) VALUES (?, ?)", ('stable_name', 'إسطبل الأصيل'))
        self.conn.commit()

        backup_fd, backup_file = tempfile.mkstemp(suffix='.db')
        shutil.copy2(self.db_path, backup_file)

        verify_conn = sqlite3.connect(backup_file)
        row = verify_conn.execute("SELECT value FROM settings WHERE key='stable_name'").fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 'إسطبل الأصيل')
        verify_conn.close()

        os.close(backup_fd)
        if os.path.exists(backup_file):
            os.unlink(backup_file)

    def test_csv_report_generation(self):
        self.conn.execute('''
            INSERT INTO horses (microchip, name, breed, sex, birth_date, owner_name, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('982000000000005', 'غزال', 'عربي أصيل', 'ذكر', '2020-03-15', 'سلطان القحطاني', 'نشط'))
        self.conn.commit()

        horses = self.conn.execute('SELECT * FROM horses').fetchall()
        si = io.StringIO()
        writer = csv.writer(si)
        writer.writerow(['ID', 'Microchip', 'Name', 'Breed', 'Sex', 'Birth Date', 'Owner Name', 'Status'])
        for h in horses:
            writer.writerow([h['id'], h['microchip'], h['name'], h['breed'], h['sex'], h['birth_date'], h['owner_name'], h['status']])
        
        csv_str = si.getvalue()
        self.assertIn('982000000000005', csv_str)
        self.assertIn('غزال', csv_str)

    def test_multi_filter_search(self):
        self.conn.executemany('''
            INSERT INTO horses (microchip, name, breed, sex, status, stall) VALUES (?, ?, ?, ?, ?, ?)
        ''', [
            ('101', 'رياح', 'عربي أصيل', 'ذكر', 'نشط', 'A-01'),
            ('102', 'وردة', 'عربي أصيل', 'أنثى', 'نشط', 'A-02'),
            ('103', 'بركان', 'ثوروبريد', 'ذكر', 'راحة', 'B-01'),
            ('104', 'شمس', 'عربي أصيل', 'أنثى', 'مؤرشف', 'C-01')
        ])
        self.conn.commit()

        # Filter active arabian males
        query = '''
            SELECT * FROM horses 
            WHERE (name LIKE ? OR microchip LIKE ?)
              AND (?='' OR breed=?)
              AND (?='' OR sex=?)
              AND (?='' OR status=?)
        '''
        results = self.conn.execute(query, ('%%', '%%', 'عربي أصيل', 'عربي أصيل', 'ذكر', 'ذكر', 'نشط', 'نشط')).fetchall()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'رياح')

if __name__ == '__main__':
    unittest.main()
