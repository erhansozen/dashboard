import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime, timedelta
from st_aggrid import AgGrid, GridOptionsBuilder

# 📌 SQLite Bağlantısı
conn = sqlite3.connect("tasks.db", check_same_thread=False)
cursor = conn.cursor()

# 📌 Eksik Sütunları Ekleyelim
try:
    cursor.execute("ALTER TABLE tasks ADD COLUMN start_time TEXT;")
    cursor.execute("ALTER TABLE tasks ADD COLUMN end_time TEXT;")
    conn.commit()
except sqlite3.OperationalError:
    pass  # Eğer sütunlar zaten varsa hata almamak için

# 📌 Eğer tablo yoksa oluştur
cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        category TEXT,
        subcategory TEXT,
        task TEXT,
        deadline DATE,
        start_time TEXT,
        end_time TEXT,
        activity INT
    )
""")
conn.commit()

# 📌 Sayfa Seçimi (Ana Menü)
st.sidebar.title("📌 Menü")
page = st.sidebar.radio("Gitmek istediğiniz sayfayı seçin:", ["🏠 Ana Sayfa", "📅 Takvim", "➕ Görev Ekle", "📊 Aktivite Analizi"])

# 📌 Kullanıcı Seçimi
st.sidebar.subheader("👥 Kullanıcı Seç")
users = ["Erhan", "Harun"]
selected_user = st.sidebar.radio("Kullanıcıyı Seç:", users)

# 📌 🏠 ANA SAYFA
if page == "🏠 Ana Sayfa":
    st.title(f"🏠 {selected_user} için Kişisel Dashboard")

    # 📅 Günlük Plan
    st.subheader(f"📆 {selected_user} için Bugün Neler Yapacaksın?")
    tasks_today = st.text_area("Bugünün Planı", placeholder="Örn: Kod yaz, kitap oku, spor yap...")
    
    st.subheader("📝 Notlar")
    notes = st.text_area("Bugün için önemli notlarını buraya ekleyebilirsin.")

    # 📊 Haftalık Çalışma Saati Grafiği
    st.subheader("📈 Haftalık Çalışma Saati Grafiği")
    cursor.execute("SELECT deadline, SUM(activity) FROM tasks WHERE user=? GROUP BY deadline ORDER BY deadline DESC LIMIT 7", (selected_user,))
    data = cursor.fetchall()
    
    if data:
        df = pd.DataFrame(data, columns=["Tarih", "Toplam Efor"])
        df["Tarih"] = pd.to_datetime(df["Tarih"])
        fig = px.line(df, x="Tarih", y="Toplam Efor", title=f"{selected_user} için Haftalık Çalışma Saati Grafiği", color_discrete_sequence=["blue"] if selected_user == "Erhan" else ["red"])
        st.plotly_chart(fig)
    else:
        st.write(f"📊 {selected_user} için henüz çalışma verisi yok!")

# 📌 📅 TAKVİM SAYFASI
elif page == "📅 Takvim":
    st.title(f"📅 {selected_user} için Takvim ve Görevler")

    # 📆 Görünüm Seçimi
    view_type = st.radio("📅 Görünüm Tipi:", ["Günlük", "Haftalık", "Aylık"])

    # Tarih Aralığı Belirleme
    today = datetime.today().date()
    if view_type == "Günlük":
        start_date, end_date = today, today
    elif view_type == "Haftalık":
        start_date, end_date = today - timedelta(days=today.weekday()), today + timedelta(days=(6 - today.weekday()))
    else:
        start_date, end_date = today.replace(day=1), today.replace(day=28) + timedelta(days=4)

    st.write(f"📆 **{start_date} - {end_date} tarihleri arasındaki görevler**")

    # Görevleri Getir
    cursor.execute("""
        SELECT user, category, subcategory, task, deadline, start_time, end_time
        FROM tasks 
        WHERE deadline BETWEEN ? AND ? 
        ORDER BY deadline, start_time
    """, (start_date, end_date))
    tasks = cursor.fetchall()

    if tasks:
        df = pd.DataFrame(tasks, columns=["Kullanıcı", "Kategori", "Alt Kategori", "Görev", "Tarih", "Başlangıç", "Bitiş"])
        df["Tarih"] = pd.to_datetime(df["Tarih"])
        df["Başlangıç"] = pd.to_datetime(df["Başlangıç"], format='%H:%M:%S').dt.time
        df["Bitiş"] = pd.to_datetime(df["Bitiş"], format='%H:%M:%S').dt.time

        # 📌 Takvimi Grid Formatında Gösterelim
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination()
        gb.configure_default_column(editable=True)
        grid_options = gb.build()
        AgGrid(df, gridOptions=grid_options, height=400)

    else:
        st.write("⛔ Bu tarih aralığında görev bulunmuyor.")

# 📌 ➕ GÖREV EKLEME SAYFASI
elif page == "➕ Görev Ekle":
    st.title("➕ Yeni Görev Ekle")

    user = st.selectbox("Görev Atanacak Kullanıcı:", users)
    categories = {
        "İngilizce": ["Listening", "Reading", "Speaking", "Writing"],
        "Kodlama": ["Python", "JavaScript", "Go"],
        "Spor": ["Koşu", "Fitness", "Yoga"]
    }

    main_category = st.selectbox("Ana Kategori Seç:", list(categories.keys()))
    sub_category = st.selectbox("Alt Kategori Seç:", categories[main_category])
    task = st.text_input("Görev Açıklaması:")
    deadline = st.date_input("Son Tarih:")
    start_time = st.time_input("Başlangıç Saati:")
    end_time = st.time_input("Bitiş Saati:")
    activity = st.number_input("Bu kategori için kaç saat çalıştınız?", min_value=0, step=1)

    if st.button("Görevi Kaydet"):
        cursor.execute("""
            INSERT INTO tasks (user, category, subcategory, task, deadline, start_time, end_time, activity) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user, main_category, sub_category, task, deadline, start_time, end_time, activity))
        conn.commit()
        st.success("✅ Görev başarıyla eklendi!")

# 📊 AKTİVİTE ANALİZİ SAYFASI
elif page == "📊 Aktivite Analizi":
    st.title("📊 Aktivite Analizi")

    cursor.execute("SELECT category, subcategory, SUM(activity) FROM tasks WHERE user=? GROUP BY category, subcategory", (selected_user,))
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
