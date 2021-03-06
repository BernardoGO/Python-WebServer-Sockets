#!/usr/bin/python

import socket
import signal
import time
import os, sys
import config


class Server:
    def __init__(self, port=config.__INTERNAL_PORT__):
        # lib_path = os.path.abspath('www/')
        #sys.path.append(lib_path)

        self.host = ''
        self.port = port
        self.www_dir = config.__WWW_DIR__

    def recvall(self, sock):
        data = ""
        part = None
        retry = 0
        packetnum = 0
        while retry < 1:
            print "waiting packet *" + str(retry)
            part = sock.recv(config.__PACKET_SIZE__)
            data += part

            if not "multipart/form-data" in data and packetnum == 0:
                retry = 10
            if part.rstrip().endswith('--'):
                break
            if len(part) < 2:
                retry += 1

            packetnum += 1
            print "|" + part + "|"
        print "******* END  *******"
        return data

    def splitlen(self, seq, length):
        return [seq[i:i + length] for i in range(0, len(seq), length)]

    def activate_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            srv = self.host
            if srv == '':
                srv = 'LOCAL'
            print "HTTP server on " + str(srv) + ":" + str(self.port)
            self.socket.bind((self.host, self.port))

        except Exception as e:
            print ("Warning: Could not open port:", self.port, e, "\n")
            print ("Trying 8080")

            if config.__USE_8080_AS_WHEN_FAILS__ == False:
                print("ERROR: Failed to acquire sockets for ports ", user_port, " and 8080. ")
                print("Try running the Server in a privileged user mode.")
                self.shutdown()
                import sys

                sys.exit(1)

            user_port = self.port
            self.port = 8080

            try:
                srv = self.host
                if srv == '':
                    srv = 'LOCAL'
                print "HTTP server on " + str(srv) + ":" + str(self.port)
                self.socket.bind((self.host, self.port))

            except Exception as e:
                print("ERROR: Failed to acquire sockets for ports ", user_port, " and 8080. ")
                self.shutdown()
                import sys

                sys.exit(1)

        print ("Server successfully acquired the socket with port:", self.port)
        print ("Press Ctrl+C to shut down the server and exit.")
        self._wait_for_connections()

    def shutdown(self):
        try:
            print("Shutting down the server")
            s.socket.shutdown(socket.SHUT_RDWR)

        except Exception as e:
            print("Warning: could not shut down the socket. Maybe it was already closed", e)

    def _gen_headers(self, code):
        h = ''
        if (code == 200):
            h = 'HTTP/1.1 200 OK\n'
        elif (code == 404):
            h = 'HTTP/1.1 404 Not Found\n'

        current_date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
        h += 'Date: ' + current_date + '\n'
        h += 'Server: Bernardo\n'
        h += 'Connection: close\n\n'

        return h

    def _wait_for_connections(self):
        while True:
            print ("listening for connections now")
            self.socket.listen(config.__MAX__QUEUED_CONN__)

            conn, addr = self.socket.accept()

            print("Connected: ", addr)

            data = self.recvall(conn)
            string = data  # bytes.decode(data)

            request_method = string.split(' ')[0]
            print ("Method: ", request_method)
            print ("Request body: ", string)

            if (request_method == 'GET') | (request_method == 'HEAD') | (request_method == 'POST'):


                file_requested = string.split(' ')
                file_requested = file_requested[1]

                import pages as module

                file_requested = self.www_dir + file_requested
                print ("Serving web page [", file_requested, "]")

                sresponse = module.main(string, data)
                response_headers = self._gen_headers(sresponse[0])

                server_response = response_headers.encode()

                if (request_method == 'GET' or request_method == 'POST'):
                    server_response += sresponse[1]

                print type(sresponse[1])
                for i in self.splitlen(server_response, 512):  # self.splitlen(sresponse[1], 512):
                    #server_response =  response_headers.encode()
                    #if (request_method == 'GET' or request_method == 'POST'):
                    #    server_response += i  # return additional conten for GET only
                    conn.send(i)
                print ("Closing connection with client")
                conn.close()

            else:
                print("Unknown HTTP request method:", request_method)
                req = string.split(' ')
                for ty in xrange(0, len(req)):
                    print str(ty) + ":" + req[ty]
                try:
                    print req[25].split('\r\n\r\n')[1]
                except:
                    pass


def ctrlC_shutdown(sig, dummy):
    s.shutdown()  # shut down the server
    import sys

    sys.exit(1)

###########################################################
signal.signal(signal.SIGINT, ctrlC_shutdown)

print ("Starting web server")
s = Server()
s.activate_server()
