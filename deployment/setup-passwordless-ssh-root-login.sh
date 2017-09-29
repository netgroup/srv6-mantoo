#!/bin/bash

ssh-keygen
echo $'\nhost *\n   StrictHostKeyChecking no' >> /home/user/.ssh/config
sshpass -p root ssh-copy-id -i "/home/user/.ssh/id_rsa.pub" root@localhost
