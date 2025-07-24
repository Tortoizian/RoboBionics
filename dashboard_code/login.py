import os
import streamlit as st
import streamlit.components.v1 as components
import requests
from urllib.parse import parse_qs
import base64
import os

st.set_page_config(layout="wide")

st.markdown("""<div style="height:7vh"></div>""", unsafe_allow_html=True)

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

with st.container():
    img_path = os.path.join(os.path.dirname(__file__), "..", "profile.png")
    with open(img_path, "rb") as img_file:
        profile_img_b64 = base64.b64encode(img_file.read()).decode()

    st.markdown(f"""
        <div style="height: 10vh"></div>
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
            <div style="border: 0px; padding: 2vh; border-radius: 3vh; height: 28vh; width: 28vh; display: flex; align-items: center; justify-content: center; background-color: #D9D9D9;">
                <img src='data:image/png;base64,{profile_img_b64}' alt="Profile Icon" style="width: 21vh; height: 21vh; border-radius: 50%; object-fit: contain; display: inline-block;" />
            </div>
            <div style="height: 4vh"></div>
        </div>
    """, unsafe_allow_html=True)

if 'user' not in st.session_state:
    st.session_state['user'] = None


if st.session_state['user'] is None:
    firebase_config = {
        "apiKey": st.secrets["firebase"]["apiKey"],
        "authDomain": st.secrets["firebase"]["authDomain"],
        "projectId": st.secrets["firebase"]["projectId"],
        "appId": st.secrets["firebase"]["appId"]
    }
    col = st.columns([1,1,1])
    with col[1]:
        email = st.text_input("Email", key="email_input", label_visibility="collapsed", placeholder="Email")
        password = st.text_input("Password", type="password", key="password_input", label_visibility="collapsed", placeholder="Password")
        col2 = st.columns([1,1,1])
        with col2[1]:
            st.markdown("""
                <style>
                .stButton > button {
                    background-color: #E55050;
                    color: white;
                    border-radius: 3vh;
                    height: 5vh;
                    font-size: 1.2rem;
                    margin-left: 6vh;
                }
                </style>
            """, unsafe_allow_html=True)
            login_btn = st.button("Login", key="login_btn")
        with col2[2]:
            google_btn_html = f'''
            <style>
                #google-login-btn {{
                    background-color: #fff;
                    color: #444;
                    border: 1px solid #ccc;
                    border-radius: 3vh;
                    height: 5vh;
                    font-size: 0.7rem;
                    width: 100%;
                    cursor: pointer;
                    margin-top: 2.4vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 0.5em;
                }}
                #google-login-btn:hover {{
                    background-color: #f5f5f5;
                }}
            </style>
            <button id="google-login-btn">
                Sign in with Google
            </button>
            <script src="https://www.gstatic.com/firebasejs/9.6.1/firebase-app-compat.js"></script>
            <script src="https://www.gstatic.com/firebasejs/9.6.1/firebase-auth-compat.js"></script>
            <script>
              var firebaseConfig = {firebase_config};
              if (!window.firebaseAppsInit) {{
                firebase.initializeApp(firebaseConfig);
                window.firebaseAppsInit = true;
              }}
              function googleLogin() {{
                var provider = new firebase.auth.GoogleAuthProvider();
                firebase.auth().signInWithPopup(provider).then(function(result) {{
                  const user = result.user;
                  const params = new URLSearchParams({{
                    'firebase-login': '1',
                    'email': user.email,
                    'name': user.displayName
                  }});
                  window.location.search = params.toString();
                }}).catch(function(error) {{
                  alert('Google login failed: ' + error.message);
                }});
              }}
              document.addEventListener('DOMContentLoaded', function() {{
                var btn = document.getElementById('google-login-btn');
                if (btn) btn.onclick = googleLogin;
              }});
            </script>
            '''
            components.html(google_btn_html, height=700)

    if login_btn:
        print("Login button clicked")
        FIREBASE_API_KEY = st.secrets["firebase"]["apiKey"]
        FIREBASE_AUTH_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        resp = requests.post(FIREBASE_AUTH_URL, json=payload)
        print(f"response: {resp.request.body}")
        print(f"Response text: {resp.text}")
        print(f"Response status code: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            st.session_state['user'] = {
                'email': data.get('email'),
                'idToken': data.get('idToken'),
                'localId': data.get('localId')
            }
            st.success(f"Login successful! Welcome, {data.get('email')}")
            st.switch_page("pages/list.py")
        else:
            error = resp.json().get('error', {}).get('message', 'Login failed')
            st.error(f"Login failed: {error}")
else:
    st.success(f"Logged in as: {st.session_state['user']['email']}")
    if st.session_state['user']['email'] == 'admin@example.com':
        st.header("Admin Dashboard")
        st.write("Welcome, admin! You have access to admin features.")
    else:
        st.header("User Dashboard")
        st.write(f"Welcome, {st.session_state['user']['email']}! This is your dashboard.")



query_params = st.query_params
if 'firebase-login' in query_params:
    email = query_params.get('email', [None])[0]
    name = query_params.get('name', [None])[0]
    if email:
        st.session_state['user'] = {
            'email': email,
            'name': name,
            'provider': 'google'
        }
        st.success(f"Google login successful! Welcome, {name or email}")
        st.experimental_rerun()