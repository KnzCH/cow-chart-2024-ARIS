import streamlit as st
import pandas as pd
import plotly.express as px
from urllib.parse import urlparse

# Function to convert Google Sheets URL to CSV link
def google_sheet_to_csv_url(sheet_url):
    parsed_url = urlparse(sheet_url)
    path_parts = parsed_url.path.split('/')
    if len(path_parts) >= 3:
        sheet_id = path_parts[3]
    else:
        raise ValueError("Invalid Google Sheets URL or sheet ID not found.")
    csv_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv'
    return csv_url

# Function to display cow behavior analysis
def show_cow_behavior_analysis(data):
    st.title("Cow Behavior Analysis Program")

    # Check and display the columns of the DataFrame
    if data is not None:
        st.write("Data Columns:", data.columns)
        
        # Adjust based on actual column names
        date_column = 'date'  # Replace with actual column name if different
        time_column = 'time'  # Replace with actual column name if different
        
        if date_column not in data.columns or time_column not in data.columns:
            st.error(f"Columns '{date_column}' or '{time_column}' not found in the data.")
            return

        # Create Date + Time format
        data['datetime'] = pd.to_datetime(data[date_column] + ' ' + data[time_column], format='%d-%m-%Y %H.%M.%S')

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

            fig.update_layout(
                xaxis_title='Date & Time',
                yaxis_title='Behavior',
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
                font=dict(size=12, color='white')
            )
            st.plotly_chart(fig)
    else:
        st.error("No data to display.")

# Setup Streamlit
st.title("Cow Behavior Graph Generator")
sheet_url = st.text_input("Enter Google Sheets URL:")
if sheet_url:
    csv_link = google_sheet_to_csv_url(sheet_url)
    try:
        data = pd.read_csv(csv_link)
        show_cow_behavior_analysis(data)
    except Exception as e:
        st.error(f"An error occurred: {e}")
