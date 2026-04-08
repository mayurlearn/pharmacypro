import sqlite3
from datetime import datetime
import pandas as pd
from pathlib import Path
import hashlib

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "pharmacy.db"

def get_db_connection():
    """Get database connection"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT UNIQUE,
        role TEXT DEFAULT 'staff',
        active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Medicines table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS medicines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        sku TEXT UNIQUE,
        category TEXT,
        description TEXT,
        manufacturer TEXT,
        purchase_price REAL NOT NULL,
        selling_price REAL NOT NULL,
        quantity INTEGER DEFAULT 0,
        reorder_level INTEGER DEFAULT 10,
        expiry_date DATE,
        batch_number TEXT,
        active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Suppliers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        contact_person TEXT,
        phone TEXT,
        email TEXT,
        address TEXT,
        city TEXT,
        state TEXT,
        postal_code TEXT,
        credit_limit REAL DEFAULT 0,
        payment_terms TEXT,
        active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Purchase Orders table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS purchase_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        po_number TEXT UNIQUE NOT NULL,
        supplier_id INTEGER NOT NULL,
        order_date DATE DEFAULT CURRENT_DATE,
        expected_delivery_date DATE,
        actual_delivery_date DATE,
        status TEXT DEFAULT 'pending',
        total_amount REAL DEFAULT 0,
        notes TEXT,
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
        FOREIGN KEY (created_by) REFERENCES users(id)
    )
    ''')
    
    # Purchase Order Items table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS purchase_order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        po_id INTEGER NOT NULL,
        medicine_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        batch_number TEXT,
        expiry_date DATE,
        total_price REAL DEFAULT 0,
        received_qty INTEGER DEFAULT 0,
        FOREIGN KEY (po_id) REFERENCES purchase_orders(id),
        FOREIGN KEY (medicine_id) REFERENCES medicines(id)
    )
    ''')
    
    # Customers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        address TEXT,
        city TEXT,
        state TEXT,
        postal_code TEXT,
        customer_type TEXT DEFAULT 'retail',
        loyalty_points INTEGER DEFAULT 0,
        total_purchases REAL DEFAULT 0,
        active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Sales table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bill_number TEXT UNIQUE NOT NULL,
        customer_id INTEGER,
        sale_date DATE DEFAULT CURRENT_DATE,
        sale_time TIME DEFAULT CURRENT_TIME,
        subtotal REAL DEFAULT 0,
        discount REAL DEFAULT 0,
        tax REAL DEFAULT 0,
        total_amount REAL NOT NULL,
        payment_method TEXT,
        status TEXT DEFAULT 'completed',
        notes TEXT,
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(id),
        FOREIGN KEY (created_by) REFERENCES users(id)
    )
    ''')
    
    # Sale Items table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sale_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_id INTEGER NOT NULL,
        medicine_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        discount REAL DEFAULT 0,
        total_price REAL DEFAULT 0,
        FOREIGN KEY (sale_id) REFERENCES sales(id),
        FOREIGN KEY (medicine_id) REFERENCES medicines(id)
    )
    ''')
    
    # Stock Movements table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stock_movements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        medicine_id INTEGER NOT NULL,
        movement_type TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        reference_id INTEGER,
        reference_type TEXT,
        notes TEXT,
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (medicine_id) REFERENCES medicines(id),
        FOREIGN KEY (created_by) REFERENCES users(id)
    )
    ''')
    
    # Expenses table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        expense_type TEXT NOT NULL,
        amount REAL NOT NULL,
        description TEXT,
        date DATE DEFAULT CURRENT_DATE,
        category TEXT,
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (created_by) REFERENCES users(id)
    )
    ''')
    
    # Prescriptions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS prescriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT NOT NULL,
        doctor_name TEXT,
        prescription_date DATE DEFAULT CURRENT_DATE,
        prescription_details TEXT,
        medicines_needed TEXT,
        status TEXT DEFAULT 'pending',
        filled_on DATE,
        filled_by INTEGER,
        customer_id INTEGER,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(id),
        FOREIGN KEY (filled_by) REFERENCES users(id)
    )
    ''')

    # Audit logs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        actor_user_id INTEGER,
        action TEXT NOT NULL,
        target_user_id INTEGER,
        details TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (actor_user_id) REFERENCES users(id),
        FOREIGN KEY (target_user_id) REFERENCES users(id)
    )
    ''')
    
    conn.commit()
    conn.close()
    
    # Insert default admin user if not exists
    admin_password_hash = hashlib.sha256("admin123".encode()).hexdigest()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)",
                       ('admin', admin_password_hash, 'admin@pharmacy.com', 'admin'))
        conn.commit()
    except sqlite3.IntegrityError:
        cursor.execute(
            "UPDATE users SET password = ? WHERE username = ? AND password = ?",
            (admin_password_hash, 'admin', 'admin123')
        )
        conn.commit()
    finally:
        conn.close()

# ============= EMPLOYEE / USER OPERATIONS =============

def log_audit_event(action, actor_user_id=None, target_user_id=None, details=None):
    """Write an audit log event."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO audit_logs (actor_user_id, action, target_user_id, details) VALUES (?, ?, ?, ?)",
        (actor_user_id, action, target_user_id, details)
    )
    conn.commit()
    conn.close()


def get_employee_audit_logs(limit=200):
    """Get recent audit events related to employee/user management."""
    conn = get_db_connection()
    query = """
    SELECT
        al.id,
        al.action,
        al.details,
        al.created_at,
        actor.username AS actor_username,
        target.username AS target_username
    FROM audit_logs al
    LEFT JOIN users actor ON al.actor_user_id = actor.id
    LEFT JOIN users target ON al.target_user_id = target.id
    WHERE al.action LIKE 'EMPLOYEE_%'
    ORDER BY al.created_at DESC, al.id DESC
    LIMIT ?
    """
    logs = pd.read_sql_query(query, conn, params=(limit,))
    conn.close()
    return logs

def create_employee(username, password, email=None, role='staff', actor_user_id=None):
    """Create a new employee login user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    try:
        cursor.execute(
            "INSERT INTO users (username, password, email, role, active) VALUES (?, ?, ?, ?, 1)",
            (username.strip(), password_hash, email.strip() if email else None, role)
        )
        new_user_id = cursor.lastrowid
        conn.commit()
        log_audit_event(
            action="EMPLOYEE_CREATE",
            actor_user_id=actor_user_id,
            target_user_id=new_user_id,
            details=f"Created user '{username.strip()}' with role '{role}'"
        )
        return True, "Employee login created successfully"
    except sqlite3.IntegrityError as error:
        return False, f"Unable to create employee: {error}"
    finally:
        conn.close()


def get_all_employees(include_admin=True):
    """Get all employee users."""
    conn = get_db_connection()
    if include_admin:
        query = """
        SELECT id, username, email, role, active, created_at, updated_at
        FROM users
        ORDER BY created_at DESC
        """
        employees = pd.read_sql_query(query, conn)
    else:
        query = """
        SELECT id, username, email, role, active, created_at, updated_at
        FROM users
        WHERE role != 'admin'
        ORDER BY created_at DESC
        """
        employees = pd.read_sql_query(query, conn)
    conn.close()
    return employees


def set_employee_active(user_id, is_active, actor_user_id=None):
    """Activate or deactivate an employee user."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT username, role FROM users WHERE id = ?", (user_id,))
    employee = cursor.fetchone()
    if not employee:
        conn.close()
        return False, "Employee not found"

    if employee['role'] == 'admin' and not is_active:
        conn.close()
        return False, "Admin account cannot be deactivated"

    cursor.execute(
        "UPDATE users SET active = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (1 if is_active else 0, user_id)
    )
    conn.commit()
    conn.close()

    log_audit_event(
        action="EMPLOYEE_ACTIVATE" if is_active else "EMPLOYEE_DEACTIVATE",
        actor_user_id=actor_user_id,
        target_user_id=user_id,
        details=f"Set active={1 if is_active else 0} for user '{employee['username']}'"
    )
    return True, "Employee status updated"


def update_employee_role(user_id, role, actor_user_id=None):
    """Update employee role."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT username, role FROM users WHERE id = ?", (user_id,))
    employee = cursor.fetchone()
    if not employee:
        conn.close()
        return False, "Employee not found"

    cursor.execute(
        "UPDATE users SET role = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (role, user_id)
    )
    conn.commit()
    conn.close()

    log_audit_event(
        action="EMPLOYEE_ROLE_UPDATE",
        actor_user_id=actor_user_id,
        target_user_id=user_id,
        details=f"Role changed from '{employee['role']}' to '{role}' for user '{employee['username']}'"
    )
    return True, "Employee role updated"


def reset_employee_password(user_id, new_password, actor_user_id=None):
    """Reset employee password."""
    conn = get_db_connection()
    cursor = conn.cursor()
    password_hash = hashlib.sha256(new_password.encode()).hexdigest()

    cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    employee = cursor.fetchone()
    if not employee:
        conn.close()
        return False, "Employee not found"

    cursor.execute(
        "UPDATE users SET password = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (password_hash, user_id)
    )
    conn.commit()
    conn.close()

    log_audit_event(
        action="EMPLOYEE_PASSWORD_RESET",
        actor_user_id=actor_user_id,
        target_user_id=user_id,
        details=f"Password reset for user '{employee['username']}'"
    )
    return True, "Employee password reset successfully"


def delete_employee_permanently(user_id, actor_user_id=None):
    """Permanently delete employee only when safe."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT username, role FROM users WHERE id = ?", (user_id,))
    employee = cursor.fetchone()
    if not employee:
        conn.close()
        return False, "Employee not found"

    if employee['role'] == 'admin':
        conn.close()
        return False, "Admin account cannot be deleted"

    dependency_checks = [
        ("sales", "created_by"),
        ("purchase_orders", "created_by"),
        ("stock_movements", "created_by"),
        ("expenses", "created_by"),
        ("prescriptions", "filled_by"),
    ]

    total_links = 0
    for table_name, column_name in dependency_checks:
        cursor.execute(f"SELECT COUNT(*) as count FROM {table_name} WHERE {column_name} = ?", (user_id,))
        row = cursor.fetchone()
        total_links += row['count'] if row else 0

    if total_links > 0:
        conn.close()
        return False, "Cannot delete employee with existing activity. Deactivate instead."

    deleted_username = employee['username']
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

    log_audit_event(
        action="EMPLOYEE_DELETE",
        actor_user_id=actor_user_id,
        target_user_id=user_id,
        details=f"Deleted user '{deleted_username}' permanently"
    )
    return True, "Employee deleted permanently"

# ============= MEDICINE OPERATIONS =============

def add_medicine(name, sku, category, description, manufacturer, purchase_price, 
                 selling_price, reorder_level, expiry_date=None, batch_number=None):
    """Add a new medicine"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO medicines (name, sku, category, description, manufacturer, 
                             purchase_price, selling_price, reorder_level, 
                             expiry_date, batch_number)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, sku, category, description, manufacturer, purchase_price, 
              selling_price, reorder_level, expiry_date, batch_number))
        conn.commit()
        return True, "Medicine added successfully"
    except sqlite3.IntegrityError as e:
        return False, f"Error: {str(e)}"
    finally:
        conn.close()

def get_all_medicines():
    """Get all medicines"""
    conn = get_db_connection()
    query = "SELECT * FROM medicines WHERE active = 1 ORDER BY name"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_medicine_by_id(medicine_id):
    """Get medicine details by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM medicines WHERE id = ? AND active = 1", (medicine_id,))
    medicine = cursor.fetchone()
    conn.close()
    return medicine

def update_medicine(medicine_id, name=None, category=None, description=None, 
                   manufacturer=None, purchase_price=None, selling_price=None, 
                   reorder_level=None, expiry_date=None):
    """Update medicine details"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    fields = []
    values = []
    
    if name is not None:
        fields.append("name = ?")
        values.append(name)
    if category is not None:
        fields.append("category = ?")
        values.append(category)
    if description is not None:
        fields.append("description = ?")
        values.append(description)
    if manufacturer is not None:
        fields.append("manufacturer = ?")
        values.append(manufacturer)
    if purchase_price is not None:
        fields.append("purchase_price = ?")
        values.append(purchase_price)
    if selling_price is not None:
        fields.append("selling_price = ?")
        values.append(selling_price)
    if reorder_level is not None:
        fields.append("reorder_level = ?")
        values.append(reorder_level)
    if expiry_date is not None:
        fields.append("expiry_date = ?")
        values.append(expiry_date)
    
    values.append(medicine_id)
    
    if fields:
        fields.append("updated_at = CURRENT_TIMESTAMP")
        query = f"UPDATE medicines SET {', '.join(fields)} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
    
    conn.close()

def delete_medicine(medicine_id):
    """Soft delete a medicine"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE medicines SET active = 0 WHERE id = ?", (medicine_id,))
    conn.commit()
    conn.close()

def get_low_stock_medicines():
    """Get medicines with stock below reorder level"""
    conn = get_db_connection()
    query = "SELECT * FROM medicines WHERE quantity < reorder_level AND active = 1 ORDER BY quantity"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_expired_medicines():
    """Get expired medicines"""
    conn = get_db_connection()
    query = "SELECT * FROM medicines WHERE expiry_date < DATE('now') AND active = 1"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def update_medicine_quantity(medicine_id, quantity_change):
    """Update medicine quantity"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE medicines SET quantity = quantity + ? WHERE id = ?",
        (quantity_change, medicine_id)
    )
    conn.commit()
    conn.close()

# ============= SUPPLIER OPERATIONS =============

def add_supplier(name, contact_person, phone, email, address, city, state, postal_code, 
                 credit_limit, payment_terms):
    """Add a new supplier"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO suppliers (name, contact_person, phone, email, address, 
                             city, state, postal_code, credit_limit, payment_terms)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, contact_person, phone, email, address, city, state, postal_code, 
              credit_limit, payment_terms))
        conn.commit()
        return True, "Supplier added successfully"
    except sqlite3.IntegrityError:
        return False, "Supplier already exists"
    finally:
        conn.close()

def get_all_suppliers():
    """Get all suppliers"""
    conn = get_db_connection()
    query = "SELECT * FROM suppliers WHERE active = 1 ORDER BY name"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_supplier_by_id(supplier_id):
    """Get supplier by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM suppliers WHERE id = ? AND active = 1", (supplier_id,))
    supplier = cursor.fetchone()
    conn.close()
    return supplier

# ============= CUSTOMER OPERATIONS =============

def add_customer(name, phone, email, address, city, state, postal_code, customer_type):
    """Add a new customer"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO customers (name, phone, email, address, city, state, postal_code, customer_type)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, phone, email, address, city, state, postal_code, customer_type))
    conn.commit()
    customer_id = cursor.lastrowid
    conn.close()
    return customer_id

def get_all_customers():
    """Get all customers"""
    conn = get_db_connection()
    query = "SELECT * FROM customers WHERE active = 1 ORDER BY name"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# ============= SALES OPERATIONS =============

def create_sale(customer_id, sale_items, discount, tax, payment_method, created_by, notes=None):
    """Create a new sale"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Generate bill number
    bill_number = f"BILL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Calculate totals
    subtotal = sum(item['quantity'] * item['unit_price'] for item in sale_items)
    total_amount = subtotal - discount + tax
    
    try:
        cursor.execute('''
        INSERT INTO sales (bill_number, customer_id, subtotal, discount, tax, 
                          total_amount, payment_method, created_by, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (bill_number, customer_id, subtotal, discount, tax, total_amount, 
              payment_method, created_by, notes))
        
        sale_id = cursor.lastrowid
        
        # Add sale items
        for item in sale_items:
            cursor.execute('''
            INSERT INTO sale_items (sale_id, medicine_id, quantity, unit_price, total_price)
            VALUES (?, ?, ?, ?, ?)
            ''', (sale_id, item['medicine_id'], item['quantity'], item['unit_price'], 
                  item['quantity'] * item['unit_price']))
            
            # Update medicine quantity
            cursor.execute(
                "UPDATE medicines SET quantity = quantity - ? WHERE id = ?",
                (item['quantity'], item['medicine_id'])
            )
            
            # Log stock movement
            cursor.execute('''
            INSERT INTO stock_movements (medicine_id, movement_type, quantity, 
                                        reference_id, reference_type, created_by)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (item['medicine_id'], 'SALE', -item['quantity'], sale_id, 'SALE', created_by))
        
        conn.commit()
        return True, bill_number, total_amount
    except Exception as e:
        conn.rollback()
        return False, str(e), 0
    finally:
        conn.close()

def get_all_sales(limit=100):
    """Get all sales"""
    conn = get_db_connection()
    query = "SELECT * FROM sales ORDER BY created_at DESC LIMIT ?"
    df = pd.read_sql_query(query, conn, params=(limit,))
    conn.close()
    return df

def get_sale_items(sale_id):
    """Get items for a specific sale"""
    conn = get_db_connection()
    query = '''
    SELECT si.*, m.name as medicine_name FROM sale_items si
    JOIN medicines m ON si.medicine_id = m.id
    WHERE si.sale_id = ?
    '''
    df = pd.read_sql_query(query, conn, params=(sale_id,))
    conn.close()
    return df

# ============= PURCHASE ORDER OPERATIONS =============

def create_purchase_order(supplier_id, order_items, expected_delivery_date, created_by, notes=None):
    """Create a purchase order"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    po_number = f"PO-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    total_amount = sum(item['quantity'] * item['unit_price'] for item in order_items)
    
    try:
        cursor.execute('''
        INSERT INTO purchase_orders (po_number, supplier_id, expected_delivery_date, 
                                    total_amount, created_by, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (po_number, supplier_id, expected_delivery_date, total_amount, created_by, notes))
        
        po_id = cursor.lastrowid
        
        for item in order_items:
            cursor.execute('''
            INSERT INTO purchase_order_items (po_id, medicine_id, quantity, unit_price, 
                                            batch_number, expiry_date, total_price)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (po_id, item['medicine_id'], item['quantity'], item['unit_price'],
                  item.get('batch_number'), item.get('expiry_date'), 
                  item['quantity'] * item['unit_price']))
        
        conn.commit()
        return True, po_number
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def receive_purchase_order_item(po_item_id, received_qty, medicine_id):
    """Receive items from purchase order"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Update received quantity
        cursor.execute(
            "UPDATE purchase_order_items SET received_qty = ? WHERE id = ?",
            (received_qty, po_item_id)
        )
        
        # Update medicine quantity
        cursor.execute(
            "UPDATE medicines SET quantity = quantity + ? WHERE id = ?",
            (received_qty, medicine_id)
        )
        
        conn.commit()
        return True, "Stock received successfully"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

# ============= ANALYTICS OPERATIONS =============

def get_sales_summary(days=30):
    """Get sales summary for last N days"""
    conn = get_db_connection()
    query = f'''
    SELECT 
        DATE(sale_date) as date,
        COUNT(*) as transaction_count,
        SUM(total_amount) as total_revenue,
        AVG(total_amount) as avg_transaction
    FROM sales
    WHERE sale_date >= DATE('now', '-{days} days')
    GROUP BY DATE(sale_date)
    ORDER BY date DESC
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_top_selling_medicines(limit=10):
    """Get top selling medicines"""
    conn = get_db_connection()
    query = '''
    SELECT 
        m.name,
        m.selling_price,
        SUM(si.quantity) as total_sold,
        SUM(si.total_price) as total_revenue
    FROM sale_items si
    JOIN medicines m ON si.medicine_id = m.id
    GROUP BY si.medicine_id
    ORDER BY total_sold DESC
    LIMIT ?
    '''
    df = pd.read_sql_query(query, conn, params=(limit,))
    conn.close()
    return df

def get_profit_analysis(days=30):
    """Get profit analysis"""
    conn = get_db_connection()
    query = f'''
    SELECT 
        DATE(s.sale_date) as date,
        SUM(si.quantity * (si.unit_price - m.purchase_price)) as profit
    FROM sales s
    JOIN sale_items si ON s.id = si.sale_id
    JOIN medicines m ON si.medicine_id = m.id
    WHERE s.sale_date >= DATE('now', '-{days} days')
    GROUP BY DATE(s.sale_date)
    ORDER BY date DESC
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# ============= EXPENSE OPERATIONS =============

def add_expense(expense_type, amount, description=None, date=None, category=None, created_by=None):
    """Add a new expense record."""
    conn = get_db_connection()
    cursor = conn.cursor()
    date = date or datetime.now().strftime('%Y-%m-%d')
    cursor.execute(
        "INSERT INTO expenses (expense_type, amount, description, date, category, created_by) VALUES (?, ?, ?, ?, ?, ?)",
        (expense_type, amount, description, date, category, created_by)
    )
    expense_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return expense_id

def get_all_expenses(limit=500):
    """Get all expense records."""
    conn = get_db_connection()
    query = """
    SELECT e.id, e.expense_type, e.category, e.amount, e.description, e.date,
           u.username as added_by, e.created_at
    FROM expenses e
    LEFT JOIN users u ON e.created_by = u.id
    ORDER BY e.date DESC, e.id DESC
    LIMIT ?
    """
    df = pd.read_sql_query(query, conn, params=(limit,))
    conn.close()
    return df

def get_expenses_summary(days=30):
    """Get expense summary grouped by category."""
    conn = get_db_connection()
    query = f"""
    SELECT category, expense_type, SUM(amount) as total_amount, COUNT(*) as count
    FROM expenses
    WHERE date >= DATE('now', '-{days} days')
    GROUP BY category, expense_type
    ORDER BY total_amount DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# ============= PRESCRIPTION OPERATIONS =============

def add_prescription(patient_name, doctor_name=None, prescription_date=None,
                     prescription_details=None, medicines_needed=None,
                     customer_id=None, notes=None):
    """Add a new prescription record."""
    conn = get_db_connection()
    cursor = conn.cursor()
    prescription_date = prescription_date or datetime.now().strftime('%Y-%m-%d')
    cursor.execute(
        """INSERT INTO prescriptions
           (patient_name, doctor_name, prescription_date, prescription_details,
            medicines_needed, customer_id, notes, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')""",
        (patient_name, doctor_name, prescription_date, prescription_details,
         medicines_needed, customer_id, notes)
    )
    rx_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return rx_id

def get_all_prescriptions(limit=500):
    """Get all prescriptions with linked customer and filler names."""
    conn = get_db_connection()
    query = """
    SELECT p.id, p.patient_name, p.doctor_name, p.prescription_date,
           p.medicines_needed, p.status, p.filled_on, p.notes,
           c.name as customer_name, u.username as filled_by_name,
           p.created_at
    FROM prescriptions p
    LEFT JOIN customers c ON p.customer_id = c.id
    LEFT JOIN users u ON p.filled_by = u.id
    ORDER BY p.prescription_date DESC, p.id DESC
    LIMIT ?
    """
    df = pd.read_sql_query(query, conn, params=(limit,))
    conn.close()
    return df

def update_prescription_status(prescription_id, status, filled_by=None):
    """Update prescription status (pending / filled / cancelled)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    filled_on = datetime.now().strftime('%Y-%m-%d') if status == 'filled' else None
    cursor.execute(
        """UPDATE prescriptions
           SET status = ?, filled_on = ?, filled_by = ?, updated_at = CURRENT_TIMESTAMP
           WHERE id = ?""",
        (status, filled_on, filled_by, prescription_id)
    )
    conn.commit()
    conn.close()

# ============= PURCHASE ORDER QUERY OPERATIONS =============

def get_all_purchase_orders(limit=200):
    """Get all purchase orders with supplier name."""
    conn = get_db_connection()
    query = """
    SELECT po.id, po.po_number, s.name as supplier_name, po.order_date,
           po.expected_delivery_date, po.actual_delivery_date,
           po.status, po.total_amount, po.notes, u.username as created_by_name,
           po.created_at
    FROM purchase_orders po
    LEFT JOIN suppliers s ON po.supplier_id = s.id
    LEFT JOIN users u ON po.created_by = u.id
    ORDER BY po.created_at DESC
    LIMIT ?
    """
    df = pd.read_sql_query(query, conn, params=(limit,))
    conn.close()
    return df

def get_purchase_order_items(po_id):
    """Get all items belonging to a purchase order."""
    conn = get_db_connection()
    query = """
    SELECT poi.id, m.name as medicine_name, poi.quantity, poi.unit_price,
           poi.total_price, poi.received_qty, poi.batch_number, poi.expiry_date
    FROM purchase_order_items poi
    JOIN medicines m ON poi.medicine_id = m.id
    WHERE poi.po_id = ?
    """
    df = pd.read_sql_query(query, conn, params=(po_id,))
    conn.close()
    return df

def update_purchase_order_status(po_id, status, actual_delivery_date=None):
    """Update the status of a purchase order."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if actual_delivery_date:
        cursor.execute(
            "UPDATE purchase_orders SET status = ?, actual_delivery_date = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (status, actual_delivery_date, po_id)
        )
    else:
        cursor.execute(
            "UPDATE purchase_orders SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (status, po_id)
        )
    conn.commit()
    conn.close()
