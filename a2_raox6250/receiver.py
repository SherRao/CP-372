"""
CP 372 Assignment 2
receiver.py

@author Nausher Rao (190906250)
@author X (X)
"""
from common import *

class receiver:
    def __init__(self, entityName, ns):
        self.entity = entityName;
        self.networkSimulator = ns;
        print("Initializing receiver: B: "+str(self.entity));
        return;

    def init(self):
        '''
        Initialize expected sequence number.
        '''
        self.expectedSequenceNumber = 0;
        self.ack_duplicate = None;
        return;

    def isCorrupted(self, packet):
        '''
        Checks if a received packet has been corrupted during transmission.
        Return true if computed checksum is different than packet checksum.
        '''
        return packet.checksum != checksumCalc(packet.payload + str(packet.sequenceNumber) + str(packet.ackNumber));
   
    def isDuplicate(self, packet):
        '''
        Checks if packet sequence number is the same as expected sequence number.
        '''
        return packet.sequenceNumber != self.expectedSequenceNumber;
    
    def getNextExpectedsequenceNumber(self):
        '''
        The expected sequence numbers are 0 or 1.
        '''
        return (self.expectedSequenceNumber + 1) % 2;

    def input(self, packet):
        '''
        This method will be called whenever a packet sent 
        from the sender arrives at the receiver. If the received
        packet is corrupted or duplicate, it sends a packet where
        the ack number is the sequence number of the  last correctly
        received packet. Since there is only 0 and 1 sequence numbers,
        you can use the sequence number that is not expected.
        
        If packet is OK (not a duplicate or corrupted), deliver it to the
        application layer and send an acknowledgement to the sender.
        '''
        if(not self.isCorrupted(packet) and not self.isDuplicate(packet)):
            self.networkSimulator.deliverData(self.entity, packet.payload);
            self.networkSimulator.udtSend(self.entity, packet);
            self.ack_duplicate = packet;
            self.expectedSequenceNumber = self.getNextExpectedsequenceNumber();

        elif(self.ack_duplicate is not None):
            self.networkSimulator.udtSend(self.entity, self.ack_duplicate);

        return;