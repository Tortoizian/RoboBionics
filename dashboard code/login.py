import streamlit as st

st.set_page_config(layout="wide")

# --- LOGIN PAGE ---
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
    <div style="height: 10vh"></div>
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
        <div style="border: 0px; padding: 2vh; border-radius: 2vh; height: 32vh; width: 32vh; display: flex; align-items: center; justify-content: center; background-color: #D9D9D9;">
            <span style="height: 24vh; width: 24vh; background-color: #E55050; border-radius: 50%; display: inline-block"></span>
        </div>
        <div style="height: 4vh"></div>
    </div>
""", unsafe_allow_html=True)

login_container = st.container()
with login_container:
    st.markdown("""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
            <div style="border: 0px; padding: 2vh; border-radius: 2vh; margin-bottom: 2vh; height: 8vh; width: 32vh; display: flex; align-items: center; background-color: #D9D9D9;">
                <input type="text" placeholder="Username" style="width: 100%; height: 100%; font-size: 2vh; border: none; background: transparent; outline: none; font-family: 'Inter', sans-serif; text-align: center;" id="username-box" />
            </div>
            <div style="border: 0px; padding: 2vh; border-radius: 2vh; height: 8vh; width: 32vh; display: flex; align-items: center; background-color: #D9D9D9;">
                <button style="width: 100%; height: 100%; font-size: 2vh; border: none; background: #E55050; color: white; border-radius: 2vh; font-family: 'Jost', sans-serif; cursor: pointer;" id="login-btn">Login</button>
            </div>
        </div>
    """, unsafe_allow_html=True)
