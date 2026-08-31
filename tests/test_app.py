import os
import sys
import tempfile
import unittest
import json
from datetime import date, timedelta

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import app as stable_app

class StableAppTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        stable_app.app.config['DATABASE'] = self.db_path
        stable_app.app.config['TESTING'] = True
        self.client = stable_app.app.test_client()
        with stable_app.app.app_context():
            stable_app.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'<!doctype html>' in response.data or b'<html' in response.data)

    def test_dashboard_api(self):
        response = self.client.get('/api/dashboard')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('summary', data)
        self.assertIn('tasks', data)
        self.assertGreaterEqual(data['summary']['horses'], 0)
        self.assertIn('unpaid', data['summary'])
        self.assertIn('net_balance', data['summary'])

    def test_horses_crud_and_lifecycle(self):
        # 1. Create Horse
        horse_payload = {
            'name': 'شهاب',
            'microchip': '982000000099999',
            'breed': 'عربي أصيل',
            'sex': 'ذكر',
            'birth_date': '2021-05-10',
            'colour': 'أشقر',
            'owner_name': 'عبدالرحمن محمود',
            'owner_phone': '0555555555',
            'stall': 'D-01',
            'status': 'نشط',
            'height_cm': '158',
            'weight_kg': '470',
            'sire': 'صقلاوي',
            'dam': 'كحيلة',
            'notes': 'خيل نشط ومميز'
        }
        create_res = self.client.post('/api/horses', json=horse_payload)
        self.assertEqual(create_res.status_code, 201)
        created_horse = create_res.get_json()
        self.assertEqual(created_horse['name'], 'شهاب')
        horse_id = created_horse['id']

        # 2. Prevent duplicate microchip
        dup_res = self.client.post('/api/horses', json=horse_payload)
        self.assertEqual(dup_res.status_code, 409)
        self.assertIn('مسجل مسبقاً', dup_res.get_json()['error'])

        # 3. Validation error on missing fields
        invalid_res = self.client.post('/api/horses', json={'name': ''})
        self.assertEqual(invalid_res.status_code, 400)

        # 4. Search and List Horses
        list_res = self.client.get('/api/horses?q=شهاب')
        self.assertEqual(list_res.status_code, 200)
        horses = list_res.get_json()
        self.assertEqual(len(horses), 1)
        self.assertEqual(horses[0]['microchip'], '982000000099999')

        # 5. Update Horse
        update_res = self.client.put(f'/api/horses/{horse_id}', json={'stall': 'D-02', 'weight_kg': 475})
        self.assertEqual(update_res.status_code, 200)
        
        history_res = self.client.get(f'/api/horses/{horse_id}/history')
        self.assertEqual(history_res.status_code, 200)
        h_data = history_res.get_json()['horse']
        self.assertEqual(h_data['stall'], 'D-02')
        self.assertEqual(h_data['weight_kg'], 475)

        # 6. Archive Horse
        archive_res = self.client.post(f'/api/horses/{horse_id}/archive')
        self.assertEqual(archive_res.status_code, 200)
        
        # Verify horse status is now 'مؤرشف'
        check_res = self.client.get(f'/api/horses?status=مؤرشف')
        archived_list = check_res.get_json()
        self.assertTrue(any(h['id'] == horse_id for h in archived_list))

        # 7. Restore Horse
        restore_res = self.client.post(f'/api/horses/{horse_id}/restore')
        self.assertEqual(restore_res.status_code, 200)
        check_act = self.client.get(f'/api/horses?status=نشط')
        active_list = check_act.get_json()
        self.assertTrue(any(h['id'] == horse_id for h in active_list))

        # 8. Permanent Delete
        del_res = self.client.delete(f'/api/horses/{horse_id}/permanent')
        self.assertEqual(del_res.status_code, 200)
        check_deleted = self.client.get(f'/api/horses/{horse_id}/history')
        self.assertEqual(check_deleted.status_code, 404)

    def test_tasks_flow(self):
        horses_res = self.client.get('/api/horses')
        horses = horses_res.get_json()
        self.assertGreater(len(horses), 0)
        test_horse_id = horses[0]['id']

        # Create task
        task_payload = {
            'horse_id': test_horse_id,
            'title': 'كشف بيطري دوري للعيون',
            'category': 'بيطري',
            'due_date': str(date.today() + timedelta(days=2)),
            'priority': 'عاجل'
        }
        create_task_res = self.client.post('/api/tasks', json=task_payload)
        self.assertEqual(create_task_res.status_code, 201)

        # List tasks
        tasks_res = self.client.get('/api/tasks')
        self.assertEqual(tasks_res.status_code, 200)
        tasks = tasks_res.get_json()
        new_task = next(t for t in tasks if t['title'] == 'كشف بيطري دوري للعيون')
        task_id = new_task['id']

        # Complete task
        comp_res = self.client.post(f'/api/tasks/{task_id}/complete')
        self.assertEqual(comp_res.status_code, 200)

        # Delete task
        del_res = self.client.delete(f'/api/tasks/{task_id}')
        self.assertEqual(del_res.status_code, 200)

    def test_finance_endpoints(self):
        # Summary
        summary_res = self.client.get('/api/finance/summary')
        self.assertEqual(summary_res.status_code, 200)
        summary = summary_res.get_json()
        self.assertIn('total_invoiced', summary)
        self.assertIn('paid', summary)
        self.assertIn('unpaid', summary)
        self.assertIn('expenses', summary)
        self.assertIn('net_balance', summary)

        # Create Payment / Invoice
        pay_payload = {
            'description': 'رسوم تدريب قفز خاص',
            'amount': 2500,
            'due_date': str(date.today() + timedelta(days=7)),
            'paid': 0
        }
        pay_res = self.client.post('/api/payments', json=pay_payload)
        self.assertEqual(pay_res.status_code, 201)

        # List Payments
        payments = self.client.get('/api/payments').get_json()
        target_payment = next(p for p in payments if p['description'] == 'رسوم تدريب قفز خاص')
        p_id = target_payment['id']
        self.assertEqual(target_payment['paid'], 0)

        # Toggle Paid Status
        toggle_res = self.client.post(f'/api/payments/{p_id}/toggle')
        self.assertEqual(toggle_res.status_code, 200)
        self.assertEqual(toggle_res.get_json()['paid'], 1)

        # Delete Payment
        del_pay = self.client.delete(f'/api/payments/{p_id}')
        self.assertEqual(del_pay.status_code, 200)

        # Create Expense
        exp_payload = {
            'category': 'صيانة ومرافق',
            'description': 'تركيب رشاشات مياه لتبريد الإسطبل',
            'amount': 1800,
            'vendor': 'مؤسسة الري الحديث',
            'expense_date': str(date.today())
        }
        exp_res = self.client.post('/api/expenses', json=exp_payload)
        self.assertEqual(exp_res.status_code, 201)

        expenses = self.client.get('/api/expenses').get_json()
        target_exp = next(e for e in expenses if e['description'] == 'تركيب رشاشات مياه لتبريد الإسطبل')
        
        # Delete Expense
        del_exp = self.client.delete(f'/api/expenses/{target_exp["id"]}')
        self.assertEqual(del_exp.status_code, 200)

    def test_settings_and_backups(self):
        # Get Settings
        settings_res = self.client.get('/api/settings')
        self.assertEqual(settings_res.status_code, 200)
        data = settings_res.get_json()
        self.assertIn('settings', data)
        self.assertIn('stats', data)

        # Update Settings
        update_res = self.client.post('/api/settings', json={
            'stable_name': 'إسطبل الخيّالة الملكي',
            'manager_name': 'المهندس عبدالرحمن',
            'phone': '0599999999'
        })
        self.assertEqual(update_res.status_code, 200)
        
        get_updated = self.client.get('/api/settings').get_json()['settings']
        self.assertEqual(get_updated['stable_name'], 'إسطبل الخيّالة الملكي')
        self.assertEqual(get_updated['manager_name'], 'المهندس عبدالرحمن')

        # Create Backup
        backup_res = self.client.post('/api/backups/create')
        self.assertEqual(backup_res.status_code, 201)
        backup_name = backup_res.get_json()['name']

        # List Backups
        backups_list = self.client.get('/api/backups').get_json()
        self.assertTrue(any(b['name'] == backup_name for b in backups_list))

        # Download Backup
        download_res = self.client.get(f'/api/backups/{backup_name}/download')
        self.assertEqual(download_res.status_code, 200)

        # Restore Backup
        restore_res = self.client.post(f'/api/backups/{backup_name}/restore')
        self.assertEqual(restore_res.status_code, 200)

        # Delete Backup
        del_backup = self.client.delete(f'/api/backups/{backup_name}')
        self.assertEqual(del_backup.status_code, 200)

    def test_csv_reports(self):
        horses_csv = self.client.get('/api/reports/horses/csv')
        self.assertEqual(horses_csv.status_code, 200)
        self.assertIn('text/csv', horses_csv.content_type)
        self.assertTrue(b'Microchip' in horses_csv.data or b'Name' in horses_csv.data)

        finance_csv = self.client.get('/api/reports/finance/csv')
        self.assertEqual(finance_csv.status_code, 200)
        self.assertIn('text/csv', finance_csv.content_type)
        self.assertTrue(b'Amount' in finance_csv.data or b'Description' in finance_csv.data)

    def test_alerts_api(self):
        alerts_res = self.client.get('/api/alerts')
        self.assertEqual(alerts_res.status_code, 200)
        alerts = alerts_res.get_json()
        self.assertIsInstance(alerts, list)

if __name__ == '__main__':
    unittest.main()
