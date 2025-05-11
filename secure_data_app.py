import streamlit as st
import hashlib
from cryptography.fernet import Fernet
import base64

# ----- Encryption Setup -----
KEY = Fernet.generate_key()
cipher = Fernet(KEY)

def hash_passkey(passkey):
    return hashlib.sha256(passkey.encode()).hexdigest()

def encrypt_data(text, passkey):
    return cipher.encrypt(text.encode()).decode()

def decrypt_data(encrypted_text, passkey):
    hashed_passkey = hash_passkey(passkey)
    for value in st.session_state.stored_data.values():
        if value["encrypted_text"] == encrypted_text and value["passkey"] == hashed_passkey:
            st.session_state.failed_attempts = 0
            return cipher.decrypt(encrypted_text.encode()).decode()
    st.session_state.failed_attempts += 1
    return None

# ----- Initialize Session -----
if 'stored_data' not in st.session_state:
    st.session_state.stored_data = {}
if 'failed_attempts' not in st.session_state:
    st.session_state.failed_attempts = 0
if 'is_authorized' not in st.session_state:
    st.session_state.is_authorized = True

# ----- Set Page Config -----
st.set_page_config(page_title="Secure Data Encryption System", layout="centered")

# ----- Background Styling -----
def set_bg():
    bg_img = "https://png.pngtree.com/background/20210711/original/pngtree-beautiful-technology-website-business-poster-background-template-picture-image_1107136.jpg"
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url('{bg_img}');
            background-size: cover;
            background-position: center;
            font-family: 'Segoe UI', sans-serif;
        }}
        .glassbox {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            color: white;
        }}
        .input-box input {{
            background-color: rgba(255, 255, 255, 0.15);
            border: none;
            color: white;
        }}
        </style>
    """, unsafe_allow_html=True)

set_bg()

# ----- Page Title -----
st.markdown("""
<div style='text-align:center;'>
    <img src='https://img.icons8.com/fluency/96/000000/security-checked.png' width='80'/>
    <h1 style='color:white;'>Secure Data Encryption System</h1>
</div>
""", unsafe_allow_html=True)

# ----- Navigation -----
menu = ["Home", "Store Data", "Retrieve Data", "Login"]
choice = st.selectbox("Navigate", menu)

# ----- Home Page -----
if choice == "Home":
    st.markdown("""
    <div class='glassbox'>
    <h3>🔐 Welcome!</h3>
    <p>This system securely stores and retrieves your data using encryption and passkeys.</p>
    <p>⚠️ After 3 failed attempts, you must reauthorize via login.</p>
    </div>
    """, unsafe_allow_html=True)

# ----- Store Data Page -----
elif choice == "Store Data":
    st.markdown("<div class='glassbox'>", unsafe_allow_html=True)
    st.subheader("📦 Store Your Secret")
    user_data = st.text_area("Enter data to secure:")
    passkey = st.text_input("Create a Passkey:", type="password")
    if st.button("🔐 Encrypt & Save"):
        if user_data and passkey:
            hashed = hash_passkey(passkey)
            encrypted = encrypt_data(user_data, passkey)
            st.session_state.stored_data[encrypted] = {
                "encrypted_text": encrypted,
                "passkey": hashed
            }
            st.success("✅ Data encrypted and stored!")
            st.code(encrypted, language="text")
        else:
            st.error("❗ Please enter both data and passkey.")
    st.markdown("</div>", unsafe_allow_html=True)

# ----- Retrieve Data Page -----
elif choice == "Retrieve Data":
    if not st.session_state.is_authorized:
        st.warning("🔐 Login required after 3 failed attempts.")
        st.stop()

    st.markdown("<div class='glassbox'>", unsafe_allow_html=True)
    st.subheader("🔓 Retrieve Your Data")
    encrypted_text = st.text_area("Paste your encrypted data:")
    passkey = st.text_input("Enter your Passkey:", type="password")

    if st.button("🔎 Decrypt"):
        if encrypted_text and passkey:
            result = decrypt_data(encrypted_text, passkey)
            if result:
                st.success("✅ Decrypted text:")
                st.code(result, language="text")
            else:
                attempts = st.session_state.failed_attempts
                st.error(f"❌ Incorrect passkey! Attempts left: {3 - attempts}")
                if attempts >= 3:
                    st.session_state.is_authorized = False
                    st.warning("🚫 3 failed attempts! Redirecting to login...")
                    st.experimental_rerun()
        else:
            st.error("❗ Both fields required.")
    st.markdown("</div>", unsafe_allow_html=True)

# ----- Login Page -----
elif choice == "Login":
    st.markdown("<div class='glassbox'>", unsafe_allow_html=True)
    st.subheader("🔐 Reauthorization")
    login_pass = st.text_input("Enter Master Password:", type="password")

    if st.button("✅ Login"):
        if login_pass == "admin123":
            st.session_state.failed_attempts = 0
            st.session_state.is_authorized = True
            st.success("🎉 Reauthorized! You can now access your data.")
        else:
            st.error("❌ Wrong password. Try again.")
    st.markdown("</div>", unsafe_allow_html=True)
