import streamlit as st
import requests
import uuid
import base64
import json
from base64 import b64encode

# ===================== Credentials (Replace with Valid Keys) =====================
O365_CLIENT_ID = "9ad3e943-e3ee-444c-bf13-fa9aa42271d2"
O365_CLIENT_SECRET = "FhZ8Q~IgNilr9ALPI.LJrr0RD0W~tW.FNaZAudbj"
O365_TENANT_ID = "21d775da-95bf-43f6-81ba-bf324d8ab4d7"
OKTA_API_TOKEN = "00Mv0Dh5haDKTAfnpceBFJSdPWzA0f_o1GuWwIm4Gp"
ZOOM_CLIENT_ID = "hc5_41toRg2Z1fmUrGEv0Q"
ZOOM_CLIENT_SECRET = "MkKt2xi3lbut5aWequu66C9xU4llLv8C"
ACCOUNT_ID = 'wp7_4-OQTvq7iqDgh9r9hw'      # Replace with your Account ID
API_BASE_URL = "https://us-api.mimecast.com"  # Replace with your region-specific URL
CLIENT_ID = "mfyu5BN6Q466qIvAvA6NZaxteZJQJ7xB2TaFIQZfFXDm5J9V"
CLIENT_SECRET = "JFuzAqJM6ueJ41bwH81t2jj0dJGuOGMEyST4G6srAhs5kccIGkcNmeatIxnr49ip"  # Replace with your actual Client Secret


# ===================== Error Logging =====================
error_logs = []

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
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        show_error("Microsoft 365", "Get Access Token", response.text)
        return None

def o365_create_user(access_token, email, display_name, job_title=None, phone_number=None):
    url = "https://graph.microsoft.com/v1.0/users"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "accountEnabled": True,
        "displayName": display_name,
        "mailNickname": email.split("@")[0],
        "userPrincipalName": email,
        "passwordProfile": {
            "forceChangePasswordNextSignIn": True,
            "password": "P@ssw0rd1234"
        },
        "jobTitle": job_title,
        "mobilePhone": phone_number
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 201:
        return "User created successfully in Microsoft 365."
    else:
        show_error("Microsoft 365", "Create User", response.text)
        return None

def o365_delete_user(access_token, user_id):
    url = f"https://graph.microsoft.com/v1.0/users/{user_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        return "User deleted successfully from Microsoft 365."
    else:
        show_error("Microsoft 365", "Delete User", response.text)
        return None

# ===================== OKTA Functions =====================
def okta_create_user(email, display_name, job_title=None, phone_number=None):
    name_parts = display_name.strip().split()
    first_name = name_parts[0]
    last_name = "User" if len(name_parts) == 1 else " ".join(name_parts[1:])
    url = "https://trial-7346022.okta.com/api/v1/users"
    headers = {
        "Authorization": f"SSWS {OKTA_API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "profile": {
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "login": email,

           
        },
        "credentials": {
            "password": {"value": "SecureP@ss123"}
        }
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code in [200, 201]:
        return "User created successfully in Okta."
    else:
        show_error("Okta", "Create User", response.text)
        return None

def okta_delete_user(user_id):
    url = f"https://trial-7346022.okta.com/api/v1/users/{user_id}"
    headers = {"Authorization": f"SSWS {OKTA_API_TOKEN}"}
    deactivate_resp = requests.post(f"{url}/lifecycle/deactivate", headers=headers)
    if deactivate_resp.status_code not in [200, 204]:
        show_error("Okta", "Deactivate User", deactivate_resp.text)
        return None
    delete_resp = requests.delete(url, headers=headers)
    if delete_resp.status_code == 204:
        return "User deleted successfully from Okta."
    else:
        show_error("Okta", "Delete User", delete_resp.text)
        return None

# ===================== Zoom Functions =====================
def zoom_get_access_token():
    url = 'https://zoom.us/oauth/token'
    headers = {
        'Authorization': 'Basic ' + b64encode(f'{ZOOM_CLIENT_ID}:{ZOOM_CLIENT_SECRET}'.encode()).decode(),
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {'grant_type': 'account_credentials', 'account_id': ACCOUNT_ID}
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        show_error("Zoom", "Get Access Token", response.text)
        return None

def zoom_create_user(access_token, email, first_name, last_name):
    url = 'https://api.zoom.us/v2/users'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    payload = {
        'action': 'create',
        'user_info': {
            'email': email,
            'type': 1,
            'first_name': first_name,
            'last_name': last_name
        }
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code in [200, 201]:
        return "User created successfully in Zoom."
    else:
        show_error("Zoom", "Create User", response.text)
        return None

def zoom_delete_user(access_token, user_id):
    url = f'https://api.zoom.us/v2/users/{user_id}'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        return "User deleted successfully from Zoom."
    else:
        show_error("Zoom", "Delete User", response.text)
        return None

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
        if msg["role"] == "assistant":
            with st.chat_message("assistant"):
                st.write(msg["content"])
        else:
            with st.chat_message("user"):
                st.write(msg["content"])

display_chat()

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    if st.session_state.step == "start":
        reply = "Welcome! Would you like to onboard or offboard a user?"
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.session_state.step = "action"
        with st.chat_message("assistant"):
            st.write(reply)

    elif st.session_state.step == "action":
        if "onboard" in user_input.lower():
            st.session_state.action = "Onboard"
            reply = "Which platform? (Microsoft 365, OKTA, or Zoom)"
            st.session_state.step = "platform"
        elif "offboard" in user_input.lower():
            st.session_state.action = "Offboard"
            reply = "Which platform? (Microsoft 365, OKTA, or Zoom)"
            st.session_state.step = "platform"
        else:
            reply = "Invalid action. Please type 'onboard' or 'offboard'."
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.write(reply)

    elif st.session_state.step == "platform":
        if "microsoft" in user_input.lower():
            st.session_state.platform = "Microsoft"
        elif "okta" in user_input.lower():
            st.session_state.platform = "OKTA"
        elif "zoom" in user_input.lower():
            st.session_state.platform = "Zoom"
        else:
            reply = "Invalid platform. Please choose Microsoft 365, OKTA, or Zoom."
            st.session_state.messages.append({"role": "assistant", "content": reply})
            with st.chat_message("assistant"):
                st.write(reply)
            st.stop()

        reply = "Please provide email, display name, job title, and phone number." if st.session_state.action == "Onboard" else "Please provide the user ID or email to offboard."
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.session_state.step = "collect_info"
        with st.chat_message("assistant"):
            st.write(reply)

    elif st.session_state.step == "collect_info":
    # Split by commas and trim whitespace
       input_parts = [part.strip() for part in user_input.split(",")]
   
       if st.session_state.action == "Onboard":
           # Validate there are exactly 4 parts
           if len(input_parts) == 4:
               email, display_name, job_title, phone_number = input_parts
   
               # Validate email
               if "@" not in email or "." not in email:
                   reply = "Invalid email format. Please enter a valid email address."
               # Validate phone number
               elif not phone_number.isdigit():
                   reply = "Invalid phone number. Please provide a numeric phone number."
               else:
                   # Save user data if all validations pass
                   st.session_state.user_data = {
                       "email": email,
                       "display_name": display_name,
                       "job_title": job_title,
                       "phone_number": phone_number
                   }
                   reply = f"Collected: {st.session_state.user_data}. Type 'submit' to confirm."
                   st.session_state.step = "submit"
           else:
               # If the input format is incorrect
               reply = (
                   "Invalid input. Please provide details in this format: "
                   "'email, display_name, job_title, phone_number'."
               )
   
       elif st.session_state.action == "Offboard":
           # Validate there is exactly 1 part for offboarding
           if len(input_parts) == 1:
               st.session_state.user_data = {"user_id": input_parts[0]}
               reply = f"Collected: {st.session_state.user_data}. Type 'submit' to confirm."
               st.session_state.step = "submit"
           else:
               reply = "Invalid input. Please provide only the user ID to offboard."
   
       # Append the reply and display
       st.session_state.messages.append({"role": "assistant", "content": reply})
       with st.chat_message("assistant"):
           st.write(reply)


    elif st.session_state.step == "submit":
        if "submit" in user_input.lower():
            platform = st.session_state.platform
            action = st.session_state.action
            user_data = st.session_state.user_data
            if action == "Onboard":
                if platform == "Microsoft":
                    token = o365_get_access_token()
                    reply = o365_create_user(
                        token, user_data["email"], user_data["display_name"],
                        user_data["job_title"], user_data["phone_number"]
                    )
                elif platform == "OKTA":
                    reply = okta_create_user(
                        user_data["email"], user_data["display_name"],
                        user_data["job_title"], user_data["phone_number"]
                    )
                elif platform == "Zoom":
                    token = zoom_get_access_token()
                     
                         # Try to split the display name into first and last names
                    first_name, last_name = user_data["display_name"].split()
                    reply = zoom_create_user(
                        token, user_data["email"], first_name, last_name
                    )
            elif action == "Offboard":
                if platform == "Microsoft":
                    token = o365_get_access_token()
                    reply = o365_delete_user(token, user_data["user_id"])
                elif platform == "OKTA":
                    reply = okta_delete_user(user_data["user_id"])
                elif platform == "Zoom":
                    token = zoom_get_access_token()
                    reply = zoom_delete_user(token, user_data["user_id"])
            else:
                reply = "Unknown action or platform."
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.session_state.step = "done"
            with st.chat_message("assistant"):
                st.write(reply)

    elif st.session_state.step == "done":
        reply = "All done! Type 'onboard' or 'offboard' to start over."
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.session_state.step = "start"
        with st.chat_message("assistant"):
            st.write(reply)
