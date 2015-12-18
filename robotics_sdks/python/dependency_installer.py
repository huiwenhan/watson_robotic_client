import naoqi
import socket
from naoqi import ALModule
from naoqi import ALProxy
from naoqi import ALBroker
import qi
import os
import urllib2

NAO_IP = str(socket.gethostname()) + '.local'
NAO_PORT = 9559

try:
	beh = ALProxy("ALBehaviorManager",NAO_IP,NAO_PORT)	  
except Exception, e:
	print "Error when creating proxy on ALBehaviorManager"
	print str(e)
	exit(1)
	
try:
    tts = ALProxy("ALTextToSpeech",NAO_IP,NAO_PORT)
except Exception, e:
	print "Error when creating proxy on ALTextToSpeech"
	print str(e)
	exit(1)

def check_connectivity():
    try:
        response=urllib2.urlopen('http://www.google.com',timeout=1)
        return True
    except urllib2.URLError as err: pass
    return False

def is_pepper(session=None):
    """Return True if robot is Pepper, False otherwise."""
    if not session:
        session = qi.Session()
        session.connect('localhost')
    motion = session.service('ALMotion')
    return 'juliette' in motion.getRobotConfig()[1][0]

def loadDependecies():
    try:
        import pip
        pip.main(['install', '--user', 'ws4py'])
        #os.system('pip install --user ws4py')
        tts.say("Finished installing 3 of 4")
        import ws4py
    except:
        tts.say("Problem with installing 3 of 4.")
        return False #activate the output of the box
    print "Ws4py installed sucessfully."

    try:
        import pip
        pip.main(['install', '--user', 'requests'])
        #os.system('pip install --user requests')
        tts.say("Finished installing 4 of 4")
        import requests
    except:
        tts.say("Problem with installing 4 of 4.")
        return False #activate the output of the box
    print "requests installed sucessfully."


""" Main """
if check_connectivity() == False:
    tts.say("I cannot see the internet. Your installation may fail. I will continute to install as much as I can. But please get me connected and then reinstall me.")	
loadDependecies()
