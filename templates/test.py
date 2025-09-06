import pyrebase

Config = {
  "apiKey": "AIzaSyAThQZu7ID2hpU7kJbItpFl0cDLTuxafHQ",
  "authDomain": "dealmaker-ea2ba.firebaseapp.com",
  "projectId": "dealmaker-ea2ba",
  "storageBucket": "dealmaker-ea2ba.appspot.com",  # 👈 fix: should be appspot.com not .app
  "messagingSenderId": "123350622771",
  "appId": "1:123350622771:web:b6fbefd5379a108a913946",
  "measurementId": "G-G9P3QGP2SW",
  "databaseURL": "https://dealmaker-ea2ba-default-rtdb.asia-southeast1.firebasedatabase.app/"
}

firebase = pyrebase.initialize_app(Config)

# Example usage
auth = firebase.auth()
db = firebase.database()
storage = firebase.storage()

db= firebase.database()
data = {
    'name':'sai',
    'age':20,
    'phone':7515616
}
db.push(data)