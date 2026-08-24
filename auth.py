import streamlit as st
import sqlite3
from database import get_connection

# ---------------- SAVE USER ----------------
def save_user(name, email, password, address, phone):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        INSERT INTO users (name, email, password, address, phone, role, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, email, password, address, phone, "user", "active"))

    conn.commit()
    conn.close()

# ---------------- GET USER ----------------
def get_user(email, password):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT id, name, email, role, status
        FROM users
        WHERE email=? AND password=?
    """, (email, password))

    user = c.fetchone()
    conn.close()
    return user

# ---------------- SIGNUP FORM ----------------
def signup_form():
    st.subheader("Create Account")

    name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    address = st.text_input("Address")
    phone = st.text_input("Phone")

    if st.button("Sign Up"):
        if not name or not email or not password:
            st.error("Name, Email and Password are required.")
            return

        try:
            save_user(name, email, password, address, phone)
            st.success("Account created successfully! Please login.")
        except sqlite3.IntegrityError:
            st.error("Email already exists. Please use another email.")

# ---------------- LOGIN FORM ----------------
def login_form():
    st.subheader("Login")

    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("Login"):
        user = get_user(email, password)

        if not user:
            st.error("Invalid email or password.")
            return

        user_id, name, email, role, status = user

        if status == "inactive":
            st.error("Your account is deactivated. Contact admin.")
            return

        # Save session
        st.session_state["user_id"] = user_id
        st.session_state["user_name"] = name
        st.session_state["user_email"] = email
        st.session_state["role"] = role

        st.success(f"Welcome {name}!")
        st.rerun()
