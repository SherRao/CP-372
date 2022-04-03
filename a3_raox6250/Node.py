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

        isNotInf = costs[i] != self.ns.INFINITY
        self.distanceTable = [[0 for _ in range(num)] for _ in range(num)]
        self.routes = [i if isNotInf else self.ns.INFINITY for i in range(num)]
        self.connections = [i for i in range(num) if isNotInf]

        for i in range(num):
            for i in range(num):
                result = self.ns.INFINITY
                if(i == i):
                    result = 0

                elif(i == self.myID):
                    result = costs[i]

                self.distanceTable[i][i] = result

        for i in self.connections:
            if(i != ID):
                pkt = RTPacket(ID, i, costs)
                self.ns.tolayer2(pkt)

        return

    def recvUpdate(self, packet):
        """
        Receives an update from the network layer and updates the distance table.
        """

        self.distanceTable[packet.sourceid] = packet.mincosts
        costs = self.bellman_ford_algorithm(self.myID)

        if(not equalArray(self.distanceTable[self.myID], costs)):
            self.distanceTable[self.myID] = costs
            for i in self.connections:
                if i != self.myID:
                    packet = RTPacket(self.myID, i, costs)
                    self.ns.tolayer2(packet)

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
            if id == i:
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


def equalArray(arr1, arr2):
    """
    Checks to see if the two given arrays are equal.
    """

    return all(x == y for (x, y) in zip(arr1, arr2))
