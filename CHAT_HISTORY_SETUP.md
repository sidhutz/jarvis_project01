# Cloud Chat History Setup

Jarvis saves AI chat replies in `jarvis.db` and syncs them to Firebase Firestore when Firebase credentials are available.

1. Create a Firebase project and enable Firestore.
2. In Firebase Console, open Project settings > Service accounts.
3. Generate a new private key and save it as `firebase_key.json` in this project folder.
4. Install Firebase support in your Python environment:

```bash
pip install firebase-admin
```

If `firebase_key.json` is missing or Firebase is offline, Jarvis still saves chats locally. When Firebase becomes available again, unsynced local chats are uploaded automatically the next time history loads.
