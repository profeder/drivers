#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

from I2CDevice import I2CDevice
from ctypes import c_short
from ctypes import c_ushort
from ctypes import c_long
from ctypes import c_ulong
from time import sleep

class BMP180(I2CDevice):
    
    __oss = {'mode': 0, 'time': 0.045}
    
    DEVICE_ADDRESS = 0x77
    __AC1 = c_short(408)
    __AC2 = c_short(-72)
    __AC3 = c_short(-14383)
    __AC4 = c_ushort(32741)
    __AC5 = c_ushort(32757)
    __AC6 = c_ushort(23153)
    __B1 = c_short(6190)
    __B2 = c_short(4)
    __B3 = 0
    __B4 = 0
    __B5 = 0
    __B6 = 0
    __B7 = 0
    __MB = c_short(-32768)
    __MC = c_short(-8711)
    __MD = c_short(2868)
    __test = False
        
    #Modalita' di campionamento
    ULTRA_LOW_POWER_MODE = {'mode': 0, 'time': 0.045}
    STANDARD = {'mode': 1, 'time': 0.075}
    HIGH_RESOLUTION = {'mode': 2, 'time': 0.135}
    ULTRA_HIGH_RESOLUTION = {'mode': 3, 'time': 0.255}
    
    def __init__(self, channel):
        I2CDevice.__init__(self, channel)
        if not self.__test:
            self.__AC1 = c_short(self.__read_word(0xAA))
            self.__AC2 = c_short(self.__read_word(0xAC))
            self.__AC3 = c_short(self.__read_word(0xAE))
            self.__AC4 = c_ushort(self.__read_word(0xB0))
            self.__AC5 = c_ushort(self.__read_word(0xB2))
            self.__AC6 = c_ushort(self.__read_word(0xB4))
            self.__B1 = c_short(self.__read_word(0xB6))
            self.__B2 = c_short(self.__read_word(0xB8))
            self.__MB = c_short(self.__read_word(0xBA))
            self.__MC = c_short(self.__read_word(0xBC))
            self.__MD = c_short(self.__read_word(0xBE))
        
    def setMode(self, mode):
        self.__oss = mode
        
    def __read_word(self, adr):
        high = self._channel.read_byte_data(self.DEVICE_ADDRESS, adr)
        low = self._channel.read_byte_data(self.DEVICE_ADDRESS, adr+1)
        val = (high << 8) + low
        return val

    def __readTemperature(self):
        self._channel.write_byte_data(self.DEVICE_ADDRESS, 0xF4, 0x2E)
        sleep(0.45)
        if not self.__test:
            UT = c_long(self.__read_word(0xF6))
        else:
            UT = c_long(27898)
        X1 = (UT.value - self.__AC6.value) * self.__AC5.value / pow(2, 15)
        X2 = self.__MC.value * pow(2,11) / (X1 + self.__MD.value)
        self.__B5 = X1 + X2
        T = (self.__B5 + 8)/pow(2,4)
        return float(T) / 10
    
    def __readPression(self):
        data = 0x34 + (self.__oss['mode'] << 6)
        self._channel.write_byte_data(self.DEVICE_ADDRESS, 0xF4, data)
        sleep(self.__oss['time'])
        __MBs = self._channel.read_byte_data(self.DEVICE_ADDRESS, 0xf6)
        lsb = self._channel.read_byte_data(self.DEVICE_ADDRESS, 0xf7)
        xlsb = self._channel.read_byte_data(self.DEVICE_ADDRESS, 0xf8)
        if not self.__test:
            UP = c_long((__MBs << 16) + (lsb << 8) + xlsb >> (8-self.__oss['mode']))
        else:
            UP = c_long(23843)
        
        self.__B6 = self.__B5 - 4000
        #print('B6', [self.__B6])
        
        X1 = (self.__B2.value * pow(self.__B6, 2)/pow(2,12))/pow(2, 11)
        X2 = self.__AC2.value * self.__B6 / pow(2, 11)
        X3 = X1 + X2
        #print('X1, X2, X3', [X1, X2, X3])
        
        self.__B3 = (((self.__AC1.value * 4 + X3) << self.__oss['mode']) + 2)/4
        #print('B3', [self.__B3])
        
        X1 = self.__AC3.value * self.__B6/ pow(2, 13)
        X2 = (self.__B1.value * pow(self.__B6, 2)/pow(2, 12))/pow(2, 16)
        X3 = (X1 + X2 + 2)/4
        #print('X1, X2, X3', [X1, X2, X3])
        
        self.__B4 = self.__AC4.value * c_ulong(X3 + 32768).value / pow(2, 15)
        self.__B7 = c_ulong(UP.value - self.__B3).value* (50000 >> self.__oss['mode'])
        #print('B4, B7', [self.__B4, self.__B7])
        
        if self.__B7 < 0x80000000:
            p = (self.__B7 * 2 )/ self.__B4
        else:
            p = (self.__B7 / self.__B4)*2
        #print('p: ', p)
        
        X1 = pow(p/pow(2,8), 2)
        X1 = (X1 * 3038)/pow(2,16)
        X2 = (-7357*p)/pow(2, 16)
        #print('X1, X2', [X1, X2])
        
        p = p + (X1 + X2 + 3791)/pow(2,4)
        return int(p)
        
    def getData(self):
        T = self.__readTemperature()
        P = self.__readPression()
        return {'temperature': T, 'pression': P}
    
    def print_calibration(self):
        print('__AC1: ' + repr(self.__AC1))
        print('__AC2: ' + repr(self.__AC2))
        print('__AC3: ' + repr(self.__AC3))
        print('__AC4: ' + repr(self.__AC4))
        print('__AC5: ' + repr(self.__AC5))
        print('__AC6: ' + repr(self.__AC6))
        
        print('__B1: ' + repr(self.__B1))
        print('__B2: ' + repr(self.__B2))
        
        print('__MB: ' + repr(self.__MB))
        print('__MC: ' + repr(self.__MC))
        print('__MD: ' + repr(self.__MD))
    
