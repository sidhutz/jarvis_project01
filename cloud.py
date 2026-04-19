import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

def save_chat(user, message, response):
    db.collection("chats").add({
        "user": user,
        "message": message,
        "response": response
    })

def get_history():
    chats = db.collection("chats").stream()
    data = []

    for chat in chats:
        data.append(chat.to_dict())

    print("FIREBASE DATA:", data) 

    return data