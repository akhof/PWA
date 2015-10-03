#!/usr/bin/env python
# -*- coding: UTF-8 -*-

class Request():
    def __init__(self, server, httpHandler):
        self._server = server
        self._log = server._log
        self._httpHandler = httpHandler
        
        self.path = None
        self.method = None
        self.client_adress = None
        self.http_version = None
        self.cookies = {}
        self.args = {}
        self.files = {}
        self.headers = {}