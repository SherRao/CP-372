"""
CP 372 Assignment 3
Node.py

@author Nausher Rao (190906250) - https://github.com/SherRao/
"""
from common import *


class Node:
    def __init__(self, ID, networksimulator, costs):
        """
        Initializes the node.
        """
        self.myID = ID
        self.ns = networksimulator

        num = self.ns.NUM_NODES
        def isNotInf(i): return costs[i] != self.ns.INFINITY

        self.distanceTable = [[0 for _ in range(num)] for _ in range(num)]
        self.routes = [i if isNotInf(i) else self.ns.INFINITY for i in range(num)]
        self.connections = [i for i in range(num) if isNotInf(i)]

        for i in range(num):
            for j in range(num):
                result = self.ns.INFINITY
                if(i == j):
                    result = 0

                elif(i == self.myID):
                    result = costs[j]

                self.distanceTable[i][j] = result

        for i in self.connections:
            if(i != ID):
                self.ns.tolayer2(RTPacket(ID, i, costs))

        return

    def recvUpdate(self, packet):
        """
        Receives an update from the network layer and updates the distance table.
        """

        self.distanceTable[packet.sourceid] = packet.mincosts
        costs = self.bellmanFord(self.myID)

        if(not isArrayEqual(self.distanceTable[self.myID], costs)):
            self.distanceTable[self.myID] = costs
            for i in self.connections:
                if(i != self.myID):
                    self.ns.tolayer2(RTPacket(self.myID, i, costs))

        return

    def printdt(self):
        """
        Prints the distance table.
        """

        print("   D"+str(self.myID)+" |  ", end="")
        for i in range(self.ns.NUM_NODES):
            print("{:3d}   ".format(i), end="")
        print()
        print("  ----|-", end="")

        for i in range(self.ns.NUM_NODES):
            print("------", end="")
        print()

        for i in range(self.ns.NUM_NODES):
            print("     {}|  ".format(i), end="")

            for j in range(self.ns.NUM_NODES):
                print("{:3d}   ".format(self.distanceTable[i][j]), end="")
            print()

        print()
        return

    def bellmanFord(self, id):
        """
        Performs the Bellman Ford Algorithm on the distance table.
        """

        result = []
        for i in range(self.ns.NUM_NODES):
            if(id == i):
                result.append(0)

            else:
                path = self.distanceTable[id][i]
                for j in range(self.ns.NUM_NODES):
                    if(self.distanceTable[id][j] != self.ns.INFINITY):
                        cost = self.distanceTable[id][j] + \
                            self.distanceTable[j][i]
                        if(cost < path):
                            path = cost
                            self.routes[i] = j

                result.append(path)

        return result


def isArrayEqual(a, b):
    """
    Checks to see if the two given arrays are equal.
    """

    return all(x == y for (x, y) in zip(a, b))
