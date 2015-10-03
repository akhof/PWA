#!/usr/bin/env python
# -*- coding: UTF-8 -*-

class Response():
    def __init__(self, server):
        self._server = server
        
        self.response_code = 200
        self.content_type = None
        self.content = ""
        self.headers = {}
        self.cookies = {}
        