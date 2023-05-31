import subprocess
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import gdown
import os
import zipfile

def execute_script(script_path):
    subprocess.run(['streamlit', 'run', script_path])


def login_page():
    st.title("User Login")
    username = st.text_input("Username",key="username")
    password = st.text_input("Password", type="password",key="password")
    if st.button("Login"):
        # Verify user credentials
        if username == "admin" and password == "admin_password":
            st.success("Logged in as admin!")
            return True, "admin"
        elif username == "user" and password == "user_password":
            st.success("Logged in as user!")
            return True, "user"
        else:
            st.error("Invalid username or password.")
    return False, None


def main():
    with open('./config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )

    name, authentication_status, username = authenticator.login('Login', 'main')
    
    if authentication_status:

        if username == "admin":

            execute_script('Finance-Admin.py')
                    
        if username == "user":

            execute_script('Finance-User.py')
                    
    elif authentication_status == False:
        st.error("Username/password is incorrect")

    elif authentication_status == None:
        st.warning("Please enter your username and password")
        
    else:
        st.error("Authentication failed. Please try again.")
            

if __name__ == '__main__':
    main()