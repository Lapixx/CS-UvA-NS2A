import os
import sys
import urllib
import socket
import ssl
import base64

# helper function to send back data to client
def sendData(data):
    output = str(data)
    print "Connection: close"
    print "Content-Type: text/plain"
    print "Content-Length: " + str(len(output))
    print ""
    print output

def getResponse(sock, expectedCode=""):
    data = sock.recv(1024)
    lines = data.split("\n")
    parts = lines[len(lines) - 2].split(" ") # get last line
    code = parts[0]
    message = " ".join(parts[1:])

    if expectedCode != "" and code != expectedCode:
        handleError(code, message)

    return code, message

def handleError(code, message):
    sendData("Failed (" + code + "): " + message)
    sys.exit(1)

# split the query parameters
queryString = os.environ["QUERY_STRING"]
queryPairs = queryString.split("&")
PARAMS = {}
for x in queryPairs:
    y = x.split("=")
    if len(y) < 2:
        continue
    key = urllib.unquote_plus(y[0])
    value = urllib.unquote_plus(y[1])
    PARAMS[key] = value

# check required fields
requiredFields = ["from", "to", "server", "username", "password", "subject", "body"]
for k in requiredFields:
    if not k in PARAMS:
        sendData("Required field '" + k + "' missing")
        sys.exit(0)

HOST = PARAMS["server"]
PORT = 587

# connect to server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect((HOST, PORT))
code, msg = getResponse(server, "220")

# identify
server.sendall("HELO mail.divbyzero.nl\n")
code, msg = getResponse(server, "250")

# start secure connection
server.sendall("STARTTLS\n")
code, msg = getResponse(server, "220")

serverSecure = ssl.wrap_socket(server, ssl_version=ssl.PROTOCOL_TLSv1)
serverSecure.sendall("EHLO mail.divbyzero.nl\n")
code, msg = getResponse(serverSecure, "250")

# authenticate
serverSecure.sendall("AUTH LOGIN\n")
code, msg = getResponse(serverSecure, "334")
serverSecure.sendall(base64.b64encode(PARAMS["username"]) + "\n")
code, msg = getResponse(serverSecure, "334")
serverSecure.sendall(base64.b64encode(PARAMS["password"]) + "\n")
code, msg = getResponse(serverSecure, "235")

# start building message headers
serverSecure.sendall("MAIL FROM: <" + PARAMS["from"] + ">\n")
code, msg = getResponse(serverSecure, "250")
serverSecure.sendall("RCPT TO: <" + PARAMS["to"] + ">\n")
code, msg = getResponse(serverSecure, "250")

# start message
serverSecure.sendall("DATA\n")
code, msg = getResponse(serverSecure, "354")

serverSecure.sendall("subject: " + PARAMS["subject"] + "\n")
for line in PARAMS["body"].split("\n"):
    serverSecure.sendall(line + "\n")
serverSecure.sendall(".\n")
code, msg = getResponse(serverSecure, "250")

# return server confimation message to client
sendData(msg)

# close the connection
serverSecure.sendall("QUIT\n")
code, msg = getResponse(serverSecure, "221")
serverSecure.close()
