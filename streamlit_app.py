import streamlit as st
import sqlite3

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="Voting App", layout="centered")

# -------------------- HIDE STREAMLIT UI --------------------
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# -------------------- DB --------------------
conn = sqlite3.connect("voting.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT,
    voted INTEGER DEFAULT 0
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS votes (
    option TEXT
)
""")

conn.commit()

# -------------------- FUNCTIONS --------------------
def register(username, password):
    if not username or not password:
        return False, "সব তথ্য দিন"

    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True, "রেজিস্ট্রেশন সফল হয়েছে ✅"
    except:
        return False, "এই ইউজার আগে থেকেই আছে"


def login(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    return c.fetchone()


def vote(username, option):
    c.execute("SELECT voted FROM users WHERE username=?", (username,))
    result = c.fetchone()

    if result and result[0] == 1:
        return False

    c.execute("INSERT INTO votes (option) VALUES (?)", (option,))
    c.execute("UPDATE users SET voted=1 WHERE username=?", (username,))
    conn.commit()
    return True


def results():
    c.execute("SELECT option, COUNT(*) FROM votes GROUP BY option")
    return dict(c.fetchall())


def total_votes():
    c.execute("SELECT COUNT(*) FROM votes")
    return c.fetchone()[0]


# -------------------- SESSION --------------------
if "user" not in st.session_state:
    st.session_state.user = None


# -------------------- UI --------------------
st.title("🗳️ নির্বাচনের সম্ভাব্য ফলাফল অনলাইনে যাচাই করুন")

# 🔐 Privacy Message
st.info("🔒 আপনার তথ্য গোপন থাকবে")

# -------------------- AUTH --------------------
if not st.session_state.user:

    menu = ["Login", "Register"]
    choice = st.sidebar.selectbox("Menu", menu)

    # -------- Register --------
    if choice == "Register":
        st.subheader("রেজিস্টার করুন")

        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Register"):
            success, msg = register(u, p)
            if success:
                st.success(msg)
            else:
                st.error(msg)

    # -------- Login --------
    elif choice == "Login":
        st.subheader("লগইন করুন")

        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            user = login(u, p)

            if user:
                st.session_state.user = u
                st.success("লগইন সফল ✅")
                st.rerun()
            else:
                st.error("ভুল ইউজারনেম বা পাসওয়ার্ড ❌")


# -------------------- MAIN APP --------------------
else:
    st.success(f"স্বাগতম {st.session_state.user} 🎉")

    # -------- Voting --------
    option = st.radio("আপনার ভোট দিন:", ["লাল", "গেরুয়া", "সবুজ"])

    if st.button("Vote"):
        if vote(st.session_state.user, option):
            st.success("ভোট সফলভাবে জমা হয়েছে ✅")
        else:
            st.warning("আপনি ইতিমধ্যেই ভোট দিয়েছেন ❗")

    # -------- Results --------
    st.subheader("📊 ফলাফল")
    res = results()

    for k in ["লাল", "গেরুয়া", "সবুজ"]:
        st.write(f"{k}: {res.get(k, 0)}")

    st.subheader(f"🧮 মোট ভোট: {total_votes()}")

    # -------- Logout --------
    if st.button("Logout"):
        st.session_state.user = None
        st.rerun()

    # -------- Footer / Donation --------
    st.markdown("---")

    st.markdown("### 🎉 এটি একটি fun app")
    st.write("কোনো রকম ব্যক্তিগত তথ্য নেওয়া উদ্দেশ্য নয়।")

    st.markdown("### ❤️ Support করুন")
    st.write("এই অ্যাপটি কে develop করতে donate করুন এই QR CODE এ:")

    # 👉 QR IMAGE (make sure file exists in same folder)
    st.image("qr.png", width=250)
