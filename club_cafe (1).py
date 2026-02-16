import streamlit as st
import sqlite3
import pandas as pd
import hashlib
from datetime import datetime


# ================= DATABASE SETUP =================
def init_db():
    conn = sqlite3.connect('cafe_database.db')
    c = conn.cursor()

    # Orders table
    c.execute('''CREATE TABLE IF NOT EXISTS orders
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  phone TEXT,
                  item TEXT,
                  quantity INTEGER,
                  address TEXT,
                  status TEXT,
                  username TEXT,
                  payment_mode TEXT,
                  order_time TEXT)''')

    # Messages table
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  email TEXT,
                  message TEXT)''')

    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE,
                  password TEXT)''')

    conn.commit()
    conn.close()


init_db()


# ================= SECURITY FUNCTIONS =================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def signup(username, password):
    conn = sqlite3.connect('cafe_database.db')
    c = conn.cursor()

    try:
        c.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hash_password(password))
        )
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()


def login(username, password):
    conn = sqlite3.connect('cafe_database.db')
    c = conn.cursor()

    c.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, hash_password(password))
    )

    user = c.fetchone()
    conn.close()
    return user


# ================= ORDER FUNCTIONS =================
def add_order(name, phone, item, quantity, address, username, payment_mode):
    conn = sqlite3.connect('cafe_database.db')
    c = conn.cursor()

    c.execute(
        """INSERT INTO orders
        (name, phone, item, quantity, address, status,
         username, payment_mode, order_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (name, phone, item, quantity, address,
         'Pending', username, payment_mode, str(datetime.now()))
    )

    conn.commit()
    conn.close()


def add_message(name, email, message):
    conn = sqlite3.connect('cafe_database.db')
    c = conn.cursor()

    c.execute(
        "INSERT INTO messages (name, email, message) VALUES (?, ?, ?)",
        (name, email, message)
    )

    conn.commit()
    conn.close()


# ================= SESSION STATE =================
if "user" not in st.session_state:
    st.session_state.user = None


# ================= SIDEBAR NAVIGATION =================
st.sidebar.title("Cafe App")

page = st.sidebar.radio(
    "Navigation",
    ["Login", "Signup", "Order Food", "My Orders", "Contact", "Admin Panel"]
)

# SESSION DEFAULT PAGE
if "auth_page" not in st.session_state:
    st.session_state.auth_page = "login"


# ===== LOGIN PAGE =====
if st.session_state.auth_page == "login":

    st.title("User Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if login(username, password):
            st.session_state.user = username
            st.success("Login successful")
        else:
            st.error("Invalid credentials")

    st.write("---")
    st.write("New user?")

    if st.button("Create Account"):
        st.session_state.auth_page = "signup"
        st.rerun()


# ===== SIGNUP PAGE =====
elif st.session_state.auth_page == "signup":

    st.title("Create Account")

    username = st.text_input("Choose Username")
    password = st.text_input("Choose Password", type="password")

    if st.button("Signup"):
        if signup(username, password):
            st.success("Account created — Please login")
            st.session_state.auth_page = "login"
            st.rerun()
        else:
            st.error("Username already exists")

    if st.button("Back to Login"):
        st.session_state.auth_page = "login"
        st.rerun()



# ================= ORDER FOOD =================
elif page == "Order Food":

    if not st.session_state.user:
        st.warning("Please login first")
    else:
        st.title("Order Food")

        name = st.text_input("Name")
        phone = st.text_input("Phone")
        item = st.text_input("Item")
        quantity = st.number_input("Quantity", 1)
        address = st.text_area("Address")

        payment_mode = st.selectbox(
            "Payment Mode",
            ["Cash", "UPI", "Card"]
        )

        if st.button("Place Order"):
            add_order(
                name, phone, item, quantity,
                address, st.session_state.user,
                payment_mode
            )
            st.success("Order placed successfully")


# ================= USER ORDER HISTORY =================
elif page == "My Orders":

    if not st.session_state.user:
        st.warning("Please login first")
    else:
        conn = sqlite3.connect('cafe_database.db')

        df = pd.read_sql_query(
            f"SELECT * FROM orders WHERE username='{st.session_state.user}'",
            conn
        )

        st.dataframe(df)
        conn.close()


# ================= CONTACT =================
elif page == "Contact":

    st.title("Contact Us")

    name = st.text_input("Name")
    email = st.text_input("Email")
    message = st.text_area("Message")

    if st.button("Send"):
        add_message(name, email, message)
        st.success("Message sent")


# ================= ADMIN PANEL =================
elif page == "Admin Panel":

    st.title("Admin Login")

    admin_user = st.text_input("Admin Username")
    admin_pass = st.text_input("Admin Password", type="password")

    if admin_user == st.secrets["admin_username"] and \
       admin_pass == st.secrets["admin_password"]:

        st.success("Admin logged in")

        conn = sqlite3.connect('cafe_database.db')

        st.subheader("All Orders")
        st.dataframe(pd.read_sql_query("SELECT * FROM orders", conn))

        st.subheader("Messages")
        st.dataframe(pd.read_sql_query("SELECT * FROM messages", conn))

        conn.close()

    else:
        st.info("Enter admin credentials")



# PAGE CONFIG 
st.set_page_config(page_title="Club Cafe", layout="wide")


# CUSTOM CSS 
st.markdown("""
<style>
.main-title {
    font-size: 50px;
    font-weight: bold;
    text-align: center;
}
.sub-text {
    text-align: center;
    font-size: 20px;
}
.stButton>button {
    background-color: #4A2C2A;
    color: white;
}
</style>
""", unsafe_allow_html=True)


# SIDEBAR
admin_pass = st.sidebar.text_input(
    "Admin Access",
    type="password"
)

st.sidebar.title(" Club Cafe")
if st.sidebar.button("Logout"):
    st.session_state.user = None

page = st.sidebar.radio(
    "Navigation",
    ["Home", "Menu", "Online Ordering", "Gallery",
     "About Us", "Location & Timings", "Reviews",
     "Contact Us", "Admin Panel"]
)
admin_password = st.sidebar.text_input(
    "Admin Password",
    type="password"
)


# HOME PAGE 
if page == "Home":
    st.markdown('<p class="main-title"> Welcome to Club Cafe</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-text">Delicious Cakes • Cozy Ambience • Sweet Memories</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTBvX34iHo5vbzPBG0b-vONhyOT5c8waSufPA&s",
            use_container_width=True
        )

    st.write("""
    **Club Cafe** offers premium cakes, pastries, and desserts made with love.  
    Perfect for birthdays, celebrations, and sweet cravings!
    """)


# MENU PAGE
elif page == "Menu":
    st.title(" Our Menu")

    # Signature Cakes
    st.subheader(" Signature Cakes")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR_5wELZrcZ1U5ThkVVNQsHkYxoZRX0RXII8Q&s", width=300)
        st.caption("Classic Black Forest")
    with col2:
        st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRT-eW7xysxfcjT0FLUPmjkI16_8IN_VnhfEQ&s", width=300)
        st.caption("Red Velvet Delight")
    with col3:
        st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTNd9udWKCoXTBYn5ba8reyBDVTTohfOPesng&s", width=300)
        st.caption("Chocolate Truffle")

    # Designer Cakes
    st.subheader(" Premium Designer Cakes")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("https://www.indiacakes.com/media/catalog/product/cache/a4577f844569f68fd14659d95bb20f68/a/p/appetizing_ferrero_rocher_cake_1_kg.jpg", width=300)
        st.caption("Ferrero Rocher Cake")
    with col2:
        st.image("https://i0.wp.com/www.darrycakes.com/wp-content/uploads/2019/11/chocolate-oreo-buttercream-cake-25.jpg?fit=1280%2C853&ssl=1", width=300)
        st.caption("Oreo Crunch Cake")
    with col3:
        st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSH9A1GWpYrfDHFc9F6d0erGWDwSZB63FBihw&s", width=300)
        st.caption("Blueberry Cheesecake")

    # Cupcakes
    st.subheader(" Cupcakes")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("https://bonnibakery.com/wp-content/uploads/2024/03/German-Chocolate-Cupcakes_53-1-1024x1024.jpg.webp", width=300)
        st.caption("Chocolate Fudge Cupcake")
    with col2:
        st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT0x9TzmB322pvAgqA0a2cXJuP6FwnitYLRIQ&s", width=300)
        st.caption("Vanilla Sprinkle Cupcake")
    with col3:
        st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSdiiXx7PebgAUz7jgyXGfdXytwnRddVyVftw&s", width=300)
        st.caption("Red Velvet Cupcake")

    # Pastries
    st.subheader(" Pastries")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSeQU_Kopa9mOkCRMUoqkaj7O0lQN7UTfeBPw&s", width=300)
        st.caption("Chocolate Pastry")
    with col2:
        st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcToxvsBPUt1uMGVgkW4EF5e0b-Gy48V4xrDgQ&s", width=300)
        st.caption("Strawberry Pastry")
    with col3:
        st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTXy67fvOijrYBt7qAW6Tq1R_eW2QUiH-j79g&s", width=300)
        st.caption("Butterscotch Pastry")


# ONLINE ORDER
elif page == "Online Ordering":
    st.title("🛒 Online Ordering")

    with st.form("order_form"):
        name = st.text_input("Customer Name")
        phone = st.text_input("Phone Number")
        item = st.selectbox("Select Item", [
            "Classic Black Forest", "Red Velvet Delight",
            "Chocolate Truffle", "Ferrero Rocher Cake",
            "Oreo Crunch Cake", "Chocolate Pastry"
        ])
        quantity = st.number_input("Quantity", min_value=1, value=1)
        address = st.text_area("Delivery Address")
        submit = st.form_submit_button("Place Order")

        if submit:
            if name and phone and address:
                add_order(name, phone, item, quantity, address)
                st.success(f"✅ Order placed successfully! Thank you, {name}.")
                st.balloons()
            else:
                st.error("Please fill all details.")


# GALLERY
elif page == "Gallery":
    st.title(" Gallery")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("https://images.unsplash.com/photo-1542826438-bd32f43d626f", width=300)
    with col2:
        st.image("https://images.unsplash.com/photo-1578985545062-69928b1d9587", width=300)
    with col3:
        st.image("https://images.unsplash.com/photo-1551024601-bec78aea704b", width=300)


# ABOUT 
elif page == "About Us":
    st.title(" About Club Cafe")
    st.image("https://mybites.io/wp-content/uploads/2021/08/Happy-restaurant-team-serving-delicious-dishes.jpg", width=600)
    st.write("""
    At Club Cafe, we bake fresh cakes and desserts daily using premium ingredients.
    We believe in quality, tradition, and making every celebration sweeter.
    """)


# LOCATION
elif page == "Location & Timings":
    st.title("📍 Location")
    st.map(pd.DataFrame({"lat": [18.5204], "lon": [73.8567]}))
    st.write("Open daily: 10 AM – 10 PM")


# REVIEWS
elif page == "Reviews":
    st.title("Customer Reviews")
    st.info("⭐⭐⭐⭐⭐ Loved the cakes and ambience!")


# CONTACT
elif page == "Contact Us":
    st.title("Contact Us")

    with st.form("contact_form"):
        cname = st.text_input("Name")
        cemail = st.text_input("Email")
        message = st.text_area("Message")
        send = st.form_submit_button("Send")

        if send:
            if cname and message:
                add_message(cname, cemail, message)
                st.success("Message saved!")
            else:
                st.error("Fill required fields.")


# ADMIN PANEL
elif page == "Admin Panel":
    if admin_password == "YOUR_SECRET_PASSWORD":
        st.title("Admin Dashboard")

        conn = sqlite3.connect('cafe_database.db')

        st.subheader("Orders")
        st.dataframe(pd.read_sql_query("SELECT * FROM orders", conn))

        st.subheader("Messages")
        st.dataframe(pd.read_sql_query("SELECT * FROM messages", conn))

        conn.close()

    else:
        st.error("Access denied")
