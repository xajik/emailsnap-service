# SSH

## Setup 

Create [email_snap](email_snap) ssh key before you deploy AWS infrastrcutre. 

`ssh-keygen -t rsa -b 4096 -C "your_email@example.com"`

### Connect

Copy key to `~/.ssh/` folder. 

Connect with your EC2 with private key:

```
Host emailsnap
  HostName <EC2_PUBLIC_IP>
  User ec2-user
  IdentityFile ~/.ssh/email_snap
```

Then `ssh emailsnap`

### Copy

Copy `.env` to the EC2:

```
scp -i ~/.ssh/email_snap .env ec2-user@<ID-ADDRESS>:/home/ec2-user/emailsnap-service/.env 
```

## EC2 SSH 

SSH Key on the EC2 machine will be created automatically:

* `cat ./.ssh/id_rsa.pub`
* where `pwd` is `/home/ec2-user/.ssh`