from flask import Flask, request, jsonify
import os
from supabase import create_client, Client

supabase: Client = create_client("https://rikddbisemwuyaiqmyxl.supabase.co", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJpa2RkYmlzZW13dXlhaXFteXhsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDA2NjIyMDcsImV4cCI6MjAxNjIzODIwN30.9sYM9WMFbNJTWOhe_PBo3hO2vgBTaXrEFzGOC0z32wc")

app = Flask(__name__)

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
    response = supabase.table("user").insert(data).execute()
    return jsonify(data)

@app.route("/user/getwithemail", methods=["POST"])
def get_user_with_email():
    data = request.get_json()
    response = supabase.table("user").select("*").eq("email", data["email"]).execute()
    return jsonify(response.data)
    
@app.route("/user/login", methods=["POST"])
def login():
    data = request.get_json()
    response = supabase.table("user").select("*").eq("email", data["email"]).eq("password", data["password"]).execute()
    return jsonify(response.data)

if __name__ == '__main__':
    app.run(debug=True)