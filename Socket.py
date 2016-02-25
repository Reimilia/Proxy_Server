'''
This is a http-forward server which wrap the json data with apply of privacy_policy
To security, we separate this proxy with original server and privacy_server.
So this file is designed solely intend to pass http request.
'''

import io
import requests
import json
from config import SERVER_BASE
from flask import Flask
from flask import request,redirect
from urllib import urlencode
#from resources import filter_policy

dispatcher = Flask(__name__)

KNOWN_HTTP_METHOD=['GET','POST','PUT','DELETE']
MUST_PARSE_ARGS_HEADER=['Authorization','Accept']

class ForwardError(Exception):
    pass

class UnderDevError(Exception):
    pass

def parse_request_headers():
    #print request.headers
    headers = {}
    for k,v in request.headers:
        if k in MUST_PARSE_ARGS_HEADER:
            headers[k] = v
    return headers


def wrap_data(resource,auth_header):
    '''
    The proxy aims to filter json/xml data
    Here is where the program deals with that
    :param resource: Response class, it will contain all info the proxy received at remote server
           auth_header: We must ask data_server some sufficient info we need to wrap up the data
    :return: the 'wrapped' json/xml data where the privacy policy is applied

    Note we separate this part from remote server is for better extension and maintenance
    (If someone can see full data or some requests needn't apply policy_wrapper)
    '''
    # To do : xml data is not fully supported since we did not figure out how to check data_type in
    # Response class
    if (request.status_code!= 200):
        return resource._content
    try:
        #print type(resource._content)
        #print type(json.dumps(resource.json()))
        return json.dumps(resource.json())
        #wrapped_content=filter_policy(json.dumps(resource.json()),auth_header)
    except:
        return resource._content


@dispatcher.route('/api/<path:request_url>', methods=KNOWN_HTTP_METHOD)
def request_handler(request_url):
    if request.method not in KNOWN_HTTP_METHOD:
        raise ForwardError
    if request.method == 'GET':
        auth_header = parse_request_headers()
        resp = requests.get('%s/api/%s?%s' %(SERVER_BASE, request_url,urlencode(request.args,doseq=True)), headers=auth_header)
        return wrap_data(resp,auth_header)
    elif request.method == 'POST':
        auth_header = parse_request_headers()
        resp = requests.post('%s/api/%s?%s' %(SERVER_BASE, request_url,urlencode(request.args,doseq=True)), data=request.form, headers=auth_header)
        return resp._content
    elif request.method == 'PUT':
        auth_header = parse_request_headers()
        resp = requests.put('%s/api/%s?%s' %(SERVER_BASE, request_url,urlencode(request.args,doseq=True)), data=request.form, headers=auth_header)
        return resp._content
    elif request.method == 'DELETE':
        auth_header = parse_request_headers()
        resp = requests.delete('%s/api/%s?%s' %(SERVER_BASE, request_url,urlencode(request.args,doseq=True)), headers=auth_header)
        return resp._content
    else:
        raise ForwardError


@dispatcher.route('/auth/<path:request_url>', methods=KNOWN_HTTP_METHOD)
def request_forwarder(request_url):
    '''
    This is the authorization route
    simply in demo we put forward this request while saving the cookies.
    :param request_url:
    :return:
    '''
    if request.method not in KNOWN_HTTP_METHOD:
        raise ForwardError
    if request.method=='POST':
        #print type(request.form)
        resp = requests.post('%s/auth/%s' %(SERVER_BASE,request_url), data=request.form)
        return resp.text
    elif request.method=='GET':
        #print request.session.user
        resp=redirect('%s/auth/%s?%s'% (SERVER_BASE,request_url,urlencode(request.args)))
        return resp
    else:
        raise ForwardError


@dispatcher.route('/privacy/<path:request_url>', methods = KNOWN_HTTP_METHOD)
def privacy_request(request_url):
    '''
    Well, for request to Privacy_Server, at this proxy server we will only redirect and send request to
    remote Privacy_Server, and then send the response back to client side. The protection and management will
    be settled in Privacy_Server
    :param request_url:
    :return:
    '''
    if request.method not in KNOWN_HTTP_METHOD:
        raise ForwardError
    auth_header= parse_request_headers()
    resp = requests.request(method= request.method, url='%s/privacy/%s?%s' %(SERVER_BASE,request_url,urlencode(request.args, doseq=True)), headers=auth_header, data=request.form)
    try:
        return resp._content
    except:
        raise UnderDevError


@dispatcher.route('/<path:redirect_path>', methods = KNOWN_HTTP_METHOD)
def proxy_pass(redirect_path):
    '''
    Normally pass unassigned request to data_server
    :param redirect_path:
    :return:
    '''
    if request.method not in KNOWN_HTTP_METHOD:
        raise ForwardError
    auth_header= parse_request_headers()
    resp = requests.request(method= request.method, url='%s/%s?%s' %(SERVER_BASE,redirect_path,urlencode(request.args, doseq=True)), headers=auth_header, data=request.form)
    try:
        return resp._content
    except:
        raise UnderDevError

if __name__ == '__main__':
    dispatcher.run(host='127.0.0.1',port=9090,debug=True)