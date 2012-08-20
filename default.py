import xbmc, xbmcgui, xbmcaddon
from util import *
import os
import re
import sys
import time
import smtplib
import json
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

sys.path.append(os.path.join(cwd, 'resources'))
from twitpic import TwitPicOAuthClient
import tweepy
 
try:
    Emulating = xbmcgui.Emulating
except:
    Emulating = False

screenpath = xbmc.translatePath("special://screenshots")
p = re.compile("^screenshot([0-9]{3})\.png")

__title__ = ""
def remove_file(path):
    os.remove(path)

__delete_file__ = False
class CapWindow(xbmcgui.WindowDialog):
 
    def __init__(self):

        if Emulating:
            xbmcgui.WindowDialog.__init__(self)

        self.scaleX = self.getWidth()  / 720.0
        self.scaleY = self.getHeight() / 480.0


        self.screenpath = ""

    def onControl(self, control):
        if control == self.button0:
            log("TWEET")
            self.ShowSending()
            post_screen(__title__, self.screenpath)
            self.sending.setLabel("Done")
            self.close()
        elif control == self.button1:
            if self.message("Are you sure?", "Are you sure you want to delete the screenshot? \n%s" % self.screenpath):
                global __delete_file__
                __delete_file__ = True
                self.close()
        elif control == self.button2:
            if self.message("Are you sure?", "Are you sure you want to cancel?"):
                self.close()
        elif control == self.button3:
            if self.message("Are you sure?", "Are you sure you want to tweet then delete the screenshot? \n%s" % self.screenpath):
                global __delete_file__
                __delete_file__ = True
                log("TWEET & DELETE")
                self.ShowSending()
                post_screen(__title__, self.screenpath)
                self.sending.setLabel("Done")
                self.close()

    def message(self, title, message):
        dialog = xbmcgui.Dialog()
        return dialog.yesno(title, message)

    def AddScreen(self, screenpath):
        self.screenpath = screenpath
        self.addControl(xbmcgui.ControlImage(0, 0, 
                                             1280, 
                                             720, 
                                             screenpath))
        self.button0 = xbmcgui.ControlButton(20, 20, 125, 30, "TWEET")
        self.addControl(self.button0)
        self.setFocus(self.button0)
        self.button1 = xbmcgui.ControlButton(145, 20, 125, 30, "DELETE")
        self.addControl(self.button1)
        self.button2 = xbmcgui.ControlButton(270, 20, 125, 30, "EXIT")
        self.addControl(self.button2)
        self.button3 = xbmcgui.ControlButton(20, 55, 250, 30, "TWEET & DELETE")
        self.addControl(self.button3)

        self.button0.controlRight(self.button1)
        self.button0.controlLeft(self.button2)
        self.button1.controlRight(self.button2)
        self.button1.controlLeft(self.button0)
        self.button2.controlRight(self.button0)
        self.button2.controlLeft(self.button1)
        self.button0.controlDown(self.button3)
        self.button0.controlUp(self.button3)
        self.button3.controlUp(self.button0)
        self.button3.controlDown(self.button0)
        '''
        self.addControl(xbmcgui.ControlImage(int(0 * self.scaleX), 
                                             int(23 * self.scaleY), 
                                             int(720 * self.scaleX), 
                                             int(53 * self.scale)Y,
                                             screenpath))
        '''
        self.label = xbmcgui.ControlLabel(20, 675, 
                                          700, 100, 
                                          os.path.basename(screenpath) + ' - ' + __title__, 
                                          'font14', 
                                          '0xFFFFFF00')
        self.addControl(self.label)

    def ShowSending(self):
        self.sending = xbmcgui.ControlLabel(20, 575, 
                                            400, 100, 
                                            "Sending to twitpic...", 
                                            'font14', 
                                            '0xFF00FF00')
        self.addControl(self.sending)


def get_screen():
    hi = 0
    hifile = ""
    for r, d, files in os.walk(screenpath):
        for f in files:
            m = p.match(f)
            if m is None:
                continue
            num = int(m.group(1))
            if num > hi:
                hi = num
                hifile = f

    return os.path.join(screenpath, hifile)


from PIL import Image
def valid_image(filepath):
    try:
        img = Image.open(filepath)
        if img.verify() == False:
            #notify(header="VALIDATING PNG", text="Verify failed", time=1)
            return False
    except IOError, e:
        #notify(header="VALIDATING PNG", text="IOERROR: %s" % e, time=1)
        return False
    except IndexError, e:
        #notify(header="VALIDATING PNG", text="INDEXERROR: %s" % e, time=1)
        return False

    return True
    
def validate_image(filepath):
    for i in range(20):
        if valid_image(newscreen):
            return True
        time.sleep(0.5)

    return False

def twit_pic_by_email(filename, subject=''):
    tp_email = settings.getSetting("twitpic_email")
    smtp_server = settings.getSetting("smtp_server")
    smtp_port = int(settings.getSetting("smtp_port"))
    smtp_use_ssl = settings.getSetting("smtp_use_ssl")

    # Create the container (outer) email message.
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = 'ContShot <contshot@gmail.com>'
    msg['To'] = tp_email
    #msg.preamble = title

    # Open the files in binary mode.  Let the MIMEImage class automatically
    # guess the specific image type.
    fp = open(filename, 'rb')
    img = MIMEImage(fp.read())
    fp.close()
    msg.attach(img)

    # Send the email via our own SMTP server.
    s = smtplib.SMTP(smtp_server, smtp_port)
    s.sendmail('ContShot <contshot@gmail.com>', tp_email, msg.as_string())
    s.quit()

def make_tweet(msg, picurl):
    picurl = " " + picurl
    msg_len = 140 - len(picurl)
    if len(msg) > msg_len:
        msg = msg[:msg_len-1] + u"\u2026"
    return msg + picurl

def js(method, params):
    return json.dumps({
        "jsonrpc" : "2.0",
        "id" : "0",
        "method" : method,
        "params" : params,
    })

def rpc(method, params={}):
    return json.loads(xbmc.executeJSONRPC(js(method,params)))

play_items = [
        "title",
        "artist",
        "albumartist",
        "genre",
        "year",
        "rating",
        "album",
        #"track",
        "duration",
        #"comment",
        #"lyrics",
        #"musicbrainztrackid",
        #"musicbrainzartistid",
        #"musicbrainzalbumid",
        #"musicbrainzalbumartistid",
        #"playcount",
        #"fanart",
        #"director",
        #"trailer",
        #"tagline",
        #"plot",
        #"plotoutline",
        #"originaltitle",
        #"lastplayed",
        #"writer",
        "studio",
        #"mpaa",
        #"cast",
        #"country",
        #"imdbnumber",
        #"premiered",
        #"productioncode",
        #"runtime",
        #"set",
        "showlink",
        #"streamdetails",
        #"top250",
        #"votes",
        "firstaired",
        "season",
        "episode",
        "showtitle",
        "thumbnail",
        "file",
        "resume",
        "artistid",
        "albumid",
        "tvshowid",
        "setid"]

def get_playing():
    result = rpc("Player.GetItem", {"playerid" : 1, "properties": play_items})
    log(result)
    if result.has_key("error"):
        return ""

    if not result.has_key("result"):
        return ""

    item = result['result']['item']
    t = item['type']

    if t == "movie":
        title = item["title"]
        if title != "":
            if item["year"] != 0:
                title += " ("+str(item["year"])+")"
            elif item['studio'] != "":
                title = item['studio'] + " - " + title 
            return title

    if t == "episode":
        showtitle = item["showtitle"]
        label = item['label']
        season = item["season"]
        #episode = item['episode']
        title = item['title']
        if showtitle != "":
            firstaired = item['firstaired']
            if season > 1900 and firstaired != "":
                label = firstaired + " - " + label
            #return "%s - %sx%s - %s" % (showtitle, season, episode, title)
            return "%s - %s" % (showtitle, label)

    label, _ = os.path.splitext(item['label'])
    return label


def post_screen(title, screenpath):
    notify("Tweeting screenshot...")

    consumer_key = settings.getSetting("consumer_key")
    consumer_secret = settings.getSetting("consumer_secret")
    oauth_token = settings.getSetting("oauth_token")
    oauth_token_secret = settings.getSetting("oauth_token_secret")
    service_key = settings.getSetting("service_key")

    # Twitpic
    access_token = "oauth_token=%s&oauth_token_secret=%s"  % (oauth_token, oauth_token_secret)
    twitpic = TwitPicOAuthClient(
        consumer_key = consumer_key,
        consumer_secret = consumer_secret,
        access_token = access_token,
        service_key = service_key,
    )

    # Twitter
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(oauth_token, oauth_token_secret)
    twitter = tweepy.API(auth)

    message = "Peep this"
    if title != "":
        message += " from " + title 

    try:
        response = twitpic.create('upload', {'media': screenpath, 
                                             'message': message})
        #response = {'url': "http://tiny.com/jfdklsjf"}
        tweet = make_tweet(message, response['url'])
        log(tweet)
        twitter.update_status(tweet)
        notify(header="TWEETED: %s" % os.path.basename(screenpath), text=title)
    except Exception, e: 
        log(e)
        response = twit_pic_by_email(screenpath, message)
        notify(header="EMAIL: %s" % os.path.basename(screenpath), text=title)
    log(response)
    return True

if len(sys.argv) < 2:
    xbmc.executebuiltin("TakeScreenshot()")

__title__ = get_playing()
notify(header="SCREEN CAPTURED", text="Verifying Image")
newscreen = ""
if len(sys.argv) < 2:
    time.sleep(0.25)
    newscreen = get_screen()
else:
    newscreen = os.path.join(screenpath, sys.argv[1])

w = CapWindow()
if validate_image(newscreen):
    w.AddScreen(newscreen)
    w.doModal()
else:
    notify("Failed to post: %s" % newscreen)

del w
time.sleep(1)
if __delete_file__:
    remove_file(newscreen)

log("Bye!")

