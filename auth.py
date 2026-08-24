import streamlit as st
import re
import random
from database import get_connection

# ---------------- OTP SYSTEM ----------------
def send_otp(email):
    otp = random.randint(100000, 999999)
    st.session_state["otp"] = otp
    st.session_state["otp_email"] = email
    st.info(f"OTP sent to {email}: {otp}")  # SMTP नंतर add करू

# ---------------- USER SIGNUP ----------------
def signup_form():
    st.subheader("Create Your Account")

    name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    address = st.text_input("Address (Optional)")
    phone = st.text_input("Phone (Optional)")

    # Email format validation
    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if email and not re.match(email_pattern, email):
        st.error("Invalid email format.")

    # Password rules
    password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,16}$"
    if password and not re.match(password_pattern, password):
        st.warning("""
Password must contain:
• At least 1 uppercase letter  
• At least 1 lowercase letter  
• At least 1 number  
• At least 1 special character (@$!%*?&)  
• Length between 8 to 16 characters
""")

    if st.button("Send OTP"):
        if not email:
            st.error("Email is required.")
        else:
            send_otp(email)

    otp_input = st.text_input("Enter OTP")

    if st.button("Sign Up"):
        if not name or not email or not password:
            st.error("Name, Email, Password are required.")
            return

        if "otp" not in st.session_state or otp_input != str(st.session_state["otp"]):
            st.error("Invalid OTP.")
            return

        conn = get_connection()
        c = conn.cursor()

        # Check if email exists
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        if c.fetchone():
            st.error("Email already exists.")
            conn.close()
            return

        # Insert user
        c.execute(
            "INSERT INTO users (name, email, password, address, phone, role, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, email, password, address, phone, "user", "active")
        )
        conn.commit()
        conn.close()

        st.success("Account created successfully! Please login.")

# ---------------- LOGIN (USER + ADMIN) ----------------
def login_form():
    st.subheader("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = c.fetchone()
        conn.close()

        if not user:
            st.error("Invalid email or password.")
            return

        if user[7] == "inactive":
            st.error("Your account is deactivated. Contact admin.")
            return

        st.session_state["user_email"] = user[2]
        st.session_state["role"] = user[6]

        st.success("Login successful!")
        st.experimental_rerun()
