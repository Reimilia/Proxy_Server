# Proxy_Server

The server designed to make privacy_policy applied at **Proxy Server** (i.e., all request to 
original server will still get the same result without any filtering. However the client will recieve
data that was wrapped up by this proxy server)

## How to use

1. Base Setup
    You need following parts to use this demo properly:
    *   client app ( We use [this one] https://github.com/JohnsonChern/Privacy_Server))
    *   [FHIR-Genomics-2](https://github.com/chaiery/FHIR-Genomics-2) or others acting as **Remote Server**
    *   **Privacy_Server**(See [this one](https://github.com/Reimilia/Privacy_Server))
    *   This Proxy Server
    
2. Deploy of this proxy server

    You only need basic flask package to run this proxy; however, configuration to other 
    components might be complex, please read their readmes carefully
    
    Simply do:
    ```sudo pip install -r requirements.txt```
    
    Also, it is always recommended to use ```virtualenv``` to deploy and make sandbox test.
    
3. Setup redirect path
    You may change the url of servers in config.py
    PRIVACY_BASE : base url to redirect to the **Privacy_server**
    SERVER_BASE : base url to redirect to the remote data server

4. Run server_index.py to setup proxy server

5. Make sure 4 parts are ready, and run your client app with reidrect path:
<center>```http://localhost:9090 ```</center>
   Then the proxy server will automatically use data in privacy_server and wrap the json data from
   remote server.


## How this works
Although this proxy looks pretty simple and ugly and is not compatiable with some extreme circumstances,
this is just make http-forwarding and do something before it forward the Response back to server
 
## Development Status and Further Extension

- [x] **Proxy_Server (Which designed to forward requests and filter policy)**
    - [x] http forwarding
        - [x] Basic request forwarding with Oauth2.0 authetication headers
        - [x] General Dispatching 
    - [ ] http Response filtering
        - [x] Wrap single patient resource (json)
        - [ ] Wrap single patient-related resource (json) (*under development*)
        - [x] Wrap multiple(bundled) resource (json)
        - [ ] xml data parsing and wrapping
    - [ ] X-Forwarded-For Hidding ( This means the client, if not parse http response thouroughly, will not know the real location of data server)