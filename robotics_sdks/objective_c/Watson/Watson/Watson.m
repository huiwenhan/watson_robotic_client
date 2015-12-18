//
//  Watson.m
//  Watson
//
//  Created by Alex Gerome on 7/24/15.
//  Objective-C implementation of the Watson Robotics SDK
//  This class implements core robotics services provided by Watson
//
//  IBM Confidential
//  OCO Source Materials
//
//  5727-I17
//  (C) Copyright IBM Corp. 2001, 2015 All Rights Reserved.
//
//  The source code for this program is not published or otherwise
//  divested of its trade secrets, irrespective of what has been
//  deposited with the U.S. Copyright Office.
//
//  END_COPYRIGHT

#import <Foundation/Foundation.h>
#import "Watson.h"

////Extension for private variables
//@interface Watson ()
//
//@property (nonatomic) NSDictionary *serviceMap;
//
//@end


@implementation Watson

-(instancetype)init
{
    self = [super init];
    if (self){
        //initialization of properties goes here
//        self.config = ConfigParser.ConfigParser()
//        self.config.read(expanduser("~") + "/" + "/config.ini")
//        
//        try:
//          self.license = json.loads(open(expanduser("~") + "/" + self.config.get('WATSON', 'LICENSE'), 'r+').read())
//        except:
//        raise RuntimeError(self.config.get('WATSON', 'LICENSE_ERROR'))
//        self.mac_id = self.get_mac_id()
//        self.key = self.get_key()
//        self.client_url = self.get_gateway_URL()
//        
//        self.ttspath = expanduser("~") + "/" + self.config.get('WATSON', 'AUDIO_OUTPUT_PATH')
//        self.audio_path = expanduser("~") + "/" + self.config.get('WATSON', 'AUDIO_INPUT_PATH')
        self.personality_id = @"";

        self.mac_id = @"00:13:95:12:f1:02";//self.get_mac_id()
        self.key = @"5be8f142-2107-11e5-b5f7-727283247c7f";//self.get_key()
        self.client_url = @"http://75.126.4.99:8091/RobotGateway/en"; //self.get_gateway_URL()

    }
    return self;
}

-(NSString *)initialize_chat:(NSString *)instance_id
{
    self.personality_id = instance_id;
    NSString *init_chat_resp = [self invoke_get:@{@"Content-Type":@"application/json"} service: @"initDialog" params:@{@"id" : instance_id}];
    
    NSError *error = nil;
    NSDictionary *init_response = [NSJSONSerialization
                                   JSONObjectWithData:[init_chat_resp dataUsingEncoding:NSUTF8StringEncoding]
                                   options:0
                                   error:&error];
    
    self.chat_id = init_response[@"id"];
    return init_response[@"response"];
}

-(NSString *)ask:(NSString *)query
{
//    result = self.invoke_get({'Content-Type':'application/json'}, 'askDialog', params = { 'text':query, 'id':self.personality_id, 'chatID':self.chat_id})
//    response = json.loads(result)
//    response = response["response"]
//    return str(response.encode('utf-8'))
    NSString *result = [self invoke_get:@{@"Content-Type":@"application/json"} service: @"askDialog" params:@{@"text":query, @"id":self.personality_id, @"chatID":self.chat_id}];
    
    NSError *error = nil;
    NSDictionary *response = [NSJSONSerialization
                                   JSONObjectWithData:[result dataUsingEncoding:NSUTF8StringEncoding]
                                   options:0
                                   error:&error];
    return response[@"response"];
}

-(NSString *)thunderstone:(NSString *)query
{
    NSDictionary *mergedHeaders = [self createHeaders:@{@"Content-Type":@"application/json", @"Service-Type":@"thunderstone"}];
    return [self invoke_post:mergedHeaders body:query service:@"thunderstone" params:nil];
}

-(NSString *)stt
{
//    with open(self.audio_path, "rb") as fd:
//    encoded_string = base64.b64encode(fd.read())
//    response = self.invoke_post(headers={'Service-Type':'stt'}, params=None, body=encoded_string, serviceName='stt')
//    response = response.text
//    response = response.encode('utf-8')
//    response = response.replace('\n','')
//    response = response.replace('  ','')
//    response = response[3:-3]
//    response = json.loads(response)
//try:
//    response = str(response["results"][0]["alternatives"][0]["transcript"])
//except:
//    response = self.config.get('WATSON', 'STT_ERROR_JSON')
//    return response
    return @"TODO";
}

-(void)tts:(NSString *)text voice:(NSString *)voice headers:(NSDictionary *)headers params:(NSDictionary *)params
{
    return;
}

-(NSString *)personality:(NSString *)body headers:(NSDictionary *)headers params:(NSDictionary *)params
{
    NSString *text = [NSString stringWithFormat:@"{\"contentItems\": [{\"content\": \"%@\"}]}", body];
//    NSLog(@"%@", text);
    NSDictionary *mergedHeaders = [self createHeaders:@{@"Content-Type":@"application/json", @"Service-Type":@"personality-insights"}];
    return [self invoke_post:mergedHeaders body:text service:@"personality-insights" params:params];
}

-(NSString *)tradeoff:(NSString *)body headers:(NSDictionary *)headers params:(NSDictionary *)params
{
    NSDictionary *mergedHeaders = [self createHeaders:@{@"Content-Type":@"application/json", @"Service-Type":@"tradeoff-analytics"}];
    return [self invoke_post:mergedHeaders body:body service:@"tradeoff-analytics" params:params];
}

-(NSString *)translate:(NSString *)text from:(NSString *)languageFrom to:(NSString *)languageTo headers:(NSDictionary *)headers params:(NSDictionary *)params
{
    NSDictionary *mergedHeaders = [self createHeaders:@{@"Content-Type":@"application/json", @"Service-Type":@"language-translation"}];
    return [self invoke_post:mergedHeaders body:text service:@"language-translation" params:params];
}

-(NSString *)translate_easy:(NSString *)text from:(NSString *)languageFrom to:(NSString *)languageTo
{
    return @"TODO";
}

-(NSString *)body_check:(NSString *)body except:(NSString *)exceptionType
{
    return @"TODO";
}

//ADD PARAMS?, FIX NSBUNDLE
-(NSString *)invoke_post:(NSDictionary *)headers body:(NSString *)body service:(NSString *)serviceName params:(NSDictionary *)params
{
//    //Format URL
//    NSString *services = [@"~/Desktop/Watson/" stringByExpandingTildeInPath];//[[NSBundle mainBundle] pathForResource:@"config" ofType:@"plist"];
//    NSDictionary *serviceMap = [[NSDictionary alloc] initWithContentsOfFile:services];
//    NSLog(@"%@, %@, %@", services, serviceName, [serviceMap objectForKey:serviceName]);
    NSString *fullURL = [NSString stringWithFormat:@"%@/%@", self.client_url,  @"service"];//[serviceMap objectForKey:serviceName]];
    
    //Format Post Request
    NSData* responseData = nil;
    NSURL* url = [NSURL URLWithString:fullURL];
    responseData = [NSMutableData data] ;
    NSMutableURLRequest *request=[NSMutableURLRequest requestWithURL:url];
    [request setHTTPMethod:@"POST"];
    
    //Add standard headers
    //    [request setValue:[headers objectForKey:key] forHTTPHeaderField:key];
    //Add custom headers
    for(id key in headers){
        //NSLog(@"key=%@ value=%@", key, [headers objectForKey:key]);
        [request setValue:[headers objectForKey:key] forHTTPHeaderField:key];
    }
    //Set the body text
    NSData* data = [body dataUsingEncoding:NSUTF8StringEncoding];
    [request setHTTPBody:data];
    //Send the request
    NSData *req=[NSData dataWithBytes:[body UTF8String] length:[body length]];
    [request setHTTPBody:req];
    NSURLResponse* response;
    NSError* error = nil;
    responseData = [NSURLConnection sendSynchronousRequest:request   returningResponse:&response error:&error];
    NSString *responseString = [[NSString alloc] initWithData:responseData encoding:NSUTF8StringEncoding];
    return responseString;
}

-(NSString *)invoke_get:(NSDictionary *)headers service:(NSString *)serviceName params:(NSDictionary *)params
{
    
//    //Format URL
//    NSString *services = [@"~/Desktop/Watson/" stringByExpandingTildeInPath];//[[NSBundle mainBundle] pathForResource:@"config" ofType:@"plist"];
//    NSDictionary *serviceMap = [[NSDictionary alloc] initWithContentsOfFile:services];
//    NSLog(@"%@", services);
    NSString *url = [NSString stringWithFormat:@"%@/%@", self.client_url, serviceName];//[serviceMap objectForKey:serviceName]];
    NSMutableURLRequest *request = [[NSMutableURLRequest alloc] init];


    //Add params
    NSURLComponents *components = [NSURLComponents componentsWithString:url];//@"http://stackoverflow.com"];
    NSMutableArray *parameters = [NSMutableArray array];
    for (NSString *key in params) {
        [parameters addObject:[NSURLQueryItem queryItemWithName:key value:params[key]]];
    }
    components.queryItems = parameters;
    NSString* fullURL = [components.URL absoluteString];
    
    //headers
    NSMutableDictionary *additionalHeaders = [NSMutableDictionary dictionaryWithDictionary:headers];
    additionalHeaders[@"MAC_ID"] = self.mac_id;
    additionalHeaders[@"ROBOT_KEY"] = self.key;
    for(id key in additionalHeaders){
        [request setValue:[additionalHeaders objectForKey:key] forHTTPHeaderField:key];
    }
    
    [request setHTTPMethod:@"GET"];
    [request setURL:[NSURL URLWithString:fullURL]];
    NSError *error = [[NSError alloc] init];
    NSHTTPURLResponse *responseCode = nil;
    
    NSData *oResponseData = [NSURLConnection sendSynchronousRequest:request returningResponse:&responseCode error:&error];
    NSString *response = [[NSString alloc] initWithData:oResponseData encoding:NSUTF8StringEncoding];
    
    return response;
}

-(NSDictionary *)createHeaders:(NSDictionary *)additionalHeaders
{
    NSMutableDictionary *headers = [NSMutableDictionary dictionaryWithDictionary:additionalHeaders];
    headers[@"MAC_ID"] = self.mac_id;
    headers[@"ROBOT_KEY"] = self.key;
    return headers;
}

@end