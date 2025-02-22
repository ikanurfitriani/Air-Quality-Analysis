# MIT License

# Copyright (c) 2025 Ika Nurfitriani

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

script_dir = os.path.abspath(os.path.dirname(__file__))
file_path = os.path.join(script_dir, "main_data.csv")

if os.path.exists(file_path):
    data = pd.read_csv(file_path)
    if data.empty:
        st.error("Dataset kosong! Pastikan file CSV memiliki data yang valid.")
        st.stop()
    else:
        print("File berhasil dibaca!")
else:
    st.error("Error: File tidak ditemukan, pastikan path benar atau gunakan alternatif seperti st.file_uploader().")
    st.stop()

required_columns = {"datetime", "PM2.5", "PM10", "season", "time_of_day"}
missing_columns = required_columns - set(data.columns)

if missing_columns:
    st.error(f"Dataset tidak memiliki kolom-kolom berikut: {', '.join(missing_columns)}")
    st.stop()

data["datetime"] = pd.to_datetime(data["datetime"])

image_path = "https://raw.githubusercontent.com/ikanurfitriani/Air-Quality-Analysis/master/dashboard/air-quality.png"
st.sidebar.image(image_path, use_container_width=True)
st.sidebar.markdown("<hr>", unsafe_allow_html=True)

st.sidebar.header("Opsi Filter")
min_date = data["datetime"].min().date()
max_date = data["datetime"].max().date()
start_date = st.sidebar.date_input("Waktu Awal", value=min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("Waktu Akhir", value=max_date, min_value=min_date, max_value=max_date)

if start_date > end_date:
    st.error("Tanggal awal tidak boleh lebih besar dari tanggal akhir!")
    st.stop()

selected_season = st.sidebar.selectbox("Pilih Musim", options=["Semua", "Panas", "Gugur", "Semi", "Dingin"])

filtered_data = data[(data["datetime"] >= pd.to_datetime(start_date)) & (data["datetime"] <= pd.to_datetime(end_date))]
if selected_season != "Semua":
    filtered_data = filtered_data[filtered_data['season'] == selected_season]

st.sidebar.empty()

st.sidebar.markdown(
    """
    <div style="
        margin-top: 20px;  
        text-align: center; 
        font-size: 18px; 
        color: white;">
        Copyright © 2025 Ika Nurfitriani
    </div>
    """,
    unsafe_allow_html=True
)

st.title("Dashboard Kualitas Udara Beijing (12 Stasiun, 2013-2017)")

# Fungsi untuk Menentukan Kategori Kualitas Udara Berdasarkan PM2.5 dan PM10
def categorize_air_quality_pm(row):
    pm25_thresholds = [12, 35.4, 55.4, 150.4, 250.4]
    pm10_thresholds = [54, 154, 254, 354, 424]
    categories = ["Baik", "Sedang", 
                  "Tidak Sehat bagi Kelompok Sensitif", 
                  "Tidak Sehat", "Sangat Tidak Sehat", 
                  "Berbahaya"]
    pm25_category = next((categories[i] for i, t in enumerate(pm25_thresholds) if row["PM2.5"] <= t), "Berbahaya")
    pm10_category = next((categories[i] for i, t in enumerate(pm10_thresholds) if row["PM10"] <= t), "Berbahaya")
    return max(pm25_category, pm10_category, key=categories.index)

filtered_category_summary = filtered_data.copy()
filtered_category_summary['air_quality_category'] = filtered_category_summary.apply(categorize_air_quality_pm, axis=1)
filtered_category_summary['date'] = filtered_category_summary['datetime'].dt.date
dominant_category_per_day = filtered_category_summary.groupby('date')['air_quality_category'].agg(lambda x: x.mode()[0]).reset_index()
category_counts = dominant_category_per_day['air_quality_category'].value_counts().reset_index(name='Jumlah Hari')
category_counts.columns = ['air_quality_category', 'Jumlah Hari']

st.subheader("Jumlah Hari Berdasarkan Kategori Kualitas Udara (PM2.5 dan PM10)")
columns = st.columns(4)
columns2 = st.columns(3)

categories = [
    "Baik", "Sedang",
    "Tidak Sehat bagi Kelompok Sensitif",
    "Tidak Sehat", "Sangat Tidak Sehat", 
    "Berbahaya"
]

for idx, category in enumerate(categories):
    category_data = category_counts[category_counts['air_quality_category'] == category]
    category_count = category_data['Jumlah Hari'].values[0] if not category_data.empty else 0
    if idx < 4:
        with columns[idx]:
            st.markdown(f"<p style='font-size: 18px; color: white;'>{category}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size: 25px; font-weight: bold;'>{category_count} hari</p>", unsafe_allow_html=True)
    else:
        with columns2[idx - 4]:
            st.markdown(f"<p style='font-size: 18px; color: white;'>{category}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size: 25px; font-weight: bold;'>{category_count} hari</p>", unsafe_allow_html=True)

st.subheader("Jumlah Hari Berdasarkan Kategori Kualitas Udara (Dalam Diagram Batang)")
fig8, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=category_counts, x='air_quality_category', y='Jumlah Hari', 
            hue='air_quality_category', palette='coolwarm', ax=ax)
ax.set_title('Jumlah Hari Berdasarkan Kategori Kualitas Udara (PM2.5 dan PM10)', fontsize=14, fontweight='bold')
ax.set_xlabel('')
ax.set_ylabel('')
ax.set_xticklabels([])
plt.xticks(rotation=45, ha='right')
handles, labels = ax.get_legend_handles_labels()
if not handles:
    ax.legend(handles=[plt.Line2D([0], [0], color=color, lw=4) for color in sns.color_palette('coolwarm', 6)], 
              labels=categories, title='Kategori Kualitas Udara', loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3)
st.pyplot(fig8)
plt.close(fig8)

st.subheader("Persentase Jumlah Hari Berdasarkan Kategori Kualitas Udara (PM2.5 dan PM10)")
category_counts = category_counts.set_index('air_quality_category')['Jumlah Hari']
fig9, ax = plt.subplots(figsize=(8, 8))
ax.pie(category_counts, autopct='%1.1f%%', startangle=90, 
       colors=sns.color_palette('coolwarm', len(category_counts)), labels=None)
ax.set_title('Persentase Jumlah Hari Berdasarkan Kategori Kualitas Udara (PM2.5 dan PM10)', fontsize=14, fontweight='bold')
plt.legend(category_counts.index, title='Kategori Kualitas Udara', loc='lower center', 
           bbox_to_anchor=(0.5, -0.1), ncol=3)
st.pyplot(fig9)
plt.close(fig9)

# Pertanyaan 1: Tren PM2.5 dan PM10 (2013-2017)
st.subheader("Tren Perubahan PM2.5 dan PM10 (2013-2017)")
trend_pm = (
    filtered_data.groupby(['year', 'month'])[['PM2.5', 'PM10']]
    .mean()
    .reset_index()
)
trend_pm['year_month'] = pd.to_datetime(trend_pm[['year', 'month']].assign(day=1))
fig1, ax1 = plt.subplots(figsize=(14, 8))
sns.lineplot(data=trend_pm, x='year_month', y='PM2.5', label='PM2.5', color='steelblue', linewidth=2.5)
sns.lineplot(data=trend_pm, x='year_month', y='PM10', label='PM10', color='darkorange', linewidth=2.5)
ax1.set_title('Tren Perubahan PM2.5 dan PM10 (2013-2017)', fontsize=16, fontweight='bold')
ax1.set_xlabel('Periode Waktu')
ax1.set_ylabel('Konsentrasi Rata-rata (µg/m³)')
st.pyplot(fig1)
plt.close(fig1)

# Pertanyaan 2: PM2.5 dan PM10 di Pagi dan Sore
st.subheader("Rata-rata PM2.5 dan PM10 di Pagi dan Sore Berdasarkan Musim")
seasonal_trends = (
    filtered_data[filtered_data['time_of_day'].isin(['Pagi', 'Sore'])]
    .groupby(['season', 'time_of_day'])[['PM2.5', 'PM10']]
    .mean()
    .reset_index()
)
fig2, ax2 = plt.subplots(2, 1, figsize=(12, 16))
sns.barplot(data=seasonal_trends, x='season', y='PM2.5', hue='time_of_day', ax=ax2[0], palette="coolwarm")
ax2[0].set_title('Rata-rata PM2.5 di Pagi dan Sore')
sns.barplot(data=seasonal_trends, x='season', y='PM10', hue='time_of_day', ax=ax2[1], palette="coolwarm")
ax2[1].set_title('Rata-rata PM10 di Pagi dan Sore')
st.pyplot(fig2)
plt.close(fig2)

# Pertanyaan 3: Tren Polutan Gas
st.subheader("Tren Polutan Gas (SO2, NO2, CO, O3) (2013-2017)")
trend_gases = (
    filtered_data.groupby(['year', 'month'])[['SO2', 'NO2', 'CO', 'O3']]
    .mean()
    .reset_index()
)
trend_gases['year_month'] = pd.to_datetime(trend_gases[['year', 'month']].assign(day=1))
fig3, ax3 = plt.subplots(figsize=(16, 10))
sns.lineplot(data=trend_gases, x='year_month', y='SO2', label='SO2', color='darkblue')
sns.lineplot(data=trend_gases, x='year_month', y='NO2', label='NO2', color='green')
sns.lineplot(data=trend_gases, x='year_month', y='CO', label='CO', color='red')
sns.lineplot(data=trend_gases, x='year_month', y='O3', label='O3', color='purple')
ax3.set_title('Tren Polutan Gas (SO2, NO2, CO, O3)', fontsize=16, fontweight='bold')
st.pyplot(fig3)
plt.close(fig3)

# Pertanyaan 4: Tekanan Udara vs PM2.5 dan PM10
st.subheader("Hubungan Tekanan Udara (PRES) dengan PM2.5 dan PM10")
fig4, ax4 = plt.subplots(figsize=(14, 8))
sns.regplot(data=filtered_data, x='PRES', y='PM2.5', scatter_kws={'alpha': 0.5}, label='PM2.5', color='blue', ax=ax4)
sns.regplot(data=filtered_data, x='PRES', y='PM10', scatter_kws={'alpha': 0.5}, label='PM10', color='orange', ax=ax4)
ax4.set_title('Tekanan Udara vs PM2.5 & PM10')
ax4.legend()
st.pyplot(fig4)
plt.close(fig4)

# Pertanyaan 5: Kecepatan Angin vs Polutan
st.subheader("Distribusi Polutan Berdasarkan Kecepatan Angin")
if 'wind_speed_category' in filtered_data.columns:
    wind_speed_palette = {'Low (<1 m/s)': 'steelblue', 'High (≥1 m/s)': 'darkorange'}
    fig5, ax5 = plt.subplots(1, 2, figsize=(14, 8))
    sns.boxplot(data=filtered_data, x='wind_speed_category', y='PM2.5', ax=ax5[0], 
                hue='wind_speed_category', palette=wind_speed_palette, dodge=False, legend=False)
    ax5[0].set_title('Distribusi PM2.5 Berdasarkan Kecepatan Angin')
    sns.boxplot(data=filtered_data, x='wind_speed_category', y='PM10', ax=ax5[1], 
                hue='wind_speed_category', palette=wind_speed_palette, dodge=False, legend=False)
    ax5[1].set_title('Distribusi PM10 Berdasarkan Kecepatan Angin')
    st.pyplot(fig5)
    plt.close(fig5)
else:
    st.error("Kolom 'wind_speed_category' tidak ditemukan di dataset.")

# Pertanyaan 6: Dampak Hujan Deras terhadap PM2.5 dan PM10
st.subheader("Dampak Hujan Deras (>20 mm) terhadap Konsentrasi PM2.5 dan PM10")
rain_heavy = filtered_data[filtered_data['RAIN'] > 20]
if not rain_heavy.empty:
    avg_pm_heavy = rain_heavy[['PM2.5', 'PM10']].mean()
    pm_data = pd.DataFrame({
        'Polutan': ['PM2.5', 'PM10'],
        'Konsentrasi Rata-rata (µg/m³)': [avg_pm_heavy['PM2.5'], avg_pm_heavy['PM10']]
    })

    fig6, ax6 = plt.subplots(figsize=(8, 6))
    sns.barplot(data=pm_data, x='Polutan', y='Konsentrasi Rata-rata (µg/m³)', hue='Polutan', palette='Blues', dodge=False, legend=False)
    ax6.set_title('Rata-rata Konsentrasi PM2.5 dan PM10 pada Hujan Deras (>20 mm)', fontsize=14, fontweight='bold')
    ax6.set_ylabel('Konsentrasi (µg/m³)')
    st.pyplot(fig6)
    plt.close(fig6)
else:
    st.write("Tidak ada data hujan deras (>20 mm) pada rentang waktu yang dipilih.")

# Pertanyaan 7: Pengaruh Penurunan Suhu Malam terhadap Polutan Berbahaya (CO, NO2, SO2)
st.subheader("Pengaruh Penurunan Suhu Malam terhadap Polutan Berbahaya (CO, NO2, SO2)")
night_time = filtered_data[(filtered_data['hour'] >= 18) | (filtered_data['hour'] <= 6)]
if not night_time.empty:
    fig7, ax7 = plt.subplots(1, 3, figsize=(18, 6))

    sns.scatterplot(data=night_time, x='TEMP', y='CO', color='blue', ax=ax7[0], alpha=0.5)
    ax7[0].set_title('Suhu (TEMP) vs CO', fontsize=12)
    ax7[0].set_xlabel('Suhu (°C)')
    ax7[0].set_ylabel('Kadar CO (µg/m³)')

    sns.scatterplot(data=night_time, x='TEMP', y='NO2', color='green', ax=ax7[1], alpha=0.5)
    ax7[1].set_title('Suhu (TEMP) vs NO2', fontsize=12)
    ax7[1].set_xlabel('Suhu (°C)')
    ax7[1].set_ylabel('Kadar NO2 (µg/m³)')

    sns.scatterplot(data=night_time, x='TEMP', y='SO2', color='red', ax=ax7[2], alpha=0.5)
    ax7[2].set_title('Suhu (TEMP) vs SO2', fontsize=12)
    ax7[2].set_xlabel('Suhu (°C)')
    ax7[2].set_ylabel('Kadar SO2 (µg/m³)')

    plt.tight_layout()
    st.pyplot(fig7)
    plt.close(fig7)
else:
    st.write("Tidak ada data suhu malam hari pada rentang waktu yang dipilih.")

plt.close('all')