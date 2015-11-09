#! /usr/bin/python
"""
Netwerken en Systeembeveiliging Lab 2A - HTTP and SMTP
NAME: Tijn Kersjes
STUDENT ID: 11048018
DESCRIPTION:
"""

import sys
import socket
import mimetypes

STATUS_CODES = {
    200: "OK",
    404: "Not Found",
    501: "Not Implemented"
}

def getContentType(fname):
    parts = fname.split(".")
    ext = parts[len(parts) - 1]
    mime = mimetypes.types_map["." + ext]
    return mime

def sendFile(client, fname):
    mime = getContentType(fname)
    size = os.path.getsize(fname)
    sendHeaders(client, 200, mime, size)
    fh = open(fname, "r")
    for line in fh:
        client.send(line)
    fh.close()


def sendMessage(client, message, status=200):
    sendHeaders(client, status, "text/plain", str(len(message)))
    client.sendall(message)

def sendHeaders(client, status=200, mime="text/plain", size=0):
    client.send("HTTP/1.1 " + str(status) + " " + STATUS_CODES[status] + "\n")
    client.send("Connection: close\n")
    client.send("Content-Type: " + mime + "\n")
    client.send("Content-Length: " + str(size) + "\n")
    client.send("\n")

def serve(IP, PORT, PUBLIC_HTML, CGIBIN):

    mimetypes.init()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP, PORT))
    server.listen(10)

    print "Listening at " + (IP or "localhost") + ":" + str(PORT) + "..."

    while True:
        try:
            client, (cip, cport) = server.accept()
            print " >> connected: "+ str(cip) + ":" + str(cport)
            while 1:

                # receive and process data
                data = client.recv(1024)
                req = data.split();

                print data

                # invalid request
                if len(req) < 3:
                    client.close()
                    break

                # only GET requests are supported
                elif req[0] != "GET":
                    body = "Sorry, unable to handle " + req[0] + " requests"
                    sendMessage(client, body, 501)

                # check if resource exists
                elif not os.path.isfile(PUBLIC_HTML + "/" + req[1]) :
                    body = "File '" + str(req[1]) + "' was not found :("
                    sendMessage(client, body, 404)

                # send the file contents
                else:
                    sendFile(client, PUBLIC_HTML + "/" + req[1])

                # close connection
                client.close()
                break

        # close server on SIGINT
        except (KeyboardInterrupt, SystemExit):
            print "\nClosing server..."
            server.close()
            print "Cheers!"
            sys.exit(0)

# This the entry point of the script.
# Do not change this part.
if __name__ == '__main__':
	import os, sys, argparse
	p = argparse.ArgumentParser()
	p.add_argument('--ip', help='ip to bind to', default="")
	p.add_argument('--port', help='port to bind to', default=8080, type=int)
	p.add_argument('--public_html', help='home directory', default='./public_html')
	p.add_argument('--cgibin', help='cgi-bin directory', default='./cgi-bin')
	args        = p.parse_args(sys.argv[1:])
	public_html = os.path.abspath(args.public_html)
	cgibin      = os.path.abspath(args.cgibin)
	serve(args.ip, args.port, public_html, cgibin)
