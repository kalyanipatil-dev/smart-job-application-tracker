import hashlib
import hmac
import os
import re

import streamlit as st

from database import get_connection
from crud import add_log


EMAIL_RE = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$"
)


def validate_email(email):
    email = email.strip()
    return bool(EMAIL_RE.fullmatch(email))


def validate_password(password):
    if len(password) < 8 or len(password) > 16:
        return False, "Password must be 8–16 characters long."

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."

    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one digit."

    if not re.search(
        r"""[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\/'`~;]""",
        password
    ):
        return False, "Password must contain at least one special character."

    return True, ""


def validate_mobile(mobile):
    mobile = mobile.strip()

    if not mobile:
        return False, "Mobile number is required."

    if not mobile.isdigit():
        return False, "Invalid mobile number. Please use numbers only (0–9)."

    return True, ""


def hash_password(password):
    salt = os.urandom(16)

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        120000
    )

    return "pbkdf2_sha256$120000$%s$%s" % (
        salt.hex(),
        digest.hex()
    )


def verify_password(password, stored):
    if not stored:
        return False, False

    if stored.startswith("pbkdf2_sha256$"):
        try:
            _, iterations, salt_hex, digest_hex = stored.split("$", 3)

            digest = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode(),
                bytes.fromhex(salt_hex),
                int(iterations)
            )

            return hmac.compare_digest(
                digest.hex(),
                digest_hex
            ), False

        except (ValueError, TypeError):
            return False, False

    return hmac.compare_digest(
        password,
        stored
    ), True


def get_user_by_email(email):
    conn = get_connection()

    row = conn.execute(
        """
        SELECT
            id,
            name,
            username,
            email,
            mobile,
            password,
            role,
            status
        FROM users
        WHERE LOWER(email) = LOWER(?)
        """,
        (email.strip(),)
    ).fetchone()

    conn.close()

    return row


def get_user_by_username(username):
    conn = get_connection()

    row = conn.execute(
        """
        SELECT
            id,
            name,
            username,
            email,
            mobile,
            password,
            role,
            status,
            first_login,
            otp_code
        FROM users
        WHERE LOWER(username) = LOWER(?)
        """,
        (username.strip(),)
    ).fetchone()

    conn.close()

    return row


def _upgrade_plaintext_password(user_id, password):
    conn = get_connection()

    conn.execute(
        """
        UPDATE users
        SET password=?
        WHERE id=?
        """,
        (
            hash_password(password),
            user_id
        )
    )

    conn.commit()
    conn.close()


def signup_form():
    st.subheader("Create Account")

    name = st.text_input(
        "Full Name",
        key="signup_name"
    )

    username = st.text_input(
        "Username",
        key="signup_username"
    )

    email = st.text_input(
        "Email",
        key="signup_email"
    )

    mobile = st.text_input(
        "Mobile Number",
        key="signup_mobile"
    )

    password = st.text_input(
        "Password",
        type="password",
        key="signup_password"
    )

    st.caption(
        "Password: 8–16 characters, with uppercase, lowercase, "
        "number and special character."
    )

    st.caption(
        "Mobile: numbers only. No fixed length is enforced "
        "for international users."
    )

    if st.button(
        "Create Account",
        key="signup_btn",
        type="primary"
    ):
        name = name.strip()
        username = username.strip()
        email = email.strip().lower()
        mobile = mobile.strip()

        if not all(
            [name, username, email, mobile, password]
        ):
            st.error("All fields are required.")
            return

        valid_mobile, mobile_msg = validate_mobile(mobile)

        if not valid_mobile:
            st.error(mobile_msg)
            return

        if not validate_email(email):
            st.error(
                "Invalid email address. Please enter a valid email."
            )
            return

        valid_pass, pass_msg = validate_password(password)

        if not valid_pass:
            st.error(pass_msg)
            return

        if get_user_by_email(email):
            st.error(
                "An account with this email already exists. "
                "Please log in instead."
            )
            return

        if get_user_by_username(username):
            st.error(
                "That username is already in use. "
                "Please choose another username."
            )
            return

        conn = get_connection()

        try:
            conn.execute(
                """
                INSERT INTO users
                (
                    name,
                    username,
                    email,
                    mobile,
                    password,
                    role,
                    status,
                    first_login
                )
                VALUES (?, ?, ?, ?, ?, 'user', 'active', 0)
                """,
                (
                    name,
                    username,
                    email,
                    mobile,
                    hash_password(password)
                )
            )

            conn.commit()

        except Exception as exc:
            conn.rollback()

            if "unique" in str(exc).lower():
                st.error(
                    "Email or username already exists."
                )
            else:
                st.error(
                    "Unable to create the account. Please try again."
                )

            return

        finally:
            conn.close()

        add_log(
            email,
            "SIGNUP",
            "User created an account."
        )

        st.success(
            "Account created successfully. Please log in."
        )


def login_form():
    st.subheader("Login")

    email = st.text_input(
        "Email",
        key="user_login_email"
    )

    password = st.text_input(
        "Password",
        type="password",
        key="user_login_pass"
    )

    if st.button(
        "Login",
        key="user_login_btn",
        type="primary"
    ):
        email = email.strip().lower()

        if not validate_email(email):
            st.error(
                "Invalid email address. Please enter a valid email."
            )
            return

        user = get_user_by_email(email)

        if not user:
            st.error("Invalid credentials.")
            return

        if user["status"] != "active":
            st.error("Account is deactivated.")
            return

        valid, was_plaintext = verify_password(
            password,
            user["password"]
        )

        if not valid:
            st.error("Invalid credentials.")
            return

        if was_plaintext:
            _upgrade_plaintext_password(
                user["id"],
                password
            )

        st.session_state["user_id"] = user["id"]
        st.session_state["user_name"] = user["name"]
        st.session_state["user_email"] = user["email"]
        st.session_state["role"] = user["role"]

        add_log(
            user["email"],
            "LOGIN",
            "User logged in."
        )

        st.success(
            "Logged in successfully!"
        )

        st.rerun()


def admin_normal_login(admin):
    st.subheader("🔐 Admin Login")

    username = st.text_input(
        "Admin Username",
        value=admin["username"],
        key="admin_normal_username"
    )

    password = st.text_input(
        "Admin Password",
        type="password",
        key="admin_normal_pass"
    )

    if st.button(
        "Login as Admin",
        key="admin_normal_login_btn",
        type="primary"
    ):
        if username.strip().lower() != admin["username"].lower():
            st.error("Invalid admin credentials.")
            return

        if admin["status"] != "active":
            st.error("Admin account is deactivated.")
            return

        valid, was_plaintext = verify_password(
            password,
            admin["password"]
        )

        if not valid:
            st.error("Invalid admin credentials.")
            return

        if was_plaintext:
            _upgrade_plaintext_password(
                admin["id"],
                password
            )

        st.session_state["user_id"] = admin["id"]
        st.session_state["user_name"] = admin["name"]
        st.session_state["user_email"] = admin["email"]
        st.session_state["role"] = "admin"

        st.session_state.pop(
            "show_admin_login",
            None
        )

        add_log(
            admin["email"],
            "ADMIN_LOGIN",
            "Admin logged in."
        )

        st.success(
            "Admin logged in successfully!"
        )

        st.rerun()


def logout_user():
    email = st.session_state.get(
        "user_email"
    )

    if email:
        add_log(
            email,
            "LOGOUT",
            "User logged out."
        )

    for key in [
        "user_id",
        "user_name",
        "user_email",
        "role",
        "show_admin_login",
        "admin_otp_user_id",
        "admin_verified",
        "confirm_delete_id"
    ]:
        st.session_state.pop(
            key,
            None
        )
