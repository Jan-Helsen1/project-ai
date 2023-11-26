from flask import Flask, request, jsonify
import os
from supabase import create_client, Client
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.llms import Ollama

from langchain.chains.conversation.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain.memory import  ChatMessageHistory

from langchain.chains import ConversationChain

supabase: Client = create_client("https://rikddbisemwuyaiqmyxl.supabase.co", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJpa2RkYmlzZW13dXlhaXFteXhsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDA2NjIyMDcsImV4cCI6MjAxNjIzODIwN30.9sYM9WMFbNJTWOhe_PBo3hO2vgBTaXrEFzGOC0z32wc")
llm = Ollama(
    model="mindmate", callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]), stop=["Human:", "human:", "assistant:" ,"### System:", "<|im_end|>", "Current conversation:", "Your previous messages:"]
)
memory = ConversationBufferMemory()
# memory.save_context({"input": "Feeling stressed"}, {"output":"why are you feeling stressed?"})
# memory.save_context({"input": "I have a lot of work"}, {"output":"what kind of work?"})
# memory.save_context({"input": "school work"}, {"output":"can you go in detail?"})
# memory.save_context({"input": "No it just gives me stress"}, {"output":"Maybe talking about it can make you feel better"})

conversation = ConversationChain(llm=llm, memory=memory, verbose=True)

app = Flask(__name__)
# conversation = None

@app.route("/")
def home():
    return "Home"

@app.route("/user", methods=["GET"])
def get_users():
    response = supabase.table("user").select("*").execute()
    return jsonify(response.data)

@app.route("/user", methods=["POST"])
def add_user():
    data = request.get_json()
    response = supabase.table("user").insert({"username": data["username"], "password": data["password"]}).execute()
    return jsonify(response.data)

@app.route("/user/getwithemail", methods=["POST"])
def get_user_with_email():
    data = request.get_json()
    response = supabase.table("user").select("*").eq("email", data["email"]).execute()
    return jsonify(response.data)
    
@app.route("/user/login", methods=["POST"])
def login():
    data = request.get_json()
    response = supabase.table("user").select("*").eq("username", data["username"]).eq("password", data["password"]).execute()
    return jsonify(response.data)

@app.route("/message", methods=["GET"])
def get_messages():
    response = supabase.table("message").select("*").execute()
    return jsonify(response.data)

@app.route("/message", methods=["POST"])
def add_message():
    data = request.get_json()
    answer = ""
    if "chat_id" in data:
        answer = conversation.run(data["prompt"])
        response = supabase.table("message").insert({"chat_id": data["chat_id"], "question": data["prompt"], "answer": answer}).execute()
    else:
        answer = conversation.run(data["prompt"])
    return jsonify(answer)

@app.route("/message", methods=["DELETE"])
def delete_message():
    data = request.get_json()
    response = supabase.table("message").delete().eq("id", data["id"]).execute()
    return jsonify(response.data)

@app.route("/message/getwithid", methods=["POST"])
def get_message_with_id():
    data = request.get_json()
    memory.clear()
    response = supabase.table("message").select("*").eq("chat_id", data["chat_id"]).execute()
    for message in response.data:
        memory.save_context({"input": message["question"]}, {"output": message["answer"]})
    return jsonify(response.data)

@app.route("/chat", methods=["GET"])
def get_chats():
    response = supabase.table("chat").select("*").execute()
  
    return jsonify(response.data)

@app.route("/chat/getwithid", methods=["POST"])
def get_chat_with_id():
    data = request.get_json()
    response = supabase.table("chat").select("*").eq("user_id", data["user_id"]).execute()
    return jsonify(response.data)

@app.route("/chat", methods=["POST"])
def add_chat():
    data = request.get_json()
    response = supabase.table("chat").insert(data).execute()
    return jsonify(response.data)

@app.route("/chat", methods=["DELETE"])
def delete_chat():
    data = request.get_json()
    response = supabase.table("chat").delete().eq("id", data["id"]).execute()
    return jsonify(response.data)

if __name__ == '__main__':
    app.run(debug=True)