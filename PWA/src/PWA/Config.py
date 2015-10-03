#!/usr/bin/env python
# -*- coding: UTF-8 -*-

class Config():
    def __init__(self):
        self.host = "localhost"
        self.port = 80
        self.requestsInThread = True #each request is handle in thread
        self.runInThread = False #server is running in thread
        self.enable_statics = False
        self.statics_path = ""
        self.debug = True
        self.enable_filelog = False
        self.filelog_path = ""
        self.filelog_maxsize = 1024*1000*10 #10 MB = 10.240.000 bytes
        