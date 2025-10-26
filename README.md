# 💰 Expense Tracker - Personal Finance Management System

A comprehensive command-line expense tracking application built with Python that helps you manage your finances across multiple profiles, track income and expenses, generate detailed reports, and monitor your financial health.

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Modules Overview](#modules-overview)
- [Data Storage](#data-storage)
- [Financial Health Score](#financial-health-score)
- [Security Features](#security-features)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### 👤 User Management
- **Secure Registration & Login**: Password hashing using bcrypt
- **Multi-Profile Support**: Create and manage multiple financial profiles
- **Profile Management**: Switch between profiles, create new ones, or delete existing profiles
- **Currency Support**: Each profile can have its own currency

### 💳 Transaction Management
- **Add Transactions**: Record income and expenses with detailed information
- **Edit & Delete**: Modify or remove transactions with password confirmation
- **Transaction Details**:
  - Transaction ID (auto-generated)
  - Amount
  - Category
  - Date
  - Description
  - Payment method
- **Search & Filter**: Advanced filtering by:
  - Keyword (category or description)
  - Date range
  - Amount range
  - Transaction type
  - Sorting options (date/amount, ascending/descending)

### 📊 Reports & Analytics
- **Summary Report**:
  - Total income and expenses
  - Net savings
  - Top spending category
  - Expense breakdown by category with ASCII bar charts
  
- **Monthly Report**:
  - Filter transactions by specific month and year
  - Monthly income, expenses, and net savings
  - Detailed transaction list

- **Financial Health Score**:
  - Automated calculation based on savings ratio
  - Monthly trend analysis
  - Historical comparison
  - Personalized recommendations
  - Score categories: Critical, Weak, Good, Very Good, Excellent

### 📥📤 Import/Export
- **Export Transactions**: Export profile transactions to timestamped CSV files
- **Import Transactions**: Import transactions from CSV with:
  - Format validation
  - Duplicate detection
  - Error reporting
  - Confirmation before import

### 🔄 Backup System
- **Automatic Monthly Backups**: Creates backups of users and transactions
- **Smart Backup**: Only backs up once per month
- **Backup Location**: `backups/` directory with timestamped files

## 📁 Project Structure
```
expense-tracker/
│
├── main.py                  # Application entry point
├── users.py                 # User authentication and profile management
├── transactions.py          # Transaction CRUD operations
├── reports.py              # Report generation and analytics
├── financial_health.py     # Financial health score calculation
├── import_export.py        # CSV import/export functionality
├── storage.py              # Data storage and backup management
├── utils.py                # Utility functions (hashing, formatting, UI)
│
├── data/
│   ├── users.json          # User accounts and profiles
│   └── transaction.csv     # All transactions
│
├── backups/                # Monthly backups directory
│   ├── users_YYYY-MM.json
│   └── transaction_YYYY-MM.csv
│
├── last_backup.txt         # Tracks last backup date
└── README.md              # This file
```

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Steps

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/expense-tracker.git
cd expense-tracker
```

2. **Install dependencies**:
```bash
pip install bcrypt
```

3. **Create data directory**:
```bash
mkdir data
```

4. **Run the application**:
```bash
python main.py
```

## 📖 Usage

### First Time Setup

1. **Register a new account**:
   - Select option `2` from the main menu
   - Enter username and password
   - Create your first profile with a name and currency

2. **Login**:
   - Select option `1` from the main menu
   - Enter your credentials

### Main Workflow
```
Main Menu → Login → Select/Create Profile → Home Page
```

### Home Page Options

1. **Transactions**: Add, view, edit, delete, or search transactions
2. **Reports**: View summary, monthly reports, or financial health score
3. **Import/Export**: Export transactions or import from CSV
4. **Switch Profile**: Change to a different profile
5. **Logout**: Return to main menu

## 🔧 Modules Overview

### `main.py`
- Application entry point
- Menu navigation
- Session management

### `users.py`
- User registration and authentication
- Profile CRUD operations
- Password-protected profile deletion

### `transactions.py`
- Add income/expense transactions
- Edit and delete transactions (with authentication)
- Search and filter with multiple criteria
- Transaction display and formatting

### `reports.py`
- Summary report with category breakdown
- Monthly filtering and analysis
- ASCII bar chart visualization
- Integration with financial health module

### `financial_health.py`
- Calculates financial health score (0-100)
- Based on savings ratio: (Income - Expenses) / Income
- Monthly trend analysis
- Personalized recommendations
- Score categories:
  - **Critical (0-39)**: Deficit or very low savings
  - **Weak (40-59)**: Less than 10% savings
  - **Good (60-74)**: 10-25% savings
  - **Very Good (75-89)**: 25-40% savings
  - **Excellent (90-100)**: Over 40% savings

### `import_export.py`
- Export transactions to CSV with timestamp
- Import with validation and duplicate detection
- Format checking
- User/profile filtering

### `storage.py`
- JSON storage for users and profiles
- CSV storage for transactions
- Automatic monthly backup system
- Profile transaction cleanup

### `utils.py`
- Password hashing with bcrypt
- Date validation
- Currency formatting
- UI helpers (PrintMenu, PrintMesg)

## 💾 Data Storage

### Users Data (`data/users.json`)
```json
[
  {
    "user_id": "uuid",
    "name": "username",
    "password": "hashed_password",
    "profiles": [
      {
        "profile_id": "uuid",
        "profile_name": "Personal",
        "currency": "USD"
      }
    ]
  }
]
```

### Transactions Data (`data/transaction.csv`)
```csv
transaction_id,user,profile_id,type,amount,category,date,description,payment_method
TXN1234567890,username,profile-uuid,expense,50.00,Food,2025-10-26,Grocery shopping,Credit Card
```

## 📈 Financial Health Score

The Financial Health Score is calculated based on your monthly savings ratio:

**Formula**: `Savings Ratio = (Income - Expenses) / Income`

**Scoring System**:
- **< 0%** (Deficit) → Score: 0-25 ⚠️ Critical
- **0-10%** → Score: 25-50 📉 Weak
- **10-25%** → Score: 50-75 👍 Good
- **25-40%** → Score: 75-90 💪 Very Good
- **> 40%** → Score: 90-100 ⭐ Excellent

**Features**:
- Monthly breakdown with detailed metrics
- Average score calculation
- 3-month trend analysis
- 6-month comparison for improvement tracking
- Personalized recommendations based on your score

## 🔐 Security Features

- **Password Hashing**: All passwords are hashed using bcrypt
- **Password Confirmation**: Required for sensitive operations (delete transactions, delete profiles)
- **Profile Isolation**: Users can only access their own profiles and transactions
- **Input Validation**: Comprehensive validation for all user inputs
- **Secure Password Input**: Uses `getpass` to hide password entry

## 🎨 UI Features

- **ASCII Box Drawing**: Beautiful menu and message formatting
- **Emoji Support**: Visual indicators throughout the interface
- **Color-Coded Status**: Financial health categories with emoji indicators
- **Progress Visualization**: ASCII bar charts for expense breakdown
- **Structured Output**: Clean, organized data presentation

## 🔄 Backup System

- **Automatic**: Runs on application startup
- **Monthly**: One backup per month (YYYY-MM format)
- **Includes**: Both users.json and transaction.csv
- **Location**: `backups/` directory
- **Tracking**: `last_backup.txt` prevents duplicate monthly backups

## 🛠️ Advanced Features

### Search & Filter
```
Available Filters:
- Keyword search (category/description)
- Date range (from/to)
- Amount range (min/max)
- Transaction type (income/expense)
- Sort by date or amount
- Sort order (ascending/descending)
```

### Import Validation
```
Checks:
✓ Required fields present
✓ Valid transaction type
✓ Positive amount
✓ Date format (YYYY-MM-DD)
✓ User and profile match
✓ Duplicate detection
```

## 📝 Sample Workflow
```bash
# 1. Start application
python main.py

# 2. Register (first time)
Select: 2
Username: john_doe
Password: ********
Profile name: Personal
Currency: USD

# 3. Add an expense
Home > Transactions > Add Expense
Amount: 50
Category: Food
Date: 2025-10-26
Description: Grocery shopping
Payment: Credit Card

# 4. View reports
Home > Reports > View Summary Report
# See total income, expenses, and category breakdown

# 5. Check financial health
Home > Reports > Financial Health Score
# View monthly scores and recommendations

# 6. Export data
Home > Import/Export > Export Transactions
# Creates: export_Personal_20251026_143022.csv
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Guidelines:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🐛 Known Issues

- Console encoding may vary on different systems (UTF-8 recommended)
- Large CSV imports may take time without progress indicator

## 🔮 Future Enhancements

- [ ] Budget planning and alerts
- [ ] Recurring transactions
- [ ] Data visualization with charts
- [ ] Mobile app integration
- [ ] Cloud backup support
- [ ] Multi-currency conversion
- [ ] Receipt attachment support
- [ ] Advanced analytics and predictions

## 📧 Contact

For questions or suggestions, please open an issue on GitHub.

---

**Made with ❤️ for better financial management**
