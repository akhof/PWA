#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os, urllib
from mimetypes import MimeTypes
from Response import Response

class Handler():
    def __init__(self, server, request, httpHandler):
        self._server = server
        self._log = server._log
        self._httpHandler = httpHandler
        self.request = request
        self.response = Response(server)
    
    def finish(self):
        self._httpHandler.sendResponse(self.response)
    def error(self, errorname):
        self._httpHandler.sendError(self.request, errorname)
    
    def onHandle(self):
        pass
    
        
class FileHandler(Handler):
    def __init__(self, path, *a, **k):
        Handler.__init__(self, *a, **k)
        self._path = path
    
    def onHandle(self):
        if not os.path.isfile(self._path):
            self.error("404")
        else:
            try:
                f = open(self._path)
            except:
                self.error("500")
                return
            self._httpHandler.send_response(200)
            self._httpHandler.send_header("Content-type", MimeTypes().guess_type(urllib.pathname2url(self._path)))
            self._httpHandler.send_header("Content-length", str(os.path.getsize(self._path)))
            self._httpHandler.end_headers()
            
            while True:
                ctn = f.read(1024 * 100) #100 kb
                if len(ctn) == 0:
                    break
                self._httpHandler.wfile.write(ctn)
            self._httpHandler.wfile.close()
        