import streamlit as st
import requests
import json

st.title("MindMate")
side_bar = st.sidebar
main_component = st.container()
with main_component:
    chat_component = st.container()

def submitForm(username, password):
    st.write("Submitted")
    headers={"Content-Type": "application/json", "Accept": "text/plain"}
    response = requests.post("http://localhost:5000/user/login", data=json.dumps({"username": username, "password": password}), headers=headers)
    data = response.json()
    if response.json() == []:
        if username != "" and password != "":
            response = requests.post("http://localhost:5000/user", data=json.dumps({"username": username, "password": password}), headers=headers)
            data = response.json()
            st.session_state.user = data[0]
    else:
        st.session_state.user = data[0]
    # st.session_state.messages.append({"role": "user", "content": prompt})

def getChats(user_id):
    headers={"Content-Type": "application/json", "Accept": "text/plain"}
    response = requests.post("http://localhost:5000/chat/getwithid", data=json.dumps({"user_id": user_id}), headers=headers)
    data = response.json()
    return data

def getMessages(chat_id):
    headers={"Content-Type": "application/json", "Accept": "text/plain"}
    response = requests.post("http://localhost:5000/message/getwithid", data=json.dumps({"chat_id": chat_id}), headers=headers)
    data = response.json()
    # i want to change the format of the dict from {"id": 1, chat_id: 1, question: "hello", answer: "hi"} to {"role": "user", "content": {question}} and {"role": "assistant", "content": {answer}}
    chats = [{"role": "assistant", "content": "Hello, I'm MindMate. How can I help you?"}]
    for message in data:
        user_dict = {"role": "user", "content": message["question"]}
        assistant_dict = {"role": "assistant", "content": message["answer"]}
        chats.append(user_dict)
        chats.append(assistant_dict)
    st.session_state.messages.clear()  
    st.session_state.messages = chats
    if st.session_state.messages != [{"role": "assistant", "content": "Hello, I'm MindMate. How can I help you?"}]:
        st.session_state.chat_id = chat_id
    else:
        if "chat_id" in st.session_state:
            del st.session_state.chat_id

def init_side_bar():
    title = st.empty()
    placeholder = st.empty()
    chat_placeholder = st.empty()
    button_placeholder = st.empty()
    if "user" not in st.session_state:
        with placeholder.form("my_form"):
            st.title("Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            # Every form must have a submit button.
            submitted = st.form_submit_button("Login or sign up", on_click=submitForm(username, password))
            if submitted:
                user = st.session_state.user
                chats = getChats(user["id"])
                placeholder.empty()
                with chat_placeholder.container():
                    title.title("Chats")
                    for chat in chats:
                        st.button(chat["name"], on_click=(lambda chat_id=chat["id"] : getMessages(chat_id)))
    else:
        user = st.session_state.user
        chats = getChats(user["id"])
        placeholder.empty()
        button_placeholder.empty()
        with chat_placeholder.container():
            title.title("Chats")
            button_placeholder.button("New Chat", on_click=(lambda : getMessages(0)))
            for chat in chats:
                st.button(chat["name"], on_click=(lambda chat_id=chat["id"] : getMessages(chat_id)))

with side_bar:
    init_side_bar()

# first a login or register page
# get all chats first getAll
# homepage is a new chat new chat
# when clicked on chat to the right you open that chat
# initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello, I'm MindMate. How can I help you?"}]	

# Display chat messages from history on app rerun
with main_component:
    with chat_component:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"].replace('"', " ").replace("\\r", " ").replace("\\n", " "))

    # React to user input
    if prompt := st.chat_input("What would you like to say?"):
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add user message to chat history    
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            headers={"Content-Type": "application/json", "Accept": "text/plain"}
            full_response = ""
            if "chat_id" in st.session_state:
                full_response = requests.post("http://localhost:5000/message", data=json.dumps({"prompt": prompt, "chat_id": st.session_state.chat_id}), headers=headers).text
            elif "user" in st.session_state:
                data = requests.post("http://localhost:5000/chat", data=json.dumps({"user_id": st.session_state.user["id"], "name": " ".join(prompt.split()[:2])}), headers=headers).json()
                chat = data[0]
                st.session_state.chat_id = chat["id"]
                full_response = requests.post("http://localhost:5000/message", data=json.dumps({"prompt": prompt, "chat_id": st.session_state.chat_id}), headers=headers).text
            else:
                full_response = requests.post("http://localhost:5000/message", data=json.dumps({"prompt": prompt}), headers=headers).text
            without_quotes = full_response.replace('"', " ")
            cleaned_string = without_quotes.replace("\\r", " ").replace("\\n", " ")
            message_placeholder.markdown(cleaned_string)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        