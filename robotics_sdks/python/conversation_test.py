from ws4py.client.threadedclient import WebSocketClient

def main():
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