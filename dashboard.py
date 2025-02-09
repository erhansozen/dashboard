import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import date, timedelta

# 📌 SQLite Bağlantısı
conn = sqlite3.connect("tasks.db", check_same_thread=False)
cursor = conn.cursor()

# 📌 Eğer tablolar yoksa oluştur
cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        category TEXT,
        subcategory TEXT,
        task TEXT,
        deadline DATE,
        activity INT
    )
""")
conn.commit()

# 📌 Sayfa Seçimi
st.sidebar.title("📌 Menü")
page = st.sidebar.radio("Gitmek istediğiniz sayfayı seçin:", ["📅 Takvim", "➕ Görev Ekle", "📊 Aktivite Analizi"])

# 📌 📅 TAKVİM SAYFASI
if page == "📅 Takvim":
    st.title("📅 Takvim ve Görevler")

    # Takvim Görünümü Seçimi
    view_type = st.radio("Görünüm Tipi:", ["Günlük", "Haftalık", "Aylık"])

    # Seçime göre tarih aralığı belirle
    today = date.today()
    if view_type == "Günlük":
        start_date, end_date = today, today
    elif view_type == "Haftalık":
        start_date, end_date = today - timedelta(days=today.weekday()), today + timedelta(days=(6 - today.weekday()))
    else:
        start_date, end_date = today.replace(day=1), today.replace(day=28) + timedelta(days=4)  # Yaklaşık 1 ay

    st.write(f"📆 **Görevler {start_date} - {end_date} tarihleri arasında**")

    # Görevleri getir
    cursor.execute("SELECT category, subcategory, task, deadline FROM tasks WHERE deadline BETWEEN ? AND ?", (start_date, end_date))
    tasks = cursor.fetchall()

    if tasks:
        for category, subcategory, task, deadline in tasks:
            st.write(f"📌 **{category} > {subcategory}** - {task} (⏳ {deadline})")
    else:
        st.write("Henüz bu tarihlerde bir görev bulunmuyor.")

# 📌 ➕ GÖREV EKLEME SAYFASI
elif page == "➕ Görev Ekle":
    st.title("➕ Yeni Görev Ekle")

    # Kullanıcı seçimi
    user = st.selectbox("Kullanıcı Seç", ["Ali", "Ayşe", "Mehmet", "Ortak"])

    # Ana Kategori ve Alt Kategori
    categories = {
        "İngilizce": ["Listening", "Reading", "Speaking", "Writing"],
        "Kodlama": ["Python", "JavaScript", "Go"],
        "Spor": ["Koşu", "Fitness", "Yoga"]
    }

    main_category = st.selectbox("Ana Kategori Seç:", list(categories.keys()))
    sub_category = st.selectbox("Alt Kategori Seç:", categories[main_category])

    # Görev Bilgisi
    task = st.text_input("Görev Açıklaması:")
    deadline = st.date_input("Son Tarih:")
    activity = st.number_input("Bu kategori için kaç saat çalıştınız?", min_value=0, step=1)

    # Görev Ekle Butonu
    if st.button("Görevi Kaydet"):
        cursor.execute("INSERT INTO tasks (user, category, subcategory, task, deadline, activity) VALUES (?, ?, ?, ?, ?, ?)",
                       (user, main_category, sub_category, task, deadline, activity))
        conn.commit()
        st.success("✅ Görev başarıyla eklendi!")

# 📌 📊 AKTİVİTE ANALİZİ SAYFASI
elif page == "📊 Aktivite Analizi":
    st.title("📊 Aktivite Analizi")

    # Kullanıcı Seçimi
    user = st.selectbox("Kullanıcı Seç", ["Ali", "Ayşe", "Mehmet", "Ortak"])

    # Görevleri ve Aktiviteyi Getir
    cursor.execute("SELECT category, subcategory, SUM(activity) FROM tasks WHERE user=? GROUP BY category, subcategory", (user,))
    data = cursor.fetchall()

    if data:
        df = pd.DataFrame(data, columns=["Ana Kategori", "Alt Kategori", "Toplam Efor"])
        st.dataframe(df)

        # 📊 Grafik Gösterimi
        st.subheader("📌 Kategori Bazlı Aktivite Dağılımı")
        fig = px.bar(df, x="Alt Kategori", y="Toplam Efor", color="Ana Kategori", title="Kategorilere Göre Efor Dağılımı")
        st.plotly_chart(fig)
    else:
        st.write("Henüz aktivite kaydedilmedi!")
