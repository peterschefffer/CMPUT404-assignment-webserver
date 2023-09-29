#  coding: utf-8 
import socketserver

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip().decode()
        #print ("Got a request of: %s\n" % self.data)
        #self.request.sendall(bytearray("OK",'utf-8'))
        re = self.parse_request()
        self.fulfill_request(re)

    def fulfill_request(self, re):
        # Test for non-get request
        if re[0] != 'GET':
            self.send_405(re)
        
        file_path_header = 'www'
        file_path = re[1]
        final_file_path = file_path_header + file_path
        if 'www/www/' in final_file_path:
            final_file_path = final_file_path[4:]

        if 'etc' in final_file_path or 'group' in final_file_path:
            self.send_404(re)

        if final_file_path[-1] == '/':
                final_file_path = final_file_path + 'index.html'
                f = open(final_file_path)
                body = f.read()
                f.close()
                self.send_html(body, re)
        else:
            try:
                f = open(final_file_path)
                body = f.read()
                f.close()
                extension = final_file_path.split('.')[-1]
                if extension == 'css':
                    self.send_css(body, re)
                elif extension == 'html':
                    self.send_html(body, re)         
            except FileNotFoundError:
                self.send_404(re)
            except IsADirectoryError:
                self.send_301(re, final_file_path)
    
    def send_css(self, body, re):
        protocol = re[2].strip('\r')
        code = ' 200'
        mess = ' Ok'
        header = protocol + code + mess + '\n'
        content = 'Content-Type: text/css\n'
        header += content + '\n'
        final_send = header + body
        self.request.send(final_send.encode())
    
    def send_html(self, body, re):
        protocol = re[2].strip('\r')
        code = ' 200'
        mess = ' Ok'
        header = protocol + code + mess + '\n'
        content = 'Content-Type: text/html\n'
        header += content + '\n'
        final_send = header + body
        self.request.send(final_send.encode())

    def send_404(self, re):
        protocol = re[2].strip('\r')
        code = ' 404'
        mess = ' Not Found'
        header = protocol + code + mess
        header = header.encode()
        self.request.send(header)
    
    def send_405(self, re):
        protocol = re[2].strip('\r')
        code = ' 405'
        mess = ' Not Allowed'
        header = protocol + code + mess
        header = header.encode()
        self.request.send(header)
    
    def send_301(self, re, file_path):
        protocol = re[2].strip('\r')
        code = ' 301'
        mess = ' Moved Permanently'
        header = protocol + code + mess + '\n'
        body = 'Location: ' + file_path + '/'
        body = body[4:]
        final_message = header + body +'\n'
        self.request.send(final_message.encode())
    
    def parse_request(self):
        request = self.data.split('\n')
        request = request[0]
        req_data = request.split(' ')
        return req_data


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
