from cryptography.fernet import Fernet
import json


def load_key():
    return open("secret.key", "rb").read()


def encrypt_and_save_data(data_list, filename):
    key = load_key()
    fernet = Fernet(key)
    data_json = json.dumps(data_list)
    encrypted_data = fernet.encrypt(data_json.encode())

    with open(filename, "wb") as file:
        file.write(encrypted_data)


account_info = [
    {"name": "BD-APIC", "ip": "10.10.10.10", "id": "admin", "password": "password"},
    {"name": "SJ-APIC", "ip": "20.20.20.20", "id": "admin", "password": "password"},
]
encrypt_and_save_data(account_info, "encrypted_list.bin")

# bdl2 form
# account_info = [
#     {
#         "center": "BD-MGMT",
#         "network": "OOB_MGMT",
#         "name": "Switch1",
#         "ip": "10.10.10.10",
#         "id": "admin",
#         "password": "password",
#     },
#     {
#         "center": "BD-MGMT",
#         "network": "DEV/VER_MGMT",
#         "name": "Switch2",
#         "ip": "20.20.20.20",
#         "id": "admin",
#         "password": "password",
#     },
# ]

# sjl2 form
# account_info = [
#     {
#         "center": "SJ-MGMT",
#         "network": "OOB_MGMT",
#         "name": "Switch1",
#         "ip": "10.10.10.10",
#         "id": "admin",
#         "password": "password",
#     },
#     {
#         "center": "SJ-MGMT",
#         "network": "DEV/VER_MGMT",
#         "name": "Switch2",
#         "ip": "20.20.20.20",
#         "id": "admin",
#         "password": "password",
#     },
# ]
