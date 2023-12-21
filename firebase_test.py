import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use a service account
cred = credentials.Certificate('dokosen-firebase-adminsdk.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

def fetchData():
    docs = db.collection('teachers').get()
    for doc in docs:
        print(doc.to_dict())

def updateData():
    doc_ref = db.collection('teachers').document("0")
    doc_ref.update({
        "status": "kougi",
    })

    fetchData()

#fetchData()
updateData()
