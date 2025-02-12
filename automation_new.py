import streamlit as st
import requests
import base64
import uuid

# ===================== Sidebar Navigation =====================
st.sidebar.title("Navigation")


O365_CLIENT_ID = st.sidebar.text_input("O365 Client ID", type="password")
O365_CLIENT_SECRET = st.sidebar.text_input("O365 Client Secret", type="password")
O365_TENANT_ID  = st.sidebar.text_input("O365 Tenant ID", type="password")
OKTA_API_TOKEN = st.sidebar.text_input("Okta API Token", type="password")
ZOOM_CLIENT_ID= st.sidebar.text_input("Zoom Client ID", type="password")
ZOOM_CLIENT_SECRET = st.sidebar.text_input("Zoom Client Secret", type="password")
ACCOUNT_ID  = st.sidebar.text_input("Zoom Account ID", type="password")

# ===================== Credentials =====================
# O365_CLIENT_ID = "9ad3e943-e3ee-444c-bf13-fa9aa42271d2"
# O365_CLIENT_SECRET = "FhZ8Q~IgNilr9ALPI.LJrr0RD0W~tW.FNaZAudbj"
# O365_TENANT_ID = "21d775da-95bf-43f6-81ba-bf324d8ab4d7"
# OKTA_API_TOKEN = "00Mv0Dh5haDKTAfnpceBFJSdPWzA0f_o1GuWwIm4Gp"
# ZOOM_CLIENT_ID = "hc5_41toRg2Z1fmUrGEv0Q"
# ZOOM_CLIENT_SECRET = "MkKt2xi3lbut5aWequu66C9xU4llLv8C"
# ACCOUNT_ID = "wp7_4-OQTvq7iqDgh9r9hw"

# ===================== Error Logging =====================
def show_error(platform, action, response):
    st.error(f"Error in {platform} during {action}: {response}")

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

def o365_create_user(access_token, email, display_name, job_title=None, phone_number=None):
    url = "https://graph.microsoft.com/v1.0/users"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    payload = {
        "accountEnabled": True,
        "displayName": display_name,
        "mailNickname": email.split("@")[0],
        "userPrincipalName": email,
        "passwordProfile": {"forceChangePasswordNextSignIn": True, "password": "P@ssw0rd1234"},
        "jobTitle": job_title,
        "mobilePhone": phone_number
    }
    response = requests.post(url, json=payload, headers=headers)
    return "User created successfully in Microsoft 365." if response.status_code == 201 else None

def o365_disable_user(access_token, user_id):
    url = f"https://graph.microsoft.com/v1.0/users/{user_id}"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    payload = {"accountEnabled": False}
    response = requests.patch(url, json=payload, headers=headers)
    return "User disabled successfully in Microsoft 365." if response.status_code == 200 else None

# ===================== OKTA Functions =====================
def okta_create_user(email, display_name, job_title=None, phone_number=None):
    url = "https://trial-7346022.okta.com/api/v1/users"
    headers = {"Authorization": f"SSWS {OKTA_API_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "profile": {"firstName": display_name.split()[0], "lastName": " ".join(display_name.split()[1:]), "email": email, "login": email, "jobTitle": job_title, "mobilePhone": phone_number},
        "credentials": {"password": {"value": "SecureP@ss123"}}
    }
    response = requests.post(url, json=payload, headers=headers)
    return "User created successfully in OKTA." if response.status_code in [200, 201] else None

def okta_disable_user(user_id):
    url = f"https://trial-7346022.okta.com/api/v1/users/{user_id}/lifecycle/deactivate"
    headers = {"Authorization": f"SSWS {OKTA_API_TOKEN}"}
    response = requests.post(url, headers=headers)
    return "User disabled successfully in OKTA." if response.status_code == 200 else None

# ===================== Zoom Functions =====================
def zoom_get_access_token():
    url = 'https://zoom.us/oauth/token'
    headers = {'Authorization': 'Basic ' + b64encode(f'{ZOOM_CLIENT_ID}:{ZOOM_CLIENT_SECRET}'.encode()).decode(), 'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'grant_type': 'account_credentials', 'account_id': ACCOUNT_ID}
    response = requests.post(url, headers=headers, data=data)
    return response.json().get('access_token') if response.status_code == 200 else None

def zoom_create_user(access_token, email, first_name, last_name):
    url = 'https://api.zoom.us/v2/users'
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
    payload = {'action': 'create', 'user_info': {'email': email, 'type': 1, 'first_name': first_name, 'last_name': last_name}}
    response = requests.post(url, json=payload, headers=headers)
    return "User created successfully in Zoom." if response.status_code in [200, 201] else None

def zoom_disable_user(access_token, user_id):
    url = f'https://api.zoom.us/v2/users/{user_id}/status'
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
    payload = {"action": "deactivate"}
    response = requests.put(url, json=payload, headers=headers)
    return "User disabled successfully in Zoom." if response.status_code == 200 else None

# ===================== Streamlit Chatbot =====================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "step" not in st.session_state:
    st.session_state.step = "start"
if "user_data" not in st.session_state:
    st.session_state.user_data = {}

st.title("Onboarding/Offboarding Chatbot")
user_input = st.chat_input("Type your message here...")

def display_chat():
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

display_chat()

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
    elif st.session_state.step == "platform":
        st.session_state.platform = user_input
        reply = "Please provide the required details." if st.session_state.action == "Onboard" else "Enter user ID."
        st.session_state.step = "collect_info"
    elif st.session_state.step == "collect_info":
        st.session_state.user_data = {"info": user_input}
        reply = "Type 'submit' to proceed."
        st.session_state.step = "submit"
    elif st.session_state.step == "submit" and "submit" in user_input.lower():
        if st.session_state.action == "Onboard":
            reply = "Onboarding user..."
        else:
            reply = "Disabling user..."
        st.session_state.step = "done"
    elif st.session_state.step == "done":
        reply = "Process completed! Type 'onboard' or 'offboard' to start again."

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.write(reply)
