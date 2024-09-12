import streamlit as st
import pandas as pd
import plotly.express as px
from urllib.parse import urlparse

def google_sheet_to_csv_url(sheet_url):
    parsed_url = urlparse(sheet_url)
    path_parts = parsed_url.path.split('/')
    
    if len(path_parts) >= 3:
        sheet_id = path_parts[3]
    else:
        raise ValueError("Invalid Google Sheets URL or sheet ID not found.")
    
    csv_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv'
    return csv_url

#####################################################
# Setup Document
######################################################
st.title("Cow Behavior Summarizer")
st.subheader("How to use")
st.write(":green-background[ขั้นตอนที่ 1] ตรวจสอบหัวตารางของชีทว่าเขียนถูกต้องตามภาพ")
st.image("sheet-header.png")

st.write(":green-background[ขั้นตอนที่ 2]  คัดลอก URL ของชีทตัวเองมาวาง พร้อมตรวจสอบให้แน่ใจว่าแชร์เป็นสาธารณะแบบ Viewer แล้ว")
st.image("how-to-copy.png", width=400)
st.write(":green-background[ขั้นตอนที่ 3] เลือกวัวที่ต้องการดูสรุปพฤติกรรม เมื่อเลือกแล้วจะมีตารางเวลาออกมา สามารถซูมเข้าออกด้วยการลากหรือใช้เครื่องมือขวาบนของกราฟได้")
st.image("chart-menu.png")

st.divider()

#####################################################
# Setup Generator
######################################################

st.title("Cow Behavior Graph Generator")

sheet_url = st.text_input(":blue-background[Enter Google Sheets URL:]")
if sheet_url:
    csv_link = google_sheet_to_csv_url(sheet_url)
    data = pd.read_csv(csv_link)

    # Normalize Case
    data.columns = [col.lower() for col in data.columns]

    # Convert Date + Time to datetime format, skipping broken date and time
    data['datetime'] = pd.to_datetime(data['date'] + ' ' + data['time'], format='%d-%m-%Y %H.%M.%S', errors='coerce')

    # Drop rows where 'datetime' is empty or null
    data = data.dropna(subset=['datetime'])

    # Calculate the time difference between behaviors
    data['duration'] = data['datetime'].shift(-1) - data['datetime']

    # Drop NA rows
    data = data.dropna(subset=['duration'])

    # Define behaviors
    behaviors = ['ยืน', 'นอน', 'กิน', 'ดื่ม', 'เกย', 'คร่อม', 'ยืนติดรั้ว', 'ยืนนิ่ง', 'หาย']

    cow_options = {
        "cow-a (black)": data.columns[2],
        "cow-b (white-pattern)": data.columns[3],
        "cow-c (black-pattern)": data.columns[4]
    }
    
    cow_name = st.selectbox(":blue-background[Select Cow]", list(cow_options.keys()))

    if cow_name:
        column_name = cow_options[cow_name]
        
        data[column_name] = data[column_name].fillna('Unknown')  
        
        data['behavior_index'] = data[column_name].apply(lambda x: behaviors.index(x) if x in behaviors else -1)
        
        # Filter out behaviors not present in the data
        present_behavior_indices = data['behavior_index'].dropna().unique()
        filtered_behaviors = [behaviors[i] for i in present_behavior_indices if i != -1]
        
        filtered_data = data[data['behavior_index'].isin(present_behavior_indices)]
        
        fig = px.timeline(filtered_data, 
                          x_start='datetime', 
                          x_end=filtered_data['datetime'] + filtered_data['duration'],
                          y='behavior_index', 
                          color='behavior_index',
                          labels={'behavior_index': 'Behavior'},
                          color_continuous_scale=px.colors.sequential.Viridis,
                          title=f'Behavior Timeline of {cow_name}',
                          height=600)

        # Calculate date to create V-line
        unique_days = pd.date_range(start=filtered_data['datetime'].min().normalize(), 
                                    end=filtered_data['datetime'].max().normalize(), 
                                    freq='D')

        shapes = [dict(
            type='line',
            x0=day,
            x1=day,
            y0=-0.5,
            y1=len(filtered_behaviors) - 0.5,
            line=dict(color='white', width=1)
        ) for day in unique_days]

        fig.update_layout(
            xaxis_title='วันที่ & เวลา',
            yaxis_title='พฤติกรรม',
            yaxis=dict(
                tickmode='array',
                tickvals=list(range(len(filtered_behaviors))),
                ticktext=filtered_behaviors,
                title_font=dict(color='white'),
                tickfont=dict(color='white')
            ),
            xaxis=dict(
                tickformat='%d-%m-%Y %H:%M:%S',
                tickangle=45,
                title_font=dict(color='white'),
                tickfont=dict(color='white')
            ),
            autosize=True,
            margin=dict(l=40, r=40, t=40, b=100),
            plot_bgcolor='black',
            paper_bgcolor='black',
            font=dict(size=12, color='white'),
            shapes=shapes
        )
        st.plotly_chart(fig)
