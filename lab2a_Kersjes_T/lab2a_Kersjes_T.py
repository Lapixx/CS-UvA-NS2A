"""
Netwerken en Systeembeveiliging Lab 2A - HTTP and SMTP
NAME:
STUDENT ID:
DESCRIPTION:
"""

# This is just an example of how you could implement the server. You may change
# this however you wish. For example, you could do a really nice object oriented
# version if you like.
def serve(port, public_html, cgibin):
	"""
	The entry point of the HTTP server.
	port: The port to listen on.
	public_html: The directory where all static files are stored.
	cgibin: The directory where all CGI scripts are stored.
	"""
	pass

# This the entry point of the script.
# Do not change this part.
if __name__ == '__main__':
	import os, sys, argparse
	p = argparse.ArgumentParser()
	p.add_argument('--port', help='port to bind to', default=8080, type=int)
	p.add_argument('--public_html', help='home directory', default='./public_html')
	p.add_argument('--cgibin', help='cgi-bin directory', default='./cgi-bin')
	args        = p.parse_args(sys.argv[1:])
	public_html = os.path.abspath(args.public_html)
	cgibin      = os.path.abspath(args.cgibin)
	serve(args.port, public_html, cgibin)
