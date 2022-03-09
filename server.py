#############################
# author: Miika Pynttäri
# course: Distributed Systems
# sources: https://pythonprogramming.net/server-chatroom-sockets-tutorial-python-3/
#############################

# server-side code for a python TCP chatroom app
# expanded upon the https://pythonprogramming.net/ source linked above



import socket
import select


HEADERLEN = 10
IP = socket.gethostname()
PORT = 3000


# creating and connecting to the socket

serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

serv_sock.bind(('', PORT))
serv_sock.listen(4)


# keeping track of the sockets and clients with lists

sock_list = [serv_sock]
clients = {}
print(f'Listening to {IP}:{PORT}...')



# message receiving function

def receive_msg(client):
    
    # checking if received anything
    
    try:
        
        
        # saving the received sockets header into a variable
        
        msg_header = client.recv(HEADERLEN)
        
        
        # if the header was empty, client has closed the connection
        
        if not len(msg_header): return False
        
        
        # decoding the message and saving it as an object
        
        msg_length = int(msg_header.decode('utf-8').strip())
        return { 'header': msg_header, 'data': client.recv(msg_length) }
    
    
    # edge-case checking, e.g. user pressed ctrl-c
    except: return False
    
    
def main():
    while True:
        read_sockets, _, exception_sockets = select.select(sock_list, [], sock_list)
        
        
        # checking all the notified sockets
        
        for notified_socket in read_sockets:
            
            
            # if notified_sock == serv_sock --> there's a new connection, let's accept that
            
            if notified_socket == serv_sock:
                
                
                # creating a unique socket for this client only
                
                client_sock, client_addr = serv_sock.accept()
                
                
                # checking that the user has a socket. if not, dismissing the function
                
                user = receive_msg(client_sock)
                if user is False: continue
                
                
                # adding the newly accepted socket into the socket list
                # while saving the user's data
                
                sock_list.append(client_sock)
                clients[client_sock] = user
                
                print(f"New connection from {client_addr[0]}:{client_addr[1]} user: {user['data'].decode('utf-8')}")
              
              
                
            else:
                
                msg = receive_msg(notified_socket)
                
                
                # handling if the client wants to disconnect
                
                if (msg) and (msg['data'].decode('utf-8') == '!qq'):
                    print(f"Connection closed from {clients[notified_socket]['data'].decode('utf-8')}")
                    msg = receive_msg(notified_socket)
                    
                    for cl_sock in clients:
                        if cl_sock != notified_socket:
                            cl_sock.send(user['header'] + user['data'] + msg['header'] + msg['data'])
                    
                    
                    # removing the client from the list
                    
                    sock_list.remove(notified_socket)
                    del clients[notified_socket]
                    continue
                    
                
                user = clients[notified_socket]
                
                
                # sending the client's message
                
                if (msg):
                    print(f"Message from {user['data'].decode('utf-8')}: {msg['data'].decode('utf-8')}")
                    
                    for cl_sock in clients:
                        if cl_sock != notified_socket:
                            cl_sock.send(user['header'] + user['data'] + msg['header'] + msg['data'])


        # other exception handling

        for notified_socket in exception_sockets:
            sock_list.remove(notified_socket)
            del clients[notified_socket]
            
main()