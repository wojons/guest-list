# guest-list

## About
Have you always been trying to find the best way to provide and manage SSH keys for  cluster of servers but hate the idea of a jump box. Have you thought about the crazy enterprise setups that will drive you crazy. Well hopefully thise can solve all your problems. guest-list is a program to help you have a list of guest that are able to sign up on your servers

## Features
* Auto pulls users public ssh keys
* Creates user accounts automatically
* Assigns Permissions for each user with linux groups
* Give users access based on hostname pattern mattching (no need to give everyone root)

## Install
Now add the following to your /etc/sshd/sshd_config file:

AuthorizedKeysCommand      /usr/local/bin/userkeys.sh
AuthorizedKeysCommandUser  nobody
