import streamlit as st
import pandas as pd
import datetime
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
import json
import os

df = pd.read_excel("accident.xlsx")

st.set_page_config(layout="wide")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

vehicle_counts = df["vehicle_type"].value_counts().reset_index()
vehicle_counts.columns = ["vehicle_type", "count"]

image = Image.open('f1.jpg')

col1, col2 = st.columns([0.1, 0.9])
with col1:
    st.image(image, width=100)
html_title = """
    <style>
        .title-test {
            font-weight:bold;
            padding:5px;
            border-radius:6px;
        }
    </style>
    <center><h1 class="title-test">Accident 2019-2024 in Thailand</h1></center>
    """
st.subheader("Accident Data (accident.csv)")
st.dataframe(df)

csv = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8")


# ข้อมูลอุบัติเหตุทั้งหมด
total_accidents = len(df)
st.metric("เกิดอุบัติเหตุทั้งหมด (ครั้ง)", total_accidents)

# ข้อมูลอุบัติเหตุแยกตามปี
df["incident_datetime"] = pd.to_datetime(df["incident_datetime"])
df["Year"] = df["incident_datetime"].dt.year

# สร้าง dictionary เพื่อเก็บข้อมูลอุบัติเหตุแยกตามปี
accidents_by_year = {}
for year in range(2019, 2025):
    accidents_by_year[year] = df[df["Year"] == year]

# คำนวณค่าสถิติ
def calculate_statistics(data):
    if len(data) > 0:
        min_injuries = data["number_of_injuries"].min()
        max_injuries = data["number_of_injuries"].max()
        avg_injuries = data["number_of_injuries"].mean()
        total_injuries = data["number_of_injuries"].sum()
    else:
        min_injuries, max_injuries, avg_injuries, total_injuries = 0, 0, 0, 0
    return min_injuries, max_injuries, avg_injuries, total_injuries

# แสดงข้อมูลในตาราง
num_cols = 2  # จำนวนคอลัมน์ที่ต้องการแสดง
num_years = len(accidents_by_year)
num_rows = (num_years + num_cols - 1) // num_cols  # คำนวณจำนวนแถวที่ต้องการ

for i in range(num_rows):
    cols = st.columns(num_cols)
    for j in range(num_cols):
        year_index = i * num_cols + j
        if year_index < num_years:
            year = list(accidents_by_year.keys())[year_index]
            data = accidents_by_year[year]
            min_injuries, max_injuries, avg_injuries, total_injuries = calculate_statistics(data)

            with cols[j]:
                st.subheader(f"จำนวนอุบัติเหตุในปี {year}")
                st.metric("จำนวนอุบัติเหตุ", len(data))
                st.write(f"Min Injuries: {min_injuries}")
                st.write(f"Max Injuries: {max_injuries}")
                st.write(f"Avg Injuries: {avg_injuries:.2f}")
                st.write(f"Total Injuries: {total_injuries}")

with col2:
    st.markdown(html_title, unsafe_allow_html=True)

# กราฟ 3 แถว แถวละ 3 กราฟ
col_graphs = st.columns(3)

with col_graphs[0]:
    fig = px.bar(vehicle_counts, x="vehicle_type", y="count",
                 labels={"count": "Number of Vehicles"},
                 title="Number of Vehicles by Type",
                 template="gridon", height=500)
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

with col_graphs[1]:
    weather_counts = df["weather_condition"].value_counts()
    fig3 = px.pie(names=weather_counts.index, values=weather_counts.values,
                 title="Weather Conditions Distribution")
    st.plotly_chart(fig3, use_container_width=True)

with col_graphs[2]:
    province_counts = df["province_th"].value_counts().reset_index()
    province_counts.columns = ["province_th", "count"]
    fig4 = px.bar(province_counts, x="province_th", y="count",
                 title="Number of Accidents by Province",
                 labels={"count": "Number of Accidents", "province_th": "Province"},
                 template="gridon")
    fig4.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig4, use_container_width=True)

# แถวที่ 2
col_graphs2 = st.columns(3)

with col_graphs2[0]:
    df["incident_datetime"] = pd.to_datetime(df["incident_datetime"])
    df_filtered = df[(df["incident_datetime"] >= "2019-01-01") & (df["incident_datetime"] <= "2024-12-31")]
    df_filtered["Month_Year"] = df_filtered["incident_datetime"].dt.strftime("%Y-%m")
    result = df_filtered.groupby("Month_Year").agg({"number_of_injuries": "sum"}).reset_index()
    fig1 = px.line(result, x="Month_Year", y="number_of_injuries", title="Total Injuries by Month (2019-2024)",
                 template="gridon")
    st.plotly_chart(fig1, use_container_width=True)

with col_graphs2[1]:
    df_filtered["Year"] = df_filtered["incident_datetime"].dt.year
    injuries_by_year = df_filtered.groupby("Year").agg({"number_of_injuries": "sum"}).reset_index()
    fig5 = px.line(injuries_by_year, x="Year", y="number_of_injuries",
                 title="Total Injuries by Year (2019-2024)",
                 labels={"number_of_injuries": "Number of Injuries", "Year": "Year"},
                 template="gridon")
    st.plotly_chart(fig5, use_container_width=True)

with col_graphs2[2]:
    fig6 = px.scatter(df_filtered, x="number_of_injuries", y="number_of_fatalities",
                 title="Relationship between Injuries and Fatalities",
                 labels={"number_of_injuries": "Number of Injuries", "number_of_fatalities": "Number of Fatalities"},
                 template="gridon")
    st.plotly_chart(fig6, use_container_width=True)

# แถวที่ 3 เพิ่มกราฟ "Number of Vehicles by Type Over Years (2019-2024)" และ Stacked Bar Chart
col_graphs3 = st.columns(2)

with col_graphs3[0]:
    vehicles_by_year = df_filtered.groupby(["Year", "vehicle_type"]).size().reset_index(name="count")
    fig2 = px.line(vehicles_by_year, x="Year", y="count", color="vehicle_type",
                 title="Number of Vehicles by Type Over Years (2019-2024)",
                 labels={"count": "Count", "vehicle_type": "Vehicle Type"},
                 template="gridon")
    st.plotly_chart(fig2, use_container_width=True)

col_graphs4 = st.columns(1)
with col_graphs4[0]:
    # แปลงคอลัมน์ 'incident_datetime' เป็น datetime (ถ้ายังไม่ได้แปลง)
    df['incident_datetime'] = pd.to_datetime(df['incident_datetime'])

    # ดึงปีจาก 'incident_datetime' และสร้างคอลัมน์ 'Year'
    df['Year'] = df['incident_datetime'].dt.year

    fig = px.scatter(df, x="Year", y="accident_type", color="weather_condition",
                     title="Relationship between Year and Accident Type by Weather Condition",
                     labels={"Year": "Year", "accident_type": "Accident Type", "weather_condition": "Weather Condition"},
                     template="plotly_dark")  # ใช้ธีมสีเข้ม

    st.plotly_chart(fig, use_container_width=True)


with col_graphs3[1]:
    # สร้าง Box Plot
    fig_box = px.box(df, x="vehicle_type", y="number_of_vehicles_involved",
                     title="Number of Vehicles Involved by Vehicle Type",
                     labels={"vehicle_type": "Vehicle Type", "number_of_vehicles_involved": "Number of Vehicles Involved"},
                     template="gridon")
    st.plotly_chart(fig_box, use_container_width=True)

col_graphs5 = st.columns(1)
with col_graphs5[0]:
    # สร้าง Stacked Bar Chart
    presumed_cause_by_year = df.groupby(["Year", "presumed_cause"]).size().reset_index(name="count")  # ใช้ df แทน df_filtered
    fig_stacked_bar = px.bar(presumed_cause_by_year, x="Year", y="count", color="presumed_cause",
                               title="Presumed Causes of Accidents by Year",
                               labels={"count": "Number of Accidents", "presumed_cause": "Presumed Cause"},
                               template="gridon", width=1800)  # ปรับขนาดกราฟ
    fig_stacked_bar.update_layout(margin=dict(l=50, r=50, t=60, b=50))  # ปรับ margin
    st.plotly_chart(fig_stacked_bar, use_container_width=True)