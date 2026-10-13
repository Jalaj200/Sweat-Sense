# Sweat Sense

> **"Sensing Sweat. Exploring Health."**

Sweat Sense is a biomedical technology project and modern patient healthcare portal exploring the detection and analysis of C-reactive protein (CRP) in human sweat using a sweat-based biosensing approach.

---

## 🔬 Scientific Context & Research Focus

C-reactive protein (CRP) is a key clinical biomarker associated with systemic inflammation, cardiovascular risk, and infection monitoring. Conventional CRP testing relies primarily on invasive venipuncture. Sweat Sense explores non-invasive, sweat-based biosensing as an emerging research direction while providing patients with an integrated healthcare management platform.

> **Educational Notice:** *C-reactive protein (CRP) is a biomarker associated with inflammation. Sweat Sense explores sweat-based CRP detection as a research direction. Clinical diagnoses and medical decisions should always be guided by qualified healthcare professionals and accredited laboratory diagnostics.*

---

## 🚀 Key Portal Features

The portal provides an intuitive patient interface organized into **strictly five primary sections**:

1. **Home Dashboard (`/dashboard/`)**: Overview metrics, educational CRP biosensing card, active care summary, upcoming appointments, and quick action shortcuts.
2. **Doctor Consultation (`/consultation/`)**: Doctor directory with specialties, consulting modes (In-Person / Video Teleconsult), appointment scheduling with slot-collision prevention, and booking cancellation.
3. **Blood Collection (`/blood-collection/`)**: Diagnostic sample collection booking (Home Visit vs. Partner Center), fasting requirement acknowledgment, telephone validation, and tracking.
4. **Reports (`/reports/`)**: Diagnostic report repository with search, modality filter tabs (*CRP Biosensing*, *Blood Chemistry*, *Consultation Summary*), printable report view, and ownership-enforced downloads.
5. **History (`/history/`)**: Chronological audit timeline aggregating consultations, lab collections, and diagnostic reports with status badges.

### Security & Authentication
- Dual-identifier authentication (sign in with either username or registered email).
- PBKDF2 SHA-256 password encryption and minimum complexity validation.
- "Remember Me" session duration management (persistent 14-day cookie vs. browser session).
- Top-bar user profile dropdown with secure `POST` logout and modal account details.
- Object-level authorization preventing unauthorized cross-patient document access.

---

## 🛠️ Technology Stack

- **Backend:** Python 3.12+, Django (>=5.1, <6.1)
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5, Bootstrap Icons
- **Database:** SQLite (local development), PostgreSQL ready for production
- **Architecture:** Modular Django apps (`accounts`, `dashboard`, `consultations`, `blood_collection`, `reports`)

---

## 💻 Local Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Jalaj200/Sweat-Sense.git
cd Sweat-Sense
```

### 2. Create and Activate a Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and set your configuration:
```bash
# Optional for local development; defaults are provided in settings.py
cp .env.example .env
```

### 5. Apply Database Migrations
```bash
python manage.py migrate
```

### 6. Run the Test Suite
```bash
python manage.py test
```

### 7. Start the Development Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

---

## 📁 Project Structure

```text
Sweat-Sense/
├── accounts/             # Authentication, dual-identifier backend, forms & tests
├── blood_collection/     # Blood sample requisition models, views, and forms
├── consultations/        # Doctor profiles, consultation bookings, slot checks
├── dashboard/            # Home patient dashboard and history timeline views
├── reports/              # Medical report models, search, filters & secure streaming
├── smart_sense/          # Django project configuration (settings, routing, wsgi, asgi)
├── static/               # CSS stylesheets, JavaScript helpers, and branding assets
├── templates/            # Django HTML templates (portal_base, accounts, dashboard, etc.)
├── .env.example          # Environment variable template
├── .gitignore            # Git exclusion rules (excluding db, media, venv, secrets)
├── manage.py             # Django management CLI
├── README.md             # Project documentation
└── requirements.txt      # Project Python dependencies
```

---

## 📄 License & Disclaimer

This project is developed for educational, research, and non-commercial exploration into biosensing technology and healthcare portal design.
