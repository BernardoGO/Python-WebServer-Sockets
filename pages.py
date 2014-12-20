import socket  # Networking support
import signal  # Signal support (server shutdown on signal receive)
import time    # Current time
import os, sys
import re
import StringIO
import config
#pat = r'.*?\<%(.*)%>.*'


#response_content

def handle_includes(response):
    match = re.compile(r'include\((.+?)\)', flags=re.DOTALL)
    results = match.findall(response)
    response_content = response
    print " TYPEEEEEEEEEEEEEEEEEEEEEEEEEEE"+ str(results)
    for res in results:
        
        i = 2        
        file_handler2 = open(config.__WWW_DIR__+"/"  +res.replace("\"","" ),'rb')
        text = file_handler2.read()
        response_content = response_content.replace("include("+res+")", "%>" +text+ "<%" )
    return response_content

def main(request, data):
    request_method = request.split(' ')[0]
    file_requested = request.split(' ')[1].replace(".py", ".html")
    if (file_requested == '/'):  # in case no file is specified by the browser
        file_requested = '/index.html' # load index.html by default
    file_requested = config.__WWW_DIR__ +file_requested
    file_requestedOrg = file_requested
    file_requested = file_requested.split('?')[0]  # disregard anything after '?'
    _GET_ = {}    
    _POST_ = {}    

    try:
        getvars = file_requestedOrg.split('?')[1]
        varEval = getvars.split('&')
        for op in varEval:
            _GET_[op.split('=')[0]] = op.split('=')[1]
    except:
        pass

    try:
        getvars2 = request.split('\n')[-1]
        varEval2 = getvars2.split('&')
        for op in varEval2:
            _POST_[op.split('=')[0]] = op.split('=')[1]
    except:
        pass
    

    print "aaaaaaaaaaa" + file_requested
    try:
        file_handler = open(file_requested,'rb')
        if (request_method == 'GET' or request_method == 'POST'):  #only read the file when GET
            response = file_handler.read() # read file content
            response = handle_includes(response)
            match = re.compile(r'<%(.+?)%>', flags=re.DOTALL)
            results = match.findall(response)
            response_content = response

            for res in results:
                codeOut = StringIO.StringIO()
                sys.stdout = codeOut
                exec(res)
                sys.stdout = sys.__stdout__
                response2 = codeOut.getvalue()
                response_content = response_content.replace("<%"+res+"%>", response2)

            match = re.compile(r'!%(.+?)%!', flags=re.DOTALL)
            results = match.findall(response)
            for res in results:
                response_content = response_content.replace("!%"+res+"%!", eval(res))

        file_handler.close()
        response_headers = 200#self._gen_headers( 200)

    except Exception as e: #in case file was not found, generate 404 page
        print ("Warning, file not found. Serving response code 404\n", e)
        response_headers = 404
        if (request_method == 'GET'):
            response_content += b"<html><body><p>Error 404: File not found</p><p>"+str(e)+" </p></body></html>"

    #server_response =  response_headers.encode() # return headers for GET and HEAD
    if (request_method == 'GET' or request_method == 'POST'):
        server_response =  response_content  # return additional conten for GET only
        return [response_headers,server_response]


if __name__ == "__main__":
	main("dssad")
