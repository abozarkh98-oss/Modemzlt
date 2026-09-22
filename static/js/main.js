let currentPackages = [];
let chartInstance = null;
let activeTab = 'daily';

// --- Routing ---
function handleRoute() {
    const hash = window.location.hash || '#/store';
    document.querySelectorAll('.page-view').forEach(el => el.classList.add('hidden'));

    if (hash === '#/dashboard') {
        document.getElementById('view-dashboard').classList.remove('hidden');
        loadDashboardData();
    } else if (hash === '#/admin-dashboard') {
        document.getElementById('view-admin-dashboard').classList.remove('hidden');
        loadAdminData();
    } else if (hash === '#/login') {
        document.getElementById('view-login').classList.remove('hidden');
    } else {
        document.getElementById('view-store').classList.remove('hidden');
        loadPackages();
    }
    updateNav();
}

window.addEventListener('hashchange', handleRoute);
window.addEventListener('load', handleRoute);

function updateNav() {
    const nav = document.getElementById('nav-actions');
    fetch('/api/user/status')
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                nav.innerHTML = `
                    <a href="#/dashboard" class="bg-slate-800 hover:bg-slate-700 text-sky-400 border border-sky-500/30 px-4 py-2 rounded-xl text-sm font-medium flex items-center gap-2">
                        👤 پنل کاربری (${data.username})
                    </a>
                `;
            } else {
                nav.innerHTML = `
                    <a href="#/login" class="bg-slate-800 hover:bg-slate-700 text-sky-400 border border-sky-500/30 px-4 py-2 rounded-xl text-sm font-medium flex items-center gap-2">
                        ورود مشتریان
                    </a>
                `;
            }
        })
        .catch(() => {
            nav.innerHTML = `
                <a href="#/login" class="bg-slate-800 hover:bg-slate-700 text-sky-400 border border-sky-500/30 px-4 py-2 rounded-xl text-sm font-medium flex items-center gap-2">
                    ورود مشتریان
                </a>
            `;
        });
}

// --- Store & Packages ---
function loadPackages() {
    fetch('/api/packages')
        .then(res => res.json())
        .then(pkgs => {
            currentPackages = pkgs;
            switchTab(activeTab);
        });
}

function switchTab(category) {
    activeTab = category;
    ['daily', 'weekly', 'monthly'].forEach(cat => {
        const btn = document.getElementById(`btn-${cat}`);
        if (btn) {
            btn.className = (cat === category) ? "tab-btn active" : "tab-btn";
        }
    });

    const container = document.getElementById('packages-container');
    if (!container) return;
    container.innerHTML = '';

    const filtered = currentPackages.filter(p => p.category === category);
    filtered.forEach(pkg => {
        const card = document.createElement('div');
        card.className = "bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between relative hover:border-sky-500/50 transition duration-300 group";
        card.innerHTML = `
            <div>
                <div class="flex justify-between items-start mb-4">
                    <span class="bg-sky-500/10 text-sky-400 text-xs font-semibold px-3 py-1 rounded-full border border-sky-500/20">${pkg.tag}</span>
                    <span class="text-xs text-slate-400 font-mono">ZLT-X28</span>
                </div>
                <h3 class="text-lg font-bold text-white mb-2 group-hover:text-sky-400 transition">${pkg.name}</h3>
                <p class="text-slate-400 text-xs leading-relaxed mb-6">${pkg.desc}</p>
                
                <div class="bg-slate-950 p-4 rounded-xl border border-slate-800/80 mb-6 flex items-center justify-between">
                    <div>
                        <span class="text-xs text-slate-500 block">حجم بسته</span>
                        <span class="text-base font-bold text-emerald-400">${pkg.data_gb} گیگابایت</span>
                    </div>
                    <div class="text-left">
                        <span class="text-xs text-slate-500 block">مبلغ سرمایه‌گذاری</span>
                        <span class="text-lg font-extrabold text-white">${pkg.price_toman.toLocaleString('fa-IR')} <small class="text-xs text-slate-400">تومان</small></span>
                    </div>
                </div>
            </div>
            <button onclick="handleBuy(${pkg.id}, '${pkg.name}')" class="w-full bg-slate-800 hover:bg-sky-500 text-slate-200 hover:text-white font-medium py-3 rounded-xl transition duration-200 text-sm glow-button border border-slate-700 hover:border-sky-400">انتخاب و خرید بسته</button>
        `;
        container.appendChild(card);
    });
}

function handleBuy(pkgId, pkgName) {
    fetch('/api/buy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ package_id: pkgId })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            Swal.fire({ icon: 'success', title: 'خرید موفق', text: data.message, confirmButtonColor: '#0ea5e9' })
            .then(() => window.location.hash = '#/dashboard');
        } else {
            Swal.fire({ icon: 'warning', title: 'خطا', text: data.message, confirmButtonColor: '#0ea5e9' })
            .then(() => { if (!data.success) window.location.hash = '#/login'; });
        }
    });
}

// --- Login & Dashboard ---
function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            if (data.is_admin) {
                window.location.hash = '#/admin-dashboard';
            } else {
                window.location.hash = '#/dashboard';
            }
        } else {
            Swal.fire({ icon: 'error', title: 'خطا', text: data.message, confirmButtonColor: '#0ea5e9' });
        }
    });
}

function loadDashboardData() {
    fetch('/api/user/status')
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                document.getElementById('welcome-user').innerText = `خوش آمدید، (${data.username})`;
                document.getElementById('total-traffic').innerText = data.total + ' گیگابایت';
                document.getElementById('used-traffic').innerText = data.used + ' گیگابایت';
                document.getElementById('remain-traffic').innerText = data.remaining + ' گیگابایت';
                document.getElementById('remain-days').innerText = data.days_left + ' روز';
                document.getElementById('traffic-progress').style.width = data.percent + '%';

                const msgBox = document.getElementById('user-admin-msg');
                if (data.admin_msg) {
                    msgBox.innerText = '✉️ پیام مدیر: ' + data.admin_msg;
                    msgBox.classList.remove('hidden');
                } else {
                    msgBox.classList.add('hidden');
                }

                // سابقه خرید
                const ordersDiv = document.getElementById('user-orders-list');
                if (data.orders.length > 0) {
                    ordersDiv.innerHTML = data.orders.map(o => `
                        <div class="flex justify-between border-b border-slate-800 py-1 text-slate-300">
                            <span>${o.package_name}</span>
                            <span class="text-emerald-400 font-bold">${o.price_toman.toLocaleString('fa-IR')} تومان</span>
                        </div>
                    `).join('');
                } else {
                    ordersDiv.innerHTML = '<p class="text-slate-500 text-center">هیچ خریدی ثبت نشده است.</p>';
                }

                renderChart(data.used, data.remaining);
            } else {
                window.location.hash = '#/login';
            }
        });
}

function renderChart(used, remaining) {
    const ctx = document.getElementById('userUsageChart').getContext('2d');
    if (chartInstance) chartInstance.destroy();

    chartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['مصرف شده', 'باقی‌مانده'],
            datasets: [{
                data: [used, remaining],
                backgroundColor: ['#f59e0b', '#10b981'],
                borderWidth: 0
            }]
        },
        options: {
            cutout: '75%',
            plugins: { legend: { display: false } },
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

function logout() {
    fetch('/api/logout', { method: 'POST' })
        .then(() => {
            window.location.hash = '#/store';
            updateNav();
        });
}

// --- Admin ---
function loadAdminData() {
    fetch('/api/admin/stats')
        .then(res => res.json())
        .then(data => {
            document.getElementById('adm-stat-users').innerText = data.user_count;
            document.getElementById('adm-stat-orders').innerText = data.order_count;
            document.getElementById('adm-stat-income').innerText = data.total_revenue.toLocaleString('fa-IR');
        });

    fetch('/api/admin/users')
        .then(res => res.json())
        .then(users => {
            const table = document.getElementById('adm-table-users');
            table.innerHTML = users.map(u => `
                <tr class="border-b border-slate-950 hover:bg-slate-950/50">
                    <td class="p-3 font-bold text-white">${u.username}</td>
                    <td class="p-3">${u.total_gb} GB</td>
                    <td class="p-3 text-amber-400">${u.used_gb} GB</td>
                    <td class="p-3 text-emerald-400">${Math.max(0, u.total_gb - u.used_gb).toFixed(1)} GB</td>
                    <td class="p-3">${u.days_left} روز</td>
                    <td class="p-3 text-slate-400">${u.admin_msg || '-'}</td>
                    <td class="p-3">
                        <button onclick="editUserPrompt('${u.username}', ${u.total_gb}, ${u.used_gb}, ${u.days_left}, '${u.admin_msg || ''}')" class="text-sky-400 hover:underline">ویرایش</button>
                    </td>
                </tr>
            `).join('');
        });
}

function handleSaveUser(e) {
    e.preventDefault();
    const data = {
        username: document.getElementById('adm-username').value,
        password: document.getElementById('adm-password').value,
        total_gb: document.getElementById('adm-total').value,
        used_gb: document.getElementById('adm-used').value,
        days_left: document.getElementById('adm-days').value,
        admin_msg: document.getElementById('adm-msg').value
    };

    fetch('/api/admin/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(res => {
        Swal.fire({ icon: 'success', title: 'موفق', text: 'اطلاعات کاربر ذخیره شد.', confirmButtonColor: '#10b981' });
        loadAdminData();
    });
}

function editUserPrompt(u, total, used, days, msg) {
    document.getElementById('adm-username').value = u;
    document.getElementById('adm-total').value = total;
    document.getElementById('adm-used').value = used;
    document.getElementById('adm-days').value = days;
    document.getElementById('adm-msg').value = msg;
                                                                                                                                     }
