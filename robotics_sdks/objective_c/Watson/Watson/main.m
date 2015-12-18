//
//  main.m
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

int main(int argc, const char * argv[]) {
    @autoreleasepool {
        NSLog(@"Hello, World!");
        
        Watson *watson = [[Watson alloc] init];

//        NSString *body = @"{\"model_id\": \"en-es\", \"text\":[\"Fred is still alive\"] }";
//        NSLog(@"%@",[watson translate:body from:nil to:nil headers:nil params:nil]);
//        NSLog(@"%@", [watson thunderstone:@"What is the capital of Texas?"]);
//        NSLog(@"%@", [watson personality:@"know that we shall join with them to oppose aggression or subversion anywhere in the Americas And let every other power know that this Hemisphere intends to remain the master of its own house. To that world assembly of sovereign states, the United Nations, our last best hope in an age where the instruments of war have far outpaced the instruments of peace, we renew our pledge of support to prevent it from becoming merely a forum for invective to strengthen its shield of the new and the weak and to enlarge the area in which its writ may run. Finally, to those nations who would make themselves our adversary we offer not a pledge but a request that both sides begin anew the quest for peace, before the dark powers of destruction unleashed by science engulf all humanity in planned or accidental self destruction. We dare not tempt them with weakness For only when our arms are sufficient beyond doubt can we be certain beyond doubt that they will never be employed" headers:nil params:nil]);
//        NSLog(@"%@", [watson tradeoff:<?> headers:nil params:nil]);
//        NSLog(@"%@", [watson invoke_get:@{@"Content-Type":@"application/json"} service: @"initDialog" params:@{@"id" : @"48"}]);
//---------------------
        //GET
//        NSString *url = [NSString stringWithFormat: @"%@/%@", [watson client_url], @"initDialog?id=48"];
//        NSMutableURLRequest *request = [[NSMutableURLRequest alloc] init];
//        [request setHTTPMethod:@"GET"];
//        [request setURL:[NSURL URLWithString:url]];
//        
//        NSError *error = [[NSError alloc] init];
//        NSHTTPURLResponse *responseCode = nil;
//        
//        NSData *oResponseData = [NSURLConnection sendSynchronousRequest:request returningResponse:&responseCode error:&error];
//        
//        NSLog(@"%@", [[NSString alloc] initWithData:oResponseData encoding:NSUTF8StringEncoding]);
//
//        NSLog(@"%@",[watson initialize_chat:@"48"]);
//        NSLog(@"%@",[watson ask:@"Where are the elevators?"]);
        
        
    }
    return 0;
}
