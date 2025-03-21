# encrypted
$ ansible-vault encrypt credential.txt

# view encrypted context
$ ansible-vault view credential.txt

# edit encrypted context
$ ansible-vault edit credential.txt

# create encrypted context
$ ansible-vault create credential.txt

# change password
$ ansible-vault rekey credential.txt

# decrypt password
$ ansible-vault decrypt credential.txt



실행 
(python 활용)
$ ansible-playbook test-vault.yml --vault-password-file vault_password.py

(textfile 활용)
$ ansible-playbook test-vault.yml --vault-password-file vault_passwd.txt

(직접입력)
$ ansible-playbook test-vault.yml --ask-vault-pass