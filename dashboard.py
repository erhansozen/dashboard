import streamlit as st
import pandas as pd
import datetime
import random

# 🎯 Başlık
st.title("📊 Kişisel Dashboard")

# 📅 Günlük Tarih ve Saat
st.write(f"Tarih: {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")

# ✅ **Yapılacaklar Listesi**
st.subheader("✅ Yapılacaklar Listesi")
tasks = st.text_area("Bugün neler yapacaksın?", placeholder="Örn: Kod yaz, kitap oku, spora git...")
st.write("📝 Bugünün Planı:")
st.write(tasks)

# 📌 **Hedeflerini Kaydet**
st.subheader("🎯 Hedefler")
goal = st.text_input("Bu hafta başarmak istediğin bir hedef nedir?", placeholder="Örn: 5 saat Python çalış")
if goal:
    st.success(f"Harika! Bu hafta '{goal}' hedefine ulaşmak için çalışacaksın!")

# 📊 **Veri Tablosu (Örnek İlerleme Verisi)**
st.subheader("📈 Günlük Çalışma Saati Takibi")

data = {
    "Tarih": pd.date_range(start="2025-02-01", periods=7, freq="D"),
    "Çalışma Saati": [random.randint(1, 8) for _ in range(7)]
}
df = pd.DataFrame(data)

st.dataframe(df)

# 📈 **Çalışma Saatleri Grafiği**
st.subheader("📉 Haftalık Çalışma Saati Grafiği")
st.line_chart(df.set_index("Tarih"))

# 📌 Motivasyon Notu
st.sidebar.header("💡 Motivasyon Notu")
motivation_quotes = [
    "Başlamak için mükemmel olmak zorunda değilsin, ama mükemmel olmak için başlamalısın.",
    "Bugün yapabileceklerini yarına bırakma!",
    "Başarı, tekrar tekrar denemekten geçer."
]
st.sidebar.write(random.choice(motivation_quotes))

# 🎉 Bitti!
st.write("🚀 Verimli bir gün geçir! 💪")
