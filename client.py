#############################
# author: Miika Pynttäri
# course: Distributed Systems
# sources: https://pythonprogramming.net/client-chatroom-sockets-tutorial-python-3/
#############################

# client-side code for a python TCP chatroom app
# expanded upon the https://pythonprogramming.net/ source linked above



import socket
import errno
import sys


HEADERLEN = 10
PORT = 3000

nickname = input("Enter a username: ")

IP = input("Give a room IP to connect to (default: '127.0.0.1'): ")
print(f'Connected to room {IP}, type !qq to disconnect.\n')


# creating a connecting to a new socket

client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_sock.connect((IP, PORT))
client_sock.setblocking(False)


# encoding the user's nickname and header for sending

encoded_nick = nickname.encode('utf-8')
encoded_header = f'{len(encoded_nick):<{HEADERLEN}}'.encode('utf-8')
client_sock.send(encoded_header + encoded_nick)


while True:
    
    # enabling the user to chat
    
    msg = input(f' {nickname}: ')
    
    
    # checking that the user typed something
    
    if msg:
        
        
        # same encoding as before
        
        msg = msg.encode('utf-8')
        msg_header = f'{len(msg):<{HEADERLEN}}'.encode('utf-8')
        client_sock.send(msg_header + msg)
        
        
        # if the user typed '!qq' --> disconnecting the user
        
        if msg.decode('utf-8') == "!qq":
            print(f'You have disconnected.')
            
            msg = f'has disconnected.'
            
            
            # sending the disconnect message forward to the server
            
            msg = msg.encode('utf-8')
            msg_header = f'{len(msg):<{HEADERLEN}}'.encode('utf-8')
            client_sock.send(msg_header + msg)
            sys.exit()
        
    
    # error handling with try-except 
    
    try:
        while True:
            
            encoded_header = client_sock.recv(HEADERLEN)
            
            
            # if there was no message = user closed the server
            
            if not len(encoded_header):
                print(f'Server closed the connection.')
                sys.exit()
                
            
            nickname_len = int(encoded_header.decode('utf-8').strip())
            encoded_nick = client_sock.recv(nickname_len).decode('utf-8')
            
            msg_header = client_sock.recv(HEADERLEN)
            msg_length = int(msg_header.decode('utf-8').strip())
            msg = client_sock.recv(msg_length).decode('utf-8')
            
            
            # checking if we received a user's disconnect message
            
            if msg == 'has disconnected.':
                print(f'{encoded_nick} has disconnected.')
            
            
            # if the message was normal, printing it to screen
                
            else:
                print(f' {encoded_nick}: {msg}')
        
    
    # checking for IOErrors
            
    except IOError as err:
        if (err.errno != errno.EAGAIN) and (err.errno != errno.EWOULDBLOCK):
            print(f'>> err: {str(err)}')
            sys.exit()
        
        
        # if nothing was received, skipping past this
         
        continue
    
    
    # checking for any other errors, if so, shutting everything down
    
    except Exception as err:
        print(f'>> err: {str(err)}')
        sys.exit()