#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import re

class UrlConfig():
    def getHandler(self, request, server):
        pass

class SimpleUrlConfig(UrlConfig):
    def __init__(self):
        self.urls = []
    
    def addUrl(self, regex, handler):
        self.urls.append( (regex, handler) )
    
    def getHandler(self, server, request):
        for regex, handler in self.urls:
            if re.compile(regex).match(request.path):
                return handler