# 💊 Pharmacy Management System

A comprehensive, professional pharmacy management system built with **Streamlit** (frontend) and **SQLite** (database). Designed for managing inventory, sales, suppliers, customers, and analytics for a modern pharmacy store.

## 🎯 Features

### 📦 Inventory Management
- Add, edit, and delete medicines
- Track stock levels in real-time
- Set reorder levels for automatic alerts
- Manage medicine categories, manufacturers, batch numbers
- Expiry date tracking

### 💳 Billing & Sales
- Point of Sale (POS) system for quick billing
- Support for cash, card, check, and online payments
- Customer selection for every transaction
- Discount and tax calculations
- Automatic stock deduction on sale

### 🏭 Supplier Management
- Maintain supplier database
- Track contact information
- Credit limit management
- Payment terms tracking

### 👥 Customer Management
- Customer profiles and history
- Loyalty points tracking
- Customer type classification (Retail, Wholesale, Institutional)
- Purchase history and reports

### 📋 Purchase Orders
- Create and track purchase orders
- Supplier order history
- Expected delivery date management
- Batch and expiry date assignment on receipt

### ⚠️ Smart Alerts
- Low stock notifications
- Expired medicine alerts
- Automatic reorder reminders

### 📊 Analytics & Reports
- Sales reports and trends
- Profit analysis
- Top-selling medicines
- Daily/weekly/monthly analytics
- Inventory value reports
- Revenue and profit tracking

### 🔐 Authentication & Authorization
- Secure user login
- Role-based access control (Admin, Staff)
- Employee management

### 📈 Dashboard
- Real-time key metrics
- Sales trends visualization
- Top-selling products
- Quick access to critical alerts
- Today's sales summary

## 📋 Requirements

- Python 3.10+
- Streamlit
- Pandas
- SQLite3 (included with Python)

## 🚀 Installation & Setup

### 1. Clone or Download the Project
```bash
cd pharmacy-management-system
```

### 2. Create Virtual Environment (Optional but Recommended)
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

## 🔑 Default Login Credentials

```
Username: admin
Password: admin123
```

**⚠️ Change these credentials on first login!**

## 📁 Project Structure

```
pharmacy-management-system/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                        # This file
├── database/
│   ├── __init__.py                 # Package initializer
│   └── db.py                       # Database models & operations
├── modules/
│   ├── __init__.py
│   ├── utils.py                    # Utility functions
│   └── (auth.py, reports.py - to be added)
└── data/
    └── pharmacy.db                 # SQLite database (auto-created)
```

## 💻 Usage Guide

### Adding Medicines
1. Navigate to "📦 Inventory"
2. Go to "Add Medicine" tab
3. Fill in all required fields
4. Click "Add Medicine"

### Creating a Sale
1. Navigate to "💳 Billing & Sales"
2. Select customer (optional)
3. Choose payment method
4. Select medicines and quantities
5. Apply discounts if needed
6. Click "Complete Sale"

### Viewing Alerts
1. Navigate to "⚠️ Stock Alerts"
2. See low stock items and expired medicines
3. Place orders for low stock items

### Generating Reports
1. Navigate to "📈 Reports & Analytics"
2. Choose report type (Sales, Profit, Stock)
3. Select date range
4. View charts and detailed data

### Managing Suppliers
1. Navigate to "🏭 Suppliers"
2. View existing suppliers or add new ones
3. Manage contact and payment information

## 🗄️ Database Schema

### Main Tables
- **users**: System users and staff
- **medicines**: Product inventory
- **suppliers**: Supplier information
- **customers**: Customer database
- **sales**: Sales transactions
- **sale_items**: Individual items in each sale
- **purchase_orders**: Orders from suppliers
- **purchase_order_items**: Items in each PO
- **stock_movements**: Inventory transaction history
- **expenses**: Business expenses
- **prescriptions**: Patient prescriptions

## 🔧 Key Features Implementation

### Real-time Inventory Tracking
- Stock automatically decremented on sale
- Stock incremented on purchase order receipt
- Movement history for audit trail

### Financial Calculations
- Automatic profit margin calculation
- Tax computation
- Discount management
- Revenue and profit analytics

### Smart Notifications
- Low stock alerts based on reorder level
- Expiry date warnings
- Dashboard summary

## 🐛 Troubleshooting

### Application won't start
- Ensure Python 3.10+ is installed
- Run `pip install -r requirements.txt` again
- Check for port 8501 availability

### Database errors
- Delete `data/pharmacy.db` to reset (will lose data!)
- Run `python -c "from database.db import init_db; init_db()"`

### Import errors
- Activate virtual environment
- Reinstall requirements: `pip install --upgrade -r requirements.txt`

## 🔐 Security Notes

1. **Change Default Credentials**: Update admin password on first login
2. **Database Backup**: Regularly backup `data/pharmacy.db`
3. **Access Control**: Implement role-based access in production
4. **Data Validation**: All inputs validated before database operations

## 📈 Future Enhancements

- [ ] Multi-user support with session management
- [ ] Advanced reporting with PDF export
- [ ] Barcode/QR code scanning
- [ ] Mobile app compatibility
- [ ] Prescription management system
- [ ] Insurance integration
- [ ] Multi-store management
- [ ] Automated backup system
- [ ] Email notifications
- [ ] API integration for suppliers

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review the code comments
3. Check Streamlit documentation: https://docs.streamlit.io

## 📄 License

This project is provided as-is for educational and commercial use.

## 👨‍💻 Developer

Pharmacy Management System - v1.0
Built with ❤️ for efficient pharmacy operations

---

**Last Updated**: April 2026
**Status**: Active Development
