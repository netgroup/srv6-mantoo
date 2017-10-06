#!/bin/bash

#
# Copyright (C) 2017 Pier Luigi Ventre, Stefano Salsano - (CNIT and University of Rome "Tor Vergata")
#
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Script for configuration of the passwordless login.
#
# @author Pier Luigi Ventre <pier.luigi.ventre@uniroma2.it>
# @author Stefano Salsano <stefano.salsano@uniroma2.it>
#

# Check the existence of the configuration file
if [ ! -f nodes.sh ];
  then
    # If cfg file is present in current folder, use it
    echo "---> File not found, exit..."
    exit -1
fi

# Read configuration file
source nodes.sh

# Init steps
MININET_USER="root"
GENERATED=0

# Debug print
echo -e "Configuring ssh for the following nodes:"
echo -e "${NODES[@]}\n"

# Generate ssh key
while true; do
    read -p "Generate ssh key (y/n)?" yn
    case $yn in
        [Yy]* ) ssh-keygen;  GENERATED=1; break;;
        [Nn]* ) break;;
        * ) echo "(y/n)";;
    esac
done

# Specify RSA path for the key and update properly
echo "Please specifiy RSA path (empty for /home/$USER/.ssh/id_rsa): "
TEMP=/home/$USER/.ssh/id_rsa
read RSA_PATH
# User does not provide a path
if [ "$RSA_PATH" = "" ]; then
  # We use the default one
  RSA_PATH=$TEMP
fi
# Let's add the key to the ssh-agent
if [ "$GENERATED" -eq 1 ]; then
  echo -e "adding the key to the ssh-agent"
  eval $(ssh-agent)
  ssh-add -D
  ssh-add "$RSA_PATH"
fi

# Enable login without password using ssh-copy-id
for i in ${NODES[@]}; do
  echo "Enabling ssh access without password for: $i"
  # Provide ssh key through sshpass
  sshpass -p root ssh-copy-id -i "$RSA_PATH.pub" $MININET_USER@$i
done
echo -e "\n"
