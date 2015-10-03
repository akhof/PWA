from PWA import Handler, FileHandler, Config, SimpleUrlConfig, ModuleList, Server, staticModule, Errorpage
    
class MainPage(Handler):
    def onHandle(self):
        content = "<h1>Hello World!</h1>"
        
        self.response.content = self._server.getModule("template").call("build", content)
        self.response.content_type = "text/html"
        self.response.response_code = 200
        self.finish()
        
class Logo(FileHandler):
    def __init__(self, *a, **k):
        FileHandler.__init__(self, "/home/aha/Dropbox/cd-1127232232.png", *a, **k)

class Template(staticModule):
    def build(self, content):
        return u"""
<html>
    <head>
        <meta content="text/html;" http-equiv="content-type">
    </head>
    <body style="background-color: rgb(204, 204, 255); color: rgb(0, 0, 0);" alink="#ee0000" link="#0000ee" vlink="#551a8b">
        <table style="text-align: left; width: 90%; margin-left: auto; margin-right: auto;" border="0" cellpadding="2" cellspacing="2">
            <tbody>
                <tr>
                    <td style="vertical-align: top; width: 100%;">
                        {}
                    </td>
                </tr>
            </tbody>
        </table>
        <br />
    </body>
</html>
""".format(content)    
    
class NotFound(Errorpage):
    def onHandle(self):
        content = "<b>404</b> - Not Found! :("
        
        self.response.content = self._server.getModule("template").call("build", content)
        self.response.content_type = "text/html"
        self.response.response_code = 404

def getConfig():
    c = Config()
    c.port = 8080
    c.enable_statics = True
    c.statics_path = "/home/user"            # http://[SERVER]/statics/abc.py → /home/aha/abc.py would be responsed
    c.enable_filelog = True
    c.filelog_path = "/home/user/LOG.txt"
    return c

def getUrlConfig():
    u = SimpleUrlConfig()
    u.addUrl(r"/$", MainPage)
    u.addUrl(r"/logo.png$", Logo)
    return u

def getModuleList():
    m = ModuleList()
    m.addStaticModule("template", Template)
    return m

if __name__ == "__main__":
    config =        getConfig()
    urls =          getUrlConfig()
    modules =       getModuleList()
    errorpages =    {"404" : NotFound}
    
    s = Server(config, urls, modules, errorpages)
    s.start()
    