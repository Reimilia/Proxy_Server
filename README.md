# Proxy_Server

The server designed to make privacy_policy applied at **Proxy Server** (i.e., all request to 
original server will still get the same result without any filterance.

## How to use

1. Base Setup
    You need following parts to use this demo properly:
    *   client app
    *   [FHIR-Genomics-2](https://github.com/chaiery/FHIR-Genomics-2) or others acting as **Remote Server**
    *   **Privacy_Server**(See [this one](https://github.com/Reimilia/Privacy_Server)
    *   This Proxy Server
    
2. Deploy of this proxy server

    You only need basic flask package to run this proxy; however, configuration to other 
    components might be complex, please read their readmes carefully
    
    Simply do:
    ```sudo pip install flask```
    
    Also, it is always recommended to use ```virtualenv```
    
3. Setup redirect path
    You may change the url of servers in [config.py](./config.py)
    PRIVACY_BASE : base url to redirect to the **Privacy_server**
    SERVER_BASE : base url to redirect to the remote data server

4. Run [server_index.py](./server_index.py) to setup proxy server

5. Make sure 4 parts are ready, and run your client app with reidrect path:
<center>http://localhost:9090 </center>
   Then the proxy server will automaticlly use data in privacy_server and wrap the json data from
   remote server.


## How this works
Although this proxy looks pretty simple and ugly and is not compatiable with some extreme circumstances,
this is just make http-forwarding and do something before it forward the Response back to server
