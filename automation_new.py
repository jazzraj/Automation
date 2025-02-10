

import streamlit as st
import requests
import uuid
import base64
import json
from base64 import b64encode

# ===================== Sidebar Navigation =====================
st.sidebar.title("Navigation")
menu = st.sidebar.selectbox("Select an option", ["Chatbot", "API Credentials"])

# ===================== API Credentials Input =====================
if menu == "API Credentials":
    with st.sidebar.expander("Enter API Credentials"):
        platform = st.selectbox("Select Platform", ["Microsoft 365", "OKTA", "Zoom"])
        if platform == "Microsoft 365":
            O365_CLIENT_ID = st.text_input("O365 Client ID", type="password")
            O365_CLIENT_SECRET = st.text_input("O365 Client Secret", type="password")
            O365_TENANT_ID = st.text_input("O365 Tenant ID", type="password")
        elif platform == "OKTA":
            OKTA_API_TOKEN = st.text_input("Okta API Token", type="password")
        elif platform == "Zoom":
            ZOOM_CLIENT_ID = st.text_input("Zoom Client ID", type="password")
            ZOOM_CLIENT_SECRET = st.text_input("Zoom Client Secret", type="password")
            ACCOUNT_ID = st.text_input("Zoom Account ID", type="password")

# ===================== Microsoft 365 Functions =====================
def o365_get_access_token():
    url = f"https://login.microsoftonline.com/{O365_TENANT_ID}/oauth2/v2.0/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": O365_CLIENT_ID,
        "client_secret": O365_CLIENT_SECRET,
        "scope": "https://graph.microsoft.com/.default"
    }
    response = requests.post(url, data=data)
    return response.json().get("access_token") if response.status_code == 200 else None

def o365_disable_user(access_token, user_id):
    url = f"https://graph.microsoft.com/v1.0/users/{user_id}"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    payload = {"accountEnabled": False}
    response = requests.patch(url, json=payload, headers=headers)
    return "User disabled successfully" if response.status_code == 200 else "Error disabling user"

def o365_reset_password(access_token, user_id):
    url = f"https://graph.microsoft.com/v1.0/users/{user_id}/changePassword"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    payload = {"passwordProfile": {"forceChangePasswordNextSignIn": True, "password": "NewP@ssw0rd123"}}
    response = requests.post(url, json=payload, headers=headers)
    return "Password changed successfully" if response.status_code == 200 else "Error changing password"

# ===================== Streamlit Chatbot =====================
if menu == "Chatbot":
    st.title("Onboarding/Offboarding Chatbot")
    user_input = st.chat_input("Type your message here...")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "step" not in st.session_state:
        st.session_state.step = "start"
    if "user_data" not in st.session_state:
        st.session_state.user_data = {}
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
        
        if st.session_state.step == "start":
            reply = "Would you like to onboard or offboard a user?"
            st.session_state.step = "action"
        elif st.session_state.step == "action":
            if "onboard" in user_input.lower():
                st.session_state.action = "Onboard"
                reply = "Which platform? (Microsoft 365, OKTA, Zoom)"
                st.session_state.step = "platform"
            elif "offboard" in user_input.lower():
                st.session_state.action = "Offboard"
                reply = "Which platform? (Microsoft 365, OKTA, Zoom)"
                st.session_state.step = "platform"
            else:
                reply = "Invalid action. Please type 'onboard' or 'offboard'."
        elif st.session_state.step == "platform":
            if "microsoft" in user_input.lower():
                st.session_state.platform = "Microsoft"
            elif "okta" in user_input.lower():
                st.session_state.platform = "OKTA"
            elif "zoom" in user_input.lower():
                st.session_state.platform = "Zoom"
            else:
                reply = "Invalid platform. Choose Microsoft 365, OKTA, or Zoom."
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.stop()
            reply = "Provide user ID for offboarding."
            st.session_state.step = "collect_info"
        elif st.session_state.step == "collect_info":
            st.session_state.user_data = {"user_id": user_input.strip()}
            reply = "Confirm by typing 'submit'."
            st.session_state.step = "submit"
        elif st.session_state.step == "submit":
            if "submit" in user_input.lower():
                user_id = st.session_state.user_data["user_id"]
                if st.session_state.action == "Offboard":
                    if st.session_state.platform == "Microsoft":
                        token = o365_get_access_token()
                        disable_resp = o365_disable_user(token, user_id)
                        password_resp = o365_reset_password(token, user_id)
                        reply = f"{disable_resp}\n{password_resp}"
                    else:
                        reply = "Feature not implemented for this platform."
                st.session_state.step = "done"
            else:
                reply = "Type 'submit' to confirm."
        elif st.session_state.step == "done":
            reply = "All done! Type 'onboard' or 'offboard' to start over."
            st.session_state.step = "start"
        
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.write(reply)

