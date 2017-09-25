#!/usr/bin/python

from collections import defaultdict
from mininet.log import info

import networkx as nx
import time

# Build shortest path routing for the given topology
class SPFRouting( object ):

  def routing(self, routes, topology, destinations, interfaces_to_ip):
    # Init steps
    info("Building routing...\n")
    # Calculate all the shortest path for the given topology
    shortest_paths = nx.all_pairs_shortest_path(topology)
    # Iterate over nodes
    for node in topology.nodes(data=True):
      # Access to data
      node_type   = node[1]['type']
      # Access to name
      node        = node[0]
      # This node is a server
      if node_type == "server":
        # Just skip
        continue
      # Iterate over destinations:
      for destination, via in destinations.iteritems():
        # If it is directly attached
        if node in via:
          # Just skip
          continue
        # Log the procedure
        info("Calculating route from " + node + " -> " + destination + "...")
        # Initialize min via
        min_via = via[0]
        # Iterate over remaining via
        for i in range(1, len(via)):
          # Get hops of the old via
          old_hops      = len(shortest_paths[node][min_via])
          # Get hops of the current via
          current_hops  = len(shortest_paths[node][via[i]])
          # Lower
          if current_hops < old_hops:
            # Update min_via
            min_via = via[i]
        # Init route
        route = {}
        # Save the destination
        route["subnet"]   = destination
        # Get the link from the topology
        link_topology     = topology[node][shortest_paths[node][min_via][1]]
        # Get the gateway. We are assuming no multi-links
        gateway           = interfaces_to_ip[link_topology[0]["rhs_intf"]]
        # Save the gateway
        route["gateway"]  = gateway
        # Get the device
        route["device"]   = link_topology[0]["lhs_intf"]
        # Save the route
        routes[node].append(route)
        # Log the found via
        info("found " + gateway + "\n")
    # Done
    return routes 

# Build equal cost multi path routing for the given topology
class ECMPRouting( object ):

  def routing(self, routes, topology, destinations, interfaces_to_ip):
    # Init steps
    shortest_paths  = {}
    # Calculate all the shortest path for the given topology
    paths           = nx.all_pairs_shortest_path(topology)
    # TODO finish ecmp routing