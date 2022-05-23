# Python program to implement server side of chat room.
import os
import socket
import select
import sys
import fcntl
from threading import Thread

'''Replace "thread" with "_thread" for python 3'''
from _thread import *

"""The first argument AF_INET is the address domain of the
socket. This is used when we have an Internet Domain with
any two hosts The second argument is the type of socket.
SOCK_STREAM means that data or characters are read in
a continuous flow."""
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# checks whether sufficient arguments have been provided
if len(sys.argv) != 3:
    print("Correct usage: script, IP address, port number")
    exit()

# takes the first argument from command prompt as IP address
IP_address = str(sys.argv[1])

# takes second argument from command prompt as port number
Port = int(sys.argv[2])

"""
binds the server to an entered IP address and at the
specified port number.
The client must be aware of these parameters
"""
server.bind((IP_address, Port))

"""
listens for 100 active connections. This number can be
increased as per convenience.
"""
server.listen(100)

map_of_clients = {}


def clientthread(conn, tname):
    # sends a message to the client whose user object is conn
    conn.send("Welcome to this chatroom!".encode())

    while True:
        try:
            message = conn.recv(2048)
            if message:

                """prints the message and address of the
					user who just sent the message on the server
					terminal"""
                messageList = message.decode().split(" ")
                sys.stdout.write(message.decode())
                sys.stdout.flush()
                # Calls broadcast function to send message to all
                if (messageList[0].startswith('@')):
                    name = messageList[0][1:]
                    msg = message.decode().split(' ', 1)[1]
                    if name in map_of_clients:
                        sendToOne(msg, name)
                    else:
                        print("client not found")
                else:
                    broadcast(tname, message.decode(),  conn)

            else:
                """message may have no content if the connection
				is broken, in this case we remove the connection"""
                remove(conn)

        except Exception as e:
            print(str(e))
            continue


"""Using the below function, we broadcast/send the message to all/one
clients who's object is not the same as the one sending
the message """


def sendToOne(message, client):
    conn = map_of_clients[client]
    try:
        conn.send((client + "=> " + message).encode())
    except Exception as e:
        print(str(e))
        conn.close()
        remove(conn)


def broadcast(name, message, connection):
    for clients in map_of_clients:
        if map_of_clients[clients] != connection:
            try:
                map_of_clients[clients].send((name + "=> " + message).encode())
            except Exception as e:
                print(str(e))
                map_of_clients[clients].close()

                # if the link is broken, we remove the client
                remove(clients)


"""The following function simply removes the object
from the list that was created at the beginning of
the program"""


def remove(connection):
    if connection in map_of_clients:
        map_of_clients.remove(connection)


while True:
    """Accepts a connection request and stores two parameters,
	conn which is a socket object for that user, and addr
	which contains the IP address of the client that just
	connected"""
    conn, addr = server.accept()
    message = conn.recv(2048)
    # fcntl.fcntl(conn, fcntl.F_SETFL, os.O_NONBLOCK)
    """Maintains a list of clients for ease of broadcasting
	a message to all available people in the chatroom"""
    map_of_clients[message.decode()] = conn

    # prints the address of the user that just connected
    print(addr[0] + "/" + message.decode() + " connected")

    # creates and individual thread for every user
    # that connects
    thread = Thread(target=clientthread, args=(conn, message.decode()))
    thread.start()

conn.close()
server.close()
