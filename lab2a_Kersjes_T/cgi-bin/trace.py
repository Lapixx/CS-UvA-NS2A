import os
import subprocess

# split the query parameters
queryString = os.environ["QUERY_STRING"]
queryPairs = queryString.split("&")
params = {}
for x in queryPairs:
    y = x.split("=")
    if len(y) < 2:
        continue
    params[y[0]] = y[1]

if "ip" in params:
    opts = ["-w", "1", "-q", "1"]
    output = str(subprocess.check_output(["traceroute"] + opts + [params["ip"]]))
else:
    output = "IP missing"

print "Connection: close"
print "Content-Type: text/plain"
print "Content-Length: " + str(len(output))
print ""
print output
