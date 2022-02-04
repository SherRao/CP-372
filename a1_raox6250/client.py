"""
CP 372 - Assignment 1
The main client.

Nausher Rao - 190906250
"""
import time;
import socket; 
import struct;
import sys;

SERVER_ADDRESS = "localhost";
INITIAL_SERVER_PORT = 12000;
CLIENT_ENTITY = 1;
SERVER_ENTITY = 2;

def main():
    try: 
        phaseA = a();
        time.sleep(0.25);
        
        phaseB = b(phaseA);
        time.sleep(0.25);

        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        phaseC = c(phaseB, clientSocket);
        time.sleep(0.25);

        d(phaseB, phaseC, clientSocket);

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
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);

    response = processPhaseA(clientSocket, SERVER_ADDRESS, INITIAL_SERVER_PORT, 0, "Hello World!!!");
    clientSocket.close();

    print(f"Data received from server={response}");
    print("--------- End of Stage A ---------");
    return response;


def b(phaseA: object):
    print("\n--------- Starting Stage B ---------");
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);
    clientSocket.settimeout(1);
    response = processPhaseB(clientSocket, SERVER_ADDRESS, phaseA["udpPort"], phaseA["repeat"], phaseA["codeA"], bytearray(phaseA["len"]));
    clientSocket.close();
    
    print(f"Data received from server={response}");
    print("--------- End of Stage B ---------");
    return response;


def c(phaseB: object, clientSocket: object):
    print("\n--------- Starting Stage C ---------");
    response = processPhaseC(clientSocket, SERVER_ADDRESS, phaseB["tcpPort"]);
    
    print(f"Data received from server={response}");
    print("--------- End of Stage C ---------");
    return response; 


def d(phaseB: object, phaseC: object, clientSocket: object):
    print("\n--------- Starting Stage D ---------");
    char = phaseC["char"];
    repeat = phaseC["len2"];

    response = processPhaseD(clientSocket, SERVER_ADDRESS, phaseB["tcpPort"], phaseC["repeat2"], phaseC["codeC"], phaseC["len2"], (char * repeat).encode());
    
    print(f"Data received from server={response}");
    print("--------- End of Stage D ---------");
    return response;


"""
Phase A

Send a basic UDP packet to the server, and then receives a response.
"""
def processPhaseA(clientSocket: object, address: str, port: int, pcode: int, data: str):
    dataLength = len(data.encode());
    while dataLength % 4 > 0:
        data += '0';
        dataLength += 1;

    header = struct.pack("!IHH", dataLength, pcode, CLIENT_ENTITY);
    packet = header + data.encode("UTF-8");
    clientSocket.sendto(packet, (address, port));
    response = clientSocket.recv(2048);

    print(f"Data sent to server={{'dataLength'={dataLength}, 'pcode'={pcode}, 'entity'={CLIENT_ENTITY}, 'data'={data}}}");
    serverDataLength, serverPcode, serverEntity, serverRepeat, serverUdpPort, serverLen, serverCodeA = struct.unpack_from("!IHHIIHH", response);
    while(serverLen % 4 > 0):
        serverLen += 1;

    if serverPcode == 555:
        print(response[8:].decode());
        sys.exit();

    else:
        return {
            "dataLength": serverDataLength,
            "pcode": serverPcode,
            "entity": serverEntity,
            "repeat": serverRepeat,
            "udpPort": serverUdpPort,
            "len": serverLen,
            "codeA": serverCodeA
        };


"""
Phase B

Sends multiple packets via UDP. Each packet requires an ACK packet to be received from the server.
If a packet doesn't receive an ACK, it will be resent. At the end of the repeat packets, a final 
data packet is received from the server.
"""
def processPhaseB(clientSocket: object, address: str, port: str, repeat: int, pcode: int, data: str):
    for i in range(repeat):
        dataLength = len(data) + 4;
        header = struct.pack("!IHHI", dataLength, pcode, CLIENT_ENTITY, i);
        packet = header + data;

        clientSocket.sendto(packet, (address, port));
        print(f"Data sent to server={{'dataLength'={dataLength}, 'pcode'={pcode}, 'entity'={CLIENT_ENTITY}, 'pid'={i}}}");
        received = False;
        while(not received):
            try:
                response = clientSocket.recv(2048);
                received = True;
                ackDataLength, ackPcode, ackEntity, ackId = struct.unpack_from("!IHHI", response);
                print(f"ACK received from server={{'ackDataLength'={ackDataLength}, 'ackPcode'={ackPcode}, 'ackEntity'={ackEntity}, 'ackId'={ackId}}}");

            except:
                clientSocket.sendto(packet, (address, port));
            
    response = clientSocket.recv(2048);
    serverDataLength, serverPcode, serverEntity, serverTcpPort, serverCodeB = struct.unpack_from("!IHHII", response);
    if serverPcode == 555:
        print(response[8:].decode());
        sys.exit();

    else:
        return {
            "dataLength": serverDataLength,
            "pcode": serverPcode,
            "entity": serverEntity,
            "tcpPort": serverTcpPort,
            "codeB": serverCodeB
        };


"""
Phase C

Connects to the server via TCP and parses data sent from the server.
"""
def processPhaseC(clientSocket: object, address: str, port: int):
    clientSocket.connect((address, port));
    response = clientSocket.recv(2048);
    serverDataLength, serverPcode, serverEntity, serverRepeat, serverLen, serverCodeC, serverChar = struct.unpack_from("!IHHIIIc", response);
    while(serverLen % 4 > 0):
        serverLen += 1;
    
    if serverPcode == 555:
        print(response[8:].decode());
        sys.exit();

    else:
        return {
            "dataLength": serverDataLength,
            "pcode": serverPcode,
            "entity": serverEntity,
            "repeat2": serverRepeat,
            "len2": serverLen,
            "codeC": serverCodeC,
            "char": serverChar.decode()
        };


"""
Phase D

Sends repeat packets via the same TCP connection from Phase C. At the end of the
repeat packets, a final data packet is received from the server.
"""
def processPhaseD(clientSocket: object, address: str, port: int, repeat: int, pcode: int, dataLength: int, data: str):
    for i in range(repeat):
        header = struct.pack("!IHH", dataLength, pcode, CLIENT_ENTITY);
        packet = header + data;
        clientSocket.send(packet);
        print(f"Data sent to server={{'dataLength'={dataLength}, 'pcode'={pcode}, 'entity'={CLIENT_ENTITY}}}");

    response = clientSocket.recv(2048);
    serverDataLength, serverPcode, serverEntity, serverCodeD = struct.unpack_from("!IHHI", response);
    if serverPcode == 555:
        print(response[8:].decode());
        sys.exit();
    
    else:
        return {
            "dataLength": serverDataLength,
            "pcode": serverPcode,
            "entity": serverEntity,
            "codeD": serverCodeD
        };


if(__name__=="__main__"):
    main();