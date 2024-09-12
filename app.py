import streamlit as st
import pandas as pd
import plotly.express as px
from urllib.parse import urlparse

# Function to convert Google Sheets URL to CSV link
def google_sheet_to_csv_url(sheet_url):
    # Parse the URL to extract the sheet ID
    parsed_url = urlparse(sheet_url)
    path_parts = parsed_url.path.split('/')
    
    # The sheet ID is the 3rd part of the path in the URL (index 2)
    if len(path_parts) >= 3:
        sheet_id = path_parts[3]
    else:
        raise ValueError("Invalid Google Sheets URL or sheet ID not found.")
    
    # Construct the CSV export URL
    csv_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv'
    return csv_url

# Setup Streamlit
st.title("Cow Behavior Summarizer")
st.subheader("How to use")
st.write(":green-background[ขั้นตอนที่ 1] ตรวจสอบหัวตารางของชีทว่าเขียนถูกต้องตามภาพ")
st.image("sheet-header.png")

st.write(":green-background[ขั้นตอนที่ 2]  คัดลอก URL ของชีทตัวเองมาวาง พร้อมตรวจสอบให้แน่ใจว่าแชร์เป็นสาธารณะแบบ Viewer แล้ว")
st.image("how-to-copy.png", width=400)
st.write(":green-background[ขั้นตอนที่ 3] เลือกวัวที่ต้องการดูสรุปพฤติกรรม เมื่อเลือกแล้วจะมีตารางเวลาออกมา สามารถซูมเข้าลอกด้วยการลากหรือใช้เครื่องมือขวาบนของกราฟได้")

st.divider()

st.title("Cow Behavior Graph Generator")

sheet_url = st.text_input("Enter Google Sheets URL:")
if sheet_url:
    csv_link = google_sheet_to_csv_url(sheet_url)
    data = pd.read_csv(csv_link)

    # Normalize column names to lowercase
    data.columns = [col.lower() for col in data.columns]

    # Convert Date + Time to datetime format, skipping broken formats
    data['datetime'] = pd.to_datetime(data['date'] + ' ' + data['time'], format='%d-%m-%Y %H.%M.%S', errors='coerce')

    # Drop rows where 'datetime' is NaT
    data = data.dropna(subset=['datetime'])

    # Calculate the time difference between behaviors
    data['duration'] = data['datetime'].shift(-1) - data['datetime']

    # Drop NA rows
    data = data.dropna(subset=['duration'])

    # Define behaviors
    behaviors = ['ยืน', 'นอน', 'กิน', 'ดื่ม', 'เกย', 'คร่อม', 'ยืนติดรั้ว']

    # Select Cow that you want to see its behavior summary
    cow_options = {
        "cow-a (black)": data.columns[2],
        "cow-b (white-pattern)": data.columns[3],
        "cow-c (black-pattern)": data.columns[4]
    }
    
    cow_name = st.selectbox("Select Cow", list(cow_options.keys()))

    if cow_name:
        column_name = cow_options[cow_name]
        
        data[column_name] = data[column_name].fillna('Unknown')  
        
        data['behavior_index'] = data[column_name].apply(lambda x: behaviors.index(x) if x in behaviors else -1)
        
        filtered_data = data[data['behavior_index'] != -1]
        
        fig = px.timeline(filtered_data, 
                          x_start='datetime', 
                          x_end=filtered_data['datetime'] + filtered_data['duration'],
                          y='behavior_index', 
                          color='behavior_index',
                          labels={'behavior_index': 'Behavior'},
                          color_continuous_scale=px.colors.sequential.Viridis,
                          title=f'Behavior Timeline of {cow_name}',
                          height=600)

        # Figure Styling!
        fig.update_layout(
            xaxis_title='วันที่ & เวลา',
            yaxis_title='พฤติกรรม',
            yaxis=dict(
                tickmode='array',
                tickvals=list(range(len(behaviors))),
                ticktext=behaviors,
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
            shapes=[
                # Add white lines for better clarity
                dict(
                    type='line',
                    x0=filtered_data['datetime'].min(),
                    x1=filtered_data['datetime'].max(),
                    y0=-0.5,
                    y1=-0.5,
                    line=dict(color='white', width=1)
                ),
                dict(
                    type='line',
                    x0=filtered_data['datetime'].min(),
                    x1=filtered_data['datetime'].max(),
                    y0=len(behaviors) - 0.5,
                    y1=len(behaviors) - 0.5,
                    line=dict(color='white', width=1)
                ),
                dict(
                    type='line',
                    x0=filtered_data['datetime'].min(),
                    x1=filtered_data['datetime'].min(),
                    y0=-0.5,
                    y1=len(behaviors) - 0.5,
                    line=dict(color='white', width=1)
                ),
                dict(
                    type='line',
                    x0=filtered_data['datetime'].max(),
                    x1=filtered_data['datetime'].max(),
                    y0=-0.5,
                    y1=len(behaviors) - 0.5,
                    line=dict(color='white', width=1)
                )
            ]
        )
        st.plotly_chart(fig)