import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore


st.set_page_config(layout="wide")

import json
if not firebase_admin._apps:
    firebase_json = st.secrets["firebase_json"]
    cred_dict = json.loads(firebase_json)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

doc_ref = db.collection('patients').document('patient1')
doc_ref.set({
    'name': 'test',
    'age': 20,
    'test_graph': [10, 20, 30]
})
db.collection("patients").add({
    "name": "test2",
    "age": 45
})


doc = db.collection('patients').document('patient1').get()
st.write(doc.to_dict())

st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Inter&family=Jost&display=swap" rel="stylesheet">
    <style>
        .block-container {
            padding-top: 0rem;
            overflow: hidden;
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
    st.markdown("""
        <div style="border: 0px; padding: 2vh; border-radius: 2vh; margin-top: 1.5vh; margin-left: 18vh; height: 32vh; width: 32vh; display: flex; align-items: center; justify-content: center; background-color: #D9D9D9;">
            <span style="height: 24vh; width: 24vh; background-color: #E55050; border-radius: 50%; display: inline-block"> </span>
        </div>
    """, unsafe_allow_html=True)

with info_row[1]:
    st.markdown("""
        <div style="border: 0px; padding: 2vh; border-radius: 2vh; margin-top: 1.5vh; margin-bottom: .5vh; margin-left: 11vh; height: 15vh; width: 32vh; display: flex; align-items: center; justify-content: center; text-align: center; flex-direction: column; background-color: #D9D9D9;">
            <p style="font-family: 'Jost', sans-serif; letter-spacing: -0.1vh; font-size: 2.7vh; margin-top:1vh"> Device Serial Number </p> 
            <p style="font-family: 'Inter', sans-serif; font-size: 1.5vh; margin-top:-1vh"> XX.XX.XXXX </p> 
        </div>
    """, unsafe_allow_html=True)
    st.markdown("""
        <div style="border: 0px; padding: 2vh; border-radius: 2vh; margin-top: 1.5vh; margin-left: 11vh; height: 15vh; width: 32vh; display: flex; align-items: center; justify-content: center; text-align: center; flex-direction: column; background-color: #D9D9D9;">
            <p style="font-family: 'Jost', sans-serif; letter-spacing: -0.1vh; font-size: 2.7vh; margin-top:1vh"> Warranty Validity </p> 
            <p style="font-family: 'Inter', sans-serif; font-size: 1.5vh; margin-top:-1vh"> XX.XX.XXXX </p> 
        </div>
    """, unsafe_allow_html=True)

with info_row[2]:
    st.markdown("""
        <div style="border: 0px; padding: 2vh; border-radius: 2vh; margin-top: 1.5vh; margin-bottom: .5vh; margin-left: 3vh; height: 15vh; width: 32vh; display: flex; align-items: center; justify-content: center; text-align: center; flex-direction: column; background-color: #D9D9D9;">
            <p style="font-family: 'Jost', sans-serif; letter-spacing: -0.1vh; font-size: 2.7vh; margin-top:1vh"> Clinic Name </p> 
            <p style="font-family: 'Inter', sans-serif; font-size: 1.5vh; margin-top:-1vh"> XX.XX.XXXX </p> 
        </div>
    """, unsafe_allow_html=True)
    st.markdown("""
        <div style="border: 0px; padding: 2vh; border-radius: 2vh; margin-top: 1.5vh; margin-left: 3vh; height: 15vh; width: 32vh; display: flex; align-items: center; justify-content: center; text-align: center; flex-direction: column; background-color: #D9D9D9;">
            <p style="font-family: 'Jost', sans-serif; letter-spacing: -0.1vh; font-size: 2.7vh; margin-top:1vh"> Date Of Fitment </p> 
            <p style="font-family: 'Inter', sans-serif; font-size: 1.5vh; margin-top:-1vh"> XX.XX.XXXX </p> 
        </div>
    """, unsafe_allow_html=True)

with info_row[3]:
    st.markdown("""
        <div style="border: 0px; padding: 2vh; border-radius: 2vh; margin-top: 3.5vh; margin-left: -5vh; height: 28vh; width: 32vh; display: flex; flex-direction: column; justify-content: center; background-color: #D9D9D9;">
            <div style="display: flex; justify-content: space-between; margin-bottom: .5vh; margin-top: 2.5vh">
                <p style="font-family: 'Jost', sans-serif; font-size: 2vh; letter-spacing: -0.1vh">Device Serial Number</p>
                <p style="font-family: 'Inter', sans-serif; font-size: 1.5vh; margin-top: .7vh">XXX</p>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: .5vh;">
                <p style="font-family: 'Jost', sans-serif; font-size: 2vh; letter-spacing: -0.1vh">Warranty Validity</p>
                <p style="font-family: 'Inter', sans-serif; font-size: 1.5vh; margin-top: .7vh">XXX</p>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: .5vh;">
                <p style="font-family: 'Jost', sans-serif; font-size: 2vh; letter-spacing: -0.1vh">Clinic Name</p>
                <p style="font-family: 'Inter', sans-serif; font-size: 1.5vh; margin-top: .7vh">XXX</p>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <p style="font-family: 'Jost', sans-serif; font-size: 2vh; letter-spacing: -0.1vh">Date Of Fitment</p>
                <p style="font-family: 'Inter', sans-serif; font-size: 1.5vh; margin-top: .7vh">XXX</p>
            </div>
    """, unsafe_allow_html=True)


st.markdown("""
    <div style="height:1vh"></div>
""", unsafe_allow_html=True)


graph_row = st.columns([1,1,1])

with graph_row[0]:
    st.markdown("""
        <div style="border: 0px; padding: 2vh; border-radius: 2vh; margin-top: 1vh; margin-left: 9vh; height: 25vh; width: 50vh; display: flex; align-items: center; justify-content: center; background-color: #D9D9D9">
        </div>
    """, unsafe_allow_html=True)
    st.markdown("""
        <div style="border: 0px; padding: 2vh; border-radius: 2vh; margin-top: 2vh; margin-left: 9vh; height: 25vh; width: 50vh; display: flex; align-items: center; justify-content: center; background-color: #D9D9D9">
        </div>
    """, unsafe_allow_html=True)

with graph_row[1]:
    st.markdown("""
        <div style="border: 0px; padding: 2vh; border-radius: 2vh; margin-top: 1vh; margin-left: 0vh; height: 25vh; width: 50vh; display: flex; align-items: center; justify-content: center; background-color: #D9D9D9">
        </div>
    """, unsafe_allow_html=True)
    st.markdown("""
        <div style="border: 0px; padding: 2vh; border-radius: 2vh; margin-top: 2vh; margin-left: 0vh; height: 25vh; width: 50vh; display: flex; align-items: center; justify-content: center; background-color: #D9D9D9">
        </div>
    """, unsafe_allow_html=True)
    # st.line_chart(data1)

with graph_row[2]:
    st.markdown("""
        <div style="border: 0px; padding: 2vh; border-radius: 2vh; margin-top: 3vh; margin-left: -7vh; height: 48vh; width: 59vh; display: flex; align-items: center; justify-content: center; background-color: #D9D9D9">
            <span style="height: 36vh; width: 36vh; background-color: #E55050; border-radius: 50%; display: inline-block"></span>
        </div>
    """, unsafe_allow_html=True)


st.markdown("""
            <p style="font-family: 'Jost', sans-serif; letter-spacing: -0.1vh; font-size: 2.7vh; margin-top: 2vh; margin-left: -10vh; color: #ffffff; font-size: 1.5vh">Our Products & Services are inline with the UN’s SDGs and this dashboard can be extracted as a report for CSR & ESG purposed, by citing RoboBionics</p>
""", unsafe_allow_html=True)