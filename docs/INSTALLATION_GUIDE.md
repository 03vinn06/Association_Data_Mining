# Installation Guide
## Association Rule Mining and Market Basket Analysis System

---

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Web browser (Chrome, Firefox, Edge)

---

## Step-by-Step Installation

### Step 1: Download/Clone the Project

Place the project folder on your computer (e.g., `C:\Users\YourName\Desktop\DM`)

### Step 2: Open Terminal/Command Prompt

Navigate to the project directory:
```bash
cd C:\Users\YourName\Desktop\DM
```

### Step 3: Install Required Libraries

```bash
pip install -r requirements.txt
```

This installs:
- Flask (web framework)
- Flask-SQLAlchemy (database)
- Flask-Login (authentication)
- pandas (data manipulation)
- numpy (numerical computing)
- matplotlib (charts)
- seaborn (statistical visualization)
- mlxtend (Apriori/FP-Growth algorithms)
- networkx (network graphs)
- plotly (interactive charts)
- openpyxl (Excel export)
- reportlab (PDF generation)

### Step 4: Run the Application

```bash
python run.py
```

### Step 5: Open in Browser

Navigate to: **http://127.0.0.1:5000**

### Step 6: Login

- **Username:** admin
- **Password:** admin123

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Module not found | Run `pip install -r requirements.txt` again |
| Port 5000 in use | Change port in `run.py` to 5001 |
| Database error | Delete `instance/arm_system.db` and restart |
| Chart not showing | Ensure matplotlib is installed correctly |

---

## Project Structure

```
DM/
├── run.py                  ← Start the application here
├── config.py               ← Configuration settings
├── requirements.txt        ← Python dependencies
├── app/
│   ├── __init__.py         ← App factory
│   ├── models.py           ← Database models
│   ├── routes/             ← All route handlers
│   ├── templates/          ← HTML pages
│   └── static/             ← CSS, JS, charts
├── uploads/                ← Uploaded CSV files
├── reports/                ← Generated reports
├── instance/               ← SQLite database
└── docs/                   ← Documentation
```
