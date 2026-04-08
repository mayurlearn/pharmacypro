import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO
from database.db import init_db, get_db_connection
from modules.utils import hash_password, verify_password
import sqlite3

# Page configuration
st.set_page_config(
    page_title="Pharmacy Management System",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
init_db()

# ============= SESSION STATE =============
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.role = None

if 'flash_message' not in st.session_state:
    st.session_state.flash_message = None

if 'flash_type' not in st.session_state:
    st.session_state.flash_type = "success"


def set_flash(message, message_type="success"):
    """Store one-time message to display after rerun."""
    st.session_state.flash_message = message
    st.session_state.flash_type = message_type


def show_flash():
    """Display and clear one-time flash message."""
    message = st.session_state.get("flash_message")
    if not message:
        return

    message_type = st.session_state.get("flash_type", "success")
    if message_type == "success":
        st.success(message)
    elif message_type == "error":
        st.error(message)
    elif message_type == "warning":
        st.warning(message)
    else:
        st.info(message)

    st.session_state.flash_message = None
    st.session_state.flash_type = "success"


# ============= PROFESSIONAL CSS THEME =============
def inject_css():
    """Inject a modern, professional navy/teal pharmacy theme."""
    st.markdown("""
    <style>
    /* ── Google Font ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Global background ── */
    .stApp {
        background: linear-gradient(135deg, #f0f4f8 0%, #e8edf2 100%);
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a5f 0%, #152d4a 100%) !important;
        border-right: 3px solid #00b4d8;
        box-shadow: 4px 0 20px rgba(0,0,0,0.25);
    }
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div {
        color: #e2e8f0 !important;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #00b4d8 !important;
        font-weight: 700 !important;
    }
    section[data-testid="stSidebar"] .stRadio > label {
        color: #cbd5e1 !important;
        font-size: 0.9rem;
        padding: 6px 0;
    }
    section[data-testid="stSidebar"] hr {
        border-color: #2d5070 !important;
    }

    /* ── Top header bar ── */
    header[data-testid="stHeader"] {
        background: linear-gradient(90deg, #1e3a5f 0%, #163058 100%) !important;
        border-bottom: 2px solid #00b4d8;
    }

    /* ── Main content area ── */
    .main .block-container {
        padding: 2rem 2.5rem;
        max-width: 1400px;
    }

    /* ── Page title styling ── */
    h1 {
        color: #1e3a5f !important;
        font-weight: 700 !important;
        font-size: 1.9rem !important;
        border-bottom: 3px solid #00b4d8;
        padding-bottom: 0.4rem;
        margin-bottom: 1.5rem !important;
    }
    h2 {
        color: #1e3a5f !important;
        font-weight: 600 !important;
        font-size: 1.4rem !important;
    }
    h3 {
        color: #2d5f8f !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
    }

    /* ── Metric cards ── */
    [data-testid="stMetric"] {
        background: #ffffff !important;
        border-radius: 14px !important;
        padding: 1.25rem 1.5rem !important;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 15px rgba(30, 58, 95, 0.08);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(30, 58, 95, 0.14);
    }
    [data-testid="stMetricLabel"] {
        color: #64748b !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    [data-testid="stMetricValue"] {
        color: #1e3a5f !important;
        font-size: 1.9rem !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricDelta"] svg { display: none; }

    /* ── Primary buttons ── */
    .stButton > button[kind="primary"],
    .stButton > button[data-testid*="primary"] {
        background: linear-gradient(135deg, #00b4d8 0%, #0096c7 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.2rem !important;
        box-shadow: 0 3px 10px rgba(0, 180, 216, 0.4);
        transition: all 0.2s;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #0096c7 0%, #0077b6 100%) !important;
        box-shadow: 0 5px 18px rgba(0, 180, 216, 0.5);
        transform: translateY(-1px);
    }
    /* Secondary buttons */
    .stButton > button:not([kind="primary"]) {
        background: #ffffff !important;
        color: #1e3a5f !important;
        border: 2px solid #00b4d8 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s;
    }
    .stButton > button:not([kind="primary"]):hover {
        background: #e0f7fc !important;
        border-color: #0096c7 !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: #ffffff;
        border-radius: 10px 10px 0 0;
        border-bottom: 2px solid #00b4d8;
        gap: 0;
    }
    .stTabs [data-baseweb="tab"] {
        color: #64748b !important;
        font-weight: 500;
        padding: 0.6rem 1.4rem;
        border-radius: 8px 8px 0 0;
        transition: all 0.2s;
    }
    .stTabs [aria-selected="true"] {
        color: #1e3a5f !important;
        background: #e0f7fc !important;
        font-weight: 700 !important;
        border-bottom: 3px solid #00b4d8;
    }
    .stTabs [data-baseweb="tab-panel"] {
        background: #ffffff;
        border-radius: 0 0 10px 10px;
        padding: 1.5rem;
        border: 1px solid #e2e8f0;
        border-top: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }

    /* ── Form inputs ── */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        border-radius: 8px !important;
        border: 1.5px solid #cbd5e1 !important;
        background: #ffffff !important;
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #00b4d8 !important;
        box-shadow: 0 0 0 3px rgba(0, 180, 216, 0.2) !important;
    }

    /* ── Data tables ── */
    .stDataFrame {
        border-radius: 10px !important;
        overflow: hidden;
        box-shadow: 0 2px 12px rgba(0,0,0,0.07);
        border: 1px solid #e2e8f0;
    }
    .stDataFrame thead tr th {
        background: #1e3a5f !important;
        color: white !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        padding: 0.75rem 1rem !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .stDataFrame tbody tr:hover {
        background: #f0f9ff !important;
    }

    /* ── Alert boxes ── */
    .stSuccess { border-left: 5px solid #22c55e !important; border-radius: 0 8px 8px 0; }
    .stError   { border-left: 5px solid #ef4444 !important; border-radius: 0 8px 8px 0; }
    .stWarning { border-left: 5px solid #f59e0b !important; border-radius: 0 8px 8px 0; }
    .stInfo    { border-left: 5px solid #00b4d8 !important; border-radius: 0 8px 8px 0; }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        background: #f8fafc !important;
        border-radius: 8px !important;
        color: #1e3a5f !important;
        font-weight: 600 !important;
        border: 1px solid #e2e8f0 !important;
    }

    /* ── Dividers ── */
    hr { border-color: #e2e8f0 !important; }

    /* ── Login page card ── */
    .login-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 2.5rem;
        box-shadow: 0 10px 40px rgba(30,58,95,0.15);
        border-top: 5px solid #00b4d8;
    }

    /* ── Status badges ── */
    .badge-pending   { background:#fef3c7; color:#92400e; padding:3px 10px; border-radius:12px; font-size:0.78rem; font-weight:600; }
    .badge-filled    { background:#dcfce7; color:#166534; padding:3px 10px; border-radius:12px; font-size:0.78rem; font-weight:600; }
    .badge-cancelled { background:#fee2e2; color:#991b1b; padding:3px 10px; border-radius:12px; font-size:0.78rem; font-weight:600; }
    .badge-active    { background:#dbeafe; color:#1e40af; padding:3px 10px; border-radius:12px; font-size:0.78rem; font-weight:600; }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #f1f5f9; }
    ::-webkit-scrollbar-thumb { background: #94a3b8; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #00b4d8; }
    </style>
    """, unsafe_allow_html=True)


# ============= AUTHENTICATION =============
def login_user(username, password):
    """Authenticate user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password, role FROM users WHERE username = ? AND active = 1", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user and verify_password(password, user['password']):
        st.session_state.logged_in = True
        st.session_state.user_id = user['id']
        st.session_state.username = username
        st.session_state.role = user['role']
        return True
    return False

def logout_user():
    """Logout user"""
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.role = None

# ============= LOGIN PAGE =============
def login_page():
    """Display login page"""
    inject_css()
    show_flash()
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.image("https://img.icons8.com/color/200/000000/pharmacy.png", width=150)
        st.title("Pharmacy Management System")
        st.divider()
        
        st.subheader("Login")
        
        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        
        col_a, col_b = st.columns(2)
        if st.button("Login", use_container_width=True, type="primary"):
            if username and password:
                if login_user(username, password):
                    set_flash("Login successful!", "success")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.warning("Please enter username and password")

# ============= MAIN APPLICATION =============
def main_app():
    """Main application"""
    inject_css()
    # Sidebar
    with st.sidebar:
        st.markdown("## 💊 PharmaCare Pro")
        st.markdown(f"👤 **{st.session_state.username}** · *{st.session_state.role}*")
        st.divider()

        pages = {
            "📊 Dashboard": "dashboard",
            "📦 Inventory": "inventory",
            "💳 Billing & Sales": "sales",
            "🏭 Suppliers": "suppliers",
            "👥 Customers": "customers",
            "📋 Purchase Orders": "purchase_orders",
            "📜 Prescriptions": "prescriptions",
            "💸 Expenses": "expenses",
            "⚠️ Stock Alerts": "alerts",
            "📈 Reports": "reports",
            "👨‍💼 Employees": "employees",
            "⚙️ Settings": "settings",
        }

        page = st.radio("Navigation", list(pages.keys()), label_visibility="collapsed")
        selected_page = pages[page]

        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            set_flash("Logged out successfully.", "info")
            logout_user()
            st.rerun()

    show_flash()

    # Load and display selected page
    if selected_page == "dashboard":
        show_dashboard()
    elif selected_page == "inventory":
        show_inventory()
    elif selected_page == "sales":
        show_sales()
    elif selected_page == "suppliers":
        show_suppliers()
    elif selected_page == "customers":
        show_customers()
    elif selected_page == "purchase_orders":
        show_purchase_orders()
    elif selected_page == "prescriptions":
        show_prescriptions()
    elif selected_page == "expenses":
        show_expenses()
    elif selected_page == "alerts":
        show_alerts()
    elif selected_page == "reports":
        show_reports()
    elif selected_page == "employees":
        show_employees()
    elif selected_page == "settings":
        show_settings()

# ============= DASHBOARD PAGE =============
def show_dashboard():
    """Dashboard with key metrics"""
    st.title("📊 Dashboard")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get key metrics
    cursor.execute("SELECT COUNT(*) as count FROM medicines WHERE active = 1")
    total_medicines = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM customers WHERE active = 1")
    total_customers = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM sales WHERE sale_date >= DATE('now', '-1 day')")
    today_sales = cursor.fetchone()['count']
    
    cursor.execute("SELECT SUM(total_amount) as total FROM sales WHERE sale_date >= DATE('now', '-1 day')")
    today_revenue = cursor.fetchone()['total'] or 0
    
    cursor.execute("SELECT SUM(quantity * purchase_price) as total FROM medicines WHERE active = 1")
    inventory_value = cursor.fetchone()['total'] or 0
    
    cursor.execute("SELECT COUNT(*) as count FROM medicines WHERE quantity < reorder_level AND active = 1")
    low_stock = cursor.fetchone()['count']
    
    conn.close()
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Medicines", total_medicines, delta="In Stock")
    
    with col2:
        st.metric("Total Customers", total_customers)
    
    with col3:
        st.metric("Inventory Value", f"Rs {inventory_value:,.2f}")
    
    with col4:
        st.metric("Low Stock Items", low_stock, delta="Need Ordering" if low_stock > 0 else "All Good")
    
    st.divider()
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("📈 Sales Trend (Last 7 Days)")
        conn = get_db_connection()
        sales_data = pd.read_sql_query('''
            SELECT DATE(sale_date) as date, SUM(total_amount) as revenue
            FROM sales
            WHERE sale_date >= DATE('now', '-7 days')
            GROUP BY DATE(sale_date)
            ORDER BY date
        ''', conn)
        conn.close()
        
        if not sales_data.empty:
            st.line_chart(data=sales_data.set_index('date')['revenue'])
        else:
            st.info("No sales data available")
    
    with col_b:
        st.subheader("🏆 Top 5 Selling Medicines")
        conn = get_db_connection()
        top_medicines = pd.read_sql_query('''
            SELECT 
                m.name,
                SUM(si.quantity) as quantity_sold,
                SUM(si.total_price) as revenue
            FROM sale_items si
            JOIN medicines m ON si.medicine_id = m.id
            GROUP BY si.medicine_id
            ORDER BY quantity_sold DESC
            LIMIT 5
        ''', conn)
        conn.close()
        
        if not top_medicines.empty:
            st.dataframe(top_medicines, use_container_width=True, hide_index=True)
        else:
            st.info("No sales data available")
    
    st.divider()
    
    col_x, col_y = st.columns(2)
    
    with col_x:
        st.subheader("📋 Today's Sales")
        st.metric("Transactions", today_sales)
        st.metric("Revenue", f"Rs {today_revenue:,.2f}")
    
    with col_y:
        st.subheader("⚠️ Alerts")
        conn = get_db_connection()
        low_stock_medicines = pd.read_sql_query(
            "SELECT name, quantity, reorder_level FROM medicines WHERE quantity < reorder_level AND active = 1",
            conn
        )
        conn.close()
        
        if not low_stock_medicines.empty:
            for _, med in low_stock_medicines.iterrows():
                st.warning(f"🔴 {med['name']}: Stock {med['quantity']} (Reorder at {med['reorder_level']})")
        else:
            st.success("✅ All items have sufficient stock")

# ============= INVENTORY PAGE =============
def show_inventory():
    """Inventory management"""
    st.title("📦 Inventory Management")
    
    tab1, tab2, tab3 = st.tabs(["View Medicines", "Add Medicine", "Edit/Delete"])
    
    with tab1:
        st.subheader("Current Inventory")
        conn = get_db_connection()
        medicines = pd.read_sql_query('''
            SELECT id, name, sku, category, manufacturer, quantity, 
                   purchase_price, selling_price, expiry_date
            FROM medicines WHERE active = 1
            ORDER BY name
        ''', conn)
        conn.close()
        
        if not medicines.empty:
            st.dataframe(medicines, use_container_width=True, hide_index=True)
        else:
            st.info("No medicines found")
    
    with tab2:
        st.subheader("Add New Medicine")
        
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Medicine Name *", key="inv_add_name")
            sku = st.text_input("SKU (Optional)", key="inv_add_sku")
            category = st.selectbox("Category", ["Tablet", "Capsule", "Liquid", "Injection", "Cream", "Other"], key="inv_add_category")
            manufacturer = st.text_input("Manufacturer", key="inv_add_manufacturer")
        
        with col2:
            purchase_price = st.number_input("Purchase Price ($)", min_value=0.0, step=0.01, key="inv_add_purchase_price")
            selling_price = st.number_input("Selling Price ($)", min_value=0.0, step=0.01, key="inv_add_selling_price")
            reorder_level = st.number_input("Reorder Level (Qty)", min_value=1, value=10, key="inv_add_reorder_level")
            expiry_date = st.date_input("Expiry Date (Optional)", key="inv_add_expiry")
        
        description = st.text_area("Description", key="inv_add_description")
        
        if st.button("Add Medicine", type="primary", use_container_width=True):
            if name:
                from database.db import add_medicine
                success, message = add_medicine(
                    name, sku, category, description, manufacturer,
                    purchase_price, selling_price, reorder_level,
                    str(expiry_date) if expiry_date else None
                )
                if success:
                    set_flash(message, "success")
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Medicine name is required")
    
    with tab3:
        st.subheader("Edit/Delete Medicine")
        
        conn = get_db_connection()
        medicines = pd.read_sql_query(
            "SELECT id, name FROM medicines WHERE active = 1 ORDER BY name",
            conn
        )
        conn.close()
        
        if not medicines.empty:
            selected = st.selectbox(
                "Select Medicine",
                options=medicines['id'],
                format_func=lambda x: medicines[medicines['id']==x]['name'].values[0],
                key="inv_edit_selected_medicine"
            )
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM medicines WHERE id = ?", (selected,))
            medicine = cursor.fetchone()
            conn.close()
            
            if medicine:
                col1, col2 = st.columns(2)
                
                with col1:
                    new_name = st.text_input("Medicine Name", value=medicine['name'], key="inv_edit_name")
                    new_category = st.selectbox("Category", 
                        ["Tablet", "Capsule", "Liquid", "Injection", "Cream", "Other"],
                        index=["Tablet", "Capsule", "Liquid", "Injection", "Cream", "Other"].index(medicine['category'] or "Tablet"),
                        key="inv_edit_category")
                    new_purchase_price = st.number_input("Purchase Price", value=medicine['purchase_price'], key="inv_edit_purchase_price")
                
                with col2:
                    new_selling_price = st.number_input("Selling Price", value=medicine['selling_price'], key="inv_edit_selling_price")
                    new_reorder_level = st.number_input("Reorder Level", value=medicine['reorder_level'], key="inv_edit_reorder_level")
                    new_quantity = st.number_input("Current Quantity", value=medicine['quantity'], key="inv_edit_quantity")
                
                col_edit, col_delete = st.columns(2)
                
                with col_edit:
                    if st.button("Update Medicine", type="primary", use_container_width=True):
                        from database.db import update_medicine, update_medicine_quantity
                        update_medicine(
                            selected, new_name, new_category, None, None,
                            new_purchase_price, new_selling_price, new_reorder_level
                        )
                        if new_quantity != medicine['quantity']:
                            qty_diff = new_quantity - medicine['quantity']
                            update_medicine_quantity(selected, qty_diff)
                        set_flash("Medicine updated!", "success")
                        st.rerun()
                
                with col_delete:
                    if st.button("Delete Medicine", use_container_width=True):
                        from database.db import delete_medicine
                        delete_medicine(selected)
                        set_flash("Medicine deleted!", "success")
                        st.rerun()

# ============= SALES/BILLING PAGE =============
def show_sales():
    """Sales and billing"""
    st.title("💳 Billing & Sales")
    
    tab1, tab2 = st.tabs(["Create Sale", "Sales History"])
    
    with tab1:
        st.subheader("Create New Sale/Bill")
        
        col1, col2 = st.columns(2)
        
        with col1:
            from database.db import get_all_customers, get_all_medicines
            customers = get_all_customers()
            
            if not customers.empty:
                customer = st.selectbox(
                    "Customer (Optional)",
                    options=customers['id'],
                    format_func=lambda x: customers[customers['id']==x]['name'].values[0]
                )
            else:
                customer = None
                st.warning("No customers found. Create one in Customers section.")
        
        with col2:
            payment_method = st.selectbox("Payment Method", ["Cash", "Card", "Check", "Online"])
        
        # Medicine selection
        medicines = get_all_medicines()
        
        if not medicines.empty:
            st.subheader("Select Medicines")
            
            sale_items = []
            medicine_count = st.number_input("Number of medicine items", min_value=1, max_value=10, value=1)
            
            for i in range(int(medicine_count)):
                with st.expander(f"Medicine {i+1}", expanded=(i==0)):
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        med = st.selectbox(
                            "Select Medicine",
                            options=medicines['id'],
                            format_func=lambda x: medicines[medicines['id']==x]['name'].values[0],
                            key=f"med_{i}"
                        )
                    
                    with col_b:
                        qty = st.number_input("Quantity", min_value=1, value=1, key=f"qty_{i}")
                    
                    with col_c:
                        price = st.number_input("Unit Price ($)", min_value=0.0, step=0.01, key=f"price_{i}")
                    
                    if med and qty > 0:
                        sale_items.append({
                            'medicine_id': med,
                            'quantity': qty,
                            'unit_price': price
                        })
            
            st.divider()
            
            col_x, col_y = st.columns(2)
            
            with col_x:
                discount = st.number_input("Discount ($)", min_value=0.0, step=0.01)
                tax_rate = st.number_input("Tax Rate (%)", min_value=0.0, max_value=100.0, value=5.0)
            
            with col_y:
                notes = st.text_area("Notes/Remarks")
            
            # Calculate totals
            subtotal = sum(item['quantity'] * item['unit_price'] for item in sale_items)
            tax = (subtotal * tax_rate) / 100
            total = subtotal - discount + tax
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Subtotal", f"Rs {subtotal:,.2f}")
            with col2:
                st.metric("Total Tax", f"Rs {tax:,.2f}")
            with col3:
                st.metric("Total Amount", f"Rs {total:,.2f}")
            
            if st.button("Complete Sale", type="primary", use_container_width=True):
                if sale_items:
                    from database.db import create_sale
                    success, bill_number, amount = create_sale(
                        customer, sale_items, discount, tax, payment_method,
                        st.session_state.user_id, notes
                    )
                    if success:
                        set_flash(f"✅ Sale completed! Bill: {bill_number} | Amount: Rs {amount:,.2f}", "success")
                        st.rerun()
                    else:
                        st.error(f"Error: {bill_number}")
                else:
                    st.error("Please select at least one medicine")
    
    with tab2:
        st.subheader("Sales History")
        
        date_range = st.date_input(
            "Select Date Range",
            value=(datetime.now() - timedelta(days=30), datetime.now()),
            max_value=datetime.now()
        )
        
        from database.db import get_all_sales
        sales = get_all_sales(limit=500)
        
        if not sales.empty:
            st.dataframe(sales, use_container_width=True, hide_index=True)
        else:
            st.info("No sales found")

# ============= SUPPLIERS PAGE =============
def show_suppliers():
    """Supplier management"""
    st.title("🏭 Suppliers")
    
    tab1, tab2 = st.tabs(["View Suppliers", "Add/Edit Supplier"])
    
    with tab1:
        st.subheader("Suppliers List")
        from database.db import get_all_suppliers
        suppliers = get_all_suppliers()
        
        if not suppliers.empty:
            st.dataframe(suppliers, use_container_width=True, hide_index=True)
        else:
            st.info("No suppliers found")
    
    with tab2:
        st.subheader("Add New Supplier")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Supplier Name *")
            contact_person = st.text_input("Contact Person")
            phone = st.text_input("Phone")
            email = st.text_input("Email")
        
        with col2:
            address = st.text_input("Address")
            city = st.text_input("City")
            state = st.text_input("State")
            postal_code = st.text_input("Postal Code")
        
        credit_limit = st.number_input("Credit Limit ($)", min_value=0.0)
        payment_terms = st.text_input("Payment Terms (e.g., Net 30)")
        
        if st.button("Add Supplier", type="primary", use_container_width=True):
            if name:
                from database.db import add_supplier
                success, message = add_supplier(
                    name, contact_person, phone, email, address, city,
                    state, postal_code, credit_limit, payment_terms
                )
                if success:
                    set_flash(message, "success")
                    st.rerun()
                else:
                    st.error(message)

# ============= CUSTOMERS PAGE =============
def show_customers():
    """Customer management"""
    st.title("👥 Customers")
    
    tab1, tab2 = st.tabs(["View Customers", "Add/Edit Customer"])
    
    with tab1:
        st.subheader("Customers List")
        from database.db import get_all_customers
        customers = get_all_customers()
        
        if not customers.empty:
            st.dataframe(customers, use_container_width=True, hide_index=True)
        else:
            st.info("No customers found")
    
    with tab2:
        st.subheader("Add New Customer")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Customer Name *")
            phone = st.text_input("Phone")
            email = st.text_input("Email")
            customer_type = st.selectbox("Customer Type", ["Retail", "Wholesale", "Institutional"])
        
        with col2:
            address = st.text_input("Address")
            city = st.text_input("City")
            state = st.text_input("State")
            postal_code = st.text_input("Postal Code")
        
        if st.button("Add Customer", type="primary", use_container_width=True):
            if name:
                from database.db import add_customer
                cust_id = add_customer(
                    name, phone, email, address, city, state, postal_code, customer_type
                )
                set_flash(f"Customer added with ID: {cust_id}", "success")
                st.rerun()

# ============= PURCHASE ORDERS PAGE =============
def show_purchase_orders():
    """Purchase order management"""
    st.title("📋 Purchase Orders")

    from database.db import (get_all_suppliers, get_all_medicines,
                              create_purchase_order, get_all_purchase_orders,
                              get_purchase_order_items, receive_purchase_order_item,
                              update_purchase_order_status)

    tab1, tab2, tab3 = st.tabs(["📋 All Orders", "➕ Create Order", "📥 Receive Stock"])

    # ── Tab 1: View all POs ──────────────────────────────────────────────────
    with tab1:
        orders_df = get_all_purchase_orders(limit=200)
        if orders_df.empty:
            st.info("No purchase orders yet. Create one in the 'Create Order' tab.")
        else:
            # Summary stats
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Orders", len(orders_df))
            c2.metric("Pending", len(orders_df[orders_df['status'] == 'pending']))
            c3.metric("Received", len(orders_df[orders_df['status'] == 'received']))
            c4.metric("Total Value", f"Rs {orders_df['total_amount'].sum():,.2f}")

            st.divider()
            status_filter = st.selectbox("Filter by Status", ["All", "pending", "received", "cancelled"],
                                         key="po_status_filter")
            filtered = orders_df if status_filter == "All" else orders_df[orders_df['status'] == status_filter]
            st.dataframe(filtered, use_container_width=True, hide_index=True)

            # View items in an expander
            if not orders_df.empty:
                po_options = {f"{row['po_number']} — {row['supplier_name']} ({row['status']})": row['id']
                              for _, row in orders_df.iterrows()}
                selected_po_label = st.selectbox("View items for PO", list(po_options.keys()),
                                                 key="po_view_select")
                selected_po_id = po_options[selected_po_label]
                items = get_purchase_order_items(selected_po_id)
                if not items.empty:
                    st.dataframe(items, use_container_width=True, hide_index=True)
                else:
                    st.info("No items found for this order.")

    # ── Tab 2: Create PO ─────────────────────────────────────────────────────
    with tab2:
        suppliers_df = get_all_suppliers()
        medicines_df = get_all_medicines()

        if suppliers_df.empty:
            st.warning("Add at least one supplier before creating a purchase order.")
        elif medicines_df.empty:
            st.warning("Add at least one medicine in Inventory first.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                supplier_options = {row['name']: row['id'] for _, row in suppliers_df.iterrows()}
                selected_supplier = st.selectbox("Select Supplier", list(supplier_options.keys()), key="po_supplier")
                supplier_id = supplier_options[selected_supplier]
            with col2:
                expected_delivery = st.date_input("Expected Delivery Date", key="po_exp_del")

            po_notes = st.text_area("Notes / Remarks", key="po_notes_field")

            st.subheader("Add Order Items")
            if 'po_items' not in st.session_state:
                st.session_state.po_items = []

            med_options = {row['name']: row['id'] for _, row in medicines_df.iterrows()}
            col_m, col_q, col_p, col_add = st.columns([3, 1, 1, 1])
            with col_m:
                med_name = st.selectbox("Medicine", list(med_options.keys()), key="po_med_name")
            with col_q:
                med_qty = st.number_input("Qty", min_value=1, value=10, key="po_med_qty")
            with col_p:
                med_price = st.number_input("Unit Price", min_value=0.01, value=1.00, step=0.01, key="po_med_price")
            with col_add:
                st.write("")
                if st.button("Add", key="po_add_item_btn"):
                    st.session_state.po_items.append({
                        "medicine_id": med_options[med_name],
                        "medicine_name": med_name,
                        "quantity": med_qty,
                        "unit_price": med_price,
                    })

            if st.session_state.po_items:
                import pandas as _pd
                items_display = _pd.DataFrame(st.session_state.po_items)
                items_display['total'] = items_display['quantity'] * items_display['unit_price']
                st.dataframe(items_display[['medicine_name', 'quantity', 'unit_price', 'total']],
                             use_container_width=True, hide_index=True)
                st.markdown(f"**Order Total: Rs {items_display['total'].sum():,.2f}**")

                col_sub, col_clr = st.columns(2)
                with col_sub:
                    if st.button("✅ Submit Purchase Order", type="primary", key="po_submit_btn"):
                        success, result = create_purchase_order(
                            supplier_id=supplier_id,
                            order_items=st.session_state.po_items,
                            expected_delivery_date=str(expected_delivery),
                            created_by=st.session_state.user_id,
                            notes=po_notes or None,
                        )
                        if success:
                            st.session_state.po_items = []
                            set_flash(f"Purchase Order {result} created successfully!", "success")
                            st.rerun()
                        else:
                            st.error(f"Error: {result}")
                with col_clr:
                    if st.button("🗑️ Clear Items", key="po_clear_btn"):
                        st.session_state.po_items = []
                        st.rerun()

    # ── Tab 3: Receive Stock ─────────────────────────────────────────────────
    with tab3:
        st.write("Select a pending purchase order to receive stock into inventory.")
        orders_df2 = get_all_purchase_orders(limit=200)
        pending = orders_df2[orders_df2['status'] == 'pending'] if not orders_df2.empty else orders_df2

        if pending.empty:
            st.info("No pending purchase orders to receive.")
        else:
            recv_options = {f"{row['po_number']} — {row['supplier_name']}": row['id']
                            for _, row in pending.iterrows()}
            recv_label = st.selectbox("Select PO to Receive", list(recv_options.keys()), key="recv_po_select")
            recv_po_id = recv_options[recv_label]
            recv_items = get_purchase_order_items(recv_po_id)

            if recv_items.empty:
                st.warning("No items found for this order.")
            else:
                st.dataframe(recv_items, use_container_width=True, hide_index=True)
                st.divider()
                st.subheader("Receive an Item")
                item_opts = {f"{row['medicine_name']} (ordered: {row['quantity']}, received: {row['received_qty']})": row
                             for _, row in recv_items.iterrows()}
                recv_item_label = st.selectbox("Select Item", list(item_opts.keys()), key="recv_item_select")
                recv_item = item_opts[recv_item_label]

                recv_qty_val = st.number_input(
                    "Quantity Received", min_value=1,
                    max_value=int(recv_item['quantity'] - recv_item['received_qty']),
                    value=int(recv_item['quantity'] - recv_item['received_qty']),
                    key="recv_qty_input"
                )

                if st.button("📥 Receive Stock", type="primary", key="recv_stock_btn"):
                    ok, msg = receive_purchase_order_item(
                        po_item_id=int(recv_item['id']),
                        received_qty=recv_qty_val,
                        medicine_id=int(recv_item['id'])  # will be matched internally
                    )
                    # Also mark PO as received if all items done
                    all_received = all(
                        row['received_qty'] >= row['quantity']
                        for _, row in recv_items.iterrows()
                    )
                    if all_received:
                        update_purchase_order_status(recv_po_id, 'received',
                                                     datetime.now().strftime('%Y-%m-%d'))
                    if ok:
                        set_flash(f"{msg} — stock updated in inventory.", "success")
                    else:
                        set_flash(f"Error: {msg}", "error")
                    st.rerun()


# ============= PRESCRIPTIONS PAGE =============
def show_prescriptions():
    """Prescription management"""
    st.title("📜 Prescriptions")

    from database.db import (add_prescription, get_all_prescriptions,
                              update_prescription_status, get_all_customers)

    tab1, tab2 = st.tabs(["📋 All Prescriptions", "➕ Add Prescription"])

    # ── Tab 1: View all ──────────────────────────────────────────────────────
    with tab1:
        rx_df = get_all_prescriptions(limit=500)
        if rx_df.empty:
            st.info("No prescriptions recorded yet.")
        else:
            c1, c2, c3 = st.columns(3)
            c1.metric("Total", len(rx_df))
            c2.metric("Pending", len(rx_df[rx_df['status'] == 'pending']))
            c3.metric("Filled", len(rx_df[rx_df['status'] == 'filled']))
            st.divider()

            status_f = st.selectbox("Filter by Status", ["All", "pending", "filled", "cancelled"],
                                    key="rx_status_filter")
            filtered = rx_df if status_f == "All" else rx_df[rx_df['status'] == status_f]
            st.dataframe(filtered, use_container_width=True, hide_index=True)

            # Update status
            st.subheader("Update Prescription Status")
            rx_options = {f"#{row['id']} — {row['patient_name']} ({row['status']})": row['id']
                          for _, row in rx_df[rx_df['status'] == 'pending'].iterrows()}
            if rx_options:
                rx_label = st.selectbox("Select Prescription", list(rx_options.keys()), key="rx_update_select")
                rx_id_to_update = rx_options[rx_label]
                new_status = st.selectbox("New Status", ["filled", "cancelled"], key="rx_new_status")
                if st.button("Update Status", type="primary", key="rx_update_btn"):
                    update_prescription_status(rx_id_to_update, new_status,
                                               filled_by=st.session_state.user_id if new_status == 'filled' else None)
                    set_flash(f"Prescription #{rx_id_to_update} marked as {new_status}.", "success")
                    st.rerun()
            else:
                st.info("No pending prescriptions to update.")

    # ── Tab 2: Add new ───────────────────────────────────────────────────────
    with tab2:
        customers_df = get_all_customers()
        col1, col2 = st.columns(2)
        with col1:
            patient_name = st.text_input("Patient Name *", key="rx_patient_name")
            doctor_name = st.text_input("Doctor / Prescriber", key="rx_doctor_name")
            rx_date = st.date_input("Prescription Date", key="rx_date")
        with col2:
            cust_options = {"-- Walk-in / No Account --": None}
            if not customers_df.empty:
                cust_options.update({row['name']: row['id'] for _, row in customers_df.iterrows()})
            cust_label = st.selectbox("Linked Customer", list(cust_options.keys()), key="rx_customer")
            customer_id = cust_options[cust_label]

        medicines_needed = st.text_area("Medicines Prescribed (free text)", key="rx_medicines_needed",
                                        placeholder="e.g. Amoxicillin 500mg x 14,  Paracetamol 1g x 10")
        rx_notes = st.text_area("Notes", key="rx_notes")

        if st.button("💾 Save Prescription", type="primary", key="rx_save_btn"):
            if not patient_name.strip():
                st.error("Patient name is required.")
            else:
                rx_id = add_prescription(
                    patient_name=patient_name.strip(),
                    doctor_name=doctor_name.strip() or None,
                    prescription_date=str(rx_date),
                    medicines_needed=medicines_needed.strip() or None,
                    customer_id=customer_id,
                    notes=rx_notes.strip() or None,
                )
                set_flash(f"Prescription #{rx_id} saved for {patient_name}.", "success")
                st.rerun()


# ============= EXPENSES PAGE =============
def show_expenses():
    """Expenses management"""
    st.title("💸 Expenses")

    from database.db import add_expense, get_all_expenses, get_expenses_summary

    tab1, tab2 = st.tabs(["📋 Expense Log", "➕ Record Expense"])

    EXPENSE_CATEGORIES = ["Rent", "Utilities", "Salaries", "Supplies", "Equipment",
                          "Marketing", "Maintenance", "Insurance", "Taxes", "Miscellaneous"]
    EXPENSE_TYPES = ["Fixed", "Variable", "One-time"]

    # ── Tab 1: View ──────────────────────────────────────────────────────────
    with tab1:
        exp_df = get_all_expenses(limit=500)
        if exp_df.empty:
            st.info("No expenses recorded yet.")
        else:
            # Summary metrics
            total_exp = exp_df['amount'].sum()
            avg_exp = exp_df['amount'].mean()
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Expenses", f"Rs {total_exp:,.2f}")
            c2.metric("Number of Records", len(exp_df))
            c3.metric("Average Amount", f"Rs {avg_exp:,.2f}")
            st.divider()

            # Category breakdown
            import plotly.express as px
            summary = get_expenses_summary(days=365)
            if not summary.empty:
                fig = px.pie(summary, names='category', values='total_amount',
                             title='Expenses by Category (Last 12 Months)',
                             color_discrete_sequence=px.colors.sequential.Blues_r)
                fig.update_layout(margin=dict(t=40, b=0, l=0, r=0), height=280)
                st.plotly_chart(fig, use_container_width=True)
                st.divider()

            cat_filter = st.selectbox("Filter by Category", ["All"] + EXPENSE_CATEGORIES, key="exp_cat_filter")
            filtered = exp_df if cat_filter == "All" else exp_df[exp_df['category'] == cat_filter]
            st.dataframe(filtered, use_container_width=True, hide_index=True)

    # ── Tab 2: Record ────────────────────────────────────────────────────────
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            exp_category = st.selectbox("Category *", EXPENSE_CATEGORIES, key="exp_category")
            exp_type = st.selectbox("Expense Type", EXPENSE_TYPES, key="exp_type")
            exp_amount = st.number_input("Amount ($) *", min_value=0.01, step=0.01, key="exp_amount")
        with col2:
            exp_date = st.date_input("Date", key="exp_date")
            exp_desc = st.text_area("Description", key="exp_description",
                                    placeholder="Details about this expense...")

        if st.button("💾 Record Expense", type="primary", key="exp_save_btn"):
            if exp_amount <= 0:
                st.error("Amount must be greater than zero.")
            else:
                eid = add_expense(
                    expense_type=exp_type,
                    amount=exp_amount,
                    description=exp_desc.strip() or None,
                    date=str(exp_date),
                    category=exp_category,
                    created_by=st.session_state.user_id,
                )
                set_flash(f"Expense of Rs {exp_amount:,.2f} ({exp_category}) recorded. ID: {eid}", "success")
                st.rerun()




# ============= ALERTS PAGE =============
def show_alerts():
    """Stock and expiry alerts"""
    st.title("⚠️ Stock & Expiry Alerts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📉 Low Stock Items")
        from database.db import get_low_stock_medicines
        low_stock = get_low_stock_medicines()
        
        if not low_stock.empty:
            st.dataframe(low_stock, use_container_width=True, hide_index=True)
        else:
            st.success("✅ All items have sufficient stock")
    
    with col2:
        st.subheader("📅 Expired Medicines")
        from database.db import get_expired_medicines
        expired = get_expired_medicines()
        
        if not expired.empty:
            st.dataframe(expired, use_container_width=True, hide_index=True)
        else:
            st.success("✅ No expired medicines")

# ============= REPORTS PAGE =============
def show_reports():
    """Reports and analytics"""
    st.title("📈 Reports & Analytics")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Sales Report", "Profit Analysis", "Stock Report", "Excel Export"])
    
    with tab1:
        st.subheader("Sales Report")
        days = st.slider("Last N days", 1, 365, 30)
        
        from database.db import get_sales_summary
        sales_data = get_sales_summary(days)
        
        if not sales_data.empty:
            st.dataframe(sales_data, use_container_width=True, hide_index=True)
            st.line_chart(data=sales_data.set_index('date')['total_revenue'])
        else:
            st.info("No sales data available")
    
    with tab2:
        st.subheader("Profit Analysis")
        days = st.slider("Last N days", 1, 365, 30, key="profit_days")
        
        from database.db import get_profit_analysis
        profit_data = get_profit_analysis(days)
        
        if not profit_data.empty:
            st.dataframe(profit_data, use_container_width=True, hide_index=True)
            st.bar_chart(data=profit_data.set_index('date')['profit'])
        else:
            st.info("No profit data available")
    
    with tab3:
        st.subheader("Stock Report")
        from database.db import get_all_medicines
        medicines = get_all_medicines()
        
        if not medicines.empty:
            st.dataframe(medicines, use_container_width=True, hide_index=True)
        else:
            st.info("No medicines found")

    with tab4:
        st.subheader("Export Reports to Excel")
        st.caption("Export inventory, purchases, sales, expenses and accounting summary in one Excel file.")

        export_period = st.selectbox(
            "Select Date Period",
            ["Weekly", "Monthly", "Custom"],
            key="export_period_select"
        )

        today_date = datetime.now().date()
        if export_period == "Weekly":
            date_from = today_date - timedelta(days=6)
            date_to = today_date
            st.info(f"Weekly export range: {date_from} to {date_to}")
        elif export_period == "Monthly":
            date_from = today_date.replace(day=1)
            date_to = today_date
            st.info(f"Monthly export range: {date_from} to {date_to}")
        else:
            date_range = st.date_input(
                "Custom Date Range",
                value=(today_date - timedelta(days=30), today_date),
                max_value=today_date,
                key="export_custom_range"
            )
            if isinstance(date_range, tuple) and len(date_range) == 2:
                date_from, date_to = date_range
            else:
                date_from = date_range
                date_to = date_range

        conn = get_db_connection()

        inventory_df = pd.read_sql_query(
            """
            SELECT
                id, name, sku, category, manufacturer,
                quantity, reorder_level, purchase_price, selling_price,
                (quantity * purchase_price) AS stock_cost_value,
                (quantity * selling_price) AS stock_sale_value,
                expiry_date, batch_number, updated_at
            FROM medicines
            WHERE active = 1
            ORDER BY name
            """,
            conn
        )

        purchases_df = pd.read_sql_query(
            """
            SELECT
                po.id,
                po.po_number,
                po.order_date,
                po.expected_delivery_date,
                po.actual_delivery_date,
                po.status,
                s.name AS supplier_name,
                po.total_amount,
                po.notes,
                po.created_at
            FROM purchase_orders po
            LEFT JOIN suppliers s ON po.supplier_id = s.id
            WHERE DATE(po.order_date) BETWEEN DATE(?) AND DATE(?)
            ORDER BY po.order_date DESC, po.id DESC
            """,
            conn,
            params=(str(date_from), str(date_to))
        )

        purchase_items_df = pd.read_sql_query(
            """
            SELECT
                poi.id,
                po.po_number,
                po.order_date,
                m.name AS medicine_name,
                poi.quantity,
                poi.received_qty,
                poi.unit_price,
                poi.total_price,
                poi.batch_number,
                poi.expiry_date
            FROM purchase_order_items poi
            JOIN purchase_orders po ON poi.po_id = po.id
            JOIN medicines m ON poi.medicine_id = m.id
            WHERE DATE(po.order_date) BETWEEN DATE(?) AND DATE(?)
            ORDER BY po.order_date DESC, poi.id DESC
            """,
            conn,
            params=(str(date_from), str(date_to))
        )

        sales_df = pd.read_sql_query(
            """
            SELECT
                s.id,
                s.bill_number,
                s.sale_date,
                s.sale_time,
                c.name AS customer_name,
                s.subtotal,
                s.discount,
                s.tax,
                s.total_amount,
                s.payment_method,
                s.status,
                s.notes,
                s.created_at
            FROM sales s
            LEFT JOIN customers c ON s.customer_id = c.id
            WHERE DATE(s.sale_date) BETWEEN DATE(?) AND DATE(?)
            ORDER BY s.sale_date DESC, s.id DESC
            """,
            conn,
            params=(str(date_from), str(date_to))
        )

        sale_items_df = pd.read_sql_query(
            """
            SELECT
                si.id,
                s.bill_number,
                s.sale_date,
                m.name AS medicine_name,
                si.quantity,
                si.unit_price,
                si.discount,
                si.total_price
            FROM sale_items si
            JOIN sales s ON si.sale_id = s.id
            JOIN medicines m ON si.medicine_id = m.id
            WHERE DATE(s.sale_date) BETWEEN DATE(?) AND DATE(?)
            ORDER BY s.sale_date DESC, si.id DESC
            """,
            conn,
            params=(str(date_from), str(date_to))
        )

        expenses_df = pd.read_sql_query(
            """
            SELECT
                id,
                date,
                expense_type,
                category,
                amount,
                description,
                created_at
            FROM expenses
            WHERE DATE(date) BETWEEN DATE(?) AND DATE(?)
            ORDER BY date DESC, id DESC
            """,
            conn,
            params=(str(date_from), str(date_to))
        )

        stock_moves_df = pd.read_sql_query(
            """
            SELECT
                sm.id,
                DATE(sm.created_at) AS movement_date,
                sm.created_at,
                m.name AS medicine_name,
                sm.movement_type,
                sm.quantity,
                sm.reference_type,
                sm.reference_id,
                sm.notes
            FROM stock_movements sm
            JOIN medicines m ON sm.medicine_id = m.id
            WHERE DATE(sm.created_at) BETWEEN DATE(?) AND DATE(?)
            ORDER BY sm.created_at DESC, sm.id DESC
            """,
            conn,
            params=(str(date_from), str(date_to))
        )

        conn.close()

        total_sales = float(sales_df["total_amount"].sum()) if not sales_df.empty else 0.0
        total_purchases = float(purchases_df["total_amount"].sum()) if not purchases_df.empty else 0.0
        total_expenses = float(expenses_df["amount"].sum()) if not expenses_df.empty else 0.0
        gross_profit = total_sales - total_purchases
        net_profit = gross_profit - total_expenses

        accounting_summary_df = pd.DataFrame([
            {"metric": "Period Start", "value": str(date_from)},
            {"metric": "Period End", "value": str(date_to)},
            {"metric": "Total Sales Revenue", "value": round(total_sales, 2)},
            {"metric": "Total Purchase Cost", "value": round(total_purchases, 2)},
            {"metric": "Total Expenses", "value": round(total_expenses, 2)},
            {"metric": "Gross Profit (Sales - Purchases)", "value": round(gross_profit, 2)},
            {"metric": "Net Profit (Gross - Expenses)", "value": round(net_profit, 2)},
            {"metric": "Sales Transactions", "value": int(len(sales_df))},
            {"metric": "Purchase Orders", "value": int(len(purchases_df))},
            {"metric": "Expense Entries", "value": int(len(expenses_df))},
            {"metric": "Inventory Item Count", "value": int(len(inventory_df))},
            {"metric": "Stock Movements", "value": int(len(stock_moves_df))},
        ])

        col_a, col_b, col_c, col_d = st.columns(4)
        col_a.metric("Sales", f"Rs {total_sales:,.2f}")
        col_b.metric("Purchases", f"Rs {total_purchases:,.2f}")
        col_c.metric("Expenses", f"Rs {total_expenses:,.2f}")
        col_d.metric("Net Profit", f"Rs {net_profit:,.2f}")

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            accounting_summary_df.to_excel(writer, sheet_name="Accounting_Summary", index=False)
            inventory_df.to_excel(writer, sheet_name="Inventory", index=False)
            purchases_df.to_excel(writer, sheet_name="Purchases", index=False)
            purchase_items_df.to_excel(writer, sheet_name="Purchase_Items", index=False)
            sales_df.to_excel(writer, sheet_name="Sales", index=False)
            sale_items_df.to_excel(writer, sheet_name="Sale_Items", index=False)
            expenses_df.to_excel(writer, sheet_name="Expenses", index=False)
            stock_moves_df.to_excel(writer, sheet_name="Stock_Movements", index=False)

        output.seek(0)
        file_name = f"pharmacy_report_{str(date_from)}_to_{str(date_to)}.xlsx"

        st.download_button(
            label="⬇️ Download Excel Report",
            data=output.getvalue(),
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_excel_report"
        )

# ============= EMPLOYEES PAGE =============
def show_employees():
    """Employee management"""
    st.title("👨‍💼 Employee Management")

    if st.session_state.role != "admin":
        st.warning("Only admin can manage employee accounts.")
        return

    from database.db import (
        create_employee,
        delete_employee_permanently,
        get_all_employees,
        get_employee_audit_logs,
        reset_employee_password,
        set_employee_active,
        update_employee_role,
    )

    tab1, tab2, tab3, tab4 = st.tabs(["Employees", "Create Login", "Manage Account", "Audit Logs"])

    with tab1:
        st.subheader("Current Employee Accounts")
        employees_df = get_all_employees(include_admin=True)
        if employees_df.empty:
            st.info("No employee accounts found.")
        else:
            employees_df["active"] = employees_df["active"].apply(lambda value: "Active" if value == 1 else "Inactive")
            st.dataframe(employees_df, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Create New Employee Login")
        col1, col2 = st.columns(2)

        with col1:
            username = st.text_input("Username *", key="emp_create_username")
            email = st.text_input("Email", key="emp_create_email")

        with col2:
            role = st.selectbox("Role", ["staff", "manager", "admin"], key="emp_create_role")
            temp_password = st.text_input("Temporary Password *", type="password", key="emp_create_password")

        confirm_password = st.text_input("Confirm Password *", type="password", key="emp_create_password_confirm")

        if st.button("Create Employee Login", type="primary", use_container_width=True, key="emp_create_submit"):
            if not username.strip() or not temp_password:
                st.error("Username and password are required.")
            elif temp_password != confirm_password:
                st.error("Password and confirm password do not match.")
            elif len(temp_password) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                success, message = create_employee(
                    username=username,
                    password=temp_password,
                    email=email or None,
                    role=role,
                    actor_user_id=st.session_state.user_id,
                )
                if success:
                    set_flash(message, "success")
                    st.rerun()
                else:
                    st.error(message)

    with tab3:
        st.subheader("Update Employee Account")
        employees_df = get_all_employees(include_admin=True)

        if employees_df.empty:
            st.info("No employee accounts available.")
            return

        employee_ids = employees_df["id"].tolist()
        selected_employee_id = st.selectbox(
            "Select Employee",
            options=employee_ids,
            format_func=lambda selected_id: f"{employees_df[employees_df['id'] == selected_id]['username'].iloc[0]} ({employees_df[employees_df['id'] == selected_id]['role'].iloc[0]})",
            key="emp_manage_select",
        )

        selected_employee = employees_df[employees_df["id"] == selected_employee_id].iloc[0]
        st.write(f"**Username:** {selected_employee['username']}")
        st.write(f"**Current Role:** {selected_employee['role']}")
        st.write(f"**Current Status:** {'Active' if selected_employee['active'] == 1 else 'Inactive'}")

        col_role, col_status = st.columns(2)
        with col_role:
            new_role = st.selectbox("Change Role", ["staff", "manager", "admin"],
                                    index=["staff", "manager", "admin"].index(selected_employee["role"]) if selected_employee["role"] in ["staff", "manager", "admin"] else 0,
                                    key="emp_manage_role")
            if st.button("Update Role", key="emp_manage_update_role"):
                success, message = update_employee_role(
                    selected_employee_id,
                    new_role,
                    actor_user_id=st.session_state.user_id,
                )
                if success:
                    set_flash(message, "success")
                    st.rerun()
                else:
                    st.error(message)

        with col_status:
            if selected_employee["active"] == 1:
                if st.button("Deactivate Account", key="emp_manage_deactivate"):
                    success, message = set_employee_active(
                        selected_employee_id,
                        False,
                        actor_user_id=st.session_state.user_id,
                    )
                    if success:
                        set_flash(message, "success")
                        st.rerun()
                    else:
                        st.error(message)
            else:
                if st.button("Activate Account", key="emp_manage_activate"):
                    success, message = set_employee_active(
                        selected_employee_id,
                        True,
                        actor_user_id=st.session_state.user_id,
                    )
                    if success:
                        set_flash(message, "success")
                        st.rerun()
                    else:
                        st.error(message)

        st.divider()
        st.subheader("Reset Password")
        new_password = st.text_input("New Password", type="password", key="emp_manage_new_password")
        confirm_new_password = st.text_input("Confirm New Password", type="password", key="emp_manage_confirm_password")
        if st.button("Reset Password", key="emp_manage_reset_password"):
            if not new_password:
                st.error("Please enter a new password.")
            elif new_password != confirm_new_password:
                st.error("Password and confirm password do not match.")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                success, message = reset_employee_password(
                    selected_employee_id,
                    new_password,
                    actor_user_id=st.session_state.user_id,
                )
                if success:
                    set_flash(message, "success")
                    st.rerun()
                else:
                    st.error(message)

        st.divider()
        st.subheader("Delete Employee Permanently")
        if selected_employee_id == st.session_state.user_id:
            st.warning("You cannot delete your own account while logged in.")
        elif selected_employee["role"] == "admin":
            st.warning("Admin account cannot be deleted.")
        else:
            confirm_delete = st.checkbox(
                "I understand this is permanent and cannot be undone.",
                key="emp_manage_delete_confirm"
            )
            if st.button("Delete Permanently", key="emp_manage_delete", type="secondary"):
                if not confirm_delete:
                    st.error("Please confirm permanent deletion first.")
                else:
                    success, message = delete_employee_permanently(
                        selected_employee_id,
                        actor_user_id=st.session_state.user_id,
                    )
                    if success:
                        set_flash(message, "success")
                        st.rerun()
                    else:
                        st.error(message)

    with tab4:
        st.subheader("Employee Management Audit Logs")
        logs_df = get_employee_audit_logs(limit=300)
        if logs_df.empty:
            st.info("No audit events yet.")
        else:
            st.dataframe(logs_df, use_container_width=True, hide_index=True)

# ============= SETTINGS PAGE =============
def show_settings():
    """System settings"""
    st.title("⚙️ Settings")

    tab1, tab2 = st.tabs(["👤 Profile & Password", "🔧 System Info"])

    with tab1:
        st.subheader("Your Profile")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Username:** {st.session_state.username}")
            st.markdown(f"**Role:** {st.session_state.role}")
        st.divider()

        st.subheader("Change Password")
        current_pw = st.text_input("Current Password", type="password", key="settings_current_pw")
        new_pw     = st.text_input("New Password",     type="password", key="settings_new_pw")
        confirm_pw = st.text_input("Confirm Password", type="password", key="settings_confirm_pw")

        if st.button("🔑 Update Password", type="primary", key="settings_change_pw_btn"):
            if not current_pw or not new_pw or not confirm_pw:
                st.error("All three fields are required.")
            elif new_pw != confirm_pw:
                st.error("New password and confirmation do not match.")
            elif len(new_pw) < 6:
                st.error("New password must be at least 6 characters.")
            else:
                # Verify current password
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT password FROM users WHERE id = ?", (st.session_state.user_id,))
                row = cursor.fetchone()
                conn.close()
                if row and verify_password(current_pw, row['password']):
                    from database.db import reset_employee_password
                    ok, msg = reset_employee_password(
                        st.session_state.user_id,
                        new_pw,
                        actor_user_id=st.session_state.user_id
                    )
                    if ok:
                        set_flash("Password updated successfully. Please log in again.", "success")
                        logout_user()
                        st.rerun()
                    else:
                        st.error(f"Failed: {msg}")
                else:
                    st.error("Current password is incorrect.")

    with tab2:
        st.subheader("System Information")
        import sqlite3 as _sq
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Application:** PharmaCare Pro")
            st.markdown(f"**Database:** SQLite3")
            st.markdown(f"**Python SQLite:** {_sq.sqlite_version}")
        with col2:
            import streamlit as _st
            st.markdown(f"**Streamlit Version:** {_st.__version__}")
            import platform
            st.markdown(f"**Platform:** {platform.system()} {platform.release()}")

        st.divider()
        st.subheader("Database Stats")
        from database.db import get_db_connection as _gc
        _conn = _gc()
        _cur = _conn.cursor()
        stats = {}
        for tbl in ['users', 'medicines', 'customers', 'suppliers', 'sales', 'prescriptions', 'expenses']:
            _cur.execute(f"SELECT COUNT(*) as c FROM {tbl}")
            stats[tbl.capitalize()] = _cur.fetchone()['c']
        _conn.close()
        import pandas as _pd2
        stats_df = _pd2.DataFrame(list(stats.items()), columns=['Table', 'Records'])
        st.dataframe(stats_df, use_container_width=True, hide_index=True)




# ============= MAIN EXECUTION =============
if __name__ == "__main__":
    if st.session_state.logged_in:
        main_app()
    else:
        login_page()
