"""Python implementation of the Watson Robotics SDK"""
# -*- coding: utf-8 -*-
# This class implements core robotics services provided by Watson
#
# IBM Confidential
# OCO Source Materials
#
# 5727-I17
# (C) Copyright IBM Corp. 2001, 2015 All Rights Reserved.
#
# The source code for this program is not published or otherwise
# divested of its trade secrets, irrespective of what has been
# deposited with the U.S. Copyright Office.
#
# END_COPYRIGHT

import json
import os
from os.path import expanduser
import requests
import ConfigParser
import uuid



class Version():
    """This class is responsible for checking if the client version matches the version of the sdk available."""
    def __init__(self, license_key=None):
        self.config = ConfigParser.ConfigParser()
        self.config.read(expanduser("~") + "/" + "/config.ini")
        self.license = None
        
        try:
            self.license = json.loads(open(expanduser("~") + "/" + self.config.get('WATSON', 'LICENSE'), 'r+').read())
            self.key = self.get_key()
            self.mac_id = self.get_mac_id()
            self.client_url = self.get_gateway_URL()
            self.version = self.get_sdk_version()
        except:
            if self.license == None and license_key == None:
                print "Please provide your ROBOT_KEY which is present in your activation email."
                return
            elif self.license == None and license_key is not None:
                self.validate_license(license_key)
            else:
                raise RuntimeError(self.config.get('WATSON', 'LICENSE_ERROR'))

    def get_version(self):
        """Sends a request to the backend to get the current SDK version"""
        self.personality_id = instance_id
        try:
            init_response = json.loads(init_chat_resp)
            self.chat_id = init_response['id']
            return self.invoke_post(headers=merged_headers, params=params, body=None, files = None).content
        except (IOError, IndexError) as err:
            raise RuntimeError('Error getting the Chat ID: {}'.format(err))

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

    def get_sdk_version(self):
        """Extracts the Gateway Socket URL from the license file. This is the location of the gateway to send calls to."""
        return self.config.get('WATSON', 'SDK_VERSION') 

    def invoke_post(self, url, headers, body=None, params = None, files = None):
        """Universal method to format a post request
        :param headers: Headers used in the post call
        :param body: The text being posted
        :param serviceName: The service that is being called
        :param params: Parameters for the post call"""
        headers = self.createHeaders(headers)
        return requests.request('POST', url, verify=False, headers=headers, data=body, params=params, files=files)


    def createHeaders(self, additional_headers):
        """Helper method to construct common headers
        :param additional_headers: Headers to be added to the normal set of headers used in calls"""
        if additional_headers == None:
        	return  {'MAC_ID': self.mac_id,'ROBOT_KEY': self.key}
        mergedHeaders = merge_dicts(additional_headers, {'MAC_ID':str(self.mac_id),'ROBOT_KEY': str(self.key)})
        
        return mergedHeaders
        
    def download_watson_sdk(self):
        home = expanduser("~")
        license = json.loads( open(home+'/'+'.watson/license.wat', 'r+').read() )
        key = license['ROBOT_KEY']
        mac_id = self.get_mac_id()
        client_url = license['ROBOT_GATEWAY_URL']

        watson_path = home+'/watson.py'
        alwatson_path = home+'/alwatson.py'
        config_path = home+'/config.ini'
        
        url = client_url + '/file'
        headers = {"ROBOT_KEY": key, "MAC_ID":mac_id}
        watson_payload = json.dumps({"filename":"watson.py"})
        alwatson_payload = json.dumps({"filename":"alwatson.py"})
        config_payload = json.dumps({"filename":"config.ini"})
        watson_data = self.invoke_post(url, headers, watson_payload, None, None)
        alwatson_data = self.invoke_post(url, headers, alwatson_payload, None, None)
        config_data = self.invoke_post(url, headers, config_payload, None, None)
		        
        self.write_string_file(watson_path, watson_data.content)
        self.write_string_file(alwatson_path, alwatson_data.content)
        self.write_string_file(config_path, config_data.content)
    def write_string_file(self, filename, data):
        text_file = open(filename, "w")
        text_file.write(data)
        text_file.close()

def main():
    v = Version()
    headers = v.createHeaders(None)
    currentVersion = v.invoke_post(v.get_gateway_URL()+'/version', headers)
    if (v.get_sdk_version() != str(currentVersion)):
         v.download_watson_sdk()

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

if __name__ == '__main__':
    main()
