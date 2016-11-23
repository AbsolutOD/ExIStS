# ExIStS == Ec2 IAM SSH User Sync

The goal of ExIStS is to help manage OS level users by harnessing IAM users and their SSHKeys.  I needed something fast, so I whipped this up.  I will evolve it over time to make it nicer/easier for people to use.

## Overview
ExIStS works by comparing users on an instance to the users in an `ec2-user` IAM group.  It will create users that are in the IAM group, but not on the instance.  It will also remove users that are one the instance, but aren't in the IAM group.

Users will be create and their keys will be downloaded from IAM and added to their .ssh/authorized_keys file.  All of the users sshkey's in IAM will get added to their authorized_keys file.  The file gets recreated each time ExIStS runs.  That way there aren't any old keys left on the instance.

When ExIStS removes a user, it just removes the ability of the user to login to the instance.  ExIStS doesn't remove their actual home directory.  There have been time where silly developers write needed applications or use their own crontab for production things.  This might be a config option later, but it is easy enough to remove home directories with remote execution tools like ansible and the like.

There are a few things you need to setup in order for the ExIStS to work.  You need to create a group that you can assign users that you want sync'ed to instances.  Will also a custom policy that you can attach to an instance role or any existing role you already have defined.

### IAM Setup
The script only syncs users from a specific group, so create a `ec2-user` group.  All users in this group will be sync to instances that have ExIStS installed.   The instances will need a policy that allows them to pull the ec2-user group, list the users, and pull their sshkeys from IAM.

First, let's create the `ec2-user` group.  You will assign users to this group to that you want sync'ed to the instances.

Now let's create a custom IAM policy to grant permission to get the users in a group and pull their sshkeys down.  Let's name the custom policy `iam-user-sshkey`.  You can cut and paste the below into the custom field.

```javascript
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Stmt1476999181000",
            "Effect": "Allow",
            "Action": [
                "iam:ListUsers",
                "iam:GetGroup"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Sid": "Stmt1476999233000",
            "Effect": "Allow",
            "Action": [
                "iam:GetSSHPublicKey",
                "iam:ListSSHPublicKeys"
            ],
            "Resource": [
                "arn:aws:iam::<ACCOUNT ID>:user/*"
            ]
        }
    ]
}
```

The instances needs a role to use the above policy.  Create an instance role and let's name it `iam-ec2-user`.  Make sure to attach `iam-user-sshkey` we just created.

If you have other instance roles defined, then you will need to add the `iam-user-sshkey` policy to that role in order for ExIStS to work.

### Boot/Cron
You just need to clone this repo into a user's home directory with sudo permissions.  Then call iam-user-sync.py from rc.local and setup a cron job.

Yeah, I know this is an extremely manual setup, but I needed a solution fast.  If you would like to help feel free to submit a PR.

# TODO
* install script
* ability to configure it
* general logging mechanism for auditing
