"""Python implementation of the Watson Robotics SDK"""
# This class implements core robotics services provided by Watson
#
# IBM Confidential
# OCO Source Materials
#
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
#
# END_COPYRIGHT

import json
import os
from os.path import expanduser
import requests
import base64
import uuid
import ConfigParser
from ws4py.client.threadedclient import WebSocketClient
from subprocess import Popen, PIPE
import threading
import shlex
import time
import subprocess


class Watson():
    """Watson python service. This makes direct calls to the robot gateway for Watson supported services."""
    def __init__(self, license_key=None):
        self.config = ConfigParser.ConfigParser()
        self.config.read(expanduser("~") + "/" + "config.ini")
        self.license = None
        self.stt_ws = None
        self.conversation_ws = None

        try:
            self.license = json.loads(open(expanduser("~") + "/" + self.config.get('WATSON', 'LICENSE'), 'r+').read())
            #self.key = self.get_key()
            #self.mac_id = self.get_mac_id()
            #self.client_url = self.get_gateway_URL()
            self.initialize_license()
            self.ttspath = expanduser("~") + "/" + self.config.get('WATSON', 'AUDIO_OUTPUT_PATH')
            self.audio_path = expanduser("~") + "/" + self.config.get('WATSON', 'AUDIO_INPUT_PATH')
            self.personality_id = ''
        except:
            if self.license == None and license_key == None:
                print "Please provide your ROBOT_KEY which is present in your activation email."
                return
            elif self.license == None and license_key is not None:
                self.validate_license(license_key)
            else:
                raise RuntimeError(self.config.get('WATSON', 'LICENSE_ERROR'))
                
    def initialize_license(self):
        self.license = json.loads(open(expanduser("~") + "/" + self.config.get('WATSON', 'LICENSE'), 'r+').read())
        self.key = self.get_key()
        self.mac_id = self.get_mac_id()
        self.client_url = self.get_gateway_URL()
        self.gateway_socket_URL = self.get_gateway_socket_URL()


    def initialize_chat(self, instance_id):
        """Initializes a client for a dialog instance in Cognea. It also sets a Chat id for subsequent calls to ask.
        :param instance_id: The Cognea instance that you want to hit."""
        self.personality_id = instance_id
        # get chat ID
        init_chat_resp = self.invoke_get({'Content-Type':'application/json'}, 'initDialog', params = {'id' : instance_id})
        init_chat_resp = cleanResponseString(init_chat_resp)
        try:
            init_response = json.loads(init_chat_resp)
            self.chat_id = init_response['id']
            return self.chat_id, str(init_response['response'].encode('utf-8'))
        except (IOError, IndexError) as err:
            raise RuntimeError('Error getting the Chat ID: {}'.format(err))

    def ask(self, query, instance_id=None, chat_id=None):
        """Make conversational query to Watson dialog with the chat that has been initialized.
        initialize_chat must be called first.
        :param query: The sentence to be sent to Cognea/dialog"""
        local_personality_id = 0
        if (chat_id == None):
            chat_id = self.chat_id
        if( instance_id != None):
            local_personality_id = instance_id
        else:
            local_personality_id = self.personality_id

        result = self.invoke_get({'Content-Type':'application/json'}, 'askDialog', params = { 'text':query, 'id':local_personality_id, 'chatID':chat_id})
        response = cleanResponseString(result)
        response = json.loads(result)
        response = response["response"]
        return str(response.encode('utf-8'))
        
    def watson_engagement_advisor(self, text):
        """Make a translation post. This translates something from one language to another intelligently
        :param text: The block of text to be translated
        :param languageFrom: The language that the text is currently in (origin language, or base language)
        :param languageTo: The destination language for the text
        :param headers: Additional headers that are passed in for the call
        :param params: Additional parameters that are passed in for the call"""
        #body, success = self.body_check(text, ValueError)
        #if not success:
        #    return self.translate_easy(text,languageFrom,languageTo)
        #merged_headers = merge_dicts(headers, {'Content-Type':'application/json', 'Service-Type':'language-translation'})
        body = {"question":{"questionText":text,"evidenceRequest":{"items":3,"profile":"no"},"formattedAnswer":"true"}}
        body = json.dumps(body)
        print body
        headers = {'Content-Type':'application/json', 'Service-Type':'WATSON_ENGAGEMENT_ADVISOR'}
        response = self.invoke_post(headers=headers, params=None, body=body, files = None, serviceName='WATSON_ENGAGEMENT_ADVISOR').content
        #print response
        return cleanResponseString(response)        

    def thunderstone(self, query):
        """Sends a question to the thunderstone pipeline
        :param query: The question to be answered by thunderstone"""
        headers = {'Service-Type':'thunderstone','Content-Type':'application/json'}
        response=self.invoke_post(headers = headers, params = None, body = query, files = None, serviceName = 'thunderstone')
        response = response.content
        response = cleanResponseString(response)
        return response

    def stt(self, headers = None, params = None):
        """Sets up a call to bluemix speech to text using a wav file generated by the robot.
        It needs to be stored at the location specified by AUDIO_INPUT_PATH (self.audio_path)"""
        # if (params != None):
            # params = json.dumps(params).strip()
        with open(self.audio_path, "rb") as fd:
            encoded_string = base64.b64encode(fd.read())
        merged_headers = merge_dicts(headers,{'Service-Type':'stt'})
        try:
            response = self.invoke_post(headers=merged_headers, params=params, body=encoded_string, files = None, serviceName='stt').json()
        except ValueError, TypeError:
            print "Failure to parse STT JSON"
        return response

    def stt_stream(self, headers = None, params = None):
        """Sets up a call to the stt websocket and streams audio for one question/sentence at a time"""
        try:
            service_map = self.config.get('WATSON', 'SERVICE_MAP')
            service_map = json.loads(service_map)
            ws = STTWebSocket('{}/{}'.format(self.gateway_socket_URL , service_map['stt-stream'] ))
            ws.set_credentials("{\"MAC_ID\":\""+self.mac_id+"\",\"ROBOT_KEY\":\""+self.key+"\",\"Service-Type\":\"stt-stream\"}")
            ws.connect()
            ws.run_forever()
        except KeyboardInterrupt:
            ws.close()
        return ws.get_response()

    def stt_stream_all(self, headers = None, params = None):
        try:
            print "IN ALL!"
            service_map = self.config.get('WATSON', 'SERVICE_MAP')
            service_map = json.loads(service_map)
            if self.stt_ws is not None:
                self.stt_ws.close()
            self.stt_ws = STTWebSocketAll('{}/{}'.format(self.gateway_socket_URL , service_map['stt-stream'] ))
            self.stt_ws.set_credentials("{\"MAC_ID\":\""+self.mac_id+"\",\"ROBOT_KEY\":\""+self.key+"\",\"Service-Type\":\"stt-stream\", \"continuous\":true, \"interim\":true}")
            self.stt_ws.connect()
            self.stt_ws.stay_alive()
        except KeyboardInterrupt:
            self.stt_ws.close()

    def stt_stream_all_continue(self, headers = None, params = None):
        print "IN CONTINUE!"
        self.stt_ws.continue_stream()
        return self.stt_ws.get_response()

    def stt_stream_all_close(self, headers = None, params = None):
        print "CLOSEING WEB SOCKET!"
        self.stt_ws.close()

    def conversation_stream(self, headers = None, params = None):
        """Sets up a call to stt websocket and streams audio for one questions/sentence at a time to conversation API"""
        try:
            service_map = self.config.get('WATSON', 'SERVICE_MAP')
            service_map = json.loads(service_map)
            self.conversation_ws = ConversationWebSocketAll('{}/{}'.format(self.gateway_socket_URL, service_map['stt-stream'] ))
            self.conversation_ws.set_credentials("{\"MAC_ID\":\""+self.mac_id+"\",\"ROBOT_KEY\":\""+self.key+"\",\"Service-Type\":\"conversation-text-in-stream\"}")
            self.conversation_ws.connect()           
        except KeyboardInterrupt:
            self.conversation_ws.close()
        return self.conversation_ws.get_greeting()

    def conversation_stream_continue(self, headers = None, params = None):
        print "IN CONTINUE"
        self.conversation_ws.continue_stream()
        return self.conversation_ws.get_response()

    def conversation_stream_close(self, headers = None, params = None):
        print "CLOSING WEB SOCKET"
        self.conversation_ws.stop_stream()
        self.conversation_ws.close()       

    def image_tagging(self, imagePath, headers=None, params=None):
        """Sets up a call to alchemy image tagging using a jpg photo taken by the robot)"""
        with open(imagePath) as f:
            encoded_string = base64.b64encode(f.read())
        merged_headers = merge_dicts(headers,{'Service-Type':'image-tagging'})
        merged_params = merge_dicts(params,{'outputMode':'json'})
        content = self.invoke_post(headers=merged_headers, params=merged_params, body=encoded_string, files= None, serviceName = 'image-tagging')
        response = cleanResponseString(content.text)
        try:
            response = json.loads(response)
        except:
            print "Failure to parse Image Tagging JSON"
        return response


    def tts(self, text, voice = None, headers = None, params = None):
        """Sets up a call to bluemix text to speech. This returns an audio file from bluemix, and
        it must be played by the robot. It is at the location specified by AUDIO_OUTPUT_PATH
        (self.ttspath)
        :param text: The text to be turned into speech
        :param voice: The voice used to speak the text. These voices are specified by Bluemix.
        :param headers: Additional headers that are passed in for the call
        :param params: Additional parameters that are passed in for the call"""
        merged_headers = merge_dicts(headers, {'Content-Type':'application/json', 'Service-Type':'tts'})
        if params == None:
            params = {'accept':'audio/wav'}
        else:
            params['accept'] = 'audio/wav'
        if voice != None:
            params['voice'] = voice
        folderPath = self.ttspath[:self.ttspath.rfind('/')]
        if not os.path.exists(folderPath):
            os.makedirs(folderPath)
        if os.path.isfile(self.ttspath):
            os.remove(self.ttspath)
        payload = json.dumps({'text': text})
        data = self.invoke_post(headers=merged_headers, params=params, body=payload, files = None, serviceName='tts').content
        data=bytearray(data)
        with open(self.ttspath,'wb') as tts_file:
            tts_file.write(data)

    def personality(self, body, headers=None,params=None):
        """Make a personality insights post. It analyses a block of text to determine personality traits.
        This requires at least 100 words to be sent in 'body', but around 2000 are recommended.
        :param body: The block of text to be sent to Watson for personality evaluation
        :param headers: Additional headers that are passed in for the call
        :param params: Additional parameters that are passed in for the call"""
        body, success = self.body_check(body, ValueError)
        if not success:
            body=json.dumps({"contentItems":[{"content": body }]})
        merged_headers = merge_dicts(headers, {'Content-Type':'application/json', 'Service-Type':'personality-insights'})
        response = self.invoke_post(headers=merged_headers, params=params, body=body, files = None, serviceName='personality-insights').content
        response = cleanResponseString(response)
        return response
        
    def sentiment_analysis(self, body, headers=None,params=None):
        # print self.config.get('WATSON', 'SERVICE_MAP')
        """Make a Sentiment analysis post. It analyses a block of text to determine text sentiment
            :param body: The block of text to be sent to Watson for personality evaluation
            :param headers: Additional headers that are passed in for the call
            :param params: Additional parameters that are passed in for the call"""
        params = merge_dicts( {"outputMode":"json"},params)
        merged_headers = merge_dicts(headers, {'Service-Type':'sentiment-analysis'})
        response = self.invoke_post(headers=merged_headers, params=params, body=body, files = None, serviceName='sentiment-analysis').json()
        return response

    def natural_language_train(self, files, headers=None, params=None):
        """ Train natural language classifier, look at blue mix for necessary file params"""
        merged_headers = merge_dicts(headers, {'Service-Type':'natural-language-train', 'Content-Type':'application/json'})
        response = self.invoke_post(headers=merged_headers, params=params, body=None, files=files, serviceName='natural-language-train').content
        response = cleanResponseString(response)
        return json.loads(response)

    def natural_language_classify(self, text, params, headers=None):
        """classify a string of text given the provided classifier_id (which is set in the params dict"""
        merged_headers = merge_dicts(headers, {'Service-Type':'natural-language-classify', 'Content-Type':'application/json'})
        payload = json.dumps({'text': text})
        return self.invoke_post(headers=merged_headers, params=params, body=payload, files=None, serviceName='natural-language-classify').content

    def natural_language_list(self, params = None, headers = None):
        """list the classifiers associated with the account"""
        merged_headers = merge_dicts(headers, {'Service-Type','natural-language-classifier-list'})
        return self.invoke_post(headers=merged_headers, params=params, body=None, files=None, serviceName='natural-language-classifier-list').json()

    def natural_language_delete(self, headers=None, params=None):
        """Delete a natural language classifier"""
        #params = merge_dicts(params,{'classifier_id':classifier_id})
        headers = merge_dicts(headers,{'Service-Type':'natural-language-delete'})
        content = self.invoke_post(headers=headers, params=params,body=None,files=None,serviceName='natural-language-delete').text
        content = content[content.index('{'): content.rfind('}')+1]
        response_json = ""
        try:
            response_json = json.loads(content)
        except ValueError :
            response_json = content
            return False
        if(json.dumps(response_json) == '{}'):
            return True
        else:
            return False

    def dialog_create(self, body, dialog_name, headers=None, params=None):
        """ Creates a dialog instance given a dialog.xml file
        :param body: dialog file content"""
        merged_headers = merge_dicts(headers, {'Service-Type':'dialog-create', 'Content-Type':'application/json'})
        params = merge_dicts(params,{'name':dialog_name})
        response = self.invoke_post(headers=merged_headers, params=params, body=body, files=None, serviceName='dialog-create').content
        response = cleanResponseString(response)
        return json.loads(response)

    def dialog_initiate(self, headers=None, params=None):
        """ Initiates an instance of dialog. It should return the conversation_id and the client_id
        :param dialog_id: The dialog_id that returns from the dialog_create method call
        :param headers: Additional headers that are passed in for the call
        :param params: Additional parameters that are passed in for the call
        returns json response object containing a conversation_id and a client_id"""
        merged_headers = merge_dicts(headers, {'Service-Type':'dialog-service', 'Content-Type':'application/x-www-form-urlencoded'})
        #params = merge_dicts(params,{'dialog_id':dialog_id})
        response = self.invoke_post(headers=merged_headers, params=params, body=None, files=None, serviceName='dialog-service').content
        return response


    def dialog_converse(self, client_id, conversation_id, input_question, service_name='dialog-service', headers=None, params=None):
        """ Used to asks questions. It returns the answer to the question.
        :param dialog_id: The dialog_id that return from the dialog_create method
        :param client_id: The client_id that return from the dialog_initiate method
        :param conversation_id: The conversation_id that return from the dialog_initiate method
        :param input_question: The question itself
        :param headers: Additional headers that are passed in for the call
        :param params: Additional parameters that are passed in for the call
        returns json reponse object containing the answer"""
        merged_headers = merge_dicts(headers, {'Service-Type':'dialog-service', 'Content-Type':'application/x-www-form-urlencoded'})
        params = merge_dicts(params,{'client_id':client_id, 'conversation_id':conversation_id, 'input':input_question})
        response = self.invoke_post(headers=merged_headers, params=params, body=None, files=None, serviceName='dialog-service').content
        response = cleanResponseString(response)
        return response


    def dialog_delete(self, dialog_id, headers=None, params=None):
        """Deletes a dialog instance"""
        #params = merge_dicts(params,{'dialog_id':dialog_id})
        headers = merge_dicts(headers,{'Service-Type':'dialog-delete'})
        content = self.invoke_post(headers=headers, params=params,body=None,files=None,serviceName='dialog-delete').text
        content = content[content.index('{'): content.rfind('}')+1]
        response_json = ""
        try:
            response_json = json.loads(content)
        except ValueError :
            response_json = content
            return False
        if(json.dumps(response_json) == '{}'):
            return True
        else:
            return False
            
    def conversation_text_in_initiate(self, headers=None, params=None):
        """ Initiates an instance of dialog. It should return the conversation_id and the client_id
        :param dialog_id: The dialog_id that returns from the dialog_create method call
        :param headers: Additional headers that are passed in for the call
        :param params: Additional parameters that are passed in for the call
        returns json response object containing a conversation_id and a client_id"""
        merged_headers = merge_dicts(headers, {'Service-Type':'conversation-text-in', 'Content-Type':'application/json', 'Accept':'application/json', 'user_token':'adsf'})
        response = self.invoke_post(headers=merged_headers, params=params, body=None, files=None, serviceName='conversation-text-in').content
        return response
        
    def conversation_text_in_converse(self, conversation_id, body, headers=None, params=None):
        """ Initiates an instance of dialog. It should return the conversation_id and the client_id
        :param dialog_id: The dialog_id that returns from the dialog_create method call
        :param headers: Additional headers that are passed in for the call
        :param params: Additional parameters that are passed in for the call
        returns json response object containing a conversation_id and a client_id"""
        params = merge_dicts(params,{'conversation_id':conversation_id})
        merged_headers = merge_dicts(headers, {'Service-Type':'conversation-text-in', 'Content-Type':'application/json', 'Accept':'application/json', 'user_token':'adsf'})
        response = self.invoke_post(headers=merged_headers, params=params, body=body, files=None, serviceName='conversation-text-in').content
        return response

    def tradeoff(self, body, headers=None,params=None):
        """Make a tradeoff analytics post on Bluemix. It analyzes many choices to help determine which
        option is the best given various tradeoffs.
        :param body: Specially formatted table-like json to query Watson
        :param headers: Additional headers that are passed in for the call
        :param params: Additional parameters that are passed in for the call"""
        body, success = self.body_check(body, ValueError)
        if not success:
            raise RuntimeError(self.config.get('WATSON', 'TRADEOFF_ERROR'))
        merged_headers = merge_dicts(headers, {'Content-Type':'application/json', 'Service-Type':'tradeoff-analytics'})
        return self.invoke_post(headers=merged_headers, params=params, body=body, files = None, serviceName='tradeoff-analytics').content

    def language_id(self, body, headers = None, params=None):
        merged_headers = merge_dicts(headers,{'Service-Type':'language-id'})
        return self.invoke_post(headers = merged_headers, params=params, body=body, files=None, serviceName='language-id').content

    def translate(self, text, languageFrom=None, languageTo=None, headers=None, params=None):
        """Make a translation post. This translates something from one language to another intelligently
        :param text: The block of text to be translated
        :param languageFrom: The language that the text is currently in (origin language, or base language)
        :param languageTo: The destination language for the text
        :param headers: Additional headers that are passed in for the call
        :param params: Additional parameters that are passed in for the call"""
        body, success = self.body_check(text, ValueError)
        if not success:
            return self.translate_easy(text,languageFrom,languageTo)
        merged_headers = merge_dicts(headers, {'Content-Type':'application/json', 'Service-Type':'language-translation'})
        response = self.invoke_post(headers=merged_headers, params=params, body=body, files = None, serviceName='language-translation').content
        return cleanResponseString(response)

    def translate_easy(self, text, languageFrom, languageTo):
        """Helper for translation that formats the body string if it is given as plain text
        :param text: The block of text to be translated
        :param languageFrom: The language that the text is currently in (origin language, or base language)
        :param languageTo: The destination language for the text"""
        english = self.config.get('WATSON', 'LANGUAGE_TRANSLATION_ENGLISH').split(",")
        spanish = self.config.get('WATSON', 'LANGUAGE_TRANSLATION_SPANISH').split(",")
        french = self.config.get('WATSON', 'LANGUAGE_TRANSLATION_FRENCH').split(",")
        portuguese = self.config.get('WATSON', 'LANGUAGE_TRANSLATION_PORTUGUESE').split(",")
        arabic = self.config.get('WATSON', 'LANGUAGE_TRANSLATION_ARABIC').split(",")
        text = unicode(text,'utf-8')
        if languageFrom.lower() in english:
            if languageTo.lower() in spanish:
                payload = {'model_id': self.config.get('WATSON', 'LANGUAGE_TRANSLATION_ENGLISH_TO_SPANISH'), 'text': text}
            elif languageTo.lower() in french:
                payload = {'model_id': self.config.get('WATSON', 'LANGUAGE_TRANSLATION_ENGLISH_TO_FRENCH'), 'text': text}
            elif languageTo.lower() in portuguese:
                payload = {'model_id': self.config.get('WATSON', 'LANGUAGE_TRANSLATION_ENGLISH_TO_PORTUGUESE'), 'text': text}
            elif languageTo.lower() in arabic:
                payload = {'model_id': self.config.get('WATSON', 'LANGUAGE_TRANSLATION_ENGLISH_TO_ARABIC'), 'text':text}
            else:
                return self.config.get('WATSON', 'LANGUAGE_TRANLATION_ERROR_ENGLISH')
        elif languageFrom.lower() in spanish:
            if languageTo.lower() in english:
                payload = {'model_id': self.config.get('WATSON', 'LANGUAGE_TRANSLATION_SPANISH_TO_ENGLISH'), 'text': text, }
            else:
                return self.config.get('WATSON', 'LANGUAGE_TRANLATION_ERROR_SPANISH')
        elif languageFrom.lower() in french:
            if languageTo.lower() in english:
                payload = {'model_id': self.config.get('WATSON', 'LANGUAGE_TRANSLATION_FRENCH_TO_ENGLISH'), 'text': text}
            else:
                return self.config.get('WATSON', 'LANGUAGE_TRANLATION_ERROR_FRENCH')
        elif languageFrom.lower() in portuguese:
            if languageTo.lower() in english:
                payload = {'model_id': self.config.get('WATSON', 'LANGUAGE_TRANSLATION_PORTUGUESE_TO_ENGLISH'), 'text': text}
            else:
                return self.config.get('WATSON', 'LANGUAGE_TRANLATION_ERROR_PORTUGUESE')
        elif languageFrom.lower() in arabic:
            if languageTo.lower() in english:
                payload = {'model_id': self.config.get('WATSON', 'LANGUAGE_TRANSLATION_ARABIC_TO_ENGLISH'), 'text': text}
            else:
                return self.config.get('WATSON', 'LANGUAGE_TRANLATION_ERROR_ARABIC')
        else:
            return self.config.get('WATSON', 'LANGUAGE_TRANLATION_ERROR_ALL')

        headers = {'Content-type': 'application/json','Service-Type':'language-translation'}
        payload = json.dumps(payload)
        return self.invoke_post(headers=headers, params=None, files=None, body=payload, serviceName='language-translation').content

    def body_check(self, body, exception_type):
        """Helper to check if a string is formatted correctly for the REST call
        :param body: The body, or text that is being sent to a REST service
        :param exception_type: The type of exception that you want to catch"""
        if isinstance(body,dict):
            body=json.dumps(body)
        else:
            try:
                json.loads(body)
            except exception_type:
                return body, False
        return body, True
        
    def heartbeat(self):
        """It requests a command to be executed.
        :param headers: Headers that are passed in for the call"""
        headers = {'Content-Type':'application/json', 'Service-Type':'heartbeat','MAC_ID':self.get_mac_id(),'ROBOT_KEY': self.get_key()}
        url = '{}/{}'.format(self.client_url, "heartbeat")
        response = requests.get(url, verify=False, headers=headers, params=None).text
        return response
        
    def get_audio_output_path(self):
        """Getter for tts_response path. This returns the path for audio output."""
        return self.ttspath

    def get_audio_input_path(self):
        """Getter for tts_response path. This returns the path for audio output."""
        return self.audio_path

    def get_key(self):
        """Extracts the robot key from a license file. It is used when sending data to the gateway to ensure the robot is registered."""
        return self.license['ROBOT_KEY']

    def get_mac_id(self):
        """Extracts the mac id from the robot. It is used when sending data to the gateway to ensure the robot is registered."""
        mac = uuid.getnode()
        return ':'.join('%02X' % ((mac >> 8*i) & 0xff) for i in reversed(xrange(6))).encode('ascii', 'ignore')

    def get_gateway_URL(self):
        """Extracts the Gateway URL from the license file. This is the location of the gateway to send calls to."""
        return self.license['ROBOT_GATEWAY_URL']

    def get_gateway_socket_URL(self):
        """Extracts the Gateway Socket URL from the license file. This is the location of the gateway to send calls to."""
        return self.license['ROBOT_GATEWAY_SOCKET_URL']

    def invoke_post(self, headers, serviceName, body=None, params = None, files = None):
        """Universal method to format a post request
        :param headers: Headers used in the post call
        :param body: The text being posted
        :param serviceName: The service that is being called
        :param params: Parameters for the post call"""
        # Url Generation
        service_map = self.config.get('WATSON', 'SERVICE_MAP')
        service_map = json.loads(service_map)
        url = '{}/{}'.format(self.client_url, service_map[serviceName])
        
        # Adding in ROBOT_KEY and MAC_ID header 
        headers = self.createHeaders(headers)
        
        return requests.request('POST', url, verify=False, headers=headers, data=body, params=params, files=files)

    def invoke_get(self, headers, serviceName, params = None):
        """Universal method to format a get request
        :param headers: Headers used in the get call
        :param serviceName: The service that is being called
        :param params: Parameters for the get call"""
        # Url Generation:
        service_map = self.config.get('WATSON', 'SERVICE_MAP')
        service_map = json.loads(service_map)
        url = '{}/{}'.format(self.client_url, service_map[serviceName])
        
        # Adding in ROBOT_KEY and MAC_ID header 
        headers = self.createHeaders(headers)
        
        return requests.get(url, verify=False, headers=headers, params=params).text

    def invoke_simple_post(self, headers, serviceName, body=None, params = None, files = None):
        """Simple post method to validate and get content for license.wat file
        :param headers: Headers used in the post call
        :param body: The text being posted
        :param serviceName: The service that is being called
        :param params: Parameters for the post call"""
        service_map = self.config.get('WATSON', 'SERVICE_MAP')
        service_map = json.loads(service_map)
        url = '{}/{}'.format(self.client_url, service_map[serviceName])
        return requests.request('POST', url, verify=False, headers=headers, data=body, params=params, files=files)

    def validate_license(self, robotKey):
        """Sends the robot key and receives back the content for the license.wat file. Then saves the file
        to home/.watson
        :param robotKey: The robot key"""
        headers = {'Content-Type':'application/json'}
        robotKey = '{"ROBOT_KEY":"'+robotKey+'"}'
        folderPath = expanduser("~") + "/.watson"
        response=self.invoke_simple_post(headers = headers, params = None, body = robotKey, files = None, serviceName = 'initClient')

        if not os.path.exists(folderPath):
            try:
                os.makedirs(folderPath)
            except (IOError) as err:
                raise RuntimeError('Error creating .watson directory: {}'.format(err))
        try:
            f = open(folderPath+'/license.wat','w')
            f.write(response.content)
            f.close()
        except (IOError) as err:
            raise RuntimeError('Error writing license key to file license.wat: {}'.format(err))

    def createHeaders(self, additional_headers):
        """Helper method to construct common headers
        :param additional_headers: Headers to be added to the normal set of headers used in calls"""
        mergedHeaders = merge_dicts(additional_headers, {'MAC_ID':self.mac_id,'ROBOT_KEY': self.key})
        return mergedHeaders

class STTWebSocket(WebSocketClient):

    response = ''
    credentials = ''

    def set_thread(self):
        #print "Entering set_thread"
        self.t = threading.Thread(target=self.stream_thread)

    def set_credentials(self, credentials):
        self.credentials = credentials
    
    def set_stop_flag(self, stop_flag):
        self.stop_flag = stop_flag    
    
    def set_response(self, response):
        self.response = response

    def get_credentials(self):
        return self.credentials

    def get_response(self):
        return self.response

    def closed(self, code, reason=None):
        print "Closed down", code, reason

    def received_message(self, m):
        reply = json.loads(str(m))  
        
        if 'results' in reply.keys():
            self.set_stop_flag(True)
            #print "Stop Flag should be True it is: {}".format(self.stop_flag)
            #print "Stoping the Thread"
            self.t.join()
            self.set_response(reply)
            print "-----------------STT Streaming Socket Now Closed-----------------"

            self.close()

    def opened(self):
        #print "Entering opened"
        print "-----------------STT Streaming Socket Now Open-----------------"
        self.set_thread()
        self.set_stop_flag(False)
        #print "Stop Flag should be False it is: {}".format(self.stop_flag)
        self.send(self.get_credentials())
        self.t.start()

    def stream_thread(self):
        #print "Entering stream_thread"

        reccmd = ["arecord", "-f", "S16_LE", "-r", "16000" ] #, "-c", "1", "-t", "raw"]
        p = subprocess.Popen(reccmd, stdout=subprocess.PIPE) 
        iterator = iter(p.stdout.readline, b"")
        while p.poll() is None:
            for line in iterator:
                try:
                    if(line != None and line != "" ):
                        self.send(line, binary=True)
                    if( self.stop_flag == True):
                        self.stop_flag == False
                        #print "killing the process"
                        p.kill()
                        return
                except Exception:
                    return
        #print "killing the process"        
        p.kill()
        return

class STTWebSocketAll(WebSocketClient):

    response = ''
    credentials = ''
    listening = False

    def set_credentials(self, credentials):
        self.credentials = credentials
    
    def set_stop_flag(self, stop_flag):
        self.stop_flag = stop_flag    
    
    def set_response(self, response):
        self.response = response

    def get_credentials(self):
        return self.credentials

    def get_response(self):
        return self.response

    def closed(self, code, reason=None):
        print "Closed down", code, reason

    def continue_stream(self):
        self.set_stop_flag(False)
        print "streaming audio"
        self.stream_thread()
        print "done streaming audio!"

    def stay_alive(self):
        self.t = threading.Thread(target=self.send_noop_thread)
        #self.t.start()

    def send_noop_thread(self):
        counter = 0
        print "setting up stay alive thread"
        while True:
            time.sleep(2)
            if(counter == 20):
                noop = {}
                noop["action"] = "no-op"
                print "Sending: " + str(noop)
                self.send(str(noop))
                counter = 0
            else:
                counter = counter + 2


    def received_message(self, m):
        reply = json.loads(str(m)) 
        print str(reply) 

        if 'state' in reply.keys():
            print "LISTENING NOW!"
            self.listening = True
        elif 'error' in reply.keys():
            print "RECEIVED ERROR!"
            self.set_stop_flag(True)
            self.set_response(reply)
            self.kill = True
        elif not reply['results']:
            print "Reply was empty!!"
            self.set_stop_flag(True)
            self.set_response(reply)
            self.listening = False
        elif reply['results'][0]['final'] is True:           
            #print "Stop Flag should be True it is: {}".format(self.stop_flag)
            #print "Stoping the Thread"
            self.set_stop_flag(True)
            self.set_response(reply)           
            self.listening = False
#            time.sleep(3)
#            action = {}
#            action['action'] = 'stop'
#            print "SENDING: " + str(action)

    def opened(self):
        #print "Entering opened"
        print "-----------------STT Streaming Socket Now Open-----------------"
        self.kill = False
#        self.set_thread()
#        self.set_stop_flag(False)
        #print "Stop Flag should be False it is: {}".format(self.stop_flag)
        self.send(self.get_credentials())
#        self.t.start()

    def stream_thread(self):
        #print "Entering stream_thread"
        reccmd = ["arecord", "-f", "S16_LE", "-r", "16000" ] #, "-c", "1", "-t", "raw"]
        p = subprocess.Popen(reccmd, stdout=subprocess.PIPE)
        print "PID: " + str(p.pid)
        iterator = iter(p.stdout.readline, b"")
        counter = 0
        while p.poll() is None:
            for line in iterator:
                try:
                    if self.kill == True:
                        print "KILLING AUDIO"
                        p.kill()
                        return
                    if(line != None and line != "" and self.listening == True):
                        self.send(line, binary=True)
                    if( self.stop_flag == True):
                        self.stop_flag == False
                        action = {}
                        action['action'] = 'stop'
                        print "SENDING: " + str(action)
                        self.send(str(action))
                        #print "killing the process"
                        p.kill()
                        print "DONE SENDING AUDIO IN FOR LOOP!"
                        return
                except Exception:
                    return
            if( self.stop_flag == True):
                self.stop_flag == False
                #print "killing the process"
                p.kill()
                print "DONE SENDING AUDIO OUTSIDE OF FOR LOOP!"
                return
        #print "killing the process"        
        p.kill()
        return       

class ConversationWebSocketAll(WebSocketClient):

    response = ''
    credentials = ''
    greeting = None
    greeting_flag = True

    def set_credentials(self, credentials):
        self.credentials = credentials
    
    def set_stop_flag(self, stop_flag):
        self.stop_flag = stop_flag    
    
    def set_response(self, response):
        self.response = response

    def get_credentials(self):
        return self.credentials

    def get_response(self):
        return self.response

    def set_greeting(self, greeting):
        print "setting greeating to: " + str(greeting)
        self.greeting = greeting

    def get_greeting(self):
        print self.greeting
        print str(self.greeting_flag)
        while self.greeting is None and self.greeting_flag == True:
            time.sleep(1)
            print str(self.greeting)
        return ""

    def get_greeting_flag(self):
        return self.greeting_flag

    def closed(self, code, reason=None):
        print "Closed down", code, reason

    def stop_stream(self):
        self.greeting_flag = False

    def continue_stream(self):
        self.set_stop_flag(False)
        print "streaming audio"
        self.stream_thread()
        print "done streaming audio!"

    def stay_alive(self):
        self.t = threading.Thread(target=self.send_noop_thread)
        #self.t.start()

    def send_noop_thread(self):
        counter = 0
        print "setting up stay alive thread"
        while True:
            time.sleep(2)
            if(counter == 20):
                noop = {}
                noop["action"] = "no-op"
                print "Sending: " + str(noop)
                self.send(str(noop))
                counter = 0
            else:
                counter = counter + 2


    def received_message(self, m):
        reply = json.loads(str(m)) 
        print "REPLY: " + str(reply) 


        if 'error' in reply.keys():
            print "RECEIVED ERROR!"
            self.set_stop_flag(True)
            self.set_response(reply)
            self.kill = True
        elif 'warn' in reply.keys():
            print "RECEIVED ERROR!"
            self.set_stop_flag(True)
            self.set_response(reply)
            self.kill = True
        elif 'greeting' in reply.keys():
            print "Initial Response"
            self.set_stop_flag(True)
            self.set_greeting(reply)
            self.listening = False
        elif 'state' in reply.keys():
            print "LISTENING NOW!"
            self.listening = True
        elif reply['responses'][0]['text'] is not None:           
            #print "Stop Flag should be True it is: {}".format(self.stop_flag)
            #print "Stoping the Thread"
            self.set_stop_flag(True)
            self.set_response(reply)           
            self.listening = False


    def opened(self):
        #print "Entering opened"
        print "-----------------Conversation STT Streaming Socket Now Open-----------------"
        self.kill = False

#        self.set_thread()
#        self.set_stop_flag(False)
        #print "Stop Flag should be False it is: {}".format(self.stop_flag)
        self.send(self.get_credentials())
#        self.t.start()

    def stream_thread(self):
        #print "Entering stream_thread"
        reccmd = ["arecord", "-f", "S16_LE", "-r", "16000" ] #, "-c", "1", "-t", "raw"]
        p = subprocess.Popen(reccmd, stdout=subprocess.PIPE)
        print "PID: " + str(p.pid)
        iterator = iter(p.stdout.readline, b"")
        counter = 0
        while p.poll() is None:
            for line in iterator:
                try:
                    if self.kill == True:
                        print "KILLING AUDIO"
                        p.kill()
                        return
                    if(line != None and line != "" and self.listening == True):
                        self.send(line, binary=True)
                    if( self.stop_flag == True):
                        self.stop_flag == False
                        action = {}
                        action['action'] = 'stop'
                        print "SENDING: " + str(action)
                        self.send(str(action))
                        print "killing the process"
                        p.kill()
                        print "DONE SENDING AUDIO IN FOR LOOP!"
                        return
                    if(self.listening != True):
                        print "NEVER RECEIVED LISTENING!"
                        error = {}
                        error['error'] = 'never received listening state' 
                        self.set_response(error)
                        self.stop_flag == False
                        action = {}
                        action['action'] = 'stop'
                        self.send(str(action))
                        p.kill()
                        return
                except Exception:
                    return
            if( self.stop_flag == True):
                self.stop_flag == False
                #print "killing the process"
                p.kill()
                print "DONE SENDING AUDIO OUTSIDE OF FOR LOOP!"
                return
        #print "killing the process"        
        p.kill()
        return       

def cleanResponseString(response):
    response = response.strip()
    response = response.encode('latin-1')
    response = response.replace('\n','')
    return response[response.index('{'): response.rfind('}')+1]

def merge_dicts(x,y):
    """Merges two dictionaries together (appends one to the other)
    :param x: The first dictionary to be merged
    :param y: The second dictionary to be merged"""
    if x == None and y == None:
        return None
    elif x == None:
        return y
    elif y == None:
        return x
    z = x.copy()
    z.update(y)
    return z


        #cmd = '/usr/bin/arecord -f S16_LE -r 16000 -c 1 -t raw'
        #process = Popen(shlex.split(cmd), stdout=PIPE)
        #print str(process)
        #iterator = iter(process.stdout.readline, b"")
        #while process.poll() is None:

