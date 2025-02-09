import streamlit as st
import sqlite3

# 📌 SQLite Veritabanı Bağlantısı
conn = sqlite3.connect("tasks.db", check_same_thread=False)
cursor = conn.cursor()

# 📌 Eğer tablo yoksa oluştur
cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        task TEXT
    )
""")
conn.commit()

# 📌 Kullanıcı Seçimi
st.sidebar.title("👥 Kullanıcı Seç")
users = ["Ali", "Ayşe", "Mehmet", "Ortak"]  # Kullanıcı listesi
selected_user = st.sidebar.selectbox("Lütfen bir kullanıcı seç:", users)

if selected_user:
    st.title(f"📌 {selected_user} için Görev Listesi")

    # 📌 Kullanıcıya Ait Görevleri Getir
    cursor.execute("SELECT id, task FROM tasks WHERE user=?", (selected_user,))
    tasks = cursor.fetchall()

    # 📌 Görevleri Listele
    st.subheader("✅ Senin Görevlerin")
    if tasks:
        for task_id, task in tasks:
            col1, col2 = st.columns([0.8, 0.2])
            col1.write(f"✔️ {task}")
            if col2.button("❌", key=f"delete_{task_id}"):
                cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
                conn.commit()
                st.experimental_rerun()
    else:
        st.write("Henüz görev eklenmedi!")

    # 📌 Yeni Görev Ekleme
    new_task = st.text_input("Yeni görev ekle:")
    if st.button("Ekle"):
        cursor.execute("INSERT INTO tasks (user, task) VALUES (?, ?)", (selected_user, new_task))
        conn.commit()
        st.success(f"📝 Yeni görev eklendi: {new_task}")
        st.experimental_rerun()
