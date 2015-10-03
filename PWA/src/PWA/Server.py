#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import thread, threading, logging, Cookie, time, sys, os, cgi

from Request import Request
from Errorpage import Default403Errorpage, Default404Errorpage, Default500Errorpage
from Handler import FileHandler

class _BaseServer(HTTPServer):
    def setServer(self, server):
        self.server = server
class _ThreadedHttpServer(ThreadingMixIn, _BaseServer):
    pass
class _NormalHttpServer(_BaseServer):
    pass

class _checkFilelogSizeThread(threading.Thread):
    def __init__(self, config):
        threading.Thread.__init__(self)
        self._config = config
    def run(self):
        path = self._config.filelog_path
        maxsize = self._config.filelog_maxsize
        while True:
            rf = open(path, "r")
            c = rf.read(maxsize)
            rf.close()
            wf = open(path, "w")
            wf.write(c)
            wf.close()
                
            time.sleep(60)

class _log():
    def __init__(self, config):
        self._config = config
        
        self._logger = logging.getLogger("PWA")
        self._logger.setLevel(logging.DEBUG)
        
        f = "%(asctime)s - %(levelname)s  \t%(message)s"
        level = logging.DEBUG if self._config.debug else logging.ERROR
            
        if self._config.enable_filelog:
            _checkFilelogSizeThread(self._config).start()
            
            fh = logging.FileHandler(self._config.filelog_path, encoding="utf-8")
            fh.setLevel(level)
            fh.setFormatter(logging.Formatter(f))
            self._logger.addHandler(fh)
        
        sh = logging.StreamHandler()
        sh.setLevel(level)
        sh.setFormatter(logging.Formatter(f))
        self._logger.addHandler(sh)
    
    def debug(self, *a, **k):
        self._logger.debug(*a, **k)
    def info(self, *a, **k):
        self._logger.info(*a, **k)
    def warn(self, *a, **k):
        self._logger.warn(*a, **k)
    def error(self, *a, **k):
        self._logger.error(*a, **k)
    def critical(self, *a, **k):
        self._logger.critical(*a, **k)
    def exception(self, e, msg="", critical=False):
        msg = u"{}  -  {}".format(msg, e)
        if critical:
            self.critical(msg)
        else:
            self.error(msg)

class Server():
    def __init__(self, config, urlConfig, moduleList=None, errorpages={}):
        self._config = config
        self._urlConfig = urlConfig
        self._modules = {}
        self._staticModules = {}
        
        self._errorpages = {"403":Default403Errorpage, "404":Default404Errorpage, "500":Default500Errorpage}
        self._baseServer = None
        self._running = False
        self._log = None
        self.__loadModules(moduleList)
        
        for errorname, errorpage in errorpages.iteritems():
            self._errorpages[errorname] = errorpage
    
    def __loadModules(self, modulelist):
        for modname in modulelist.getModuleNames():
            if modulelist.getModuleType == 1:
                self._staticModules[modname] = modulelist.getModule(modname)
            else:
                self._modules[modname] = modulelist.getModule(modname)(self)
    
    def start(self):
        self._init_logging()
        self._start_server()

    def stop(self):
        self._log.debug("Stopping server...")
        self.__httpServer.shutdown()
        self.__running = False

    def _init_logging(self):
        if self._log == None:
            self._log = _log(self._config)
        
    def _start_server(self):
        host = self._config.host
        port = self._config.port

        s = _ThreadedHttpServer if self._config.requestsInThread else _NormalHttpServer
        
        try:
            self._log.debug("\nStarting Server at {}:{}...".format(host, port))
            
            self._baseServer = s((host, port), _HttpHandler)
            self._baseServer.setServer(self)
            
            self._running = True
            
            if self._config.runInThread:
                thread.start_new(self._baseServer.serve_forever, ())
                while True:
                    try:
                        time.sleep(1)
                    except KeyboardInterrupt:
                        try:
                            self.stop()
                        except:
                            pass
                        finally:
                            sys.exit(0)
            else:
                self._baseServer.serve_forever()
        except Exception as e:
            self._running = False
            self._log.exception(e, "Cannot start Server")
    
    def getModule(self, modname):
        if modname in self._modules.keys():
            return self._modules[modname]
        elif modname in self._staticModules.keys():
            return self._staticModules[modname](self)
        else:
            self._log.error(u"Module '{}' not found".format(modname))

class _HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.startHandler("GET")
    def do_POST(self):
        self.startHandler("POST")
    def log_request(self, code="???", *a, **k):
        txt = u"Request by {} - \"{}\" - answered: {}".format(self.client_address[0], self.requestline, code)
        self.s._log.info(txt)


    def startHandler(self, method):
        server = self.server.server
        self.s = server
        request = Request(server, self)
        self.server_version = "PWA/0.1"
        
        try:
            request.path = self.path.split("?")[0]
            request.method = method
            request.client_adress = self.client_address
            request.http_version = self.protocol_version
            request.cookies = self.get_cookies()
            request.args, request.files = self.get_args(method)
            request.headers = self.headers
            
            handler = None
            if server._config.enable_statics and request.path[:8] == "/statics":
                path = os.path.join(server._config.statics_path, request.path[9:])
                class handler(FileHandler):
                    def __init__(self, *a, **k):
                        FileHandler.__init__(self, path, *a, **k) 
            else:
                handler = server._urlConfig.getHandler(server, request)
            
            if handler == None: 
                server._log.warn(u"No Handler found for url '{}'".format(request.path))
                self.sendError(request, "404")
            else:
                handler(server, request, self).onHandle()
        except Exception as e:
            self.sendError(request, "500")
            server._log.exception(e, "Cannot handle requests")
        
    def get_cookies(self):
        cookies = {}
        if "Cookie" in self.headers:
            c = Cookie.SimpleCookie(self.headers["Cookie"])
            for i in c.keys():
                try:
                    cookies[i] = c[i].value
                except:
                    pass
        return cookies
    
    def get_args(self, method):
        args = {}
        files = {}
        
        if method == "GET":
            strargs = self.path.split("?")
            if len(strargs) > 1:
                for pair in strargs[1].split("&"):
                    splittedPair = pair.split("=")
                    if len(splittedPair) == 0:
                        continue
                    elif len(splittedPair) == 1:
                        args[splittedPair[0]] = None
                    else:
                        args[splittedPair[0]] = splittedPair[1]
        else:
            form = cgi.FieldStorage(
                                    fp=self.rfile, 
                                    headers=self.headers,
                                    environ={'REQUEST_METHOD':'POST',
                                             'CONTENT_TYPE':self.headers['Content-Type']
                                             }
                                    )
            for field in form.keys():
                item = form[field]
                if item.filename:
                    files[item.filename] = item.file.read()
                else:
                    args[field] = item.value
        
        return args, files
    
    ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 
    def sendResponse(self, response):
        self.send_response(response.response_code)
        
        c = Cookie.SimpleCookie()
        for key, value in response.cookies.iteritems():
            c[key] = value
        
        response.headers["Content-type"] = response.content_type
        response.headers["Content-length"] = len(response.content)
        response.headers["Set-Cookie"] = c.output(header='')
        
        for key, value in response.headers.iteritems():
            self.send_header(key, value)
        
        self.end_headers()
        
        self.wfile.write(response.content)
        self.wfile.close()
    
    def sendError(self, request, errorname="500", secCall=False):
        server = self.s
        
        if errorname not in server._errorpages.keys():
            if errorname == "500" or secCall:
                self.send_error(500)
            else:
                self.sendError(request, "500", True)
        else:
            try:
                ep = server._errorpages[errorname](server, request, self)
                ep.onHandle()
                response = ep.response
                response.headers["Connection"] = "close"
            except:
                server._log.warn(u"Cannot generate error-page '{}'".format(errorname))
                self.sendError(request, "500", True)
                return
            self.sendResponse(response)
