import signal
import fcntl
import os
import re
import sys
import urllib2

p = re.compile("^screenshot([0-9]{3})\.png")

host = "localhost"
port = 8080

def notify_newfile(filename):
	url = 'http://%s:%s/xbmcCmds/xbmcHttp?command=ExecBuiltIn(Runscript(script.screencap,%s))' % (host, port, filename)
	print url
	try:
		urllib2.urlopen(url)
	except Exception, e:
		print e

# service.py will read standard input
#def notify_newfile(filename):
#	print filename

class DirectoryNotifier:
	def __init__(self, dirname):
		if not os.path.isdir(dirname):
			raise RuntimeError, "you can only watch a directory."
		self.dirname = dirname
		self.fd = os.open(dirname, 0)
		self.currentcontents = os.listdir(dirname)
		self.oldsig = fcntl.fcntl(self.fd, fcntl.F_GETSIG)
		fcntl.fcntl(self.fd, fcntl.F_SETSIG, 0)
		fcntl.fcntl(self.fd, fcntl.F_NOTIFY, fcntl.DN_DELETE|fcntl.DN_CREATE|fcntl.DN_MULTISHOT)

	def __del__(self):
#		fcntl.fcntl(self.fd, fcntl.F_SETSIG, self.oldsig)
		os.close(self.fd)
	
	def __str__(self):
		return "%s watching %s" % (self.__class__.__name__, self.dirname)

	# there are lots of race conditions here, but we'll live with that for now.
	def __call__(self, frame):
		newcontents = os.listdir(self.dirname)
		if len(newcontents) > len(self.currentcontents):
			new = filter(lambda item: item not in self.currentcontents, newcontents)
			self.entry_added(new)
		elif len(newcontents) < len(self.currentcontents):
			rem = filter(lambda item: item not in newcontents, self.currentcontents)
			self.entry_removed(rem)
		else:
			self.no_change()
		self.currentcontents = newcontents

	# override these in a subclass
	def entry_added(self, added):
		print added, "added to", self.dirname
		for f in added:
			m = p.match(f)
			if m == None:
				continue
			notify_newfile(f)
			time.sleep(1)

	def entry_removed(self, removed):
		print removed, "removed from", self.dirname

	def no_change(self):
		print "No change in", self.dirname

class SIGIOHandler:
	def __init__(self):
		self.handlers = []
		self.on()
	
	def on(self):
		signal.signal(signal.SIGIO, self)

	def off(self):
		signal.signal(signal.SIGIO, signal.SIG_DFL)

	def register(self, callback):
		self.handlers.append(callback)
		return len(self.handlers) - 1 # the handle

	def unregister(self, handle=0):
		if self.handlers:
			del self.handlers[handle]

	def __call__(self, sig, frame):
		for h in self.handlers:
			h(frame)

import time
try:
	manager
except NameError:
	manager = SIGIOHandler()

screenpath = sys.argv[1]
dn = DirectoryNotifier(screenpath)
manager.register(dn)
while True:
	time.sleep(60)
