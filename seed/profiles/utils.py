# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# TODO: Inject module from string rather then static import

class Struct:
    def __nonzero__(self):
        return len(self.__dict__.keys()) > 0

    def __repr__(self):
        if hasattr(self, 'name'):
            return "<%s [%s]>" % (self.name, 
                ','.join(self.__dict__.keys()))
        
        return "<%s [%s]>" % (self.__class__.__name__, 
            ','.join(self.__dict__.keys()))

    def __setattr__(self, name, value):
        self.__dict__.update({name:value})

    def __init__(self, entries): 
        for key, value in entries.iteritems():
            if isinstance(value, dict):
                value = Struct(value)
            
            if isinstance(value, list):
                new_value = []
                if len(value) > 0:
                    item = value.pop()
                    while item:
                        if isinstance(item, dict):
                            item = Struct(item)
                        new_value.append(item)
                        try:
                            item = value.pop()
                        except IndexError:
                            break

                value = new_value
            
            self.__dict__.update({
                key: value})

    def copy(self):
        return Struct(self.__dict__.copy())

