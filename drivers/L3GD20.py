# -*- coding: utf-8 -*-

import I2CDevice

class L3GD20(I2CDevice):

    def __init__(self, channel):
        I2CDevice.__init__(self, channel)