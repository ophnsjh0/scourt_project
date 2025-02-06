from cryptography.fernet import Fernet


def load_key():
    return open("secret.key", "rb").read()


def load_and_decrypt_data(filename):
    key = load_key()
    fernet = Fernet(key)

    with open(filename, "rb") as file:
        encrypted_data = file.read()

    decrypted_data = fernet.decrypt(encrypted_data).decode()

    data_list = json.loads(decrypted_data)

    return data_list

decrypted_info = load_and_decrypt_data("encrypted_list.bin")
print(f"Decrypted Info: {decrypted_info}")
