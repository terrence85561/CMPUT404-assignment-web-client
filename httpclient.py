#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
from urllib.parse import urlparse,urlencode

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = int(code)
        self.body = body
        print('the body is:\r\n',body)
        

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):

        return data.split()[1]

    def get_headers(self,data):
        #print(data)
        header = data.split("\r\n\r\n")[0]
        
        return header

    def get_body(self, data):
        body = data.split("\r\n\r\n")[1]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        decode_method = self.get_charset(buffer)
        return buffer.decode(decode_method)

    def GET(self, url, args=None):
        # call url parser to get information of url
        scheme,host_name,port,path = self.urlparser(url)
        #print('scheme:{}; host_name:{}; port:{}; path:{}'.format(scheme,host_name,port,path))
        try:
            # create a socket object, begins connection
            self.connect(host_name,port)
            
            # create payload
            payload = self.make_payload(host_name,port,path,method = "GET")
            # send payload
            self.sendall(payload)

            # receive data
            data = self.recvall(self.socket)

        except Exception as e:
            print(str(e))
            code = 404
            
            return HTTPResponse(code = code)
        
        finally:
            print('closing connection')
            self.close()
        
        
        header = self.get_headers(data)
        code = self.get_code(header)
        body = self.get_body(data)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        # call url parser to get information of url
        scheme,host_name,port,path = self.urlparser(url)
        
        # get vars in args
        if args != None:
            args = urlencode(args)
            #print('the variables in post request body are %s'%args)
        
        try:
            # create a socket object,begins connection
            self.connect(host_name,port)

            #create payload
            payload = self.make_payload(host_name,port,path,method="POST",args=args)
            
            self.sendall(payload)
            # receive data
            data = self.recvall(self.socket)
            #print(data)
        except Exception as e:
            print(str(e))
            code = 404
            return HTTPResponse(code = code)

        finally:
            self.close()
        # print(data)
        header = self.get_headers(data)
        code = self.get_code(header)
        body = self.get_body(data)
        # print(header)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
    def urlparser(self,url):
        # this function is used for analyze the infomation in url
        # parse url object
        urlParse = urlparse(url)
        scheme = urlParse.scheme
        host_name = urlParse.hostname
        port = urlParse.port # can be None, if None, 80 for http, 443 for https
        path = urlParse.path # CAN BE nONE
        if port == None:
            if scheme == 'http':
                port = 80
            elif scheme == 'https':
                port = 443

        if len(path) == 0:
            path = '/'
        
        return scheme,host_name,port,path

    def make_payload(self,host,port,path,method,args = None):
        if method == 'GET':
            payload = "GET {PATH} HTTP/1.1\r\nHOST: {HOST}:{PORT}\r\nConnection: close\r\n\r\n".format(PATH=path,HOST=host,PORT=port)
            print('payload:\r\n',payload)
            

        elif method == 'POST':
            if args != None:
                length = len(args)
                payload = "POST {PATH} HTTP/1.1\r\nHOST: {HOST}:{PORT}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {Length}\r\nConnection: close\r\n\r\n{VARS}".format(PATH=path,HOST=host,PORT=port,Length=length,VARS=args)

            else:
                length = 0
                payload = "POST {PATH} HTTP/1.1\r\nHOST: {HOST}:{PORT}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {Length}\r\nConnection: close\r\n\r\n".format(PATH=path,HOST=host,PORT=port,Length=length)

            print('payload:\r\n',payload)
        
        return payload

    def get_charset(self,data):
       
        m = re.search(b"charset=\S*\s+",data)
        if m != None:
            decode_method_byte = m.group(0).split(b'=')[1]
            decode_method = decode_method_byte.decode('utf-8')
        else:
            decode_method = 'utf-8'
        # print(decode_method)
        return decode_method


        return decode_method
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
