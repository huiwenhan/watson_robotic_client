"""watson.py Naoqi service to connect to query IBM Watson instances."""
#(c) Copyright IBM Corp. 2015  All Rights Reserved.
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.

import os
import qi
import socket
import collections
import time
import sys
from optparse import OptionParser
import watson
import json
import threading

try:
    from naoqi import ALModule
    from naoqi import ALProxy
    from naoqi import ALBroker

except ImportError, err:
    print "Error when creating proxy:"
    print str(err)
    raise err
    exit(1)

NAO_IP = socket.gethostname() + '.local'
NAO_PORT = 9559
ALWatson = None
audio = None
camera = None

class ALWatson(ALModule):
    """Watson NAOqi service."""
    def __init__(self, name):
        ALModule.__init__(self,name)
        try:
            global audio
            audio = ALProxy("ALAudioPlayer",NAO_IP, NAO_PORT)
            global camera
            camera = ALProxy("ALPhotoCapture", NAO_IP, NAO_PORT)
        except Exception, e:
            print "Error when creating proxy on ALAudioPlayer:"
            print str(e)
            exit(1)
        self.watson = watson.Watson()
    
    def initialize_chat(self, instance_id):
        return self.watson.initialize_chat(instance_id)

    def ask(self, query):
        return self.watson.ask(query)

    def stt(self):
        response = self.unicode_dict_to_string_dict(self.watson.stt())
        return response
    
    def stt_stream(self):
        s = self.watson.stt_stream()
        s1 = json.dumps(s)
        return s1

    def stt_stream_all_init(self):
        s = self.watson.stt_stream_all()
        return ""

    def stt_stream_all_continue(self):
        s = self.watson.stt_stream_all_continue()
        s1 = json.dumps(s)
        return s1

    def conversation_stream(self):
        print "HIT!"
        s = self.watson.conversation_stream()
        s1 = json.dumps(s)
        return s1
    
    def conversation_stream_continue(self):
        s = self.watson.conversation_stream_continue()
        s1 = json.dumps(s)
        return s1

    def conversation_stream_close(self):
        s = self.watson.conversation_stream_close()
        return ""

    def stt_stream_all_close(self):
        s = self.watson.stt_stream_all_close()
        return ""
        
    def unicode_dict_to_string_dict(self, data):
        if isinstance(data, basestring):
            return str(data)
        elif isinstance(data, collections.Mapping):
            return dict(map(self.unicode_dict_to_string_dict, data.iteritems()))
        elif isinstance(data, collections.Iterable):
            return type(data)(map(self.unicode_dict_to_string_dict, data))
        else:
            return data
            
    def watson_engagement_advisor(self, text):
        return self.watson.watson_engagement_advisor(text)    
    
    def natural_language_classify(self, text, params, headers=None):
        return self.watson.natural_language_classify(text, params, headers)
    
    def natural_language_train(self, files, headers=None, params=None):
        return self.watson.natural_language_train(files, headers, params)
    
    def natural_language_list(self, text, params, headers=None ):
        return self.watson.natural_language_list(text, params, headers)
    
    def natural_language_delete(self, headers=None, params=None):
        return self.watson.natural_language_delete(headers, params)

    def dialog_create(self, files, dialog_name, headers=None, params=None):
        return self.watson.dialog_create(files, dialog_name, headers, params)

    def dialog_initiate(self, headers=None, params=None ):
        return self.watson.dialog_initiate(headers, params)
        
    def dialog_converse(self, client_id, conversation_id, input_question, headers=None, params=None):
        return self.watson.dialog_converse(client_id, conversation_id, input_question, headers, params)
    
    def dialog_delete(self, headers=None, params=None):
        return self.watson.dialog_delete(headers, params)
        
    def conversation_text_in_initiate(self, headers=None, params=None):
        return self.watson.conversation_text_in_initiate(headers, params)        
        
    def conversation_text_in_converse(self, conversation_id, body, headers=None, params=None):
        return self.watson.conversation_text_in_converse(conversation_id, body, headers=None, params=None)  
        
    """REMOVE THISS"""
    def robot_sees(self):
        global camera
        camera.setResolution(2)
        camera.setCameraID(1)
        camera.setPictureFormat("jpg")
        camera.takePicture( '/home/nao/recordings/cameras','image.jpg')
        try:
            response = self.watson.image_tagging('/home/nao/recordings/cameras/image.jpg', headers=None, params=None)['imageKeywords']
        except:
            response = None
        if response == None or response == []:
            return "I don't see anything"
        else:
            return str(response [0]['text'])

    def image_tagging(self, imagePath, headers = None, params = None):
        return self.watson.image_tagging(imagePath, headers=None, params=None)
    
    def tts(self, text, voice = None, headers = None, params = None):
        self.watson.tts(text, voice, headers, params)
        global audio
        audio.playFile(self.watson.get_audio_output_path())
        
    def personality(self, body, headers=None,params=None):
        return self.watson.personality(body, headers, params)
    
    def thunderstone(self,query):
        return self.watson.thunderstone(query)
        
    def tradeoff(self, body, headers=None,params=None):
        return self.watson.tradeoff(body, headers, params)

    def translate(self, text, languageFrom=None, languageTo=None, headers=None, params=None):
        return self.watson.translate(text, languageFrom, languageTo, headers, params)

    def heartbeat(self):
        return self.watson.heartbeat()
         
def main():
    """ Main entry point

    """
    parser = OptionParser()
    parser.add_option("--pip",
        help="Parent broker port. The IP address or your robot",
        dest="pip")
    parser.add_option("--pport",
        help="Parent broker port. The port NAOqi is listening to",
        dest="pport",
        type="int")
    parser.set_defaults(
        pip=NAO_IP,
        pport=NAO_PORT)

    (opts, args_) = parser.parse_args()
    pip   = opts.pip
    pport = opts.pport

    # We need this broker to be able to construct
    # NAOqi modules and subscribe to other modules
    # The broker must stay alive until the program exists
    myBroker = ALBroker("myBroker",
       "0.0.0.0",   # listen to anyone
       0,           # find a free port and use it
       pip,         # parent broker IP
       pport)       # parent broker port


    # Warning: Watson must be a global variable
    # The name given to the constructor must be the name of the
    # variable
    global ALWatson
    ALWatson = ALWatson("ALWatson")
    beh = ALProxy("ALBehaviorManager")
    
    try:
        while True:
            time.sleep(5)
            command = ALWatson.heartbeat()
            if "wave" in str(command):
                beh.runBehavior("animations/Stand/Gestures/Hey_1")
            continue

    except KeyboardInterrupt:
        print
        print "Interrupted by user, shutting down"
        myBroker.shutdown()
        sys.exit(0)

if __name__ == "__main__":
    main()