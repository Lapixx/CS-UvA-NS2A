import os

body = str(os.environ)

print "Connection: close"
print "Content-Type: text/plain"
print "Content-Length: " + str(len(body))
print ""
print body
