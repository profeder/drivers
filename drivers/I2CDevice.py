# -*- coding: utf-8 -*-

class I2CDevice:
    
    _channel = None
    
    def __init__(self, channel):
        self._channel = channel