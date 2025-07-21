import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import requests
import datetime


st.set_page_config(layout="wide")


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
    cred = credentials.Certificate(r"C:\Users\muham\Desktop\RoboBionics\dashboard code\grippyanalytics-f1bd0a1aaf0c.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

patients_docs = db.collection('patients').stream()
date_of_fitment = None
warranty_validity = None
clinic_name = None
pat_image = None
for doc in patients_docs:
    data = doc.to_dict()
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
        pat_image = data['pat_image']
    if 'pat_fitment_dt' in data and date_of_fitment is None:
        date_of_fitment = str(data['pat_fitment_dt'])
    if warranty_validity and clinic_name and pat_image and date_of_fitment:
        break


service_docs = db.collection('Service').stream()
service_report_times = []
for doc in service_docs:
    data = doc.to_dict()
    if 'ser_reportTime' in data:
        service_report_times.append(data['ser_reportTime'])


last_service_call = service_report_times[-1] if service_report_times else 'N/A'
next_service_call = service_report_times[-2] if len(service_report_times) > 1 else 'N/A'

feedback_docs = db.collection('user_feedback').stream()
latest_feedback_date = None
for doc in feedback_docs:
    data = doc.to_dict()
    if 'usrcom_recdate_time' in data:
        try:
            date_str = str(data['usrcom_recdate_time']).split(' at ')[0]
            date_obj = datetime.datetime.strptime(date_str, '%B %d, %Y')
            if latest_feedback_date is None or date_obj > latest_feedback_date:
                latest_feedback_date = date_obj
        except Exception:
            pass
if latest_feedback_date:
    no_of_days_without_issue = (datetime.datetime.now() - latest_feedback_date).days
else:
    no_of_days_without_issue = 'N/A'

analytics_docs = db.collection('analytics').stream()
locations = []
device_serial_no = None
for doc in analytics_docs:
    data = doc.to_dict()
    if 'pat_grippy_srno' in data and device_serial_no is None:
        device_serial_no = data['pat_grippy_srno']
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
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div style="height: 5vh"></div>
    """, unsafe_allow_html=True)

info_row = st.columns([1, 1, 1, 1])

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
                <p style="font-family: 'Inter', sans-serif; font-size: 1.5vh; margin-top: .7vh">{last_used_location if last_used_location else 'N/A'}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)


st.markdown("""
    <div style="height:1vh"></div>
""", unsafe_allow_html=True)



graph_row = st.columns([1,1,1])

with graph_row[0]:
    current_pat_id = None
    patients_docs = db.collection('patients').stream()
    for doc in patients_docs:
        data = doc.to_dict()
        if 'pat_id' in data:
            current_pat_id = data['pat_id']
            break

    analytics_docs = db.collection('analytics').stream()
    cycles = []
    times = []
    for doc in analytics_docs:
        data = doc.to_dict()
        if 'an_patid' in data and data['an_patid'] == current_pat_id:
            if 'an_cycles' in data and 'an_timestamp' in data:
                cycles.append(data['an_cycles'])
                ts_str = str(data['an_timestamp']).split(' at ')[0]
                try:
                    ts_obj = datetime.datetime.strptime(ts_str, '%B %d, %Y')
                except Exception:
                    ts_obj = None
                if ts_obj is None:
                    try:
                        ts_obj = datetime.datetime.strptime(str(data['an_timestamp']), '%B %d, %Y at %I:%M:%S%p UTC%z')
                    except Exception:
                        ts_obj = None
                times.append(ts_obj)

    if cycles and times and all(t is not None for t in times):
        plot_data = sorted(zip(times, cycles), key=lambda x: x[0])
        df = pd.DataFrame({
            'Time': [x[0] for x in plot_data],
            'Cycles': [x[1] for x in plot_data]
        })
        st.line_chart(df.set_index('Time'))
    else:
        st.markdown("""
            <div style="border: 0px; padding: 2vh; border-radius: 2vh; margin-top: 1vh; margin-left: 9vh; height: 25vh; width: 50vh; display: flex; align-items: center; justify-content: center; background-color: #D9D9D9">
                <span style="color: #888;">No cycles data available for this patient.</span>
            </div>
        """, unsafe_allow_html=True)
    fallcounts = []
    fall_times = []
    analytics_docs = db.collection('analytics').stream()
    for doc in analytics_docs:
        data = doc.to_dict()
        if 'an_patid' in data and data['an_patid'] == current_pat_id:
            if 'an_fallcount' in data and 'an_timestamp' in data:
                fallcounts.append(data['an_fallcount'])
                ts_str = str(data['an_timestamp']).split(' at ')[0]
                try:
                    ts_obj = datetime.datetime.strptime(ts_str, '%B %d, %Y')
                except Exception:
                    ts_obj = None
                if ts_obj is None:
                    try:
                        ts_obj = datetime.datetime.strptime(str(data['an_timestamp']), '%B %d, %Y at %I:%M:%S%p UTC%z')
                    except Exception:
                        ts_obj = None
                fall_times.append(ts_obj)
    if fallcounts and fall_times and all(t is not None for t in fall_times):
        plot_data = sorted(zip(fall_times, fallcounts), key=lambda x: x[0])
        df = pd.DataFrame({
            'Time': [x[0] for x in plot_data],
            'Fall Count': [x[1] for x in plot_data]
        })
        st.markdown("""
            <div style='border: 0px; padding: 2vh; border-radius: 2vh; margin-top: 2vh; margin-left: 9vh; height: 25vh; width: 50vh; display: flex; align-items: center; justify-content: center; background-color: #D9D9D9'>
        """, unsafe_allow_html=True)
        st.line_chart(df.set_index('Time'))
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style='border: 0px; padding: 2vh; border-radius: 2vh; margin-top: 2vh; margin-left: 9vh; height: 25vh; width: 50vh; display: flex; align-items: center; justify-content: center; background-color: #D9D9D9'>
                <span style='color: #888;'>No fall count data available for this patient.</span>
            </div>
        """, unsafe_allow_html=True)


with graph_row[1]:
    current_pat_id = None
    patients_docs = db.collection('patients').stream()
    for doc in patients_docs:
        data = doc.to_dict()
        if 'pat_id' in data:
            current_pat_id = data['pat_id']
            break

    analytics_docs = db.collection('analytics').stream()
    motor_statuses = []
    times = []
    for doc in analytics_docs:
        data = doc.to_dict()
        if 'an_patid' in data and data['an_patid'] == current_pat_id:
            if 'an_motorstatus' in data and 'an_timestamp' in data:
                status = data['an_motorstatus']
                status_num = 1 if status.upper() == 'ONLINE' else 0
                motor_statuses.append(status_num)
                ts_str = str(data['an_timestamp']).split(' at ')[0]
                try:
                    ts_obj = datetime.datetime.strptime(ts_str, '%B %d, %Y')
                except Exception:
                    ts_obj = None
                if ts_obj is None:
                    try:
                        ts_obj = datetime.datetime.strptime(str(data['an_timestamp']), '%B %d, %Y at %I:%M:%S%p UTC%z')
                    except Exception:
                        ts_obj = None
                times.append(ts_obj)

    if motor_statuses and times and all(t is not None for t in times):
        plot_data = sorted(zip(times, motor_statuses), key=lambda x: x[0])
        df = pd.DataFrame({
            'Time': [x[0] for x in plot_data],
            'Motor Status': [x[1] for x in plot_data]
        })
        st.line_chart(df.set_index('Time'))
        st.caption('Motor Status: ONLINE=1, OFFLINE=0')
    else:
        st.markdown("""
            <div style="border: 0px; padding: 2vh; border-radius: 2vh; margin-top: 1vh; margin-left: 0vh; height: 25vh; width: 50vh; display: flex; align-items: center; justify-content: center; background-color: #D9D9D9">
                <span style="color: #888;">No motor status data available for this patient.</span>
            </div>
        """, unsafe_allow_html=True)
    ambient_temps = []
    servo_temps = []
    temp_times = []
    analytics_docs = db.collection('analytics').stream()
    for doc in analytics_docs:
        data = doc.to_dict()
        if 'an_patid' in data and data['an_patid'] == current_pat_id:
            if 'an_ambientTemp' in data and 'an_servocurrentTemp' in data and 'an_timestamp' in data:
                ambient_temps.append(data['an_ambientTemp'])
                servo_temps.append(data['an_servocurrentTemp'])
                ts_str = str(data['an_timestamp']).split(' at ')[0]
                try:
                    ts_obj = datetime.datetime.strptime(ts_str, '%B %d, %Y')
                except Exception:
                    ts_obj = None
                if ts_obj is None:
                    try:
                        ts_obj = datetime.datetime.strptime(str(data['an_timestamp']), '%B %d, %Y at %I:%M:%S%p UTC%z')
                    except Exception:
                        ts_obj = None
                temp_times.append(ts_obj)
    if ambient_temps and servo_temps and temp_times and all(t is not None for t in temp_times):
        plot_data = sorted(zip(temp_times, ambient_temps, servo_temps), key=lambda x: x[0])
        df = pd.DataFrame({
            'Time': [x[0] for x in plot_data],
            'Ambient Temp': [x[1] for x in plot_data],
            'Servo Current Temp': [x[2] for x in plot_data]
        })
        st.markdown("""
            <div style='border: 0px; padding: 2vh; border-radius: 2vh; margin-top: 2vh; margin-left: 0vh; height: 25vh; width: 50vh; display: flex; align-items: center; justify-content: center; background-color: #D9D9D9'>
        """, unsafe_allow_html=True)
        st.line_chart(df.set_index('Time'))
        st.caption('Blue: Ambient Temp, Orange: Servo Current Temp')
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style='border: 0px; padding: 2vh; border-radius: 2vh; margin-top: 2vh; margin-left: 0vh; height: 25vh; width: 50vh; display: flex; align-items: center; justify-content: center; background-color: #D9D9D9'>
                <span style='color: #888;'>No temperature data available for this patient.</span>
            </div>
        """, unsafe_allow_html=True)

with graph_row[2]:
    online_count = 0
    offline_count = 0
    analytics_docs = db.collection('analytics').stream()
    for doc in analytics_docs:
        data = doc.to_dict()
        if 'an_patid' in data and data['an_patid'] == current_pat_id:
            if 'an_motorstatus' in data:
                status = data['an_motorstatus']
                if status.upper() == 'ONLINE':
                    online_count += 1
                else:
                    offline_count += 1
    box_html = "<div style='border: 0px; padding: 2vh; border-radius: 2vh; margin-top: 3vh; margin-left: -7vh; height: 48vh; width: 59vh; display: flex; align-items: center; justify-content: center; background-color: #D9D9D9'>"
    if online_count + offline_count > 0:
        st.markdown(box_html, unsafe_allow_html=True)
        pie_df = pd.DataFrame({
            'Status': ['ONLINE', 'OFFLINE'],
            'Count': [online_count, offline_count]
        })
        st.pyplot(
            pie_df.set_index('Status').plot.pie(y='Count', autopct='%1.1f%%', colors=['#4CAF50', '#E55050'], legend=False, ylabel='', figsize=(4,4)).get_figure()
        )
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(box_html + "<span style='color: #888;'>No motor status data available for this patient.</span></div>", unsafe_allow_html=True)


st.markdown("""
            <p style="font-family: 'Jost', sans-serif; letter-spacing: -0.1vh; font-size: 2.7vh; margin-top: 2vh; margin-left: -10vh; color: #ffffff; font-size: 1.5vh">Our Products & Services are inline with the UN’s SDGs and this dashboard can be extracted as a report for CSR & ESG purposed, by citing RoboBionics</p>
""", unsafe_allow_html=True)