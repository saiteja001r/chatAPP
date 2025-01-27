import streamlit as st
import requests
import time
from frontend.rag import initialize_rag, get_ai_response
from frontend.utils import process_audio

# Backend API URL
BACKEND_URL = "http://127.0.0.1:8000"

# Initialize RAG pipeline
if "qa_chain" not in st.session_state:
    initialize_rag()
    st.session_state["qa_chain"] = True

# Function to login
def login(username, password):
    response = requests.post(f"{BACKEND_URL}/login", json={"username": username, "password": password})
    if response.status_code == 200:
        return True
    return False

# Function to create a session
def create_session(admin):
    response = requests.post(f"{BACKEND_URL}/create_session", json={"admin": admin})
    if response.status_code == 200:
        return response.json()["session_id"]
    return None

# Function to join a session
def join_session(session_id):
    response = requests.post(f"{BACKEND_URL}/join_session", params={"session_id": session_id})
    if response.status_code == 200:
        return True
    return False

# Function to send a message
def send_message(session_id, username, message, is_ai=False):
    requests.post(f"{BACKEND_URL}/send_message", json={
        "session_id": session_id,
        "username": username,
        "message": message,
        "is_ai": is_ai
    })

# Function to get messages
def get_messages(session_id):
    response = requests.get(f"{BACKEND_URL}/get_messages", params={"session_id": session_id})
    if response.status_code == 200:
        return response.json()["messages"]
    return []

# Function to delete a message
def delete_message(message_id):
    response = requests.delete(f"{BACKEND_URL}/delete_message/{message_id}")
    if response.status_code == 200:
        return True
    return False

# Streamlit app
def main():
    st.title("Interview Chat ")

    # Sidebar for session management
    st.sidebar.header("Session Management")

    # Home page options
    option = st.sidebar.radio("Choose an option:", ["Login as Admin", "Join Chat using Session ID"])

    if option == "Login as Admin":
        st.sidebar.subheader("Admin Login")
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            if login(username, password):
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.sidebar.success("Logged in successfully!")
            else:
                st.sidebar.error("Invalid username or password")

        # Create session after login
        if "logged_in" in st.session_state and st.session_state["logged_in"]:
            if st.sidebar.button("Create New Session"):
                session_id = create_session(st.session_state["username"])
                if session_id:
                    st.session_state["session_id"] = session_id
                    st.sidebar.success(f"Session created! Session ID: {session_id}")
                else:
                    st.sidebar.error("Failed to create session")

    elif option == "Join Chat using Session ID":
        st.sidebar.subheader("Join Chat")
        session_id = st.sidebar.text_input("Enter Session ID")
        if st.sidebar.button("Join"):
            if join_session(session_id):
                st.session_state["session_id"] = session_id
                st.sidebar.success("Joined session successfully! Please enter your name below.")
            else:
                st.sidebar.error("Invalid Session ID")

    # Chat interface
    if "session_id" in st.session_state:
        st.write(f"**Session ID:** {st.session_state['session_id']}")

        # Ask for username if not already set
        if "username" not in st.session_state:
            username = st.text_input("Enter Your Name to Start Chatting:")
            if username:
                st.session_state["username"] = username

        # Display chat messages
        messages = get_messages(st.session_state["session_id"])

        # Store selected message IDs for deletion
        if "selected_messages" not in st.session_state:
            st.session_state["selected_messages"] = set()

        # Display messages in WhatsApp-like format
        for msg in messages:
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                if msg[1] == st.session_state.get("username", "") or msg[3]:  # Admin or AI messages
                    # Right-aligned for admin and AI messages
                    st.markdown(
                        f"""
                        <div style="display: flex; justify-content: flex-end; margin-bottom: 10px;">
                            <div style="background-color: #DCF8C6; padding: 10px; border-radius: 10px; max-width: 70%;">
                                <strong>{msg[1]}</strong> ({msg[4]}):<br>{msg[2]}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    # Left-aligned for user messages
                    st.markdown(
                        f"""
                        <div style="display: flex; justify-content: flex-start; margin-bottom: 10px;">
                            <div style="background-color: #ECECEC; padding: 10px; border-radius: 10px; max-width: 70%;">
                                <strong>{msg[1]}</strong> ({msg[4]}):<br>{msg[2]}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            with col2:
                # Add a checkbox for message selection
                if (st.session_state.get("logged_in", False) and st.session_state["username"] == "admin") or msg[1] == st.session_state.get("username", ""):
                    if st.checkbox("Delete", key=f"delete_{msg[0]}"):
                        st.session_state["selected_messages"].add(msg[0])
                    else:
                        st.session_state["selected_messages"].discard(msg[0])

        # Delete selected messages
        if st.button("Delete Selected Messages"):
            if st.session_state["selected_messages"]:
                for message_id in st.session_state["selected_messages"]:
                    if delete_message(message_id):
                        st.success(f"Message {message_id} deleted successfully!")
                    else:
                        st.error(f"Failed to delete message {message_id}.")
                st.session_state["selected_messages"] = set()
                st.rerun()
            else:
                st.error("No messages selected for deletion.")

        # Admin options: Normal message, AI response, Voice recognition
        if "logged_in" in st.session_state and st.session_state["logged_in"]:
            st.subheader("Admin Options")
            admin_option = st.radio("Choose an option:", ["Send Normal Message", "Send AI Response", "Voice Recognition with AI Response"])

            if admin_option == "Send Normal Message":
                new_message = st.text_input("Type your message:")
                if st.button("Send"):
                    if new_message:
                        send_message(st.session_state["session_id"], st.session_state["username"], new_message)
                        st.rerun()
                    else:
                        st.error("Message cannot be empty!")

            elif admin_option == "Send AI Response":
                new_message = st.text_input("Type your message for AI response:")
                if st.button("Send"):
                    if new_message:
                        ai_response = get_ai_response(new_message)
                        send_message(st.session_state["session_id"], "AI", ai_response, is_ai=True)
                        st.rerun()
                    else:
                        st.error("Message cannot be empty!")

            elif admin_option == "Voice Recognition with AI Response":
                st.write("Click the button below to start recording.")
                if st.button("Start Recording"):
                    recognized_text = process_audio()
                    if recognized_text:
                        ai_response = get_ai_response(recognized_text)
                        send_message(st.session_state["session_id"], "AI", ai_response, is_ai=True)
                        st.rerun()

        else:
            # Non-admin input for new message
            new_message = st.text_input("Type your message:")
            if st.button("Send"):
                if new_message:
                    send_message(st.session_state["session_id"], st.session_state["username"], new_message)
                    st.rerun()
                else:
                    st.error("Message cannot be empty!")

        # Automatically refresh the chat every 2 seconds
        time.sleep(2)
        st.rerun()

if __name__ == "__main__":
    main()