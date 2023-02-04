# ansible-role-create-users

[![Build Status](https://travis-ci.org/ryandaniels/ansible-role-create-users.svg?branch=master)](https://travis-ci.org/ryandaniels/ansible-role-create-users)

Role to manage users on linux.  
Manage users in the user list config file (list is in the file vars/secret).  
Add users (with specific uid), change passwords, lock/unlock user accounts, manage sudo access (per user), add ssh key(s) for sshkey based authentication, set user's primary group and gid, add user (append) to group(s) and group will be created if doesn't exist.  
This is done on a per "group" basis (Ansible group variables), as set in the config file. The group comes from the Ansible group as set for a server in the inventory file. `all` is also supported to apply to every host in an inventory file.  

More detailed example can be found in the blog post: [User Management with Ansible](https://ryandaniels.ca/blog/ansible-user-management/)  

Note: Deleting users is not done on purpose.  

## Distros tested

* Ubuntu 22.04, 20.04, 18.04, 16.04
* CentOS / RHEL: 9.1, 8.x, 7.x, 6.5, 5.9

## Dependencies

Requires Ansible 2.6 (due to previous [bug 20096](https://github.com/ansible/ansible/issues/20096) with un-expiring users)

## ansible-vault

Use ansible-vault to encrypt sensitive info from git.

```bash
cat vars/secret
#encrypt if cleartext (before git commit/push)
ansible-vault encrypt vars/secret

#Edit encrypted file:
ansible-vault edit vars/secret

vi .vaultpass
-Enter the password for Ansible Vault from Password Safe
chmod 600 .vaultpass
vi ansible.cfg
#Insert the following lines
[defaults]
vault_password_file = ./.vaultpass
```

## .gitignore

```bash
vi .gitignore
#Insert the following lines
.vaultpass
.retry
secret
*.secret
```

## How to generate password

* on Ubuntu - Install "whois" package

```bash
mkpasswd --method=SHA-512
```

* on RedHat - Use Python

```bash
python -c 'import crypt,getpass; print(crypt.crypt(getpass.getpass(), crypt.mksalt(crypt.METHOD_SHA512)))'
```

## Default Settings

```yaml
---
# Note: 'debug_enabled_default: true' will put hashed passwords in the output.
debug_enabled_default: false
default_update_password: on_create
default_shell: /bin/bash
default_generate_ssh_key_comment: "{{ item.username }}@{{ ansible_hostname }}"
```

## User Settings

File Location: vars/secret

* **username**: username - no spaces **(required)**
* **uid**: The numerical value of the user's ID (optional)
* **user_state**: present|lock **(required)**
* **password**: sha512 encrypted password (optional). If not set, password is set to "!"
* **update_password**: always|on_create (optional, default is on_create to be safe).  
  **WARNING**: when 'always', password will be change to password value.  
  If you are using 'always' on an **existing** users, **make sure to have the password set**.
* **comment**: Full name and Department or description of application (optional) (But you should set this!)
* **primarygroup**: Primary group name (optional).
* **primarygid**: Primary group ID (optional). If same gid is reused on server the playbook will fail. If same duplicate group is specified with different gid, last configured will be used.
  **WARNING**: changing the primarygroup and/or primarygid of **existing** users will not change permissions of existing files belonging to that user. Also old entries will remain in /etc/group. Use with caution.
* **groups**: Comma separated list of groups the user will be added to (appended). If group doesn't exist it will be created on the specific server. This is not the primary group (primary group is not modified)
* **shell**: path to shell (optional, default is /bin/bash)
* **ssh_key**: Add authorized ssh key for ssh key based authentication (optional)  
  NOTE: 1 key can go on single line, but if multiple keys, use formatting below from first example.
* **exclusive_ssh_key**: yes|no (optional, default: no)  
  **WARNING**: exclusive_ssh_key: yes - will remove any ssh keys not defined here! no - will add any key specified.
* **generate_ssh_key**: Whether to generate a SSH key for the user in question. (optional, default is 'no')  
  NOTE: This will not overwrite an existing SSH key
* **ssh_key_bits**: Optionally specify number of bits in SSH key to create. (optional, default set by ssh-keygen)
* **ssh_key_passphrase**: Set a passphrase for the SSH key. If no passphrase is provided, the SSH key will default to having no passphrase.
* **generate_ssh_key_comment**: Specify the comment for the generated SSH key (optional). If not specified, will use default_generate_ssh_key_comment from defaults yaml.
* **use_sudo**: yes|no (optional, default no)
* **use_sudo_nopass**: yes|no (optional, default no). yes = passwordless sudo.
* **system**: yes|no (optional, default no). yes = create system account (uid < 1000). Does not work on existing users.
* **servers**: sub-element list of servers where changes are made. **(required)**  
  These are the Ansible groups from your Ansible inventory file. In below examples, `webserver` would be the 3 servers in the `webserver` Ansible inventory `webserver1`, `webserver2`, and `webserver3`.  

Note:
  You can have duplicate usernames on different servers, if you want to have different settings. See below example of testuser102 has sudo on servers defined as the `webserver` group in the inventory, but no sudo on the `database` group.

## Example Ansible Inventory file

```yaml
[webserver]
webserver1
webserver2
webserver3

[database]
db1
db2
db3

[monitoring]
monitor1
```

## Example config file (vars/secret)

```yaml
---
users:
  - username: testuser101
    password: $6$/y5RGZnFaD3f$96xVdOAnldEtSxivDY02h.DwPTrJgGQl8/MTRRrFAwKTYbFymeKH/1Rxd3k.RQfpgebM6amLK3xAaycybdc.60
    update_password: on_create
    comment: Test User 100
    shell: /bin/bash
    ssh_key: |
      ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx8crAHG/a9QBD4zO0ZHIjdRXy+ySKviXVCMIJ3/NMIAAzDyIsPKToUJmIApHHHF1/hBllqzBSkPEMwgFbXjyqTeVPHF8V0iq41n0kgbulJG testuser101@server1
      ssh-rsa AAAA.... testuser101@server2
    exclusive_ssh_key: yes
    use_sudo: no
    use_sudo_nopass: no
    user_state: present
    servers:
      - webserver
      - database
      - monitoring

  - username: testuser102
    password: $6$F/KXFzMa$ZIDqtYtM6sOC3UmRntVsTcy1rnsvw.6tBquOhX7Sb26jxskXpve8l6DYsQyI1FT8N5I5cL0YkzW7bLbSCMtUw1
    update_password: always
    comment: Test User 101
    groups: testcommon, testgroup102web
    shell: /bin/sh
    use_sudo: yes
    user_state: present
    servers:
      - webserver
      - all

  - username: testuser102
    password: $6$F/KXFzMa$ZIDqtYtM6sOC3UmRntVsTcy1rnsvw.6tBquOhX7Sb26jxskXpve8l6DYsQyI1FT8N5I5cL0YkzW7bLbSCMtUw1
    update_password: always
    comment: Test User 101
    groups: testcommon, testgroup102db
    shell: /bin/sh
    user_state: present
    servers:
      - database

  - username: testuser103
    password: $6$wBxBAqRmG6O$gPbg9hYShkuIe3YKMFujwiKsPKZHNFwoK4yCyTOlploljz53YSoPdCn9P5k8Qm0z062Q.8hvJ6DnnQQjwtrnS0
    user_state: present
    servers:
      - webserver

  - username: testuser104
    primarygroup: testgroup104primary
    ssh_key: ssh-rsa AAAB.... test103@server
    exclusive_ssh_key: no
    generate_ssh_key: yes
    generate_ssh_key_comment: custom comment for generated ssh key
    use_sudo: no
    user_state: present
    servers:
      - webserver
      - monitoring

  - username: testuser105
    uid: 1099
    password: $6$XEnyI5UYSw$Rlc6tXtECtqdJ3uFitrbBlec1/8Fx2obfgFST419ntJqaX8sfPQ9xR7vj7dGhQsfX8zcSX3tumzR7/vwlIH6p/
    primarygroup: testgroup105primary
    primarygid: 2222
    ssh_key: ssh-rsa AAAB.... test107@server
    generate_ssh_key: yes
    ssh_key_bits: 4096
    use_sudo: no
    user_state: lock
    servers:
      - webserver
      - database
```

## Example Playbook create-users.yml

```bash
---
- hosts: '{{inventory}}'
  vars_files:
    - vars/secret
  become: yes
  roles:
  - create-users
```

## Prep

* install ansible
* create keys
* ssh to client to add entry to known_hosts file
* configure client server authorized_keys
* run ansible commands

## Usage

Create all users

```bash
ansible-playbook create-users.yml --ask-vault-pass --extra-vars "inventory=all-dev" -i hosts
```
