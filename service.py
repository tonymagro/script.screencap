import subprocess
import util
import time
import xbmc
import re

watch = os.path.join(util.cwd, "watch.py")
proc = subprocess.Popen(['python', watch, util.screenshots], stdout=subprocess.PIPE)
util.log("python %s %s" % (watch, util.screenshots))

p = re.compile("^screenshot([0-9]{3})\.png")

while not xbmc.abortRequested:
	time.sleep(1)

proc.terminate()
