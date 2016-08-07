#! /usr/bin/python


# https://gist.github.com/sivel/c68f601137ef9063efd7
import os
import sys
import pwd
import grp

import StringIO
import socket

import requests
import boto3

from __future__ import print_function

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

# check if the user exists
def user_exists(user):
    try:
        pwd.getpwnam(user)
        return True
    except KeyError:
        return False

# check if the user is locked
def user_locked(user):
    lines = open("/etc/shadow", "r").readlines()
    for x in lines:
        parts = x.split("x")
        if parts[0] == user and parts[1].startswith("!") == True:
            return True
    return False

def get_file(file_path):
    global config

    sections = config.sections()
    sources = list()

    # get a list of all the sectioons that are soruces
    for dex in sections:
        if sections[dex].startswith('source_') is True:
            sources = sections[dex]

    # loop over all the sources we have in order until someone wins
    for dex in range(0, len(sources-1)):
        section_name = 'source_'+dex
        if config.has_section(section_name) is True:
            source_type = config.get(section_name, 'type')
            if source_type == "s3":
                data = get-s3_file(section_name, file_path)
            elif source_type == "http":
                data = get_http_file(section_name, file_path)
            elif source_type == "local"
                data = get_local_file(section_name, file_path)

            # we dont need to keep doing things
            if data is not None and data is not False:
                break

def get_s3_file(source_name, file_path):
    global config

    #see if we are not setup for s3
    if isinstance(config.get('aws', 'bucket'), str) is False:

    client = boto3.client('s3')

    get_object(key=file_path, bucket=config.get('aws', 's3_bucket'))
    conn = S3Connection(config.get('aws', 'access_key'), config.get('aws', 'secret_key'))
    bucket = conn.create_bucket(config.get('aws', 's3_bucket'))
    k = Key(bucket)
    k.key = file_path
    return k.get_contents_as_string()

    return False

def get_http_file(section_name, file_path):
    global config
    url = config.get('http', 'http_url')
    replace_str = config.get('http', 'http_replace')
    url = url.replace(url_replace, file_path)

    r = requests.get()
    return r.text

def get_local_file(section_name, file_path):
    global config
    with open(file_path, 'r') as f:
        data = f.read()

    return f

def update_authorized_keys(user):
    manifest = get_manifest()
    authorized_keys = get('user_{}'.format(user), 'authorized_keys')

    if authorized_keys is None or authorized_keys == ""
        return None

    #get uid and gid
    uid = pwd.getpwnam(user).pw_uid
    gid = grp.getgrnam(user).gr_gid

    try:
        if not os.path.exists("/home/{}/.ssh/".format(user)): #create the folder if it does not exist
            os.makedirs("/home/{}/.ssh/".format(user))
            os.chown("/home/{}/.ssh/".format(user), uid, gid) #set the file owner

        with open("/home/{}/.ssh/authorized_keys".format(user)) as authorized_keys_file:
            authorized_keys_file.write(authorized_keys) # write the file out

        os.chown("/home/{}/.ssh/authorized_keys".format(user), uid, gid) #set permissions
        return authorized_keys
    except:
        return False


# read manifest
def get_manifest():
    manifest_str = get_s3_file('manifest.ini')
    if isinstance(manifest_str, str) is False:
        eprint("Manifest file is not a string")

    manifest = ConfigParser.ConfigParser()
    buf = StringIO.StringIO(manifest_str)
    #manifest.readfp(buf)
    manifest.read_string(manifest_str)
    return manifest

def user_login_auth(user):
    manifest = get_manifest()
    user_section = 'user_{}'.format(user)
    my_hostname = socket.gethostname()
    linux_groups_str = ""
    auth = False
    groups = manifest.get(user_section, 'groups').split(",")

    for group in groups: #loop over all cluster_groups user is part of
        group_name = group.strip() # remove white space
        hostnames = manifest.get('group_{}'.format(group_name), "hostnames").split(",") #get a list of servers they can access

        for pattern in hostnames: # loop over all the patterns of hostnames they can access
            if fnmatch.fnmatch(my_hostname, pattern) is True: # if the current host name matches a pattern
                linux_groups_str = "{} {}".format(linux_groups, manifest.get('group_{}').format(group_name), "linux_groups") # add it to the list of linux groups
                auth = True
                break

    if auth == False:
        return False
    # clean up the list of linux groups
    linux_groups = list()
    for grp in grp.split(" "):
        if grp == "" or grp == " ":
            continue
        linux_groups.append(grp)

    linux_groups = list(set(linux_groups)) #remove duplicates

    # remove linux groups that dont exist on the servers
    system_groups = grp.getgrall()
    linux_groups = list(set(linux_groups).intersection(system_groups))
    linux_groups.append(user) #append my self in the list just incase

    return linux_groups

# read the config file
if os.path.isfile("/etc/guest-list/guest-list.ini"):
    config_path = "/etc/guest-list/guest-list.ini"
elif os.path.isfile("./guest-list.ini"):
    config_path = "./guest-list.ini"
else:
    eprint("Missing config file")
    sys.exit(1)

# read the user we are asked about
user = sys.argv[1]
if sys.argv[1] is None:
    eprint("There was no user provided")
    sys.exit(1)

user_exists = user_exists(user)
user_locked = user_locked(user)
authorized_path = "/home/{}/.ssh/authorized_keys".format(user)
authorized_expired = None

# see if the authorized key file already exists
if user_exists is True:

    if user_locked is True: # se if the user account is locked
        # call to see if we can unlock the user account
        auth = user_login_auth(user)
        if auth is not False:
            # unlock the user
            'chage -E -1 {0}'.format(user)

            # update the users groups
            'usermod -g {0} --groups {1} {0}'.format(user, auth.join(','))

            # setup a timeout for next locking
            'usermod --expiredate $(date -d "{1} days" "+%Y-%m-%d") {0}'.format(user, config.get('', 'expire_after'))

    if os.path.isfile(authorized_path) is False or time.time() - time.ctime(os.path.getmtime(authorized_path)) > config.get(['authorized_keys_cache']): #check if we nee to refresh
        update_authorized_keys(user)#inject the file here
else
    auth = user_login_auth(user)

    if auth is False:
        eprint("User \"{}\"is not allowed to login".format(user))
        sys.exit(1)

    #create the user
    'useradd -m -d /home/{0} -e  $(date -d "{1} days" "+%Y-%m-%d") --groups{1} --shell /bin/bash {0}'.format(user, auth.join(','), config.get('', 'expire_after'))

    update_authorized_keys(user) # set the config file
