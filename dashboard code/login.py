import streamlit as st
from streamlit_javascript import st_javascript
import base64

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

st.markdown("""
    <div style="height: 10vh"></div>
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
        <div style="border: 0px; padding: 2vh; border-radius: 3vh; height: 28vh; width: 28vh; display: flex; align-items: center; justify-content: center; background-color: #D9D9D9;">
            <span style="height: 21vh; width: 21vh; background-color: #E55050; border-radius: 50%; display: inline-block"></span>
        </div>
        <div style="height: 4vh"></div>
    </div>
""", unsafe_allow_html=True)

with st.container():
    with open("username.png", "rb") as img_file:
        username_img_b64 = base64.b64encode(img_file.read()).decode()
    with open("password.png", "rb") as img_file:
        password_img_b64 = base64.b64encode(img_file.read()).decode()

    st.markdown(f"""
        <div id="login-container" style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
            <div style="border: 0px; padding: 2vh; border-radius: 2vh; margin-bottom: 2vh; height: 8.5vh; width: 80vh; display: flex; align-items: center; background: linear-gradient(90deg, #C7C2C2 0 10vh, #D9D9D9 10vh 100%); position: relative;">
                <div style="position: absolute; left: 2vh; top: 50%; transform: translateY(-50%); width: 6vh; height: 6vh; display: flex; align-items: center; justify-content: center;">
                    <img src='data:image/png;base64,{username_img_b64}' alt="username" style="width: 4vh; height: 4vh; object-fit: contain;" />
                </div>
                <input id="username" type="text" placeholder="Username" style="flex: 1; height: 100%; font-size: 2vh; border: none; background: transparent; outline: none; font-family: 'Jost', sans-serif; text-align: left; margin-left: 10vh; padding-left: 0;"/>
            </div>
            <div style="border: 0px; padding: 2vh; border-radius: 2vh; margin-bottom: 2vh; height: 8.5vh; width: 80vh; display: flex; align-items: center; background: linear-gradient(90deg, #C7C2C2 0 10vh, #D9D9D9 10vh 100%); position: relative;">
                <div style="position: absolute; left: 2vh; top: 50%; transform: translateY(-50%); width: 6vh; height: 6vh; display: flex; align-items: center; justify-content: center;">
                    <img src='data:image/png;base64,{password_img_b64}' alt="password" style="width: 4vh; height: 4vh; object-fit: contain;" />
                </div>
                <input id="password" type="password" placeholder="Password" style="flex: 1; height: 100%; font-size: 2vh; border: none; background: transparent; outline: none; font-family: 'Jost', sans-serif; text-align: left; margin-left: 10vh; padding-left: 0;"/>
            </div>
            <div style="width: 80vh; display: flex; align-items: center; justify-content: space-between; margin-bottom: 2vh;">
                <div style="display: flex; align-items: center;">
                    <input type="checkbox" id="remember-me" style="width: 2.5vh; height: 2.5vh; margin-right: 1vh; margin-left: 1vh;" />
                    <label for="remember-me" style="font-size: 1.8vh; color: #fff; font-family: 'Jost', sans-serif; font-weight: 500;">Remember Me</label>
                </div>
                <a href="#" style="font-size: 1.8vh; color: #FFFFFF; font-family: 'Jost', sans-serif; cursor: pointer; font-weight: 500; text-decoration: none;">Forgot Password</a>
            </div>
            <div style="height:5vh"></div>
            <button id="login-btn" style="width: 18vh; height: 6vh; font-size: 2vh; border: none; background: #E55050; color: white; border-radius: 2vh; font-family: 'Jost', sans-serif; cursor: pointer;">Login</button>
        </div>
    """, unsafe_allow_html=True)

js_code = """
() => {
    return new Promise((resolve) => {
        const button = document.getElementById("login-btn");
        if (button) {
            button.onclick = () => {
                const username = document.getElementById("username").value;
                const password = document.getElementById("password").value;
                resolve({username, password});
            };
        }
    });
}
"""

result = st_javascript(js_code, key="login_script")

if result and "username" in result and "password" in result:
    st.success("Form submitted!")
    st.write("Username:", result["username"])
    st.write("Password:", result["password"])
    print("Password:", result["password"])
