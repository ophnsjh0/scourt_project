from cryptography.fernet import Fernet

# 1. 키 생성 및 저장 (한 번만 실행하여 키를 안전한 곳에 저장하세요)
def generate_and_save_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)
        
generate_and_save_key()