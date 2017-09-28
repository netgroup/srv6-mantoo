#!/bin/bash

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
