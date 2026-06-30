/* ============================================
   CarCare Mechanic — Main JS
   Handles: auth, modals, payments, toast, nav
   ============================================ */

// ─── Modal Helpers ─────────────────────────────────────────────
function openModal(id) {
    document.getElementById(id).classList.add('active');
    document.body.style.overflow = 'hidden';
}
function closeModal(id) {
    document.getElementById(id).classList.remove('active');
    document.body.style.overflow = '';
}
function switchModal(closeId, openId) {
    closeModal(closeId);
    openModal(openId);
}
// Close modal on outside click
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-overlay')) {
        e.target.classList.remove('active');
        document.body.style.overflow = '';
    }
});

// ─── Toast ─────────────────────────────────────────────────────
function showToast(msg, type = '') {
    const toast = document.getElementById('toast');
    toast.textContent = msg;
    toast.className = 'toast show ' + type;
    setTimeout(() => { toast.className = 'toast'; }, 3200);
}

// ─── Mobile Menu ───────────────────────────────────────────────
function toggleMenu() {
    document.getElementById('navLinks').classList.toggle('mobile-open');
}

// ─── Auth State ────────────────────────────────────────────────
async function checkAuth() {
    const data = await fetch('/api/me').then(r => r.json());
    const navActions = document.getElementById('navActions');
    const navUser = document.getElementById('navUser');
    const dashLink = document.getElementById('dashLink');

    if (data.logged_in) {
        navActions.style.display = 'none';
        navUser.style.display = 'flex';
        dashLink.style.display = 'block';
        document.getElementById('userGreet').textContent = `Hi, ${data.name.split(' ')[0]}`;
    } else {
        navActions.style.display = 'flex';
        navUser.style.display = 'none';
        dashLink.style.display = 'none';
    }
}
checkAuth();

// ─── Login ─────────────────────────────────────────────────────
async function doLogin(e) {
    e.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPwd').value;
    const errBox = document.getElementById('loginError');
    errBox.style.display = 'none';

    const resp = await fetch('/api/login', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({email, password})
    }).then(r => r.json());

    if (resp.success) {
        closeModal('loginModal');
        showToast(`Welcome back, ${resp.name}!`, 'success');
        setTimeout(() => {
            if (resp.role === 'owner') window.location = '/dashboard';
            else window.location.reload();
        }, 600);
    } else {
        errBox.textContent = resp.message;
        errBox.style.display = 'block';
    }
}

// ─── Register ──────────────────────────────────────────────────
async function doRegister(e) {
    e.preventDefault();
    const name = document.getElementById('regName').value;
    const email = document.getElementById('regEmail').value;
    const phone = document.getElementById('regPhone').value;
    const password = document.getElementById('regPwd').value;
    const errBox = document.getElementById('regError');
    const okBox = document.getElementById('regSuccess');
    errBox.style.display = 'none';
    okBox.style.display = 'none';

    if (password.length < 6) {
        errBox.textContent = 'Password must be at least 6 characters.';
        errBox.style.display = 'block';
        return;
    }

    const resp = await fetch('/api/register', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name, email, phone, password})
    }).then(r => r.json());

    if (resp.success) {
        okBox.textContent = resp.message + ' Please login.';
        okBox.style.display = 'block';
        setTimeout(() => switchModal('registerModal', 'loginModal'), 1200);
    } else {
        errBox.textContent = resp.message;
        errBox.style.display = 'block';
    }
}

// ─── Logout ────────────────────────────────────────────────────
async function logout() {
    await fetch('/api/logout', { method: 'POST' });
    showToast('Logged out successfully');
    setTimeout(() => window.location = '/', 500);
}

// ─── Payment Modal ─────────────────────────────────────────────
let currentPaymentBookingId = null;

function openPaymentModal(bookingId, serviceName, amount) {
    currentPaymentBookingId = bookingId;
    document.getElementById('pay_service').textContent = serviceName;
    document.getElementById('pay_bid').textContent = '#' + bookingId;
    document.getElementById('pay_amount').textContent = '₹' + Number(amount).toLocaleString();
    document.getElementById('payError').style.display = 'none';
    openModal('paymentModal');
}

async function processPayment() {
    const method = document.querySelector('input[name="payMethod"]:checked').value;
    const errBox = document.getElementById('payError');
    errBox.style.display = 'none';

    const resp = await fetch('/api/pay', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ booking_id: currentPaymentBookingId, method })
    }).then(r => r.json());

    if (resp.success) {
        closeModal('paymentModal');
        showToast(`Payment successful! Txn ID: ${resp.transaction_id}`, 'success');
        setTimeout(() => {
            if (window.location.pathname.includes('dashboard')) window.location.reload();
            else window.location = '/dashboard';
        }, 1000);
    } else {
        errBox.textContent = resp.message || 'Payment failed. Please try again.';
        errBox.style.display = 'block';
    }
}

// Navbar scroll shadow
window.addEventListener('scroll', () => {
    const nav = document.getElementById('navbar');
    if (nav) nav.style.boxShadow = window.scrollY > 10 ? '0 2px 12px rgba(0,0,0,0.08)' : 'none';
});