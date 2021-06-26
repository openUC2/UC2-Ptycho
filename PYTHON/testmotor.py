# -*- coding: utf-8 -*
"""
Created on Fri Dec 18 10:07:53 2020

@author: UC2
"""
import sys
from typing import Optional
import numpy as np
import tifffile as tif
import os
import time
import matplotlib.pyplot as plt
import grblboard as grbl

timestr = time.strftime("%Y%m%d-%H%M%S")



OFM_TO_GRBL_FAC = 1000 # necessary since OFM thinks in steps (int), GRBL in pyhsical coordinates (float)
OFM_TO_GRBL_FAC_Z = 250
#%%
import serial.tools.list_ports as port_list
ports = list(port_list.comports())
for p in ports:
    print (p)
port =  ports[-1].__dict__['device']# 'COM6' # corresponds to the device managers USB Port
board = grbl.grblboard(serialport=port)

# reset stage's position
board.zero_position()

# testing board
#%%
# -> 100 steps are ~10 mum
position = (1000,1000,0)
board.move_abs((position[0]/OFM_TO_GRBL_FAC,position[1]/OFM_TO_GRBL_FAC,position[2]/OFM_TO_GRBL_FAC_Z))
position = (0,0,0)
board.move_abs((position[0]/OFM_TO_GRBL_FAC,position[1]/OFM_TO_GRBL_FAC,position[2]/OFM_TO_GRBL_FAC_Z))
#%%
position = (0,0,1000)
board.move_abs((position[0]/OFM_TO_GRBL_FAC,position[1]/OFM_TO_GRBL_FAC,position[2]/OFM_TO_GRBL_FAC_Z))
board.set_led(1)


#%
position = (0,0,0)
board.move_abs((position[0]/OFM_TO_GRBL_FAC,position[1]/OFM_TO_GRBL_FAC,position[2]/OFM_TO_GRBL_FAC_Z))
board.set_led(0)
board.set_laser_intensity(0)


#%%
#board.close()

       