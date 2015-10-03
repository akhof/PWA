#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from threading import Lock

class _baseModule():
    def __init__(self, server):
        self._server = server
        self._log = server._log

class staticModule(_baseModule):
    def call(self, action, *a, **k):
        return eval("self.{}(*a, **k)".format(action))
class Module(_baseModule):
    def __init__(self, server, threadSave=True):
        _baseModule.__init__(self, server)
        self._threadSave = threadSave
        self.lock = Lock()
    
    def call(self, action, *a, **k):
        if self._threadSave:
            self.lock.acquire()
        try:
            return eval("self.{}(*a, **k)".format(action))
        finally:
            if self._threadSave:
                self.lock.release()

class ModuleList():
    def __init__(self):
        self.modules = {} #key=modname   value = (type, Module)   type= [1=static  2=notStatic]
    
    def addModule(self, modname, mod):
        self.modules[modname] = (2, mod)
    def addStaticModule(self, modname, mod):
        self.modules[modname] = (1, mod)
    
    def getModuleNames(self):
        return self.modules.keys()
    def getModuleType(self, modname):
        return self.modules[modname][0]
    def getModule(self, modname):
        return self.modules[modname][1]