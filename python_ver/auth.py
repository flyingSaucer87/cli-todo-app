import os, json
from datetime import datetime, timedelta
from argon2 import PasswordHasher


ph = PasswordHasher()

def load_json(key, filepath='auth.json'):
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        return {key: {}}
    try:
        with open(filepath, "r") as auth_f:
            return json.load(auth_f)
    except json.JSONDecodeError:
        # File exists but contains invalid JSON — reset it
        return {key: {}}
    
users = load_json('users')

def validate():
    last_login = load_json('last_login', 'last_login.json')
    print("============Validating...============\n")
    username = input("Enter username: ").strip()
    if username not in users["users"]:
        password = input("Enter a strong password: ")
        register(username, password)
        return [username, authenticate(username, password, last_login)]
    else:
        if username not in last_login["last_login"] or datetime.utcnow() - datetime.fromisoformat(last_login["last_login"][username]) > timedelta(hours=4):
            password = input("Enter your password: ")
            return [username, authenticate(username, password, last_login)]
        else:
            return [username, True]
        

def register(username, password):
    hash = ph.hash(password)

    users["users"][username] = hash

    with open('auth.json', "w") as auth_f:
        json.dump(users, auth_f, indent=2)

    print("registered successfully!")

def authenticate(username, password, last_login):
    try:
        ph.verify(users["users"][username], password)
        print("logged in successfully")

        last_login["last_login"][username] = datetime.utcnow().isoformat()
        with open('last_login.json', "w") as f:
            json.dump(last_login, f)
        print("\n========Validation Successful========\n")
        return True
    except:
        print("incorrect credentials...")
        return False