# guest-list

## About
Have you always been trying to find the best way to provide and manage SSH keys for  cluster of servers but hate the idea of a jump box. Have you thought about the crazy enterprise setups that will drive you crazy. Well hopefully thise can solve all your problems. guest-list is a program to help you have a list of guest that are able to sign up on your servers

## Features
* Auto pulls users public ssh keys
* Creates user accounts automatically
* Assigns Permissions for each user with linux groups
* Give users access based on hostname pattern mattching (no need to give everyone root)

## Install

### 1. Clone Repo

```git clone https://github.com/wojons/guest-list /opt/guest-list```

### 2. Install Dependancies
``` pip install -r install.```

### 3. Configure guest-list.ini (you can move it to /etc/guest-list.ini


### 4. Upload your manifest files to sources you setup


### 5. Now add the following to your /etc/sshd/sshd_config file:

```
AuthorizedKeysCommand      /opt/guest-list.sh
AuthorizedKeysCommandUser  root
```

### 6. Restart ssh server

``` service sshd restart```

### 7. Test and have fun
