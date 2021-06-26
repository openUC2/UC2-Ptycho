# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 10:07:53 2020

@author: UC2
"""
import sys
from typing import Optional
from vimba import *
import numpy as np
import tifffile as tif
import os
import time
import matplotlib.pyplot as plt
import grblboard as grbl

timestr = time.strftime("%Y%m%d-%H%M%S")

global iiter 
# Prepare Camera for ActionCommand - Trigger
myexposure = 216365/1000 # in ms 
mygain = 5
mybasepath = ".\\"
myfolder = timestr + "_PTYCHO_UC2-Texp-" + str(myexposure) + "_gain-" + str(mygain)
iiter = 0

try:
    os.mkdir(mybasepath+myfolder)
except:
    print("Already crated the folder?")

def print_preamble():
    print('///////////////////////////////////////////')
    print('/// Vimba API Asynchronous Grab Example ///')
    print('///////////////////////////////////////////\n')


def print_usage():
    print('Usage:')
    print('    python asynchronous_grab.py [camera_id]')
    print('    python asynchronous_grab.py [/h] [-h]')
    print()
    print('Parameters:')
    print('    camera_id   ID of the camera to use (using first camera if not specified)')
    print()


def abort(reason: str, return_code: int = 1, usage: bool = False):
    print(reason + '\n')

    if usage:
        print_usage()

    sys.exit(return_code)


def parse_args() -> Optional[str]:
    args = sys.argv[1:]
    argc = len(args)

    for arg in args:
        if arg in ('/h', '-h'):
            print_usage()
            sys.exit(0)

    if argc > 1:
        abort(reason="Invalid number of arguments. Abort.", return_code=2, usage=True)

    return None if argc == 0 else args[0]


def get_camera(camera_id: Optional[str]) -> Camera:
    with Vimba.get_instance() as vimba:
        if camera_id:
            try:
                return vimba.get_camera_by_id(camera_id)

            except VimbaCameraError:
                abort('Failed to access Camera \'{}\'. Abort.'.format(camera_id))

        else:
            cams = vimba.get_all_cameras()
            if not cams:
                abort('No Cameras accessible. Abort.')

            return cams[0]


def setup_camera(cam: Camera):
    with cam:
        # Try to adjust GeV packet size. This Feature is only available for GigE - Cameras.
        try:
            cam.GVSPAdjustPacketSize.run()

            while not cam.GVSPAdjustPacketSize.is_done():
                pass

        except (AttributeError, VimbaFeatureError):
            pass
                
        #cam.TriggerSelector.set('FrameStart')
        #cam.TriggerActivation.set('RisingEdge')
        #cam.TriggerSource.set('Line0')
        #cam.TriggerMode.set('On')
        cam.BlackLevel.set(100)
        cam.ExposureAuto.set("Off")
        cam.ContrastEnable.set("Off")

        cam.ExposureTime.set(myexposure*1e3)
        #cam.PixelFormat.set('Mono12')
        cam.GainAuto.set("Off")
        cam.Gain.set(mygain)
        cam.AcquisitionFrameRateEnable.set(False)
        cam.get_feature_by_name("PixelFormat").set("Mono12")

def setiter():
    global iiter
    iiter += 1

def frame_handler(cam: Camera, frame: Frame):
    #print('{} acquired {}'.format(cam, frame), flush=True)
    myframe = frame.as_numpy_ndarray()
    myfilename = mybasepath+myfolder+"\\"+str(iiter)+".tif"
    tif.imsave(myfilename, myframe)
    # not working in threads.. plt.figure(1), plt.imshow(np.squeeze(myframe)), plt.colorbar(), plt.show()
    setiter()
    print('Acquired a frame and saved it here: '+myfilename)
    
    cam.queue_frame(frame)


OFM_TO_GRBL_FAC = 1000 # necessary since OFM thinks in steps (int), GRBL in pyhsical coordinates (float)
OFM_TO_GRBL_FAC_Z = 250

'''
def position(self) -> Tuple[int, int, int]:
    # need to convert that to openflexure coordinates..
    posx, posy, posz = board.currentposition[0], board.currentposition[1], board.currentposition[2]
    return  (int(posx*OFM_TO_GRBL_FAC), int(posy*OFM_TO_GRBL_FAC), int(posz*OFM_TO_GRBL_FAC_Z))
'''

print_preamble()
cam_id = parse_args()
frameiter = 0

import serial.tools.list_ports as port_list
ports = list(port_list.comports())
for p in ports:
    print (p)
port =  ports[0].__dict__['device']# 'COM6' # corresponds to the device managers USB Port
board = grbl.grblboard(serialport=port)

# reset stage's position
board.zero_position()

# testing board
# -> 100 steps are ~10 mum
position = (100,0,0)
board.move_abs((position[0]/OFM_TO_GRBL_FAC,position[1]/OFM_TO_GRBL_FAC,position[2]/OFM_TO_GRBL_FAC_Z))
position = (0,0,0)
board.move_abs((position[0]/OFM_TO_GRBL_FAC,position[1]/OFM_TO_GRBL_FAC,position[2]/OFM_TO_GRBL_FAC_Z))

# open file for getting positions
f = open("Fermat_FOV1mm_step55um_202points.txt", "r")
print(f.readline())       

#%%

import h5py
#ptychogram = [npos,N,N] ,N=number of pixels
#umPositions_from_encoder = [npos,2] position in meters
#beam_diameter, approximated size in meters
wavelength = 450e-9
Nd = 1
zo = 

with h5py.File(f'fileName.hdf5', 'w') as hf:
    hf.create_dataset('ptychogram', data=ptychogram, dtype='f')
    hf.create_dataset('encoder', data=umPositions_from_encoder, dtype='f') 
    hf.create_dataset('dxd', data=(dxd,), dtype='f')
    hf.create_dataset('Nd', data=(ptychogram.shape[-1],), dtype='i')
    hf.create_dataset('zo', data=(zo,), dtype='f')
    hf.create_dataset('wavelength', data=(wavelength,), dtype='f')
    hf.create_dataset('entrancePupilDiameter', data=(beam_diameter,), dtype='f')
    hf.close()
    
    
iiter = 0
umPositions_from_encoder = []
with Vimba.get_instance():
    with get_camera(cam_id) as cam:

        setup_camera(cam)
        print('Press <enter> to stop Frame acquisition.')

        input("Plug off the laser")
        myframe = cam.get_frame().as_numpy_ndarray()
        myfilename = mybasepath+myfolder+"\\Background.tif"
        tif.imsave(myfilename, myframe)
        input("Ready?")
        while(True):
            try:
                position = np.float32(np.array((f.readline()).split('\n')[0].split(' ')))*10
                
                ix,iy = position[0], position[1]
                position = (ix,iy,0) 
                umPositions_from_encoder.append((ix,iy))
                board.move_abs((position[0]/OFM_TO_GRBL_FAC,position[1]/OFM_TO_GRBL_FAC,position[2]/OFM_TO_GRBL_FAC_Z))
            
                #print('{} acquired {}'.format(cam, frame), flush=True)
                myframe = cam.get_frame().as_numpy_ndarray()
                myfilename = mybasepath+myfolder+"\\"+str(iiter)+"_ix_"+str(ix)+"iy_"+str(iy)+".tif"
                tif.imsave(myfilename, myframe)
                # not working in threads.. plt.figure(1), plt.imshow(np.squeeze(myframe)), plt.colorbar(), plt.show()
                
                print('Acquired a frame and saved it here: '+myfilename)
                
                iiter += 1
            finally:
                cam.stop_streaming()
    board.move_abs((0,0,0))

# finally close the stage and the camera
board.close()
f.close()
