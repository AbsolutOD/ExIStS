# ExIStS == Ec2 IAM SSH User Sync

The goal of ExIStS is to help manage OS level users by harnessing IAM users and their SSHKeys.

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
