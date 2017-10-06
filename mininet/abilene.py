#!/usr/bin/python

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
# Deployment script for Mininet.
#
# @author Pier Luigi Ventre <pier.luigi.ventre@uniroma2.it>
# @author Stefano Salsano <stefano.salsano@uniroma2.it>
#

from optparse import OptionParser
from collections import defaultdict

# IPaddress dependency
from ipaddress import IPv6Network

# Mininet
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import RemoteController, OVSBridge, Node
from mininet.link import TCLink
from mininet.cli import CLI

# Utils
from utils import IPHost
# Routing
from routing import SPFRouting

import os
import json
import sys

import networkx as nx

from networkx.readwrite import json_graph

# Mapping host to vnfs
nodes_to_vnfs         = defaultdict(list)
# Mapping node to management address
node_to_mgmt          = {}
# Routes computed by the routing function
routes                = defaultdict(list)
# Subnets to via
subnets_to_via        = defaultdict(list)
# Network topology
topology              = nx.MultiDiGraph()
# Interface to IP map
interfaces_to_ip      = {}
# Default via
host_to_default_via   = {}
# Vnfs file
VNF_FILE              = "../deployment/vnfs.json"
# nodes.sh file for setup of the nodes
NODES_SH              = "../deployment/nodes.sh"
# Routing file
ROUTING_FILE          = "../deployment/routing.json"
# Topology file
TOPOLOGY_FILE         = "../deployment/topology.json"
# Management Mask
MGMT_MASK             = 64
# Data plane Mask
DP_MASK               = 64
# Data plane soace
DP_SPACE              = 56
# Vnf maks
VNF_MASK              = 128

# Create Abilene topology and a management network for the hosts.
class Abilene(Topo):
  # Init of the topology
  def __init__(self, bw=1, conf={}, **opts):
    # Init steps
    Topo.__init__(self, **opts)
    # Get VNFs mapping
    vnfs = conf['vnfs']

    # We are going to use bw constrained links
    linkopts          = dict( bw=bw )

    # Create subnetting objects for assigning data plane addresses
    dataPlaneSpace    = unicode('2001::0/%d' % DP_SPACE)
    dataPlaneNets     = list(IPv6Network(dataPlaneSpace).subnets(new_prefix=DP_MASK))

    # Create subnetting objects for assigning mgmt plane addresses
    mgmtPlaneSpace    = unicode('2000::0/%d' % MGMT_MASK)
    mgmtPlaneNet      = list(IPv6Network(mgmtPlaneSpace).subnets(new_prefix=MGMT_MASK))[0]
    mgmtPlaneHosts    = mgmtPlaneNet.hosts()

    # Define the switches representing the cities
    routers = ['nyc', 'chi', 'wdc', 'sea', 'sun', 'lan', 'den', 'kan', 'hou', 'atl', 'ind']

    # Define the hosts representing the cities
    hosts = ['hnyc', 'hchi', 'hwdc', 'hsea', 'hsun', 'hlan', 'hden', 'hkan', 'hhou', 'hatl', 'hind']

    # Define the edge links connecting hosts and switches
    edge_links = [('nyc', 'hnyc'), ('chi', 'hchi'), ('wdc', 'hwdc'), ('sea', 'hsea'), ('sun', 'hsun'), ('lan', 'hlan'),
    ('den', 'hden'), ('kan', 'hkan'), ('hou', 'hhou'), ('atl', 'hatl'), ('ind', 'hind')]

    # Define the core links connecting switches
    core_links = [('nyc', 'chi'), ('nyc', 'wdc'), ('chi', 'ind'), ('wdc', 'atl'), ('sea', 'sun'), ('sea', 'den'),
    ('sun', 'lan'), ('sun', 'den'), ('lan', 'hou'), ('den', 'kan'), ('kan', 'hou'), ('kan', 'ind'), ('hou', 'atl'),
    ('atl', 'ind')]

    # Iterate on the switches and generate them
    for router in routers:
      # Assign mgmt plane IP
      mgmtIP  = mgmtPlaneHosts.next()
      # Add the router to the topology
      self.addHost(
        name=router,
        cls=IPHost,
        sshd=True,
        mgmtip="%s/%s" %(mgmtIP, MGMT_MASK),
        vnfips=[]
        )
      # Save mapping node to mgmt
      node_to_mgmt[router] = str(mgmtIP)
      # Add node to the topology graph
      topology.add_node(router, mgmtip="%s/%s" %(mgmtIP, MGMT_MASK), type="router", group=200)

    # Create the mgmt switch
    br_mgmt = self.addSwitch('br-mgmt1', cls=OVSBridge)

    # Iterate on the switches and generate them
    for host in hosts:
      # Define host group
      group = 100
      # Get the assinged vnfs
      host_vnfs = vnfs[host]
      # Create an empty list
      vnfips  = []
      # If the host has assigned vnfs
      if host_vnfs > 0:
        # Update group
        group = host_vnfs
        # Assign a data-plane net to the host
        net     = dataPlaneNets.pop(0)
        # Get hosts iterator
        host_ips   = net.hosts()
        # Iterate over the number of vnfs
        for index in range(host_vnfs):
          # Add the ip to the set
          vnfips.append("%s/%d" %(host_ips.next().exploded, VNF_MASK))
        # Save the destination
        subnets_to_via[str(net.exploded)].append(host)
        # Save the mapping nodes to vnfs
        nodes_to_vnfs[host] = vnfips
      # Assign mgmt plane IP
      mgmtIP  = mgmtPlaneHosts.next()
      # Add the router to the topology
      self.addHost(
        name=host,
        cls=IPHost,
        sshd=True,
        mgmtip="%s/%s" %(mgmtIP, MGMT_MASK),
        vnfips=vnfips
        )
      # Save mapping node to mgmt
      node_to_mgmt[host] = str(mgmtIP)
      # Add node to the topology graph
      topology.add_node(host, mgmtip="%s/%s" %(mgmtIP, MGMT_MASK), type="server", group=group)

    # Assign the mgmt ip to the mgmt station
    mgmtIP        = mgmtPlaneHosts.next()
    # Mgmt name
    mgmt          ='mgt'
    # Create the mgmt node in the root namespace
    self.addHost(
      name=mgmt,
      cls=IPHost,
      sshd=False,
      mgmtip="%s/%s" %(mgmtIP, MGMT_MASK),
      inNamespace=False
      )
     # Save mapping node to mgmt
    node_to_mgmt[mgmt] = str(mgmtIP)
    # Store mgmt in hosts
    hosts.append(mgmt)

    # Iterate over the edge links and generate them
    for edge_link in edge_links:
      # The router is the left hand side of the pair
      router  = edge_link[0]
      # The host is the right hand side of the pair
      host    = edge_link[1]
      # Create the edge link
      self.addLink(router, host, **linkopts)
      # Get Port number
      portNumber                  = self.port(router, host)
      # Create lhs_intf
      lhs_intf                    = "%s-eth%d" %(router, portNumber[0])
      # Create rhs_intf
      rhs_intf                    = "%s-eth%d" %(host, portNumber[1])
      # Assign a data-plane net to this link
      net                         = dataPlaneNets.pop(0)
      # Get hosts on this subnet
      host_ips                    = net.hosts()
      # Get the default via
      default_via                 = "%s/%d" %(host_ips.next().exploded, DP_MASK) 
      # Get the host ip
      host_ip                     = "%s/%d" %(host_ips.next().exploded, DP_MASK)
      # Map lhs_intf to ip
      interfaces_to_ip[lhs_intf]  = default_via
      # Map rhs_intf to ip
      interfaces_to_ip[rhs_intf]  = host_ip
      # Map host to default via
      host_to_default_via[host]   = default_via
      # Add edge to the topology
      topology.add_edge(router, host, lhs_intf=lhs_intf, rhs_intf=rhs_intf, lhs_ip=default_via, rhs_ip=host_ip)
      # Add reverse edge to the topology
      topology.add_edge(host, router, lhs_intf=rhs_intf, rhs_intf=lhs_intf, lhs_ip=host_ip, rhs_ip=default_via)
      # Map subnets to router
      subnets_to_via[str(net.exploded)].append(router)
      # Map subnets to router
      subnets_to_via[str(net.exploded)].append(host)

    # Iterate over the core links and generate them
    for core_link in core_links:
      # Get the left hand side of the pair
      lhs = core_link[0]
      # Get the right hand side of the pair
      rhs = core_link[1]
      # Create the core link
      self.addLink(lhs, rhs, **linkopts )
      # Get Port number
      portNumber                = self.port(lhs, rhs)
      # Create lhs_intf
      lhs_intf                  = "%s-eth%d" %(lhs, portNumber[0])
      # Create rhs_intf
      rhs_intf                  = "%s-eth%d" %(rhs, portNumber[1])
      # Assign a data-plane net to this link
      net                       = dataPlaneNets.pop(0)
      # Get hosts on this subnet
      host_ips                  = net.hosts()
      # Get lhs_ip
      lhs_ip                    = "%s/%d" %(host_ips.next().exploded, DP_MASK)
      # Get rhs_ip
      rhs_ip                    = "%s/%d" %(host_ips.next().exploded, DP_MASK) 
      # Map lhs_intf to ip
      interfaces_to_ip[lhs_intf] = lhs_ip
      # Map rhs_intf to ip
      interfaces_to_ip[rhs_intf] = rhs_ip
      # Add edge to the topology
      topology.add_edge(lhs, rhs, lhs_intf=lhs_intf, rhs_intf=rhs_intf, lhs_ip=lhs_ip, rhs_ip=rhs_ip)
      # Add the reverse edge to the topology
      topology.add_edge(rhs, lhs, lhs_intf=rhs_intf, rhs_intf=lhs_intf, lhs_ip=rhs_ip, rhs_ip=lhs_ip)
      # Map subnet to lhs
      subnets_to_via[str(net.exploded)].append(lhs)
      # Map subnet to rhs
      subnets_to_via[str(net.exploded)].append(rhs)

    # Connect all the routers to the management network
    for router in routers:
      # Create a link between mgmt switch and the router
      self.addLink(router, br_mgmt, **linkopts )

    # Connect all the hosts to the management network
    for host in hosts:
      # Create a link between mgmt switch and the host
      self.addLink(host, br_mgmt, **linkopts )

# Utility function to dump relevant information of the emulation
def dump():
  # Json dump of the topology
  with open(TOPOLOGY_FILE, 'w') as outfile:
    # Get json topology
    json_topology = json_graph.node_link_data(topology)
    # Convert links
    json_topology['links'] = [
        {
            'source': json_topology['nodes'][link['source']]['id'],
            'target': json_topology['nodes'][link['target']]['id'],
            'lhs_intf': link['lhs_intf'],
            'rhs_intf': link['rhs_intf'],
            'lhs_ip': link['lhs_ip'],
            'rhs_ip': link['rhs_ip']
        }
        for link in json_topology['links']]
    # Dump the topology
    json.dump(json_topology, outfile, sort_keys = True, indent = 2)
  # Json dump of the routing
  with open(ROUTING_FILE, 'w') as outfile:
    json.dump(routes, outfile, sort_keys = True, indent = 2)
  # Dump for nodes.sh
  with open(NODES_SH, 'w') as outfile:
    # Create header
    nodes = "declare -a NODES=("
    # Iterate over management ips
    for node, ip in node_to_mgmt.iteritems():
      # Add the nodes one by one
      nodes = nodes + "%s " % ip
    # Eliminate last character
    nodes = nodes[:-1] + ")\n"
    # Write on the file
    outfile.write(nodes)
  # Json dump of the vnfs
  with open(VNF_FILE, 'w') as outfile:
    json.dump(nodes_to_vnfs, outfile, sort_keys = True, indent = 2)

# Utility function to shutdown the emulation
def shutdown():
  # Clean Mininet emulation environment
  os.system( 'sudo mn -c' )
  # Clean Mininet emulation environment
  os.system( 'sudo killall sshd' )

# Utility function to deploy Mininet topology
def deploy(options):
  # Retrieves options
  bw          = options.bw
  controller  = options.controller
  conf        = options.conf
  # Create routing
  routing = SPFRouting()
  # Set Mininet log level to info
  setLogLevel( 'info' )
  # Check if the file exist
  if os.path.isfile(conf):
    # Load configuration file
    with open(conf) as json_file:
      # load as json map
      conf = json.load(json_file)
  # File does not exist
  else:
    # Empty map
    print "Please provide a valid configuration file"
    # Exit
    sys.exit(1)
  # Create Mininet topology
  topo = Abilene(
    bw=bw,
    conf=conf
    )
  # Create Mininet net
  net = Mininet(
    topo=topo,
    link=TCLink,
    build=False,
    controller=None,
    )
  # Add manually external controller
  net.addController("c0", controller=RemoteController, ip=controller)
  # Build topology
  net.build( )
  # Start topology
  net.start( )
  # Build routing
  routing.routing(routes, topology, subnets_to_via, interfaces_to_ip)
  # Iterate over the hosts
  for host in net.hosts:
    # Get the default via, if exists
    default_via = host_to_default_via.get(host.name, None)
    # Get the subnets, if exists
    subnets     = routes.get(host.name, [])
    # Configure v6 addresses
    host.configv6(interfaces_to_ip, default_via, subnets)
  # Dump relevant information
  dump()
  # Mininet CLI
  CLI(net)
  # Stop topology
  net.stop( )

# Parse command line options and dump results
def parseOptions( ):
  parser = OptionParser( )
  # Bandwidth for the links
  parser.add_option( '--bw', dest='bw', type='int', default=1,
                     help='bandwidth for the links, default 1 Mb/s' )
  # IP of RYU controller
  parser.add_option( '--controller', dest='controller', type='string', default="127.0.0.1",
                     help='IP address of the Controlle instance' )
  # Configuration file
  parser.add_option( '--conf', dest='conf', type='string', default="foo.json",
                     help='Configuration file containing VNFs map' )
  # Parse input parameters
  (options, args) = parser.parse_args( )
  # Done, return
  return options

if __name__ == '__main__':
  # Let's parse input parameters
  opts = parseOptions( )
  # Deploy topology
  deploy(opts)
  # Clean shutdown
  shutdown()