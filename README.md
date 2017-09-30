# SRv6 Management Tools #

Tools to setup an emulated SRv6 capapable IPv6 networks (based on mininet)

### Download the VM ###

A Xubuntu 17.04 virtualbox VM can be downloaded using Vagrant. First, you have to install vagrant from https://www.vagrantup.com/ 
then you can get your ready-to-go VM as follows: 

- create a new folder, for example call it srv6
- enter in the new folder and copy the [Vagrantfile](https://github.com/netgroup/srv6-mantoo/blob/master/vagrant/Vagrantfile) (available in the vagrant folder) 
- then you can run
> vagrant up

(the VM will be downloaded from https://app.vagrantup.com/salsano/boxes/test)

### Configure the VM ###

the password for user is 1234
the password for root is root

    > cd /home/user/workspace/srv6-mantoo
    > cd deployment
    > ./setup-passwordless-ssh-root-login.sh

(this will be used to login as root in all mininet VMs without password)

### Run an example experiment ###

    > cd /home/user/workspace/srv6-mantoo
    > git pull
    > cd mininet
    > ./start.sh

now you have started the topology defined in the file abilene.py, open another terminal and execute
    > cat /home/user/workspace/srv6-mantoo/deployment/nodes.sh
it will show a list of mininet VMs on which you can login, for example
    > ssh root@2000::d

    

    
