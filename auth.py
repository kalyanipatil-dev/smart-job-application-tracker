import streamlit as st
import datetime
import re
import random

from database import get_connection
from crud import add_log

# ---------------- HELPERS ----------------
def validate_email(email: str) -> bool:
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None

def validate_password(password: str) -> (bool, str):
    if len(password) < 8 or len(password) > 16:
        return False, "Password must be 8–16 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one digit."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character."
    return True, ""

def get_user(email, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT id, name, email, role, status FROM users WHERE email=? AND password=?",
        (email, password),
    )
    row = c.fetchone()
    conn.close()
    return row

def get_user_by_username(username):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT id, name, username, email, role, status, first_login, otp_code FROM users WHERE username=?",
        (username,),
    )
    row = c.fetchone()
    conn.close()
    return row

def set_admin_password(user_id, new_password):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "UPDATE users SET password=?, first_login=0 WHERE id=?",
        (new_password, user_id),
    )
    conn.commit()
    conn.close()

def set_otp(user_id, otp_code):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "UPDATE users SET otp_code=? WHERE id=?",
        (otp_code, user_id),
    )
    conn.commit()
    conn.close()

def clear_otp(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "UPDATE users SET otp_code=NULL WHERE id=?",
        (user_id,),
    )
    conn.commit()
    conn.close()

# ---------------- USER SIGNUP ----------------
def signup_form():
    st.subheader("Sign Up")

    name = st.text_input("Full Name")
    username = st.text_input("Username")
    email = st.text_input("Email")
    mobile = st.text_input("Mobile Number")
    password = st.text_input("Password", type="password")
    st.caption("Password must be 8–16 chars, include uppercase, lowercase, digit, special character.")

    if st.button("Create Account"):
        if not name or not username or not email or not mobile or not password:
            st.error("All fields are required.")
            return

        if not mobile.isdigit():
            st.error("Mobile number must contain only digits.")
            return

        if not validate_email(email):
            st.error("Invalid email format.")
            return

        valid, msg = validate_password(password)
        if not valid:
            st.error(msg)
            return

        conn = get_connection()
        c = conn.cursor()
        try:
            c.execute(
                """
                INSERT INTO users (name, username, email, mobile, password, role, status, first_login)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (name, username, email, mobile, password, "user", "active", 0),
            )
            conn.commit()
            st.success("Account created successfully! Please login.")
            add_log(email, "signup", "User signed up")
        except Exception:
            st.error("Username or Email already exists.")
        finally:
            conn.close()

# ---------------- USER LOGIN ----------------
def login_form():
    st.subheader("User Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if not validate_email(email):
            st.error("Invalid email format.")
            return

        user = get_user(email, password)
        if not user:
            st.error("Invalid credentials.")
        else:
            _id, name, email, role, status = user

            if status == "inactive":
                st.error("Account is deactivated.")
                return

            st.session_state["user_id"] = _id
            st.session_state["user_name"] = name
            st.session_state["user_email"] = email
            st.session_state["role"] = role
            add_log(email, "login", "User logged in")
            st.success("Logged in successfully!")
            st.rerun()

# ---------------- ADMIN FIRST LOGIN (USERNAME + EMAIL + OTP) ----------------
def admin_first_login():
    st.sidebar.subheader("Admin First Login")

    username = st.sidebar.text_input("Admin Username")
    email = st.sidebar.text_input("Admin Email")

    if st.sidebar.button("Send Verification Code"):
        user = get_user_by_username(username)
        if not user:
            st.sidebar.error("Admin user not found.")
            return

        _id, name, u_username, u_email, role, status, first_login, otp_code = user

        if role != "admin":
            st.sidebar.error("This account is not admin.")
            return

        if email != u_email:
            st.sidebar.error("Email does not match admin account.")
            return

        if status == "inactive":
            st.sidebar.error("Admin account is deactivated.")
            return

        if first_login == 0:
            st.sidebar.info("First login already completed. Use username + password.")
            return

        otp = str(random.randint(100000, 999999))
        set_otp(_id, otp)

        # NOTE: सध्या testing साठी OTP स्क्रीनवर दाखवते.
        st.sidebar.success(f"Verification code sent. (Testing OTP: {otp})")

        st.session_state["admin_otp_user_id"] = _id

    if "admin_otp_user_id" in st.session_state:
        otp_input = st.sidebar.text_input("Enter Verification Code")

        if st.sidebar.button("Verify Code"):
            user_id = st.session_state["admin_otp_user_id"]
            conn = get_connection()
            c = conn.cursor()
            c.execute("SELECT otp_code FROM users WHERE id=?", (user_id,))
            row = c.fetchone()
            conn.close()

            if not row or not row[0]:
                st.sidebar.error("No OTP found. Please resend.")
                return

            if otp_input != row[0]:
                st.sidebar.error("Invalid verification code.")
                return

            clear_otp(user_id)
            st.sidebar.success("Verification successful. Set your admin password below.")

            new_password = st.sidebar.text_input("New Admin Password", type="password")
            st.sidebar.caption("Password must be 8–16 chars, include uppercase, lowercase, digit, special character.")

            if st.sidebar.button("Set Admin Password"):
                valid, msg = validate_password(new_password)
                if not valid:
                    st.sidebar.error(msg)
                    return

                set_admin_password(user_id, new_password)
                st.sidebar.success("Admin password set successfully. Now login with username + password.")
                del st.session_state["admin_otp_user_id"]

# ---------------- ADMIN NORMAL LOGIN (USERNAME + PASSWORD) ----------------
def admin_normal_login():
    st.sidebar.subheader("Admin Login")

    username = st.sidebar.text_input("Admin Username")
    password = st.sidebar.text_input("Admin Password", type="password")

    if st.sidebar.button("Login as Admin"):
        user = get_user_by_username(username)
        if not user:
            st.sidebar.error("Admin user not found.")
            return

        _id, name, u_username, u_email, role, status, first_login, otp_code = user

        if role != "admin":
            st.sidebar.error("This account is not admin.")
            return

        if status == "inactive":
            st.sidebar.error("Admin account is deactivated.")
            return

        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE id=?", (_id,))
        row = c.fetchone()
        conn.close()

        if not row or row[0] != password:
            st.sidebar.error("Invalid admin password.")
            return

        st.session_state["user_id"] = _id
        st.session_state["user_name"] = name
        st.session_state["user_email"] = u_email
        st.session_state["role"] = role
        st.success("Admin logged in successfully!")
        st.rerun()
