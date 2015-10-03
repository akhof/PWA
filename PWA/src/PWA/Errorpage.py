#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from Handler import Handler

class Errorpage(Handler):
    def __init__(self, server, request, httpHandler):
        Handler.__init__(self, server, request, httpHandler)
        self.response.response_code = 500
    
    def error(self, errorname):
        ## Cannot raise an error from an Errorpage
        raise NotImplementedError
    def finish(self):
        ## Cannot call finish() from Errorpage
        raise NotImplementedError

def _default_skin(content, title="Error"):
    skin = """
<html>
    <head>
        <meta content="text/html;" http-equiv="content-type">
        <title>{title}</title>
    </head>
    <body style="background-color: red; color: rgb(255, 255, 255);"
    alink="#ee0000" link="#0000ee" vlink="#551a8b">
        <br />
        <br />
        <center>
            <big>
                <big>
                    {ctn}
                </big>
            </big>
        </center>
    </body>
</html>"""
    return skin.format(title=title, ctn=content)

class Default403Errorpage(Errorpage):
    def onHandle(self):
        self.response.content = _default_skin("<b><u>403:</u> Forbidden</b> - Request forbidden", "Forbidden")
        self.response.response_code = 403
class Default404Errorpage(Errorpage):
    def onHandle(self):
        self.response.content = _default_skin("<b><u>404:</u> Not Found</b> - Nothing matches the given URI", "Not Found")
        self.response.response_code = 404
class Default500Errorpage(Errorpage):
    def onHandle(self):
        self.response.content = _default_skin("<b><u>500:</u> Internal Server Error</b> - Server got itself in trouble", "Internal Server Error")
        self.response.response_code = 500
