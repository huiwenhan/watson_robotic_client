#include <iostream>
#include <string>
using namespace std;

#include <cpprest/http_client.h>
#include <cpprest/asyncrt_utils.h>
#include <cpprest/json.h>
using namespace web;
using namespace web::http;
using namespace web::http::client;


pplx::task<vector< unsigned char> > TTS(string input){
  return pplx::create_task([input]{
    http_client client(U("https://stream.watsonplatform.net/text-to-speech/api/v1/synthesize?accept=audio/wav&text="+uri::encode_uri(input)));
    http_request req(methods::GET);
    req.headers().add("Authorization", "Basic YTViYWZjNGMtNjY3OC00MGRiLWJjYzQtMDU1NTUxN2QyODA3OnlXb0NOWjRueXpiNg==");
    pplx::task<http_response> responses = client.request(req);
    pplx::task< std::vector< unsigned char > > wavData = responses.get().extract_vector();

    return wavData.get();
  });
}

int main() {
  vector < unsigned char> wav = TTS("hello world").get();
  cout << wav.size() << endl;

}
