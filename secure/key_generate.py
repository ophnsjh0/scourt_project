from cryptography.fernet import Fernet

def generate_and_save_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)
        
generate_and_save_key()