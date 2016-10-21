#!/usr/bin/env python

import os
import json

import boto3

IGNORE_USERS = ["ec2-user"]



def create_ssh_dir(username):
    if not os.path.isdir(ssh_dir_path(username)):
        cmd = "mkdir {}".format(ssh_dir_path(username))
        #os.system(cmd)
        print cmd
    return ssh_dir_path(username)

    return
## The existance of an authorized_keys file means they are active
def has_key_file(username):
    return os.path.isfile(key_file_path(username))


def ssh_dir_path(username):
    return "/home/{}/.ssh".format(username)


def key_file_path(username):
    return "/home/{}/.ssh/authorized_keys".format(username)


def has_home_dir(username):
    return os.path.isdir("/home/{}".format(username))

## just to remove the loop out of the add_user func
def add_users(iam_users):
    for u in iam_users.keys():
        add_user(u, iam_users[u]['sshkeys'])

## adds the user if their homedir doesn't exist
#  Will always overwrite the SSHKeys for the usersq
def add_user(username, sshkeys):
    if not has_home_dir(username):
        cmd = "useradd -s /bin/bash -d /home/{0} -m {0}".format(username)
        print cmd
        #os.system(cmd)

    add_sshkeys(username, sshkeys)
    return True


def add_sshkeys(username, sshkeys):
    create_ssh_dir(username)
    
    if has_key_file(username):
        cmd = "rm {}".format(key_file_path(username))
        #os.system(cmd)
        print cmd

    #with open(key_file_path(username), 'w') as f:
    for k in sshkeys:
        #f.write(k)
        print "    * {}".format(k)
    return True


## We don't remove the user, just the authorized_keys file.
#  By removing the authorized_keys file they won't be able to login,
#  since we don't allow password logins.
#  We want to keep the home dir just incase that have something in there.
def remove_users(remove_users):
    for username in remove_users:
        if username in IGNORE_USERS: continue
        if has_key_file(username):
            cmd = "rm {}".format(key_file_path(username))
            #os.system(cmd)
            print cmd
            os.system("userdel {}".format(username))


## We don't use password auth, so we just get the list of homedirs.
#  An deactivated user is missing their authorized_keys file.
def get_system_usernames():
    sys_users = []
    for homedir in os.listdir("/home/"):
        if has_key_file(homedir):
            sys_users.append(homedir)
    return sys_users


def get_groups(user):
    groups = []
    for group in user.groups.all():
        print "     * {}".format(group.name)
        groups.append(group.name)
    return groups


def get_sshkeys(user):
    client = boto3.client('iam')

    sshkeys = []
    keys = client.list_ssh_public_keys(UserName=user.name)
    for key in keys['SSHPublicKeys']:
        key_id = key
        pub_key = client.get_ssh_public_key(
                        UserName=user.name,
                        SSHPublicKeyId=key['SSHPublicKeyId'],
                        Encoding='SSH'
                    )
        sshkeys.append(pub_key['SSHPublicKey']['SSHPublicKeyBody'])
        print "     * {}".format(pub_key['SSHPublicKey']['SSHPublicKeyBody'])
    return sshkeys


def get_iam_users():
    iam = boto3.resource('iam')

    iam_users = {}
    for user in iam.users.all():
        print "Name: {}".format(user.name)
        print "  -> Groups"

        groups = get_groups(user)
        sshkeys = get_sshkeys(user)

        iam_users[user.name] = {
            "groups" : groups,
            "sshkeys" : sshkeys
        }

    return iam_users


if __name__ == "__main__":
    sys_usernames = get_system_usernames()
    iam_users = get_iam_users()

    # list of users to remove
    users_to_remove = set(sys_usernames) - set(iam_users.keys())

    add_users(iam_users)
    remove_users(users_to_remove)
