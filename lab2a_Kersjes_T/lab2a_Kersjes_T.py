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
import subprocess

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
        client.sendall(line)
    fh.close()

def sendScriptOutput(client, fname, subenv):
    sendStatus(client, 200)
    output = subprocess.call(["python", fname], env = subenv, stdout = client)

def sendMessage(client, message, status=200):
    sendHeaders(client, status, "text/plain", str(len(message)))
    client.sendall(message)

def sendHeaders(client, status=200, mime="text/plain", size=0):
    sendStatus(client, status)
    client.sendall("Connection: close\n")
    client.sendall("Content-Type: " + mime + "\n")
    client.sendall("Content-Length: " + str(size) + "\n")
    client.sendall("\n")

def sendStatus(client, status=200):
    client.sendall("HTTP/1.1 " + str(status) + " " + STATUS_CODES[status] + "\n")

def serve(IP, PORT, PUBLIC_HTML, CGIBIN):

    mimetypes.init()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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

                #print data

                # valid request
                if len(req) >= 3:

                    method = str(req[0])
                    request = str(req[1])
                    req_parts = request.split("?")
                    if len(req_parts) >= 2:
                        uri, query = req_parts[0:2]
                    else:
                        uri, query = request, ""

                    # default to index.html
                    if uri == "/":
                        uri = "/index.html"

                    # only GET requests are supported
                    if method != "GET":
                        body = "Sorry, unable to handle " + method + " requests"
                        sendMessage(client, body, 501)

                    # cgi-bin handling - check if script exists
                    elif uri[0:len("/cgi-bin/")] == "/cgi-bin/" and os.path.isfile(CGIBIN + "/" + uri[len("/cgi-bin/"):]):
                        script = CGIBIN + "/" + uri[len("/cgi-bin/"):]

                        env = {
                            "DOCUMENT_ROOT": str(PUBLIC_HTML),
                            "REQUEST_METHOD": str(method),
                            "REQUEST_URI": str(uri),
                            "QUERY_STRING": str(query),
                            "PATH": os.environ["PATH"]
                        }
                        sendScriptOutput(client, script, env)

                    # check if static resource exists
                    elif os.path.isfile(PUBLIC_HTML + "/" + uri):
                        sendFile(client, PUBLIC_HTML + "/" + uri)

                    # send 404
                    else:
                        body = "File '" + uri + "' was not found :("
                        sendMessage(client, body, 404)

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
