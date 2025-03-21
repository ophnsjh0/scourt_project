(library 위치 지정)
export ANSIBLE_LIBRARY=/home/ophnsjh0/code/scourt_project/ansible/study/custom_module/library

(custom_module Test)
ansible -m custom_debug -a 'msg=hello log_path=/home/ophnsjh0/code/scourt_project/ansible/study/custom_module/tmp/debugging.log' localhost

(실행)
ansible-playbook custom-custom_debug.yml