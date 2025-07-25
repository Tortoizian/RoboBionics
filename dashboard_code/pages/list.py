import streamlit as st
import base64
import firebase_admin
from firebase_admin import credentials, firestore
import requests
import os


st.set_page_config(layout="wide")


col1, col_spacer, col_signout = st.columns([1, 5, 1])
with col1:
    img_path = os.path.join(os.path.dirname(__file__), "..", "profile.png")
    with open(img_path, "rb") as img_file:
        profile_img_b64 = base64.b64encode(img_file.read()).decode()

    st.markdown(f"""
        <div style='margin-top: 1vh; margin-left: 0.2vw;'>
            <div style="border: 0px; padding: 1vh; border-radius: 3vh; height: 20vh; width: 20vh; display: flex; align-items: center; justify-content: center; background-color: #D9D9D9;">
                <img src='data:image/png;base64,{profile_img_b64}' alt="Profile Icon" style="width: 15vh; height: 15vh; border-radius: 50%; object-fit: contain; display: inline-block;" />
            </div>
        </div>
    """, unsafe_allow_html=True)
with col_signout:
    if st.button("Sign Out", key="signout_btn", help="Sign out and return to login"):
        st.session_state.clear()
        st.switch_page("login.py")


if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase_service_account"]))
    firebase_admin.initialize_app(cred)
    
db = firestore.client()
st.markdown("""
    <style>
        body, [data-testid="stAppViewContainer"], .block-container {
            background-color: #413F42 !important;
        }
    </style>
""", unsafe_allow_html=True)

with col_spacer:
    st.markdown("""
        <style>
        form button[kind="formSubmit"], form button[kind="secondaryFormSubmit"] {
            display: none !important;
        }
        button[kind="secondaryFormSubmit"] div[data-testid="stMarkdownContainer"] > p:only-child {
            font-size: 0 !important;
        }
        button[kind="secondaryFormSubmit"] div[data-testid="stMarkdownContainer"] > p:only-child:empty {
            display: none !important;
        }
        button[kind="secondaryFormSubmit"] {
            height: 0 !important;
            min-height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
        }
        </style>
        <h2 style='margin-top: 4vh; color: #fff;'>Patients</h2>
    """, unsafe_allow_html=True)

    user = st.session_state.get('user', None)
    if not user or 'email' not in user:
        st.warning("No user logged in. Please log in first.")
    else:
        user_email = user['email']
        org_docs = db.collection('organization').stream()
        found_org = False
        for org_doc in org_docs:
            org_data = org_doc.to_dict()
            org_users = org_data.get('org_user', [])
            user_match = False
            for user_ref in org_users:
                try:
                    user_doc = user_ref.get()
                    user_info = user_doc.to_dict()
                    if user_info and user_info.get('user_email') == user_email:
                        user_match = True
                        break
                except Exception:
                    continue
            if user_match:
                found_org = True
                org_ref = org_doc.reference
                all_patients = db.collection('patients').stream()
                patient_tiles = []
                for pat_doc in all_patients:
                    pat_data = pat_doc.to_dict()
                    associated_orgs = pat_data.get('pat_associated_org', [])
                    pat_id = pat_data.get('pat_id', None)
                    for ref in associated_orgs:
                        if ref.id == org_ref.id:
                            pat_name = pat_data.get('pat_name', '')
                            pat_img_url = pat_data.get('pat_image')
                            if pat_img_url and pat_img_url.startswith("/v0/b/"):
                                pat_img_url = f"https://firebasestorage.googleapis.com{pat_img_url}?alt=media"
                            pat_img_b64 = None
                            if pat_img_url:
                                try:
                                    resp = requests.get(pat_img_url)
                                    if resp.status_code == 200:
                                        pat_img_b64 = base64.b64encode(resp.content).decode()
                                    else:
                                        print(f"Failed to fetch image, status code: {resp.status_code}")
                                except Exception as e:
                                    pat_img_b64 = None
                            if pat_img_b64:
                                img_html = f"<img src='data:image/png;base64,{pat_img_b64}' style='width:56px; height:56px; border-radius:50%; object-fit:cover; margin-right:18px; border:2px solid #fff;' />"
                            else:
                                img_html = "<div style='background:#E55050; border-radius:50%; width:56px; height:56px; display:flex; align-items:center; justify-content:center; margin-right:18px;'></div>"
                            if pat_id:
                                with st.form(key=f"pat_form_{pat_id}"):
                                    st.markdown(
                                        f"<div style='background: #D9D9D9; border-radius: 1.2vh; width: 100%; height: 90px; display: flex; align-items: center; font-size: 1.2rem; margin-bottom: -8vh; margin-top:1vh; cursor:pointer;'>"
                                        f"<div style='margin-left: 2.2vw; display: flex; align-items: center;'>"
                                        f"{img_html}"
                                        f"<span style='color:#222; font-size:1.3rem; font-family:Inter,sans-serif; margin-left: 1vw;'>{pat_name}</span>"
                                        f"</div>"
                                        f"</div>",
                                        unsafe_allow_html=True
                                    )
                                    submitted = st.form_submit_button("\u200B", use_container_width=True)
                                    if submitted:
                                        st.session_state['selected_patient_id'] = pat_id
                                        st.switch_page("dashboard.py")
        if not found_org:
            st.error("No organizations found for this user.")
