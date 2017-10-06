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

the password for user is 1234

the password for root is root

### Configure the VM ###

This will be used to login as root in all mininet VMs without password:

    > cd /home/user/workspace/srv6-mantoo
    > cd deployment
    > ./setup-passwordless-ssh-root-login.sh

### Run an example experiment ###

    > cd /home/user/workspace/srv6-mantoo
    > git pull
    > cd mininet
    > ./start.sh

now you have started the topology defined in the file abilene.py (11 routers and 11 servers):

    # Define the switches representing the cities
    routers = ['nyc', 'chi', 'wdc', 'sea', 'sun', 'lan', 'den', 'kan', 'hou', 'atl', 'ind']

    # Define the hosts representing the cities
    hosts = ['hnyc', 'hchi', 'hwdc', 'hsea', 'hsun', 'hlan', 'hden', 'hkan', 'hhou', 'hatl', 'hind']

The file topology.json in the deployment folder provides the topology with IPv6 addresses: 

    > cat /home/user/workspace/srv6-mantoo/deployment/topology.json

for example:

    "id": "chi", "mgmtip": "2000::2/64"
    "id": "den", "mgmtip": "2000::7/64"
    "id": "hden", "mgmtip": "2000::12/64", 

    "chi-eth1" : "2001:0000:0000:0012:0000:0000:0000:0002/64"
    "den-eth0" : "2001:0000:0000:000d:0000:0000:0000:0001/64"
    "hden-eth0" : "2001:0000:0000:000d:0000:0000:0000:0002/64"

You can login on any router or host using their management IP, for example login in the chi router and ping/traceroute the den router or the den host :

    > ssh root@2000::2
    # ping -6 2001:0000:0000:000d:0000:0000:0000:0001
    # traceroute -6 2001:0000:0000:000d:0000:0000:0000:0001

    # ping -6 2001:0000:0000:000d:0000:0000:0000:0002
    # traceroute -6 2001:0000:0000:000d:0000:0000:0000:0002
    
Now you can add SRv6 policies :

    # documentation in progres... please wait :-)
    
    

    

    
