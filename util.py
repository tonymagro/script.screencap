import xbmc, xbmcaddon
import os

settings   = xbmcaddon.Addon(id='script.screencap')
cwd        = settings.getAddonInfo('path')
icon       = os.path.join(cwd,"icon.png")
scriptname = "Screen Capture"
screenshots= xbmc.translatePath("special://screenshots")

def log(text):
	xbmc.log("!!%s!!: %s" % (scriptname.upper(),text))

def notify(text, time=5, icon=icon, header=scriptname):
	if text is None:
		return
	xbmc.executebuiltin("XBMC.Notification(%s,%s,%s,%s)" % (header,text,time*1000,icon))


