"""
CP 372 - Assignment 1
The main server.

Nausher Rao - 190906250
"""
import random;
import socket; 
import struct;
import sys;

INITIAL_SERVER_PORT = 12000;
CLIENT_ENTITY = 1;
SERVER_ENTITY = 2;
TIMEOUT = 3;

def main():
    try: 
        phaseA = a();
        phaseB = b(phaseA["server"]);
        phaseC = c(phaseB);
        d(phaseC["server"], phaseC["clientSocket"], phaseC["serverSocket"]);

    except socket.timeout:
        print("A socket has timed out, shutting down...");
        sys.exit();

    except socket.error:
        print("A socket has produced an error, shutting down...");
        sys.exit();

    except struct.error:
        print("A packet has produced an error, shutting down...");
        sys.exit();

    return;


def a():
    print("--------- Starting Stage A ---------");
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);
    serverSocket.settimeout(TIMEOUT);
    clientRes, serverRes = processPhaseA(serverSocket, INITIAL_SERVER_PORT);
    serverSocket.close();

    print(f"Data received from client={clientRes}");
    print(f"Data sent to client={serverRes}");
    print("--------- End of Stage A ---------\n");

    return {"client": clientRes, "server": serverRes};   


def b(phaseA: object):
    print("--------- Starting Stage B ---------");
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);
    serverSocket.settimeout(TIMEOUT);
    serverRes = processPhaseB(serverSocket, phaseA["udpPort"], phaseA["repeat"], phaseA["codeA"], phaseA["len"]);
    serverSocket.close();

    print(f"Data sent to client={serverRes}");
    print("--------- End of Stage B ---------\n");
    
    return serverRes;


def c(phaseB: object):
    print("--------- Starting Stage C ---------");
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
    serverSocket.settimeout(TIMEOUT);
    serverRes, clientSocket = processPhaseC(serverSocket, phaseB["tcpPort"], phaseB["codeB"]);

    print(f"Data sent to client={serverRes}");
    print("--------- End of Stage C ---------\n"); 

    return {"server": serverRes, "clientSocket": clientSocket, "serverSocket": serverSocket};


def d(phaseC: object, clientSocket: object, serverSocket: object):
    print("--------- Starting Stage D ---------");
    serverRes = processPhaseD(clientSocket,  phaseC["repeat"], phaseC["pcode"]);
    serverSocket.close();

    print(f"Data sent to client={serverRes}");
    print("--------- End of Stage D ---------\n");


"""
Phase A

Receives a basic UDP packet from the client, and sends back a response.
"""
def processPhaseA(serverSocket: object, port: int):
    serverSocket.bind(("", port));
    response, clientAddress = serverSocket.recvfrom(1024);
    clientDataLength, clientPcode, clientEntity, clientData = struct.unpack_from("!IHHs", response);

    repeat = random.randint(5, 20);
    udpPort = random.randint(20000, 30000);
    ln = random.randint(50, 100);
    codeA = random.randint(100, 400);

    # 12 is the size of IIHH (repeat, udpPort, codeA, len)
    packet = struct.pack("!IHHIIHH", 12, clientPcode, SERVER_ENTITY, repeat, udpPort, ln, codeA); 
    serverSocket.sendto(packet, clientAddress);

    # The response sent by the client.
    clientResponse = {
        "dataLength": clientDataLength,
        "pcode": clientPcode,
        "entity": clientEntity,
        "data": clientData.decode()
    };

    # The response sent by the server.
    serverResponse = {
        "pcode": clientPcode,
        "entity": SERVER_ENTITY,
        "repeat": repeat,
        "udpPort": udpPort,
        "len": ln,
        "codeA": codeA
    }

    return clientResponse, serverResponse;


"""
Phase B

Receives multiple packets via UDP. Randomly for each packet, an ACK packet will be sent.
At the end of the repeat packets, a final data packet is sent to the client.
"""
def processPhaseB(serverSocket: object, port: int, repeat: int, pcode: int, ln: int):
    serverSocket.bind(("", port));
    packetsReceived = 0;
    while(packetsReceived < repeat):
        response, clientAddress = serverSocket.recvfrom(1024);
        clientDataLength, clientPcode, clientEntity, clientPacketId = struct.unpack_from("!IHHI", response);
        print(f"Data received from client={{'clientDataLength'={clientDataLength}, 'clientPcode'={clientPcode}, 'clientEntity'={clientEntity} 'clientPacketId'={clientPacketId}}}");

        # Randomly send an ACK packet for each repeat packet.
        if(random.randint(0, 10) != 10):
            packet = struct.pack("!IHHI", 4, clientPcode, SERVER_ENTITY, packetsReceived);
            serverSocket.sendto(packet, clientAddress);
            packetsReceived += 1;

    # Send the final packet after all ACK packets have been sent.
    codeB = random.randint(100, 400);
    tcpPort = random.randint(20000, 30000);
    packet = struct.pack("!IHHII", 8, pcode, SERVER_ENTITY, tcpPort, codeB);
    serverSocket.sendto(packet, clientAddress);

    # The response sent by the server.
    return {
        "pcode": pcode,
        "entity": SERVER_ENTITY,
        "tcpPort": tcpPort,
        "codeB": codeB
    };


"""
Phase C

Accepts a TCP connection and sends data to the connected client.
"""
def processPhaseC(serverSocket: object, port: int, pcode: int):
    serverSocket.bind(("", port));
    serverSocket.listen(1);

    clientSocket, clientAddress = serverSocket.accept();
    repeat2 = random.randint(5, 20);
    ln2 = random.randint(50, 100);
    codeC = random.randint(100, 400);
    char = chr(random.randint(65, 90));

    print("Client connected to server");
    packet = struct.pack("!IHHIIIc", 13, pcode, SERVER_ENTITY, repeat2, ln2, codeC, char.encode());
    clientSocket.send(packet);
    
    # The response sent by the server.
    serverResponse = {
        "pcode": pcode,
        "entity": SERVER_ENTITY,
        "repeat": repeat2,
        "len": ln2,
        "codeC": codeC,
        "char": char
    };

    return serverResponse, clientSocket;


"""
Phase D

Receives repeat packets via the same TCP connection from Phase C. At the end of 
the repeat packets, a final data packet is sent to the client. 
"""
def processPhaseD(clientSocket: object, repeat: int, pcode: int):
    packetsReceived = 0;
    while(packetsReceived < repeat):
        response = clientSocket.recv(1024);
        clientDataLength, clientPcode, clientEntity, clientPacketId = struct.unpack_from("!IHHI", response);
        packetsReceived += 1;
        print(f"Data received from client={{clientDataLength={clientDataLength}, clientPcode={clientPcode}, clientEntity={clientEntity}}}");
        
    # Send the final packet after all ACK packets have been sent.
    codeD = random.randint(100, 400);
    packet = struct.pack("!IHHI", 8, pcode, SERVER_ENTITY, codeD);
    clientSocket.send(packet);

    # The response sent by the server.
    return {
        "pcode": pcode,
        "entity": SERVER_ENTITY,
        "codeD": codeD
    };
        
if(__name__ == "__main__"):
    main();
