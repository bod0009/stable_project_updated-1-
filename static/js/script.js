// --- State ---
let currentUser = null;
let horses = [];
let activeHorseId = null;
let activeHorseData = null;
let language = 'ar';
let dashData = null;
let financeData = null;
let currentCurrency = 'ج.م';

// --- Dictionary for Full Bilingual Support ---
const dict = {
  ar: {
    dashboard: 'لوحة المتابعة',
    horses: 'الخيول',
    dailyCare: 'الرعاية والمهام',
    finance: 'الحسابات والمالية',
    archive: 'الأرشيف',
    settings: 'الإعدادات والنسخ',
    stableManagement: 'نظام الإدارة الرقمية للإسطبل',
    mainStable: 'إسطبل الخيّالة',
    systemOn: '● النظام يعمل بكفاءة',
    welcome: 'مرحباً بك في لوحة الإدارة',
    greeting: 'صباح الخير، مدير الإسطبل',
    addTask: '+ مهمة رعاية',
    addPayment: '+ فاتورة/دفعة',
    addHorse: '+ إضافة حصان',
    addExpense: '+ تسجيل مصروف',
    activeHorses: 'الخيول النشطة',
    liveRecord: 'سجل حي ومحدّث',
    medicalDue: 'استحقاق بيطري',
    upcomingMedical: 'استحقاقات قريبة',
    feedingPlans: 'خطط التغذية',
    activeMeals: 'وجبات فعّالة',
    trainingSessions: 'جلسات التدريب',
    scheduledSessions: 'جلسات مجدولة',
    pendingReceivables: 'مستحقات معلقة',
    unpaidInvoices: 'فواتير بانتظار التحصيل',
    urgentAlerts: 'التنبيهات العاجلة',
    requiresAction: 'تحتاج متابعة فورية',
    dailyOps: 'تشغيل اليوم',
    careTasks: 'مهام الرعاية والعمليات',
    smartAlert: 'المساعد الذكي',
    healthFollowup: 'متابعة العمليات الميدانية',
    alertNotice: 'راجع التطعيمات وجلسات العلاج الطبيعي المستحقة وجداول التدريب المقررة اليوم.',
    viewAllTasks: 'عرض كل المهام',
    mainRecord: 'السجل الرئيسي',
    allHorses: 'جميع الخيول المسجلة',
    search: 'ابحث بالاسم، الميكروشيب، المالك، الإسطبل...',
    allBreeds: 'كل السلالات',
    allGenders: 'كل الجنسين',
    stallion: 'ذكر',
    mare: 'أنثى',
    allStatuses: 'كل الحالات',
    active: 'نشط',
    resting: 'راحة',
    treatment: 'علاج',
    departed: 'مغادر',
    sortName: 'ترتيب: الاسم',
    sortAge: 'ترتيب: تاريخ الميلاد',
    sortCreated: 'ترتيب: الأحدث تسجيلاً',
    horse: 'الحصان',
    owner: 'المالك',
    stall: 'الإسطبل',
    status: 'الحالة',
    actions: 'الإجراءات',
    operations: 'التشغيل الميداني',
    allTasks: 'سجل مهام الرعاية والتدريب',
    taskTitle: 'المهمة',
    category: 'النوع',
    dueDate: 'تاريخ الاستحقاق',
    priority: 'الأولوية',
    totalInvoiced: 'إجمالي الفواتير',
    allInvoices: 'المطالبات الصادرة',
    totalPaid: 'المحصل الفعلي',
    collectedRevenue: 'مدفوعات مستلمة',
    totalUnpaid: 'المعلق / المستحق',
    pendingInvoices: 'بانتظار السداد',
    totalExpenses: 'إجمالي المصروفات',
    operationalCosts: 'أعلاف، بيطري، صيانة',
    netCashFlow: 'صافي السيولة',
    netBalance: 'المحصل - المصروفات',
    revenueLedger: 'سجل الإيرادات',
    invoicesAndPayments: 'الفواتير والدفعات',
    costLedger: 'سجل التكاليف',
    expenses: 'المصروفات التشغيلية',
    description: 'البيان',
    amount: 'المبلغ',
    date: 'التاريخ',
    deletedRecords: 'الخيول المؤرشفة',
    archiveDesc: 'يمكنك استرجاع أي حصان مؤرشف في أي وقت إلى السجلات النشطة، أو حذفه نهائياً عند الرغبة.',
    preferences: 'تخصيص النظام',
    stableSettings: 'بيانات وإعدادات الإسطبل',
    stableName: 'اسم الإسطبل',
    managerName: 'اسم المدير المسؤول',
    phone: 'رقم الهاتف والتواصل',
    email: 'البريد الإلكتروني',
    address: 'العنوان والموقع',
    currency: 'العملة الافتراضية',
    alertDaysThreshold: 'تنبيه الاستحقاقات قبل (أيام)',
    saveSettings: 'حفظ التغييرات',
    database: 'حماية البيانات',
    backupManagement: 'النسخ الاحتياطي والاسترجاع',
    createBackupNow: '⚡ إنشاء نسخة الآن',
    backupNotice: 'يتم حفظ نسخ كاملة لقاعدة البيانات SQLite في مجلد backups لضمان عدم فقدان أي سجلات.',
    backupFile: 'اسم النسخة',
    fileSize: 'الحجم',
    createdDate: 'تاريخ الإنشاء',
    diagnostics: 'معلومات النظام والتقارير',
    systemStats: 'حالة قاعدة البيانات والطباعة السريعة',
    horseFile: 'الملف الشامل للحصان',
    basicInfo: '📋 البيانات الأساسية',
    pedigreeInfo: '🌳 النسب والخصائص البدنية',
    ownerInfo: '👤 بيانات المالك والإيواء',
    medicalFile: '💉 السجل الطبي والتطعيمات',
    medicationFile: '💊 الأدوية والعلاجات الفعالة',
    feedingSchedule: '🌾 خطة وملاحظات التغذية',
    trainingLog: '🏇 سجل وجلسات التدريب',
    careHistory: '📋 الرعاية والمهام المرتبطة',
    financialHistory: '💰 الفواتير والحسابات',
    auditTrail: '📝 سجل التغييرات والتدقيق',
    addPhoto: '📸 رفع صورة',
    edit: '✏️ تعديل البيانات',
    cancel: 'إلغاء',
    saveRecord: 'حفظ السجل',
    addTaskBtn: 'إضافة المهمة',
    saveInvoice: 'حفظ الفاتورة',
    saveExpense: 'تسجيل المصروف',
    viewProfile: 'عرض الملف',
    archiveHorse: 'أرشفة',
    permanentDelete: 'حذف نهائي',
    restore: 'استرجاع',
    markPaid: 'تحصيل',
    markUnpaid: 'تعليق',
    delete: 'حذف',
    download: 'تحميل',
    exportCsv: '📥 تصدير CSV',
    printPdf: '📄 طباعة تقرير PDF',
    printHorseProfile: '📄 طباعة ملف الحصان (PDF)',
    usernameLabel: 'اسم المستخدم',
    passwordLabel: 'كلمة المرور',
    loginBtnText: 'تسجيل الدخول للنظام',
    quickLoginTitle: 'أو اختر نوع الحساب للدخول السريع',
    completed: 'تم الإنجاز',
    inProgress: 'قيد التنفيذ',
    paid: 'مدفوعة',
    unpaid: 'معلقة',
    urgent: 'عاجل',
    high: 'عالي',
    medium: 'متوسط',
    noMatchingHorses: 'لا توجد خيول مطابقة للبحث.',
    archiveEmpty: 'الأرشيف فارغ حالياً.',
    noPendingTasks: 'لا توجد مهام معلّقة اليوم.',
    noPayments: 'لا توجد فواتير مسجلة.',
    noExpenses: 'لا توجد مصروفات مسجلة.',
    noBackups: 'لا توجد نسخ احتياطية مسجلة.',
    confirmArchive: 'هل أنت متأكد من نقل هذا الحصان إلى الأرشيف؟',
    confirmRestore: 'هل أنت متأكد من استرجاع هذا الحصان إلى السجلات النشطة؟',
    confirmDeleteHorsePermanent: 'تحذير: هل أنت متأكد من حذف هذا الحصان وجميع متعلقاته نهائياً؟ هذا الإجراء لا يمكن التراجع عنه.',
    confirmRestoreBackup: 'تحذير: استرجاع النسخة الاحتياطية سيستبدل البيانات الحالية ببيانات النسخة. هل تود الاستمرار؟',
    confirmDeleteBackup: 'هل أنت متأكد من حذف ملف النسخة الاحتياطية؟',
    confirmDeletePayment: 'هل أنت متأكد من حذف هذه الفاتورة؟',
    confirmDeleteExpense: 'هل أنت متأكد من حذف هذا المصروف؟',
    confirmLogout: 'هل تود تسجيل الخروج من النظام؟'
  },
  en: {
    dashboard: 'Dashboard',
    horses: 'Horses',
    dailyCare: 'Care & Tasks',
    finance: 'Finance & Accounting',
    archive: 'Archive',
    settings: 'Settings & Backups',
    stableManagement: 'Digital Stable Management System',
    mainStable: 'Alkhyala Stable',
    systemOn: '● System Online & Healthy',
    welcome: 'Welcome to Management Portal',
    greeting: 'Good Morning, Stable Manager',
    addTask: '+ Add Task',
    addPayment: '+ New Invoice',
    addHorse: '+ Add Horse',
    addExpense: '+ Log Expense',
    activeHorses: 'Active Horses',
    liveRecord: 'Live & updated record',
    medicalDue: 'Medical Due',
    upcomingMedical: 'Upcoming veterinary dates',
    feedingPlans: 'Feeding Plans',
    activeMeals: 'Active meal schedules',
    trainingSessions: 'Training Sessions',
    scheduledSessions: 'Scheduled workouts',
    pendingReceivables: 'Pending Receivables',
    unpaidInvoices: 'Awaiting payment',
    urgentAlerts: 'Urgent Alerts',
    requiresAction: 'Requires immediate review',
    dailyOps: 'Daily Operations',
    careTasks: 'Care & Operational Tasks',
    smartAlert: 'Smart Assistant',
    healthFollowup: 'Operational & Veterinary Follow-up',
    alertNotice: 'Review due vaccinations and physiotherapy sessions before they impact the workout calendar.',
    viewAllTasks: 'View All Tasks',
    mainRecord: 'Master Registry',
    allHorses: 'All Registered Horses',
    search: 'Search name, microchip, owner, stall...',
    allBreeds: 'All Breeds',
    allGenders: 'All Genders',
    stallion: 'Stallion',
    mare: 'Mare',
    allStatuses: 'All Statuses',
    active: 'Active',
    resting: 'Resting',
    treatment: 'Treatment',
    departed: 'Departed',
    sortName: 'Sort: Name',
    sortAge: 'Sort: Birth Date',
    sortCreated: 'Sort: Recently Added',
    horse: 'Horse',
    owner: 'Owner',
    stall: 'Stall',
    status: 'Status',
    actions: 'Actions',
    operations: 'Field Operations',
    allTasks: 'Care & Training Task Log',
    taskTitle: 'Task Title',
    category: 'Category',
    dueDate: 'Due Date',
    priority: 'Priority',
    totalInvoiced: 'Total Invoiced',
    allInvoices: 'Issued invoices',
    totalPaid: 'Collected Revenue',
    collectedRevenue: 'Payments received',
    totalUnpaid: 'Pending / Unpaid',
    pendingInvoices: 'Awaiting settlement',
    totalExpenses: 'Total Expenses',
    operationalCosts: 'Feed, vet, utilities',
    netCashFlow: 'Net Cash Flow',
    netBalance: 'Collected - Expenses',
    revenueLedger: 'Revenue Ledger',
    invoicesAndPayments: 'Invoices & Payments',
    costLedger: 'Cost Ledger',
    expenses: 'Operational Expenses',
    description: 'Description',
    amount: 'Amount',
    date: 'Date',
    deletedRecords: 'Archived Horses',
    archiveDesc: 'You can restore any archived horse back to active status at any time, or permanently delete it.',
    preferences: 'System Preferences',
    stableSettings: 'Stable Profile & Settings',
    stableName: 'Stable Name',
    managerName: 'Manager Name',
    phone: 'Contact Phone',
    email: 'Email Address',
    address: 'Location & Address',
    currency: 'Default Currency',
    alertDaysThreshold: 'Alert Threshold (Days)',
    saveSettings: 'Save Settings',
    database: 'Data Protection',
    backupManagement: 'Backup & Disaster Recovery',
    createBackupNow: '⚡ Create Backup Now',
    backupNotice: 'Full SQLite database snapshots are preserved in the backups folder.',
    backupFile: 'Backup File',
    fileSize: 'Size',
    createdDate: 'Created At',
    diagnostics: 'System Diagnostics & Reports',
    systemStats: 'Database Health & Quick Exports',
    horseFile: 'Comprehensive Horse Profile',
    basicInfo: '📋 Basic Information',
    pedigreeInfo: '🌳 Pedigree & Conformation',
    ownerInfo: '👤 Owner & Boarding Details',
    medicalFile: '💉 Medical & Vaccination Log',
    medicationFile: '💊 Active Medications & Prescriptions',
    feedingSchedule: '🌾 Feeding Plan & Supplements',
    trainingLog: '🏇 Training & Workout Log',
    careHistory: '📋 Associated Care Tasks',
    financialHistory: '💰 Invoices & Billing History',
    auditTrail: '📝 Audit Log & History',
    addPhoto: '📸 Upload Photo',
    edit: '✏️ Edit Profile',
    cancel: 'Cancel',
    saveRecord: 'Save Record',
    addTaskBtn: 'Add Task',
    saveInvoice: 'Save Invoice',
    saveExpense: 'Log Expense',
    viewProfile: 'View Profile',
    archiveHorse: 'Archive',
    permanentDelete: 'Delete Forever',
    restore: 'Restore',
    markPaid: 'Mark Paid',
    markUnpaid: 'Mark Pending',
    delete: 'Delete',
    download: 'Download',
    exportCsv: '📥 Export CSV',
    printPdf: '📄 Print PDF Report',
    printHorseProfile: '📄 Print Horse Profile (PDF)',
    usernameLabel: 'Username',
    passwordLabel: 'Password',
    loginBtnText: 'Sign In to Portal',
    quickLoginTitle: 'Or Quick Access by Role',
    completed: 'Completed',
    inProgress: 'In Progress',
    paid: 'Paid',
    unpaid: 'Pending',
    urgent: 'Urgent',
    high: 'High',
    medium: 'Medium',
    noMatchingHorses: 'No matching horses found.',
    archiveEmpty: 'Archive is currently empty.',
    noPendingTasks: 'No pending tasks for today.',
    noPayments: 'No invoices recorded.',
    noExpenses: 'No expenses recorded.',
    noBackups: 'No backups recorded.',
    confirmArchive: 'Are you sure you want to archive this horse?',
    confirmRestore: 'Are you sure you want to restore this horse to active records?',
    confirmDeleteHorsePermanent: 'WARNING: Are you sure you want to PERMANENTLY delete this horse and all related files? This cannot be undone.',
    confirmRestoreBackup: 'WARNING: Restoring this backup will replace current database state. Do you wish to proceed?',
    confirmDeleteBackup: 'Are you sure you want to delete this backup file?',
    confirmDeletePayment: 'Are you sure you want to delete this invoice?',
    confirmDeleteExpense: 'Are you sure you want to delete this expense record?',
    confirmLogout: 'Are you sure you want to log out?'
  }
};

// --- DOM Helpers ---
const $ = selector => document.querySelector(selector);
const $$ = selector => document.querySelectorAll(selector);

const esc = str => {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
};

const t = key => {
  if (!dict[language]) return key;
  return dict[language][key] || key;
};

const closeDialog = id => {
  const dlg = $(`#${id}`);
  if (dlg && typeof dlg.close === 'function') {
    dlg.close();
  }
};

const formatMoney = val => {
  const curr = language === 'ar' ? 'ج.م' : 'EGP';
  return new Intl.NumberFormat(language === 'ar' ? 'ar-EG' : 'en-EG', {
    maximumFractionDigits: 0
  }).format(val || 0) + ' ' + curr;
};

// --- API Client ---
async function api(url, opts = {}) {
  const res = await fetch(url, opts);
  const text = await res.text();
  let json = {};
  try {
    json = text ? JSON.parse(text) : {};
  } catch (err) {
    throw Error('استجابة غير صالحة من الخادم.');
  }
  if (!res.ok) {
    // If 401 Unauthorized, show login screen
    if (res.status === 401) {
      showLoginOverlay(true);
    }
    throw Error(json.error || `خطأ في الاتصال بالخادم (${res.status})`);
  }
  return json;
}

// --- AUTHENTICATION HANDLERS ---
function showLoginOverlay(show = true) {
  const screen = $('#loginScreen');
  if (screen) {
    screen.style.display = show ? 'flex' : 'none';
  }
}

function togglePasswordVisibility(inputFieldId) {
  const inp = $(`#${inputFieldId}`);
  if (inp) {
    inp.type = inp.type === 'password' ? 'text' : 'password';
  }
}

async function handleLogin(e) {
  if (e && typeof e.preventDefault === 'function') e.preventDefault();
  const username = $('#loginUsername').value.trim();
  const password = $('#loginPassword').value.trim();
  const errEl = $('#loginError');

  if (!username || !password) {
    if (errEl) {
      errEl.textContent = 'يرجى إدخال اسم المستخدم وكلمة المرور.';
      errEl.style.display = 'block';
    }
    return;
  }

  try {
    if (errEl) errEl.style.display = 'none';
    const res = await api('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    if (res.ok && res.user) {
      currentUser = res.user;
      showLoginOverlay(false);
      applyUserRole(currentUser);
      await load();
    }
  } catch (err) {
    if (errEl) {
      errEl.textContent = err.message;
      errEl.style.display = 'block';
    }
  }
}

async function quickLogin(username, password) {
  $('#loginUsername').value = username;
  $('#loginPassword').value = password;
  await handleLogin();
}

async function handleLogout() {
  if (confirm(t('confirmLogout'))) {
    try {
      await api('/api/auth/logout', { method: 'POST' });
    } catch (e) {
      console.warn(e);
    }
    currentUser = null;
    showLoginOverlay(true);
  }
}

function applyUserRole(user) {
  if (!user) return;
  const role = user.role; // 'مدير', 'طبيب بيطري', 'مدرب'

  // Update Sidebar Widget
  const nameEl = $('#userFullName');
  const badgeEl = $('#userRoleBadge');
  const avatarEl = $('#userAvatar');
  const greetingEl = $('#headerGreeting');

  if (nameEl) nameEl.textContent = user.full_name;

  if (role === 'مدير') {
    if (badgeEl) badgeEl.textContent = language === 'ar' ? '👑 مدير الإسطبل' : '👑 Stable Manager';
    if (avatarEl) avatarEl.textContent = '👑';
    if (greetingEl) greetingEl.textContent = language === 'ar' ? `صباح الخير، ${user.full_name}` : `Welcome, ${user.full_name}`;
    
    // Show restricted elements
    $$('.role-restricted-nav, .role-restricted-action, .role-restricted-card').forEach(el => el.style.display = '');
  } else if (role === 'طبيب بيطري') {
    if (badgeEl) badgeEl.textContent = language === 'ar' ? '🩺 طبيب بيطري' : '🩺 Veterinarian';
    if (avatarEl) avatarEl.textContent = '🩺';
    if (greetingEl) greetingEl.textContent = language === 'ar' ? `أهلاً د. ${user.full_name}` : `Welcome, Dr. ${user.full_name}`;
    
    // Hide finance and settings from navigation and UI
    $$('.role-restricted-nav, .role-restricted-action, .role-restricted-card').forEach(el => el.style.display = 'none');
    
    // If currently on #finance or #settings, redirect to #dashboard
    if (window.location.hash === '#finance' || window.location.hash === '#settings') {
      window.location.hash = '#dashboard';
    }
  } else if (role === 'مدرب') {
    if (badgeEl) badgeEl.textContent = language === 'ar' ? '🏇 مدرب الخيل' : '🏇 Head Trainer';
    if (avatarEl) avatarEl.textContent = '🏇';
    if (greetingEl) greetingEl.textContent = language === 'ar' ? `أهلاً كابتن ${user.full_name}` : `Welcome, Coach ${user.full_name}`;
    
    // Hide finance and settings from navigation and UI
    $$('.role-restricted-nav, .role-restricted-action, .role-restricted-card').forEach(el => el.style.display = 'none');
    
    if (window.location.hash === '#finance' || window.location.hash === '#settings') {
      window.location.hash = '#dashboard';
    }
  }
}

// --- Language Toggle ---
function toggleLanguage() {
  language = language === 'ar' ? 'en' : 'ar';
  const isAr = language === 'ar';
  const doc = document.documentElement;
  doc.lang = language;
  doc.dir = isAr ? 'rtl' : 'ltr';

  const langBtn = $('.btn-lang');
  if (langBtn) langBtn.textContent = isAr ? 'English' : 'العربية';
  document.title = isAr ? 'الخيّالة — نظام إدارة الإسطبلات الرقمي | AL-Khyala' : 'Alkhyala — Digital Stable Management System';

  // Translate all data-i18n elements
  $$('[data-i18n]').forEach(el => {
    const key = el.dataset.i18n;
    const translation = dict[language][key];
    if (translation) {
      el.textContent = translation;
    }
  });

  // Translate placeholders
  $$('[data-i18n-placeholder]').forEach(el => {
    const key = el.dataset.i18nPlaceholder;
    const translation = dict[language][key];
    if (translation) el.placeholder = translation;
  });

  if (currentUser) applyUserRole(currentUser);
  renderAll();
}

// --- Render Dashboard ---
function renderDashboard(data) {
  if (!data || !data.summary) return;
  const s = data.summary;
  currentCurrency = 'ج.م';
  
  if ($('#horsesCount')) $('#horsesCount').textContent = s.horses;
  if ($('#medicalCount')) $('#medicalCount').textContent = s.medical_due;
  if ($('#feedingCount')) $('#feedingCount').textContent = s.feeding;
  if ($('#trainingCount')) $('#trainingCount').textContent = s.training;
  if ($('#unpaidCount')) $('#unpaidCount').textContent = formatMoney(s.unpaid);
  if ($('#alertsCount')) $('#alertsCount').textContent = s.alerts;

  const todayStr = new Intl.DateTimeFormat(language === 'ar' ? 'ar-EG' : 'en-EG', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
  }).format(new Date());

  if ($('#today')) $('#today').textContent = todayStr;
  if ($('#printDate')) $('#printDate').textContent = todayStr;
  if ($('#printCurrency')) $('#printCurrency').textContent = language === 'ar' ? 'الجنيه المصري (ج.م)' : 'Egyptian Pound (EGP)';

  // Dashboard task list
  const listEl = $('#taskList');
  if (listEl) {
    if (data.tasks && data.tasks.length) {
      listEl.innerHTML = data.tasks.map(k => `
        <div class="task">
          <span class="dot ${esc(k.priority)}"></span>
          <div>
            <b>${esc(k.title)}</b>
            <small>${esc(k.horse_name)} · ${esc(k.due_date)} · ${esc(k.category)}</small>
          </div>
          <button type="button" onclick="completeTask(${k.id})">${t('completed')}</button>
        </div>
      `).join('');
    } else {
      listEl.innerHTML = `<p style="color:var(--muted);padding:10px 0;">${t('noPendingTasks')}</p>`;
    }
  }

  // Urgent Alert Box
  const u = s.urgent_care || 0;
  const alertBox = $('#urgentAlert');
  if (alertBox) {
    alertBox.textContent = u > 0
      ? `🔴 ${u} ${language === 'ar' ? 'مهمة رعاية عاجلة بانتظار الإنجاز' : 'urgent care task(s) awaiting completion'}`
      : `🟢 ${language === 'ar' ? 'جميع المهام العاجلة تحت السيطرة' : 'All urgent care tasks under control'}`;
  }
}

// --- Render Horses & Archive ---
function renderHorses(items = horses) {
  const active = items.filter(h => h.status !== 'مؤرشف');
  const archived = items.filter(h => h.status === 'مؤرشف');
  const isAdmin = currentUser ? (currentUser.role === 'مدير') : true;

  // Active Horses
  const horseList = $('#horseList');
  if (horseList) {
    if (active.length) {
      horseList.innerHTML = active.map(h => `
        <tr>
          <td>
            <span class="horse-name">${esc(h.name)}</span>
            <span class="sub">${esc(h.breed || '—')} · ${esc(h.microchip)}</span>
          </td>
          <td>
            ${esc(h.owner_name || '—')}
            <span class="sub">${esc(h.owner_phone || '')}</span>
          </td>
          <td><b>${esc(h.stall || '—')}</b></td>
          <td><span class="status ${esc(h.status)}">${t(h.status) || esc(h.status)}</span></td>
          <td class="no-print" style="text-align:left;">
            <div style="display:flex;gap:8px;justify-content:flex-end;">
              <button type="button" class="btn-sec" style="padding:6px 12px;font-size:12px;" onclick="showHistory(${h.id})">${t('viewProfile')}</button>
              <button type="button" class="btn-sec" style="padding:6px 12px;font-size:12px;color:var(--warning);" onclick="archiveHorse(${h.id})">${t('archiveHorse')}</button>
              ${isAdmin ? `<button type="button" class="btn-danger" style="padding:6px 12px;font-size:12px;" onclick="deleteHorsePermanent(${h.id})">${t('permanentDelete')}</button>` : ''}
            </div>
          </td>
        </tr>
      `).join('');
    } else {
      horseList.innerHTML = `<tr><td colspan="5" style="text-align:center;color:var(--muted);padding:25px;">${t('noMatchingHorses')}</td></tr>`;
    }
  }

  // Archived Horses
  const archiveList = $('#archiveList');
  if (archiveList) {
    if (archived.length) {
      archiveList.innerHTML = archived.map(h => `
        <tr>
          <td>
            <span class="horse-name" style="text-decoration:line-through;color:var(--muted);">${esc(h.name)}</span>
            <span class="sub">${esc(h.breed || '—')} · ${esc(h.microchip)}</span>
          </td>
          <td>${esc(h.owner_name || '—')}<span class="sub">${esc(h.owner_phone || '')}</span></td>
          <td>${esc(h.stall || '—')}</td>
          <td><span class="status archived">${t('deletedRecords') || 'مؤرشف'}</span></td>
          <td class="no-print" style="text-align:left;">
            <div style="display:flex;gap:8px;justify-content:flex-end;">
              <button type="button" class="btn-sec" style="padding:6px 12px;font-size:12px;" onclick="showHistory(${h.id})">${t('viewProfile')}</button>
              <button type="button" class="btn-primary" style="padding:6px 12px;font-size:12px;" onclick="restoreHorse(${h.id})">${t('restore')}</button>
              ${isAdmin ? `<button type="button" class="btn-danger" style="padding:6px 12px;font-size:12px;" onclick="deleteHorsePermanent(${h.id})">${t('permanentDelete')}</button>` : ''}
            </div>
          </td>
        </tr>
      `).join('');
    } else {
      archiveList.innerHTML = `<tr><td colspan="5" style="text-align:center;color:var(--muted);padding:25px;">${t('archiveEmpty')}</td></tr>`;
    }
  }
}

// --- Render All Tasks ---
async function renderAllTasks() {
  const tbody = $('#allTasksTableBody');
  if (!tbody) return;
  try {
    const tasks = await api('/api/tasks');
    if (tasks && tasks.length) {
      tbody.innerHTML = tasks.map(tItem => `
        <tr>
          <td><b>${esc(tItem.title)}</b></td>
          <td>${esc(tItem.horse_name)} (${esc(tItem.stall || '—')})</td>
          <td><span class="pill" style="font-size:11px;">${esc(tItem.category)}</span></td>
          <td>${esc(tItem.due_date)}</td>
          <td><span class="dot ${esc(tItem.priority)}"></span> ${t(tItem.priority) || esc(tItem.priority)}</td>
          <td>
            <span class="status ${tItem.completed ? 'paid' : 'unpaid'}">
              ${tItem.completed ? t('completed') : t('inProgress')}
            </span>
          </td>
          <td class="no-print" style="text-align:left;">
            <div style="display:flex;gap:6px;justify-content:flex-end;">
              ${!tItem.completed ? `<button type="button" class="btn-sec" style="padding:4px 10px;font-size:12px;" onclick="completeTask(${tItem.id})">${t('completed')}</button>` : ''}
              <button type="button" class="btn-danger" style="padding:4px 10px;font-size:12px;" onclick="deleteTask(${tItem.id})">${t('delete')}</button>
            </div>
          </td>
        </tr>
      `).join('');
    } else {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:var(--muted);padding:25px;">${t('noPendingTasks')}</td></tr>`;
    }
  } catch (e) {
    console.error('Error rendering all tasks:', e);
  }
}

// --- Render Finance (Admin only) ---
async function renderFinance() {
  if (currentUser && currentUser.role !== 'مدير') return;
  try {
    financeData = await api('/api/finance/summary');
    currentCurrency = 'ج.م';
    
    if ($('#finTotalInvoiced')) $('#finTotalInvoiced').textContent = formatMoney(financeData.total_invoiced);
    if ($('#finPaid')) $('#finPaid').textContent = formatMoney(financeData.paid);
    if ($('#finUnpaid')) $('#finUnpaid').textContent = formatMoney(financeData.unpaid);
    if ($('#finExpenses')) $('#finExpenses').textContent = formatMoney(financeData.expenses);
    if ($('#finNet')) $('#finNet').textContent = formatMoney(financeData.net_balance);

    // Payments table
    const pBody = $('#paymentsTableBody');
    if (pBody) {
      if (financeData.payments && financeData.payments.length) {
        pBody.innerHTML = financeData.payments.map(p => `
          <tr>
            <td><b>${esc(p.description)}</b></td>
            <td>${esc(p.horse_name || '—')}<span class="sub">${esc(p.owner_name || '')}</span></td>
            <td><b>${formatMoney(p.amount)}</b></td>
            <td>${esc(p.due_date)}</td>
            <td><span class="status ${p.paid ? 'paid' : 'unpaid'}">${p.paid ? t('paid') : t('unpaid')}</span></td>
            <td class="no-print" style="text-align:left;">
              <div style="display:flex;gap:6px;justify-content:flex-end;">
                <button type="button" class="btn-sec" style="padding:4px 8px;font-size:12px;" onclick="togglePayment(${p.id})">
                  ${p.paid ? t('markUnpaid') : t('markPaid')}
                </button>
                <button type="button" class="btn-danger" style="padding:4px 8px;font-size:12px;" onclick="deletePayment(${p.id})">
                  ${t('delete')}
                </button>
              </div>
            </td>
          </tr>
        `).join('');
      } else {
        pBody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:var(--muted);padding:20px;">${t('noPayments')}</td></tr>`;
      }
    }

    // Expenses table
    const eBody = $('#expensesTableBody');
    if (eBody) {
      if (financeData.expenses_list && financeData.expenses_list.length) {
        eBody.innerHTML = financeData.expenses_list.map(e => `
          <tr>
            <td><span class="pill" style="font-size:11px;">${esc(e.category)}</span></td>
            <td>${esc(e.description)}<span class="sub">${esc(e.vendor || '')}</span></td>
            <td><b>${formatMoney(e.amount)}</b></td>
            <td>${esc(e.expense_date)}</td>
            <td class="no-print" style="text-align:left;">
              <button type="button" class="btn-danger" style="padding:4px 8px;font-size:12px;" onclick="deleteExpense(${e.id})">${t('delete')}</button>
            </td>
          </tr>
        `).join('');
      } else {
        eBody.innerHTML = `<tr><td colspan="5" style="text-align:center;color:var(--muted);padding:20px;">${t('noExpenses')}</td></tr>`;
      }
    }
  } catch (err) {
    console.error('Error rendering finance:', err);
  }
}

// --- Render Settings (Admin only) ---
async function renderSettings() {
  if (currentUser && currentUser.role !== 'مدير') return;
  try {
    const data = await api('/api/settings');
    const s = data.settings || {};
    if (s.stable_name && $('#setStableName')) $('#setStableName').value = s.stable_name;
    if (s.manager_name && $('#setManagerName')) $('#setManagerName').value = s.manager_name;
    if (s.phone && $('#setPhone')) $('#setPhone').value = s.phone;
    if (s.email && $('#setEmail')) $('#setEmail').value = s.email;
    if (s.address && $('#setAddress')) $('#setAddress').value = s.address;
    
    currentCurrency = 'ج.م';
    if ($('#setCurrency')) $('#setCurrency').value = 'ج.م';
    if ($('#printCurrency')) $('#printCurrency').textContent = language === 'ar' ? 'الجنيه المصري (ج.م)' : 'Egyptian Pound (EGP)';

    if (s.alert_days && $('#setAlertDays')) $('#setAlertDays').value = s.alert_days;

    if (s.stable_name) {
      if ($('#sidebarStableName')) $('#sidebarStableName').textContent = s.stable_name;
      if ($('#printStableName')) $('#printStableName').textContent = s.stable_name;
    }

    // Stats
    if (data.stats) {
      if ($('#dbSizeKb')) $('#dbSizeKb').textContent = `${data.stats.db_size_kb} KB`;
      if ($('#dbHorsesCount')) $('#dbHorsesCount').textContent = data.stats.total_horses;
      if ($('#dbTasksCount')) $('#dbTasksCount').textContent = data.stats.total_tasks;
      if ($('#dbMedicalCount')) $('#dbMedicalCount').textContent = data.stats.total_records;
      if ($('#dbAuditCount')) $('#dbAuditCount').textContent = data.stats.total_audit_logs;
    }

    // Backups list
    const backups = await api('/api/backups');
    const bBody = $('#backupsTableBody');
    if (bBody) {
      if (backups && backups.length) {
        bBody.innerHTML = backups.map(b => `
          <tr>
            <td><b>${esc(b.name)}</b></td>
            <td>${b.size_kb} KB</td>
            <td>${esc(b.created_at)}</td>
            <td class="no-print" style="text-align:left;">
              <div style="display:flex;gap:6px;justify-content:flex-end;">
                <a href="/api/backups/${encodeURIComponent(b.name)}/download" class="btn-sec" style="padding:4px 8px;font-size:12px;">${t('download')}</a>
                <button type="button" class="btn-sec" style="padding:4px 8px;font-size:12px;color:var(--green);" onclick="restoreBackup('${b.name}')">${t('restore')}</button>
                <button type="button" class="btn-danger" style="padding:4px 8px;font-size:12px;" onclick="deleteBackup('${b.name}')">${t('delete')}</button>
              </div>
            </td>
          </tr>
        `).join('');
      } else {
        bBody.innerHTML = `<tr><td colspan="4" style="text-align:center;color:var(--muted);padding:20px;">${t('noBackups')}</td></tr>`;
      }
    }
  } catch (err) {
    console.error('Error rendering settings:', err);
  }
}

// --- Fill Horse Dropdowns ---
function fillHorseSelects() {
  const active = horses.filter(h => h.status !== 'مؤرشف');
  
  const taskSel = $('#taskHorse');
  if (taskSel) {
    taskSel.innerHTML = `<option value="">${language === 'ar' ? 'اختر الحصان' : 'Select Horse'}*</option>` +
      active.map(h => `<option value="${h.id}">${esc(h.name)} — (${esc(h.stall || 'A-01')})</option>`).join('');
  }

  const paySel = $('#paymentHorse');
  if (paySel) {
    paySel.innerHTML = `<option value="">${language === 'ar' ? 'عام / غير مخصص' : 'General / Unassigned'}</option>` +
      active.map(h => `<option value="${h.id}">${esc(h.name)} — ${esc(h.owner_name || '')}</option>`).join('');
  }

  const breeds = [...new Set(horses.map(h => h.breed).filter(Boolean))];
  const breedFilter = $('#breedFilter');
  if (breedFilter) {
    breedFilter.innerHTML = `<option value="">${t('allBreeds')}</option>` +
      breeds.map(b => `<option value="${esc(b)}">${esc(b)}</option>`).join('');
  }
}

// --- Master Load ---
async function load() {
  try {
    dashData = await api('/api/dashboard');
    if (dashData.user) {
      currentUser = dashData.user;
      applyUserRole(currentUser);
    }
    horses = await api('/api/horses');
    renderAll();
  } catch (e) {
    console.error('Load error:', e);
  }
}

function renderAll() {
  renderDashboard(dashData);
  renderHorses();
  fillHorseSelects();
  renderAllTasks();
  renderFinance();
  renderSettings();
}

// --- Search & Filters ---
async function searchHorses() {
  const q = $('#search') ? $('#search').value : '';
  const breed = $('#breedFilter') ? $('#breedFilter').value : '';
  const sex = $('#sexFilter') ? $('#sexFilter').value : '';
  const status = $('#statusFilter') ? $('#statusFilter').value : '';
  const sort = $('#sortFilter') ? $('#sortFilter').value : 'name';
  
  const url = '/api/horses?' + new URLSearchParams({ q, breed, sex, status, sort });
  try {
    const results = await api(url);
    renderHorses(results);
  } catch (e) {
    console.error('Search error:', e);
  }
}

// --- Form Tabs ---
function switchFormTab(tabId) {
  $$('.form-tabs .tab-btn').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('onclick') && btn.getAttribute('onclick').includes(tabId));
  });
  $$('.tab-content').forEach(c => {
    c.classList.toggle('active', c.id === tabId);
  });
}

// --- Open Dialogs ---
function openHorse() {
  const f = $('#horseForm');
  if (!f) return;
  f.reset();
  delete f.dataset.editId;
  if ($('#horseModalTitle')) $('#horseModalTitle').textContent = t('addHorse');
  if ($('#horseError')) $('#horseError').textContent = '';
  switchFormTab('tab-basic');
  const dlg = $('#horseDialog');
  if (dlg) dlg.showModal();
}

function openTask() {
  const f = $('#taskForm');
  if (!f) return;
  f.reset();
  if ($('#taskError')) $('#taskError').textContent = '';
  if (f.elements.due_date) f.elements.due_date.value = new Date().toISOString().slice(0, 10);
  
  // Smart category default based on user role
  if (currentUser) {
    if (currentUser.role === 'طبيب بيطري' && $('#taskCategory')) $('#taskCategory').value = 'بيطري';
    if (currentUser.role === 'مدرب' && $('#taskCategory')) $('#taskCategory').value = 'تدريب';
  }
  
  const dlg = $('#taskDialog');
  if (dlg) dlg.showModal();
}

function openPayment() {
  if (currentUser && currentUser.role !== 'مدير') {
    alert('عذراً، إدارة المالية مخصصة لمدير الإسطبل فقط.');
    return;
  }
  const f = $('#paymentForm');
  if (!f) return;
  f.reset();
  if ($('#paymentError')) $('#paymentError').textContent = '';
  if (f.elements.due_date) f.elements.due_date.value = new Date().toISOString().slice(0, 10);
  const dlg = $('#paymentDialog');
  if (dlg) dlg.showModal();
}

function openExpense() {
  if (currentUser && currentUser.role !== 'مدير') {
    alert('عذراً، تسجيل المصروفات مخصص لمدير الإسطبل فقط.');
    return;
  }
  const f = $('#expenseForm');
  if (!f) return;
  f.reset();
  if ($('#expenseError')) $('#expenseError').textContent = '';
  if (f.elements.expense_date) f.elements.expense_date.value = new Date().toISOString().slice(0, 10);
  const dlg = $('#expenseDialog');
  if (dlg) dlg.showModal();
}

// --- Horse Actions ---
async function archiveHorse(id) {
  if (confirm(t('confirmArchive'))) {
    try {
      const res = await api(`/api/horses/${id}/archive`, { method: 'POST' });
      alert(res.message || 'تمت الأرشفة بنجاح.');
      await load();
    } catch (e) {
      alert(e.message);
    }
  }
}

async function restoreHorse(id) {
  if (confirm(t('confirmRestore'))) {
    try {
      const res = await api(`/api/horses/${id}/restore`, { method: 'POST' });
      alert(res.message || 'تم الاسترجاع بنجاح.');
      await load();
    } catch (e) {
      alert(e.message);
    }
  }
}

async function deleteHorsePermanent(id) {
  if (confirm(t('confirmDeleteHorsePermanent'))) {
    try {
      const res = await api(`/api/horses/${id}/permanent`, { method: 'DELETE' });
      alert(res.message || 'تم الحذف النهائي.');
      closeDialog('horseDetails');
      await load();
    } catch (e) {
      alert(e.message);
    }
  }
}

function detailArchiveHorse() {
  if (activeHorseId) archiveHorse(activeHorseId);
}

function detailDeleteHorsePermanent() {
  if (activeHorseId) deleteHorsePermanent(activeHorseId);
}

// --- Horse Details Modal ---
async function showHistory(id) {
  activeHorseId = id;
  try {
    const d = await api(`/api/horses/${id}/history`);
    activeHorseData = d;
    const h = d.horse;
    const isManager = (currentUser && currentUser.role === 'مدير');

    if ($('#detailName')) $('#detailName').textContent = h.name;
    if ($('#detailMeta')) {
      $('#detailMeta').innerHTML = `
        <span><b>${language === 'ar' ? 'الميكروشيب:' : 'Microchip:'}</b> ${esc(h.microchip)}</span>
        <span><b>${language === 'ar' ? 'الحالة:' : 'Status:'}</b> ${t(h.status) || esc(h.status)}</span>
        <span><b>${language === 'ar' ? 'الإسطبل:' : 'Stall:'}</b> ${esc(h.stall || '—')}</span>
        ${d.photos && d.photos[0] ? `<img class="horse-photo" src="/uploads/horses/${encodeURIComponent(d.photos[0].file_name)}" alt="${esc(h.name)}">` : ''}
      `;
    }

    // Toggle delete button visibility based on role
    const delBtn = $('#detailDeleteBtn');
    if (delBtn) delBtn.style.display = isManager ? 'inline-flex' : 'none';

    // Hide/Show payments in modal based on role
    const paySec = $('#horseDetailPaymentsSection');
    if (paySec) paySec.style.display = isManager ? 'block' : 'none';

    const r = (k, v) => `<dt>${k}</dt><dd>${esc(v || '—')}</dd>`;
    
    if ($('#basicInfo')) {
      $('#basicInfo').innerHTML =
        r(language === 'ar' ? 'السلالة' : 'Breed', h.breed) +
        r(language === 'ar' ? 'الجنس' : 'Sex', t(h.sex) || h.sex) +
        r(language === 'ar' ? 'تاريخ الميلاد' : 'Birth Date', h.birth_date) +
        r(language === 'ar' ? 'اللون' : 'Colour', h.colour) +
        r(language === 'ar' ? 'ملاحظات عامة' : 'General Notes', h.notes);
    }

    if ($('#pedigreeInfo')) {
      $('#pedigreeInfo').innerHTML =
        r(language === 'ar' ? 'الطول' : 'Height', h.height_cm ? `${h.height_cm} cm` : '—') +
        r(language === 'ar' ? 'الوزن' : 'Weight', h.weight_kg ? `${h.weight_kg} kg` : '—') +
        r(language === 'ar' ? 'الأب (Sire)' : 'Sire', h.sire) +
        r(language === 'ar' ? 'الأم (Dam)' : 'Dam', h.dam) +
        r(language === 'ar' ? 'الجد (من الأب)' : 'Grand Sire', h.grand_sire) +
        r(language === 'ar' ? 'الجدة (من الأم)' : 'Grand Dam', h.grand_dam) +
        r(language === 'ar' ? 'الحساسيات' : 'Allergies', h.allergies);
    }

    if ($('#ownerInfo')) {
      $('#ownerInfo').innerHTML =
        r(language === 'ar' ? 'اسم المالك' : 'Owner Name', h.owner_name) +
        r(language === 'ar' ? 'هاتف المالك' : 'Owner Phone', h.owner_phone) +
        r(language === 'ar' ? 'موقع البوكس' : 'Stall Location', h.stall);
    }

    const renderList = (arr, fn, emptyMsg) => (arr && arr.length) ? arr.map(fn).join('') : `<div style="color:var(--muted);">${emptyMsg}</div>`;

    if ($('#medicalInfo')) {
      $('#medicalInfo').innerHTML = renderList(d.medical, x => `
        <div><b>${esc(x.record_type)}</b> - ${esc(x.record_date)}<small>${esc(x.details || '')} (د. ${esc(x.veterinarian || '—')})</small></div>
      `, language === 'ar' ? 'لا توجد سجلات طبية مسجلة.' : 'No medical records found.');
    }

    if ($('#medicationInfo')) {
      $('#medicationInfo').innerHTML = renderList(d.medications, x => `
        <div><b>${esc(x.medicine_name)}</b><small>${esc(x.dosage || '')} · من ${esc(x.start_date)} إلى ${esc(x.end_date || 'مستمر')}<br>${esc(x.reason || '')}</small></div>
      `, language === 'ar' ? 'لا توجد أدوية نشطة.' : 'No active medications.');
    }

    if ($('#feedingInfo')) {
      $('#feedingInfo').innerHTML = renderList(d.feeding, x => `
        <div><b>${esc(x.meal_time)}: ${esc(x.feed_type)}</b> (${esc(x.quantity || '')} ${esc(x.unit || '')})<small>${esc(x.supplements || '')} · ${esc(x.notes || '')}</small></div>
      `, language === 'ar' ? 'لم تسجل خطة وجبات.' : 'No feeding plan registered.') + 
      (h.feed_notes ? `<div style="margin-top:6px;background:#f0fdf4;"><b>ملاحظات التغذية:</b> ${esc(h.feed_notes)}</div>` : '');
    }

    if ($('#trainingInfo')) {
      $('#trainingInfo').innerHTML = renderList(d.training, x => `
        <div><b>${esc(x.training_type)} (${esc(x.training_level || '')})</b><small>${esc(x.session_date)} · المدرب: ${esc(x.trainer || '—')} (${esc(x.duration_minutes || '')} دقيقة)<br>${esc(x.notes || '')}</small></div>
      `, language === 'ar' ? 'لا توجد جلسات تدريب.' : 'No training sessions recorded.') +
      (h.training_notes ? `<div style="margin-top:6px;background:#f0fdf4;"><b>ملاحظات التدريب:</b> ${esc(h.training_notes)}</div>` : '');
    }

    if ($('#careInfo')) {
      $('#careInfo').innerHTML = renderList(d.tasks, x => `
        <div><b>${esc(x.title)}</b> (${esc(x.category)})<small>${esc(x.due_date)} · ${x.completed ? '✅ مكتملة' : '⏳ قيد التنفيذ'}</small></div>
      `, language === 'ar' ? 'لا توجد مهام رعاية.' : 'No care tasks.');
    }

    if ($('#paymentInfo') && isManager) {
      $('#paymentInfo').innerHTML = renderList(d.payments, x => `
        <div><b>${esc(x.description)}: ${formatMoney(x.amount)}</b><small>${esc(x.due_date)} · ${x.paid ? '✅ مدفوعة' : '⏳ معلقة'}</small></div>
      `, language === 'ar' ? 'لا توجد فواتير.' : 'No billing records.');
    }

    if ($('#auditInfo')) {
      $('#auditInfo').innerHTML = renderList(d.audit, x => `
        <div><b>${esc(x.action)}</b><small>${esc(x.details || '')} · ${esc(x.created_at)}</small></div>
      `, language === 'ar' ? 'لا توجد سجلات تدقيق.' : 'No audit entries.');
    }

    const dlg = $('#horseDetails');
    if (dlg) dlg.showModal();
  } catch (err) {
    alert(err.message);
  }
}

// --- Edit Horse ---
async function editHorse() {
  if (!activeHorseId) return;
  try {
    const d = await api(`/api/horses/${activeHorseId}/history`);
    const f = $('#horseForm');
    if (!f) return;
    f.reset();
    Object.entries(d.horse).forEach(([k, v]) => {
      if (f.elements[k]) f.elements[k].value = v || '';
    });
    f.dataset.editId = activeHorseId;
    if ($('#horseModalTitle')) {
      $('#horseModalTitle').textContent = language === 'ar' ? 'تعديل بيانات الحصان' : 'Edit Horse Profile';
    }
    closeDialog('horseDetails');
    switchFormTab('tab-basic');
    const dlg = $('#horseDialog');
    if (dlg) dlg.showModal();
  } catch (err) {
    alert(err.message);
  }
}

// --- Photo Upload ---
function openPhotoUpload() {
  if (!activeHorseId) return;
  const inp = document.createElement('input');
  inp.type = 'file';
  inp.accept = 'image/jpeg,image/png,image/webp';
  inp.onchange = async () => {
    if (!inp.files[0]) return;
    const fd = new FormData();
    fd.append('photo', inp.files[0]);
    fd.append('is_primary', '1');
    try {
      await api(`/api/horses/${activeHorseId}/photos`, { method: 'POST', body: fd });
      await showHistory(activeHorseId);
      await load();
    } catch (e) {
      alert(e.message);
    }
  };
  inp.click();
}

// --- Finance Actions (Admin Only) ---
async function togglePayment(id) {
  try {
    await api(`/api/payments/${id}/toggle`, { method: 'POST' });
    await renderFinance();
    await renderDashboard(await api('/api/dashboard'));
  } catch (e) {
    alert(e.message);
  }
}

async function deletePayment(id) {
  if (confirm(t('confirmDeletePayment'))) {
    try {
      await api(`/api/payments/${id}`, { method: 'DELETE' });
      await renderFinance();
      await renderDashboard(await api('/api/dashboard'));
    } catch (e) {
      alert(e.message);
    }
  }
}

async function deleteExpense(id) {
  if (confirm(t('confirmDeleteExpense'))) {
    try {
      await api(`/api/expenses/${id}`, { method: 'DELETE' });
      await renderFinance();
      await renderDashboard(await api('/api/dashboard'));
    } catch (e) {
      alert(e.message);
    }
  }
}

// --- Task Actions ---
async function completeTask(id) {
  try {
    await api(`/api/tasks/${id}/complete`, { method: 'POST' });
    await load();
  } catch (e) {
    alert(e.message);
  }
}

async function deleteTask(id) {
  try {
    await api(`/api/tasks/${id}`, { method: 'DELETE' });
    await load();
  } catch (e) {
    alert(e.message);
  }
}

// --- Settings Actions ---
async function saveSettings(e) {
  if (e && typeof e.preventDefault === 'function') e.preventDefault();
  const form = $('#settingsForm');
  if (!form) return;
  const data = Object.fromEntries(new FormData(form));
  try {
    const res = await api('/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    alert(res.message || 'تم حفظ الإعدادات بنجاح.');
    await load();
  } catch (err) {
    alert(err.message);
  }
}

// --- Backup Actions ---
async function createBackup() {
  try {
    const res = await api('/api/backups/create', { method: 'POST' });
    alert(res.message || 'تم إنشاء النسخة الاحتياطية بنجاح.');
    await renderSettings();
  } catch (e) {
    alert(e.message);
  }
}

async function restoreBackup(name) {
  if (confirm(t('confirmRestoreBackup'))) {
    try {
      const res = await api(`/api/backups/${encodeURIComponent(name)}/restore`, { method: 'POST' });
      alert(res.message || 'تم استرجاع قاعدة البيانات.');
      await load();
    } catch (e) {
      alert(e.message);
    }
  }
}

async function deleteBackup(name) {
  if (confirm(t('confirmDeleteBackup'))) {
    try {
      const res = await api(`/api/backups/${encodeURIComponent(name)}`, { method: 'DELETE' });
      alert(res.message || 'تم حذف النسخة.');
      await renderSettings();
    } catch (e) {
      alert(e.message);
    }
  }
}

// --- High-Fidelity PDF Printing Function for Horse Profile ---
async function printSingleHorseProfile() {
  if (!activeHorseId) return;
  try {
    const d = activeHorseData || await api(`/api/horses/${activeHorseId}/history`);
    const h = d.horse;
    const isManager = (currentUser && currentUser.role === 'مدير');
    const todayStr = new Intl.DateTimeFormat(language === 'ar' ? 'ar-EG' : 'en-EG', {
      weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
    }).format(new Date());

    const isAr = language === 'ar';
    const photoSrc = (d.photos && d.photos[0]) ? `/uploads/horses/${encodeURIComponent(d.photos[0].file_name)}` : '/static/img/logo.svg';

    const listHtml = (arr, fn, emptyText) => (arr && arr.length)
      ? arr.map(fn).join('')
      : `<div style="color:#64748b;font-style:italic;">${emptyText}</div>`;

    const dossierHtml = `
      <div class="dossier-header">
        <div class="dossier-brand">
          <img src="/static/img/logo.svg" alt="AL-Khyala">
          <div class="dossier-title">
            <h1>إسطبل الخيّالة — AL-Khyala</h1>
            <p>${isAr ? 'الملف البيطري والسجل الرسمي الشامل للخيل | الإسكندرية، مصر' : 'Official Comprehensive Equine Passport & Registry | Alexandria, Egypt'}</p>
          </div>
        </div>
        <div class="print-meta">
          <div><b>${isAr ? 'تاريخ التقرير:' : 'Date:'}</b> ${todayStr}</div>
          <div><b>${isAr ? 'رقم الوثيقة:' : 'Document ID:'}</b> #DOC-H${h.id}-${h.microchip ? String(h.microchip).slice(-4) : (h.id ? String(h.id).padStart(4, '0') : '0000')}</div>
          <div><b>${isAr ? 'العملة:' : 'Currency:'}</b> ${isAr ? 'الجنيه المصري (ج.م)' : 'EGP'}</div>
        </div>
      </div>

      <div class="dossier-hero">
        <img class="dossier-hero-photo" src="${photoSrc}" alt="${esc(h.name)}">
        <div class="dossier-hero-info">
          <div class="dossier-hero-item">
            <b>${isAr ? 'اسم الحصان' : 'Horse Name'}</b>
            <span style="font-size:14pt;color:#166534;">${esc(h.name)}</span>
          </div>
          <div class="dossier-hero-item">
            <b>${isAr ? 'رقم الميكروشيب' : 'Microchip No.'}</b>
            <span>${esc(h.microchip || '—')}</span>
          </div>
          <div class="dossier-hero-item">
            <b>${isAr ? 'الحالة الحالية' : 'Current Status'}</b>
            <span>${t(h.status) || esc(h.status)}</span>
          </div>
          <div class="dossier-hero-item">
            <b>${isAr ? 'السلالة' : 'Breed'}</b>
            <span>${esc(h.breed || '—')}</span>
          </div>
          <div class="dossier-hero-item">
            <b>${isAr ? 'الجنس' : 'Sex'}</b>
            <span>${t(h.sex) || esc(h.sex || '—')}</span>
          </div>
          <div class="dossier-hero-item">
            <b>${isAr ? 'تاريخ الميلاد' : 'Birth Date'}</b>
            <span>${esc(h.birth_date || '—')}</span>
          </div>
          <div class="dossier-hero-item">
            <b>${isAr ? 'لون الحصان' : 'Colour'}</b>
            <span>${esc(h.colour || '—')}</span>
          </div>
          <div class="dossier-hero-item">
            <b>${isAr ? 'موقع البوكس (الإسطبل)' : 'Stall'}</b>
            <span>${esc(h.stall || '—')}</span>
          </div>
          <div class="dossier-hero-item">
            <b>${isAr ? 'اسم المالك' : 'Owner'}</b>
            <span>${esc(h.owner_name || '—')} (${esc(h.owner_phone || '')})</span>
          </div>
        </div>
      </div>

      <div class="dossier-grid">
        <div class="dossier-section">
          <h3>${isAr ? '1. البيانات الأساسية والبدنية' : '1. Basic & Physical Details'}</h3>
          <dl>
            <dt>${isAr ? 'الطول' : 'Height'}:</dt><dd>${h.height_cm ? `${h.height_cm} cm` : '—'}</dd>
            <dt>${isAr ? 'الوزن' : 'Weight'}:</dt><dd>${h.weight_kg ? `${h.weight_kg} kg` : '—'}</dd>
            <dt>${isAr ? 'الحساسيات' : 'Allergies'}:</dt><dd>${esc(h.allergies || 'لا توجد')}</dd>
            <dt>${isAr ? 'ملاحظات عامة' : 'Notes'}:</dt><dd>${esc(h.notes || '—')}</dd>
          </dl>
        </div>

        <div class="dossier-section">
          <h3>${isAr ? '2. شجرة النسب والسلالة (Pedigree)' : '2. Pedigree & Ancestry'}</h3>
          <dl>
            <dt>${isAr ? 'الأب (Sire)' : 'Sire'}:</dt><dd>${esc(h.sire || '—')}</dd>
            <dt>${isAr ? 'الأم (Dam)' : 'Dam'}:</dt><dd>${esc(h.dam || '—')}</dd>
            <dt>${isAr ? 'الجد (من الأب)' : 'Grand Sire'}:</dt><dd>${esc(h.grand_sire || '—')}</dd>
            <dt>${isAr ? 'الجدة (من الأم)' : 'Grand Dam'}:</dt><dd>${esc(h.grand_dam || '—')}</dd>
          </dl>
        </div>

        <div class="dossier-section">
          <h3>${isAr ? '3. السجل الطبي واللقاحات' : '3. Medical & Vaccinations'}</h3>
          <div class="dossier-list">
            ${listHtml(d.medical, m => `
              <div class="dossier-list-item">
                <b>${esc(m.record_type)}</b> (${esc(m.record_date)}) - د. ${esc(m.veterinarian || '—')}
                <div>${esc(m.details || '')}</div>
                ${m.next_due_date ? `<small style="color:#b45309;">${isAr ? 'الاستحقاق القادم:' : 'Next Due:'} ${esc(m.next_due_date)}</small>` : ''}
              </div>
            `, isAr ? 'لا توجد سجلات طبية.' : 'No medical records.')}
          </div>
        </div>

        <div class="dossier-section">
          <h3>${isAr ? '4. العلاجات والأدوية' : '4. Active Medications'}</h3>
          <div class="dossier-list">
            ${listHtml(d.medications, med => `
              <div class="dossier-list-item">
                <b>${esc(med.medicine_name)}</b> (${esc(med.dosage || '')})
                <div>${esc(med.reason || '')} | د. ${esc(med.veterinarian || '—')}</div>
                <small>${isAr ? 'الفترة:' : 'Duration:'} ${esc(med.start_date)} ${isAr ? 'إلى' : 'to'} ${esc(med.end_date || (isAr ? 'مستمر' : 'Ongoing'))}</small>
              </div>
            `, isAr ? 'لا توجد أدوية نشطة.' : 'No active medications.')}
          </div>
        </div>

        <div class="dossier-section">
          <h3>${isAr ? '5. خطة وبرنامج التغذية' : '5. Nutrition & Feeding Plan'}</h3>
          <div class="dossier-list">
            ${listHtml(d.feeding, f => `
              <div class="dossier-list-item">
                <b>${esc(f.meal_time)}:</b> ${esc(f.feed_type)} (${esc(f.quantity || '')} ${esc(f.unit || '')})
                <small>${esc(f.supplements ? (isAr ? 'مكملات: ' : 'Supplements: ') + f.supplements : '')} ${esc(f.notes || '')}</small>
              </div>
            `, isAr ? 'لا توجد وجبات مسجلة.' : 'No feeding plan.')}
            ${h.feed_notes ? `<div style="margin-top:6px;font-size:9pt;"><b>${isAr ? 'ملاحظات التغذية:' : 'Feed Notes:'}</b> ${esc(h.feed_notes)}</div>` : ''}
          </div>
        </div>

        <div class="dossier-section">
          <h3>${isAr ? '6. سجل وجلسات التدريب' : '6. Training & Fitness'}</h3>
          <div class="dossier-list">
            ${listHtml(d.training, tr => `
              <div class="dossier-list-item">
                <b>${esc(tr.training_type)} (${esc(tr.training_level || '')})</b> - ${esc(tr.session_date)}
                <div>${isAr ? 'المدرب:' : 'Trainer:'} ${esc(tr.trainer || '—')} (${esc(tr.duration_minutes || '')} دقيقة - حالة: ${esc(tr.condition || 'جيدة')})</div>
                <small>${esc(tr.notes || '')}</small>
              </div>
            `, isAr ? 'لا توجد جلسات تدريب.' : 'No training sessions.')}
            ${h.training_notes ? `<div style="margin-top:6px;font-size:9pt;"><b>${isAr ? 'ملاحظات التدريب:' : 'Training Notes:'}</b> ${esc(h.training_notes)}</div>` : ''}
          </div>
        </div>

        <div class="dossier-section">
          <h3>${isAr ? '7. مهام الرعاية والتشغيل' : '7. Associated Care Tasks'}</h3>
          <div class="dossier-list">
            ${listHtml(d.tasks, tk => `
              <div class="dossier-list-item">
                <b>${esc(tk.title)}</b> (${esc(tk.category)}) - ${esc(tk.due_date)}
                <small>${tk.completed ? (isAr ? '✅ مكتملة' : 'Completed') : (isAr ? '⏳ بانتظار الإنجاز' : 'Pending')} (أولوية: ${esc(tk.priority)})</small>
              </div>
            `, isAr ? 'لا توجد مهام مسجلة.' : 'No care tasks.')}
          </div>
        </div>

        ${isManager ? `
        <div class="dossier-section">
          <h3>${isAr ? '8. كشف الحسابات والفواتير' : '8. Billing & Invoices'}</h3>
          <div class="dossier-list">
            ${listHtml(d.payments, p => `
              <div class="dossier-list-item">
                <b>${esc(p.description)}:</b> ${formatMoney(p.amount)}
                <small>${isAr ? 'الاستحقاق:' : 'Due:'} ${esc(p.due_date)} | ${p.paid ? (isAr ? '✅ مدفوعة' : 'Paid') : (isAr ? '⏳ معلقة' : 'Unpaid')}</small>
              </div>
            `, isAr ? 'لا توجد مطالبات مسجلة.' : 'No billing records.')}
          </div>
        </div>
        ` : ''}

        <div class="dossier-section full-width">
          <h3>${isAr ? '9. سجل العمليات والتدقيق (Audit Trail)' : '9. Audit Trail & Log'}</h3>
          <div class="dossier-list" style="grid-template-columns: repeat(2, 1fr);">
            ${listHtml(d.audit, a => `
              <div class="dossier-list-item">
                <b>${esc(a.action)}</b>: ${esc(a.details || '')}
                <small style="color:#64748b;">${esc(a.created_at)} (${isAr ? 'بواسطة:' : 'By:'} ${esc(a.actor)})</small>
              </div>
            `, isAr ? 'لا توجد عمليات مسجلة.' : 'No audit entries.')}
          </div>
        </div>
      </div>

      <div class="dossier-footer-signatures">
        <div class="signature-box">
          <div class="signature-line"></div>
          <b>${isAr ? 'توقيع الطبيب البيطري المعتمد' : 'Authorized Veterinarian'}</b>
        </div>
        <div class="signature-box">
          <div class="signature-line"></div>
          <b>${isAr ? 'توقيع مدير الإسطبل' : 'Stable Manager Signature'}</b>
        </div>
        <div class="signature-box">
          <div class="signature-line"></div>
          <b>${isAr ? 'خاتم واعتماد الإدارة' : 'Official Seal & Approval'}</b>
        </div>
      </div>
    `;

    const container = $('#horsePrintDossier');
    if (container) {
      container.innerHTML = dossierHtml;
    }

    document.body.classList.add('printing-profile');
    
    const cleanup = () => {
      document.body.classList.remove('printing-profile');
      window.removeEventListener('afterprint', cleanup);
    };
    window.addEventListener('afterprint', cleanup, { once: true });
    setTimeout(cleanup, 2500);

    setTimeout(() => {
      window.print();
    }, 150);

  } catch (err) {
    alert(err.message);
  }
}

function printHorsesRegistry() {
  document.body.classList.remove('printing-profile');
  window.location.hash = '#horses';
  setTimeout(() => {
    window.print();
  }, 150);
}

function printFinanceReport() {
  if (currentUser && currentUser.role !== 'مدير') {
    alert('عذراً، طباعة التقرير المالي مخصصة لمدير الإسطبل فقط.');
    return;
  }
  document.body.classList.remove('printing-profile');
  window.location.hash = '#finance';
  setTimeout(() => {
    window.print();
  }, 150);
}

function exportHorsesCsv() {
  window.location.href = '/api/reports/horses/csv';
}

function exportFinanceCsv() {
  if (currentUser && currentUser.role !== 'مدير') {
    alert('عذراً، تصدير الحسابات مخصص لمدير الإسطبل فقط.');
    return;
  }
  window.location.href = '/api/reports/finance/csv';
}

// --- Router and Event Initializations ---
document.addEventListener('DOMContentLoaded', async () => {
  // Check auth session
  try {
    const authRes = await api('/api/auth/me');
    if (authRes.user) {
      currentUser = authRes.user;
      showLoginOverlay(false);
      applyUserRole(currentUser);
    } else {
      showLoginOverlay(true);
    }
  } catch {
    showLoginOverlay(true);
  }

  // Hash Router
  const route = () => {
    const hash = window.location.hash || '#dashboard';
    const sections = {
      '#dashboard': '#dashboard',
      '#horses': '#horses',
      '#tasks': '#tasksSection',
      '#finance': '#finance',
      '#archive': '#archive',
      '#settings': '#settings'
    };

    // Role check for routes
    if (currentUser && currentUser.role !== 'مدير') {
      if (hash === '#finance' || hash === '#settings') {
        window.location.hash = '#dashboard';
        return;
      }
    }

    Object.entries(sections).forEach(([h, selector]) => {
      const el = $(selector);
      if (el) {
        el.style.display = (h === hash) ? 'block' : 'none';
      }
    });

    $$('aside nav a').forEach(a => {
      a.classList.toggle('active', a.getAttribute('href') === hash);
    });
  };

  window.addEventListener('hashchange', route);
  route();

  // Forms Event Listeners
  const horseForm = $('#horseForm');
  if (horseForm) {
    horseForm.addEventListener('submit', async e => {
      e.preventDefault();
      const fd = new FormData(horseForm);
      const edId = horseForm.dataset.editId;
      try {
        if (edId) {
          fd.delete('photo');
          await api(`/api/horses/${edId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(Object.fromEntries(fd))
          });
        } else {
          await api('/api/horses', { method: 'POST', body: fd });
        }
        closeDialog('horseDialog');
        await load();
      } catch (err) {
        if ($('#horseError')) $('#horseError').textContent = err.message;
      }
    });
  }

  const taskForm = $('#taskForm');
  if (taskForm) {
    taskForm.addEventListener('submit', async e => {
      e.preventDefault();
      const dt = Object.fromEntries(new FormData(taskForm));
      try {
        await api('/api/tasks', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(dt)
        });
        closeDialog('taskDialog');
        await load();
      } catch (err) {
        if ($('#taskError')) $('#taskError').textContent = err.message;
      }
    });
  }

  const paymentForm = $('#paymentForm');
  if (paymentForm) {
    paymentForm.addEventListener('submit', async e => {
      e.preventDefault();
      const dt = Object.fromEntries(new FormData(paymentForm));
      try {
        await api('/api/payments', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(dt)
        });
        closeDialog('paymentDialog');
        await load();
      } catch (err) {
        if ($('#paymentError')) $('#paymentError').textContent = err.message;
      }
    });
  }

  const expenseForm = $('#expenseForm');
  if (expenseForm) {
    expenseForm.addEventListener('submit', async e => {
      e.preventDefault();
      const dt = Object.fromEntries(new FormData(expenseForm));
      try {
        await api('/api/expenses', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(dt)
        });
        closeDialog('expenseDialog');
        await load();
      } catch (err) {
        if ($('#expenseError')) $('#expenseError').textContent = err.message;
      }
    });
  }

  // Initial Load
  load().catch(e => console.error('Bootstrap load error:', e));
});
