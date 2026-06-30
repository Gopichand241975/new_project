# CarCare Mechanic 🔧

A full-stack car maintenance booking platform — customers book services, owners accept/reject and manage them, with built-in payments.

## Tech Stack
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Backend:** Python (Flask)
- **Database:** SQLite

## Features
- Customer registration/login
- Browse 12+ car services (maintenance, repair, cleaning, tyres, etc.)
- 3-step booking flow (car details → service & time → confirm)
- Owner dashboard: accept / reject / mark-completed bookings
- Payment flow (UPI / Card / Net Banking / Cash) with transaction IDs
- Customer dashboard to track booking status & pay
- Fully responsive, professional UI

## Setup Instructions (VS Code)

1. **Create the project folder** and paste all files in the structure shown below.

2. **Open a terminal in VS Code** inside the `carcare` folder.

3. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   ```
   Activate it:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the app:**
   ```bash
   python app.py
   ```

6. **Open your browser** at: `http://127.0.0.1:5000`

The SQLite database (`carcare.db`) is created automatically on first run, pre-loaded with 12 services and a default owner account.

## Default Owner Login
```
Email: owner@carcare.com
Password: owner123
```

## Folder Structure
```
carcare/
├── app.py
├── requirements.txt
├── carcare.db            (auto-generated)
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── services.html
│   ├── booking.html
│   ├── customer_dashboard.html
│   └── owner_dashboard.html
└── static/
    ├── css/
    │   └── main.css
    └── js/
        └── main.js
```

## How It Works
1. **Customer** registers/logs in → browses services → books a service (selects car, date/time, address) → booking status = `pending`.
2. **Owner** logs in (use the default account above) → sees the booking in the Owner Dashboard → clicks **Accept** (status → `confirmed`) or **Reject**.
3. Once confirmed, the **customer** can pay via the Pay Now button (simulated payment gateway — generates a transaction ID and marks `payment_status = paid`).
4. **Owner** marks the booking **Completed** once the service is done.

## Notes
- Passwords are hashed with SHA-256 before storage.
- This payment flow is simulated (no real gateway integration) — swap in Razorpay/Stripe by replacing the `/api/pay` route logic in `app.py`.
- To reset the database, simply delete `carcare.db` and restart the app.