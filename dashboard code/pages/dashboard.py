
import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import requests
import datetime
import matplotlib.pyplot as plt
import re
import json


st.set_page_config(layout="wide")

if 'selected_patient_id' in st.session_state and st.session_state['selected_patient_id']:
    PATIENT_ID = st.session_state['selected_patient_id']
else:
    PATIENT_ID = "P00052"


def reverse_geocode(lat, lon):
    url = f"https://nominatim.openstreetmap.org/reverse"
    params = {
        "lat": lat,
        "lon": lon,
        "format": "json"
    }
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get("display_name", "Unknown location")
    return "Unknown location"

def days_without_issue(ts):
    try:
        date_str = str(ts).split(' at ')[0]
        date_obj = datetime.datetime.strptime(date_str, '%b %d, %Y')
        return (datetime.datetime.now() - date_obj).days
    except Exception:
        return 'N/A'

if not firebase_admin._apps:
    service_account_info = json.loads(st.secrets["firebase_service_account"])
    cred = credentials.Certificate(service_account_info)
    firebase_admin.initialize_app(cred)


db = firestore.client()

patient_query = db.collection('patients').where('pat_id', '==', PATIENT_ID).stream()
date_of_fitment = None
warranty_validity = None
clinic_name = None
pat_image = None
for doc in patient_query:
    data = doc.to_dict()
    print(data)
    if 'pat_warranty_dt' in data and warranty_validity is None:
        warranty_validity = data['pat_warranty_dt']
    if 'pat_associated_org' in data and isinstance(data['pat_associated_org'], list) and len(data['pat_associated_org']) > 0 and clinic_name is None:
        org_ref = data['pat_associated_org'][0]
        try:
            org_doc = org_ref.get()
            org_data = org_doc.to_dict()
            clinic_name = org_data.get('org_name', 'N/A')
        except Exception:
            clinic_name = 'N/A'
    if 'pat_image' in data and pat_image is None:
        image_path = data['pat_image']
        match = re.search(r'/o/(.+)$', image_path)
    if match:
        file_path = match.group(1)
        file_path = file_path.replace('/', '%2F')
        pat_image = f"https://firebasestorage.googleapis.com/v0/b/grippyanalytics.appspot.com/o/{file_path}?alt=media"
    else:
        pat_image = None
    if 'pat_fitment_dt' in data and date_of_fitment is None:
        date_of_fitment = str(data['pat_fitment_dt'])
    if warranty_validity and clinic_name and pat_image and date_of_fitment:
        break


service_query = db.collection('service').where('ser_pat_id', '==', PATIENT_ID).stream()
service_report_times = []
for doc in service_query:
    data = doc.to_dict()
    if 'ser_reportTime' in data:
        service_report_times.append(data['ser_reportTime'])


last_service_call = service_report_times[-1] if service_report_times else 'N/A'
next_service_call = service_report_times[-2] if len(service_report_times) > 1 else 'N/A'

feedback_query = db.collection('user_feedback').where('usrcom_patid', '==', PATIENT_ID).stream()
latest_feedback_date = None
for doc in feedback_query:
    data = doc.to_dict()
    if 'usrcom_recdate_time' in data:
        try:
            date_obj = data['usrcom_recdate_time']
            if latest_feedback_date is None or date_obj > latest_feedback_date:
                latest_feedback_date = date_obj
        except Exception:
            pass
if latest_feedback_date:
    no_of_days_without_issue = (datetime.datetime.now(datetime.timezone.utc) - latest_feedback_date).days
else:
    no_of_days_without_issue = 'N/A'

analytics_query = db.collection('analytics').where('an_patid', '==', PATIENT_ID).stream()
locations = []
device_serial_no = None
for doc in analytics_query:
    data = doc.to_dict()
    if 'an_grippysrno' in data and device_serial_no is None:
        device_serial_no = data['an_grippysrno']
    if 'an_location' in data:
        loc = data['an_location']
        if isinstance(loc, dict) and 'latitude' in loc and 'longitude' in loc:
            locations.append((loc['latitude'], loc['longitude']))

if locations:
    last_lat, last_lon = locations[-1]
    last_used_location = reverse_geocode(last_lat, last_lon)
else:
    last_used_location = 'N/A'


st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Inter&family=Jost&display=swap" rel="stylesheet">
    <style>
        .block-container {
            padding-top: 0rem;
            height: 100vh;
        }
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #413F42;
            height: 100vh;
        }
        [data-testid="stVerticalBlock"] > div[data-testid^="stHorizontalBlock"] > div[data-testid^="stVerticalBlock"] {
            background-color: #D9D9D9;
            border-radius: 2vh;
            padding: 2vh;
            margin-top: 1vh;
            margin-bottom: 2vh;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div style="height: 5vh"></div>
    """, unsafe_allow_html=True)

info_row = st.columns([1, 1, 1, 1, .25])

with info_row[0]:
    if pat_image:
        st.markdown(f"""
            <div style="border: 0px; padding: 2vh; border-radius: 2vh; margin-top: 1.5vh; margin-left: 18vh; height: 32vh; width: 32vh; display: flex; align-items: center; justify-content: center; background-color: #D9D9D9;">
                <img src='{pat_image}' style='height: 24vh; width: 24vh; background-color: #E55050; border-radius: 50%; display: inline-block; object-fit: cover;' />
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="border: 0px; padding: 2vh; border-radius: 2vh; margin-top: 1.5vh; margin-left: 18vh; height: 32vh; width: 32vh; display: flex; align-items: center; justify-content: center; background-color: #D9D9D9;">
                <span style="height: 24vh; width: 24vh; background-color: #E55050; border-radius: 50%; display: inline-block"> </span>
            </div>
        """, unsafe_allow_html=True)

with info_row[1]:
    st.markdown(f"""
        <div style="border: 0px; padding: 2vh; border-radius: 2vh; margin-top: 1.5vh; margin-bottom: .5vh; margin-left: 11vh; height: 15vh; width: 32vh; display: flex; align-items: center; justify-content: center; text-align: center; flex-direction: column; background-color: #D9D9D9;">
            <p style="font-family: 'Jost', sans-serif; letter-spacing: -0.1vh; font-size: 2.7vh; margin-top:1vh"> Device Serial Number </p> 
            <p style="font-family: 'Inter', sans-serif; font-size: 1.5vh; margin-top:-1vh"> {device_serial_no if device_serial_no else 'N/A'} </p> 
        </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
        <div style="border: 0px; padding: 2vh; border-radius: 2vh; margin-top: 1.5vh; margin-left: 11vh; height: 15vh; width: 32vh; display: flex; align-items: center; justify-content: center; text-align: center; flex-direction: column; background-color: #D9D9D9;">
            <p style="font-family: 'Jost', sans-serif; letter-spacing: -0.1vh; font-size: 2.7vh; margin-top:1vh"> Warranty Validity </p> 
            <p style="font-family: 'Inter', sans-serif; font-size: 1.5vh; margin-top:-1vh"> {warranty_validity if warranty_validity else 'N/A'} </p> 
        </div>
    """, unsafe_allow_html=True)

with info_row[2]:
    st.markdown(f"""
        <div style="border: 0px; padding: 2vh; border-radius: 2vh; margin-top: 1.5vh; margin-bottom: .5vh; margin-left: 3vh; height: 15vh; width: 32vh; display: flex; align-items: center; justify-content: center; text-align: center; flex-direction: column; background-color: #D9D9D9;">
            <p style="font-family: 'Jost', sans-serif; letter-spacing: -0.1vh; font-size: 2.7vh; margin-top:1vh"> Clinic Name </p> 
            <p style="font-family: 'Inter', sans-serif; font-size: 1.5vh; margin-top:-1vh"> {clinic_name if clinic_name else 'N/A'} </p> 
        </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
        <div style="border: 0px; padding: 2vh; border-radius: 2vh; margin-top: 1.5vh; margin-left: 3vh; height: 15vh; width: 32vh; display: flex; align-items: center; justify-content: center; text-align: center; flex-direction: column; background-color: #D9D9D9;">
            <p style="font-family: 'Jost', sans-serif; letter-spacing: -0.1vh; font-size: 2.7vh; margin-top:1vh"> Date Of Fitment </p> 
            <p style="font-family: 'Inter', sans-serif; font-size: 1.5vh; margin-top:-1vh"> {date_of_fitment if date_of_fitment else 'N/A'} </p> 
        </div>
    """, unsafe_allow_html=True)

with info_row[3]:
    location_link = 'N/A'
    if locations:
        lat, lon = locations[-1]
        location_link = f"<a href='https://www.google.com/maps?q={lat},{lon}' target='_blank' style='color: #007bff; text-decoration: underline;'>Click Here</a>"
    st.markdown(f"""
        <div style="border: 0px; padding: 2vh; border-radius: 2vh; margin-top: 3.5vh; margin-left: -5vh; height: 28vh; width: 32vh; display: flex; flex-direction: column; justify-content: center; background-color: #D9D9D9;">
            <div style="display: flex; justify-content: space-between; margin-bottom: .5vh; margin-top: 2.5vh">
                <p style="font-family: 'Jost', sans-serif; font-size: 2vh; letter-spacing: -0.1vh">Last Service Call :</p>
                <p style="font-family: 'Inter', sans-serif; font-size: 1.5vh; margin-top: .7vh">{last_service_call if last_service_call else 'N/A'}</p>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: .5vh;">
                <p style="font-family: 'Jost', sans-serif; font-size: 2vh; letter-spacing: -0.1vh">Next Service Call :</p>
                <p style="font-family: 'Inter', sans-serif; font-size: 1.5vh; margin-top: .7vh">{next_service_call if next_service_call else 'N/A'}</p>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: .5vh;">
                <p style="font-family: 'Jost', sans-serif; font-size: 2vh; letter-spacing: -0.1vh">No. Of Days Without Issue :</p>
                <p style="font-family: 'Inter', sans-serif; font-size: 1.5vh; margin-top: .7vh">{no_of_days_without_issue if no_of_days_without_issue else 'N/A'}</p>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <p style="font-family: 'Jost', sans-serif; font-size: 2vh; letter-spacing: -0.1vh">Last Used Location :</p>
                <p style="font-family: 'Inter', sans-serif; font-size: 1.5vh; margin-top: .7vh">{location_link}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

with info_row[4]:
    st.markdown(
        """
        <div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Home", key="home_btn", help="Go to patient list", use_container_width=True):
        st.switch_page("list.py")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("""
    <div style="height:10vh"></div>
""", unsafe_allow_html=True)



graph_row = st.columns([1,1,1,0.15])

with graph_row[0]:
    cycles = []
    times = []
    analytics_query = db.collection('analytics').where('an_patid', '==', PATIENT_ID).stream()
    for doc in analytics_query:
        data = doc.to_dict()
        if 'an_cycles' in data and 'an_timestamp' in data:
            cycles.append(data['an_cycles'])
            ts_obj = data['an_timestamp'] if isinstance(data['an_timestamp'], datetime.datetime) else None
            times.append(ts_obj)

    with st.container():
        if cycles and times and all(t is not None for t in times):
            plot_data = sorted(zip(times, cycles), key=lambda x: x[0])
            df = pd.DataFrame({
                'Time': [x[0] for x in plot_data],
                'Cycles': pd.to_numeric([x[1] for x in plot_data], errors='coerce')
            })
            df = df.dropna(subset=['Cycles'])
            if not df.empty:
                fig, ax = plt.subplots(figsize=(2.5, 1.2), dpi=85)
                df.set_index('Time').plot(ax=ax, legend=False, color='#1f77b4')
                ax.set_facecolor('#D9D9D9')
                fig.patch.set_facecolor('#D9D9D9')
                ax.tick_params(axis='x', labelsize=4)
                ax.tick_params(axis='y', labelsize=4)
                ax.set_xlabel("Time", fontsize=5)
                ax.set_ylabel("Cycles", fontsize=5)
                plt.tight_layout(pad=0.5)
                st.pyplot(fig)
            else:
                st.markdown("<span style='color: #888;'>No cycles data available for this patient.</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span style='color: #888;'>No cycles data available for this patient.</span>", unsafe_allow_html=True)


    fallcounts = []
    fall_times = []
    analytics_query = db.collection('analytics').where('an_patid', '==', PATIENT_ID).stream()
    for doc in analytics_query:
        data = doc.to_dict()
        if 'an_fallCount' in data and 'an_timestamp' in data:
            fallcounts.append(data['an_fallCount'])
            ts_obj = data['an_timestamp'] if isinstance(data['an_timestamp'], datetime.datetime) else None
            fall_times.append(ts_obj)
    with st.container():
        if fallcounts and fall_times and all(t is not None for t in fall_times):
            plot_data = sorted(zip(fall_times, fallcounts), key=lambda x: x[0])
            df = pd.DataFrame({
                'Time': [x[0] for x in plot_data],
                'Fall Count': pd.to_numeric([x[1] for x in plot_data], errors='coerce')
            })
            df = df.dropna(subset=['Fall Count'])
            if not df.empty:
                fig, ax = plt.subplots(figsize=(2.5, 1.2), dpi=85)
                df.set_index('Time').plot(ax=ax, legend=False, color='#ff7f0e')
                ax.set_facecolor('#D9D9D9')
                fig.patch.set_facecolor('#D9D9D9')
                ax.tick_params(axis='x', labelsize=4)
                ax.tick_params(axis='y', labelsize=4)
                ax.set_xlabel("Time", fontsize=5)
                ax.set_ylabel("Fall Count", fontsize=5)
                plt.tight_layout(pad=0.5)
                st.pyplot(fig)
            else:
                st.markdown("<span style='color: #888;'>No fall count data available for this patient.</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span style='color: #888;'>No fall count data available for this patient.</span>", unsafe_allow_html=True)



with graph_row[1]:
    motor_statuses = []
    times = []
    analytics_query = db.collection('analytics').where('an_patid', '==', PATIENT_ID).stream()
    for doc in analytics_query:
        data = doc.to_dict()
        if 'an_motorStatus' in data and 'an_timestamp' in data:
            status = data['an_motorStatus']
            status_num = 1 if status.upper() == 'ONLINE' else 0
            motor_statuses.append(status_num)
            ts_obj = data['an_timestamp'] if isinstance(data['an_timestamp'], datetime.datetime) else None
            times.append(ts_obj)

    with st.container():
        if motor_statuses and times and all(t is not None for t in times):
            plot_data = sorted(zip(times, motor_statuses), key=lambda x: x[0])
            df = pd.DataFrame({
                'Time': [x[0] for x in plot_data],
                'Motor Status': pd.to_numeric([x[1] for x in plot_data], errors='coerce')
            })
            df = df.dropna(subset=['Motor Status'])
            if not df.empty:
                fig, ax = plt.subplots(figsize=(2.5, 1.2), dpi=85)
                df.set_index('Time').plot(ax=ax, legend=False, color='#2ca02c')
                ax.set_facecolor('#D9D9D9')
                fig.patch.set_facecolor('#D9D9D9')
                
                ax.tick_params(axis='x', labelsize=4)
                ax.tick_params(axis='y', labelsize=4)
                ax.set_xlabel("Time", fontsize=5)
                ax.set_ylabel("Motor Status", fontsize=5)
                
                plt.tight_layout(pad=0.5)
                st.pyplot(fig)
            else:
                st.markdown("<span style='color: #888;'>No motor status data available for this patient.</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span style='color: #888;'>No motor status data available for this patient.</span>", unsafe_allow_html=True)

    ambient_temps = []
    servo_temps = []
    temp_times = []
    analytics_query = db.collection('analytics').where('an_patid', '==', PATIENT_ID).stream()
    for doc in analytics_query:
        data = doc.to_dict()
        if 'an_ambientTemp' in data and 'an_servocurrentTemp' in data and 'an_timestamp' in data:
            ambient_temps.append(data['an_ambientTemp'])
            servo_temps.append(data['an_servocurrentTemp'])
            ts_obj = data['an_timestamp'] if isinstance(data['an_timestamp'], datetime.datetime) else None
            temp_times.append(ts_obj)

    with st.container():
        if ambient_temps and servo_temps and temp_times and all(t is not None for t in temp_times):
            plot_data = sorted(zip(temp_times, ambient_temps, servo_temps), key=lambda x: x[0])
            df = pd.DataFrame({
                'Time': [x[0] for x in plot_data],
                'Ambient Temp': pd.to_numeric([x[1] for x in plot_data], errors='coerce'),
                'Servo Current Temp': pd.to_numeric([x[2] for x in plot_data], errors='coerce')
            })
            df = df.dropna(subset=['Ambient Temp', 'Servo Current Temp'], how='all')
            if not df.empty:
                cols_to_plot = []
                colors = []
                if df['Ambient Temp'].notna().any():
                    cols_to_plot.append('Ambient Temp')
                    colors.append('#1f77b4')
                if df['Servo Current Temp'].notna().any():
                    cols_to_plot.append('Servo Current Temp')
                    colors.append('#ff7f0e')
                fig, ax = plt.subplots(figsize=(2.5, 1.2), dpi=85)
                df.set_index('Time')[cols_to_plot].plot(ax=ax, legend=False, color=colors)
                ax.set_facecolor('#D9D9D9')
                fig.patch.set_facecolor('#D9D9D9')
                ax.tick_params(axis='x', labelsize=4)
                ax.tick_params(axis='y', labelsize=4)
                ax.set_xlabel("Time", fontsize=5)
                ax.set_ylabel("Temperature", fontsize=5)

                legend = ax.legend(fontsize=5, loc='upper right', frameon=False)

                plt.tight_layout(pad=0.5)
                st.pyplot(fig)
            else:
                st.markdown("<span style='color: #888;'>No temperature data available for this patient.</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span style='color: #888;'>No temperature data available for this patient.</span>", unsafe_allow_html=True)

with graph_row[2]:
    online_count = 0
    offline_count = 0
    analytics_query = db.collection('analytics').where('an_patid', '==', PATIENT_ID).stream()
    for doc in analytics_query:
        data = doc.to_dict()
        if 'an_motorStatus' in data:
            status = data['an_motorStatus']
            if status.upper() == 'ONLINE':
                online_count += 1
            else:
                offline_count += 1

    with st.container():
        st.markdown("<div style='margin-top: 10vh;'></div>", unsafe_allow_html=True)

        pie_df = pd.DataFrame({
            'Status': ['ONLINE', 'OFFLINE'],
            'Count': pd.to_numeric([online_count, offline_count], errors='coerce')
        })
        pie_df = pie_df.dropna(subset=['Count'])

        if pie_df['Count'].sum() > 0:
            fig, ax = plt.subplots(figsize=(2.5, 2.5), dpi=100)
            ax.pie(
                pie_df['Count'],
                labels=pie_df['Status'],
                autopct='%1.1f%%',
                colors=['#4CAF50', '#E55050']
            )
            ax.set_facecolor('#D9D9D9')
            fig.patch.set_facecolor('#D9D9D9')
            st.pyplot(fig)
        else:
            st.markdown("<span style='color: #888;'>No motor status data available for this patient.</span>", unsafe_allow_html=True)

st.markdown("""
            <p style="font-family: 'Jost', sans-serif; letter-spacing: -0.1vh; font-size: 2.7vh; margin-top: 2vh; margin-left: -10vh; color: #ffffff; font-size: 1.5vh">Our Products & Services are inline with the UN’s SDGs and this dashboard can be extracted as a report for CSR & ESG purposed, by citing RoboBionics</p>
""", unsafe_allow_html=True)