# miniPtp.py

version 10jan2023

A minimal Python PTP implementation to talk to your Camera.

Take it as an educational example for PyUsb and PTP, feel free to discover proprietary functions, such as 0x911F / EOS_UpdateFirmware.

## Installation

Tested with:
- Python 3.10 and Python 3.8
- Windows 10 + libusb-win ("libusb-win32 filter" installed with Zadig)
- Ubuntu 20.10 and MacOs 11
- Canon R6 and Ixus 180 (aka Elph 190)


## Requirements

- PyUSB 1.2.1, pyyaml

## Features

- list supported operations, properties and properties descriptions.
- list storages and files/handlers
- allow to get a file (object) using his handler 
- allow to upload a file at root dir (on Ixus 180). Error 0x200f / access denied on R6.
- Only USB transport yet, but designed with IP as possible extension
- PTP operations implemented : GetDeviceInfo, OpenSession, CloseSession, GetStorageIDs, GetStorageInfo, GetObjectHandles, GetObjectInfo, GetObject, GetDevicePropDesc, SendObjectInfo, SendObject and Canon GetMacAddress. But you can use *ptp.transaction* directly.

## Syntax
a la ptpcam:
```
usage: miniPtp.py [-h] [-o] [-p] [-d] [-i] [-L] [-g HANDLER] [-u UPLOAD]

options:
  -h, --help            show this help message and exit
  -o, --list-operations
                        list supported operations
  -p, --list-properties
                        list supported properties
  -d, --list-properties-description
                        list supported properties
  -i, --info            show device info
  -L, --list-files      list all files
  -g HANDLER, --get-file HANDLER
                        get file by given handler
  -u UPLOAD, --upload UPLOAD
                        upload file. storage,filename
```
### Upload example
```
>python miniPtp.py -u 0,miniPtp.py
+ Model= Canon IXUS 180
+ Device_version= 1-15.0.1.0
Connected
+ Model_id: 0x4030000
Try to upload miniPtp.py
PTP_SendObjectInfo returned: storage = 0x10001 and handle = 0x40029
Done

>python miniPtp.py -L
+ Model= Canon IXUS 180
+ Device_version= 1-15.0.1.0
Connected
+ Model_id: 0x4030000
+ Storage_IDs
3
{'storage_type': 4, 'filesystem_type': 3, 'access_capability': 0, 'max_capacity': 7736426496, 'free_space_bytes': 7726202880, 'free_space_objects': 4294967295, 'storage_description': 'SD', 'volume_identifier': ''}
  00080000 00010001 00000000 3001        0 DCIM
    01a00000 00010001 00080000 3001        0 104___07
      01a0aee1 00010001 01a00000 3801  4952866 IMG_2798.JPG
      01a0aef1 00010001 01a00000 3801  4637973 IMG_2799.JPG
  00040029 00010001 00000000 bf01    18517 miniPtp.py
```

## miniPtp.py example
```
>python miniPtp.py -poiL
idProduct=0x32f5
+ operations_supported
0x1001/PTP_GetDeviceInfo 0x1002/PTP_OpenSession 0x1003/PTP_CloseSession 0x1004/PTP_GetStorageIDs 0x1005/PTP_GetStorageInfo 0x1006/PTP_GetNumObjects 0x1007/PTP_GetObjectHandles 0x1008/PTP_GetObjectInfo 0x1009/PTP_GetObject 0x100a/PTP_GetThumb 0x100b/PTP_DeleteObject 0x100c/PTP_SendObjectInfo 0x100d/PTP_SendObject 0x100f/PTP_FormatStore 0x1014/PTP_GetDevicePropDesc 0x1016/PTP_SetDevicePropValue 0x101b/PTP_GetPartialObject 0x902f 0x9033/Canon_GetMacAddress 0x9050/Canon_EnableCommand 0x9051 0x905c 0x905d 0x9060 0x9068 0x9069 0x906a 0x906b 0x906c 0x906d 0x906e 0x906f 0x9077 0x9078 0x9079 0x9101 0x9102 0x9103 0x9104 0x9105 0x9106 0x9107 0x9108 0x9109 0x910a 0x910c 0x910f 0x9110 0x9114/Canon_SetRemoteMode 0x9115/Canon_SetEventMode 0x9116/Canon_GetEvent 0x9117 0x9118 0x911a 0x911b 0x911c 0x911d 0x911e 0x911f 0x9122 0x9123 0x9124 0x9127 0x9128 0x9129 0x912b 0x912c 0x912d 0x912e 0x912f 0x9130 0x9131 0x9132 0x9133 0x9134 0x9135 0x9136 0x9137 0x9138 0x9139 0x913a 0x913b 0x913c 0x913d 0x913e 0x913f 0x9140 0x9141 0x9143 0x9144 0x9145 0x9146 0x9148 0x9149 0x914a 0x914b 0x914d 0x914f 0x9150 0x9153 0x9154 0x9155 0x9157 0x9158 0x9159 0x915a 0x915b 0x915c 0x915d 0x9160 0x9166 0x916b 0x916c 0x916d 0x916e 0x916f 0x9170 0x9171 0x9172 0x9173 0x9174 0x9177 0x9178 0x9179 0x9180 0x9181 0x9182 0x9183 0x9184 0x9185 0x9186 0x9187 0x9188 0x9189 0x918a 0x91ae 0x91af 0x91b9 0x91ba 0x91d3 0x91d4 0x91d5 0x91d7 0x91d8 0x91d9 0x91da 0x91db 0x91dc 0x91dd 0x91de 0x91e1 0x91e3 0x91e6 0x91e7 0x91e8 0x91e9 0x91ec 0x91f0 0x91f1
+ device_prop_supported
0x5001/BatteryLevel 0xd303/UsedDeviceState 0xd402/DeviceFriendlyName 0xd406/SessionInitiatorVersionInfo 0xd407/PerceivedDeviceType
+ Model= Canon EOS R6
+ Device_version= 3-1.5.0
+ Model_id: 0x80000453
LensName b'RF24-105mm F4 L IS USM'
hostname b'EOSR6_xxxxxx'
+ Mac_addr b'74bfc0xxxxxx'
{'property_code': 20481, 'datatype': 2, 'get_set': 0, 'default': 63, 'current': 63, 'form': 2}
{'property_code': 54019, 'datatype': 2, 'get_set': 0, 'default': 1, 'current': 1, 'form': 0}
{'property_code': 54274, 'datatype': 65535, 'get_set': 0, 'default': 'Canon EOS R6', 'current': 'Canon EOS R6', 'form': 0}
{'property_code': 54278, 'datatype': 65535, 'get_set': 1, 'default': 'Unknown Initiator', 'current': 'Unknown Initiator', 'form': 0}
{'property_code': 54279, 'datatype': 6, 'get_set': 0, 'default': 1, 'current': 1, 'form': 0}
+ Storage_IDs
2
{'storage_type': 4, 'filesystem_type': 3, 'access_capability': 0, 'max_capacity': 15923150848, 'free_space_bytes': 15554052096, 'free_space_objects': 4294967295, 'storage_description': 'SD1', 'volume_identifier': ''}
  50000000 00010001 00000000 3001        0 DCIM
    51900000 00010001 50000000 3001        0 100CANON
      5190d321 00010001 51900000 b108 21662294 2U4A3378.CR3
      5190d381 00010001 51900000 b108 18202710 2U4A3384.CR3
      5190d391 00010001 51900000 b108 18094166 2U4A3385.CR3
...
      5190d4e1 00010001 51900000 b108 17670230 2U4A3406.CR3
      5190d4f1 00010001 51900000 b108 18219606 2U4A3407.CR3
  60080000 00010001 00000000 3001        0 MISC
0
{'storage_type': 4, 'filesystem_type': 3, 'access_capability': 0, 'max_capacity': 0, 'free_space_bytes': 0, 'free_space_objects': 4294967295, 'storage_description': 'SD2', 'volume_identifier': ''}

```
to get file 2U4A3384.CR3:
```
>python miniPtp.py -g 5190d381
...
transfering 2U4A3384.CR3 (18202710 bytes)...
done
```

## Transaction API

The transaction function is designed to allow one liners and test easily new code and parameters:


```python
  def transaction(self, code, req_params, data_phase=True, senddata=None):
    ...
  return { 'ResponseCode': ptp_header.code, 'Data':bytes(data), 'Parameter':respParams }
  
```
With the following line, you send a request with code 0x9033 and no parameter (the 2nd arg, the empty list). You got back data in the with 'Data' key. 
```python
mac_address = self.transaction( 0x9033, [] )['Data'][ptp.S_HEADER.size:]
```
In the following example, we open the session with this request which has one parameter, the session id. False means there is no data phase:
```python
self.transaction( 0x1002, [ self.session_id ], False )
```
In the following, we have got 3 parameters during request, and a list of 1 parameter (type int) inside response (type 3):
```python
  def get_num_objects( self, storage_id, object_format=0, association=0xffffffff ):
    data = self.transaction( 0x1006, [ storage_id, object_format, association ], False )['Parameter'] # all_formats, all_handles
    return data[0]
```
Of course, you can check if 'ResponseCode' is 0x2001 which means transaction worked.

You can also send data during data phase:
```python
  def set_prop_device_value( self, prop, value ): 
    res = self.transaction( 0x1016, [ prop ], senddata=value )
    #print(res['ResponseCode'])
```

## miniPtp as library

You can use use miniPtp as a library by importing ptp. In the example below (see [update_canon.py](update_canon.py)), you can send a firmware update file to you EOS camera using PTP/USB:
``` python
# update_canon.py
# python update.py filepath/EOSR6150.FIR

import sys
import os
from binascii import hexlify

from miniPtp import ptp

try:
  ptp_obj = ptp()
except ValueError as e:
  print(e)
  sys.exit()  

dev_info = ptp_obj.get_device_info() 

if 0x911f in dev_info['operations_supported']: #0x911f is EOS_UpdateFirmware
  print('Update operation is supported')
  
  ptp_obj.open_session()

  PTP_DATA_LEN = 0x200000 
  FILENAME_LEN = 32
  FIRM_CHUNK_LEN = PTP_DATA_LEN - FILENAME_LEN
    
  with open(sys.argv[1], 'rb') as firm_f:
    firm_data = firm_f.read()
    base_filename = os.path.basename(sys.argv[1])
    filename = base_filename.encode() + b'\x00'*(FILENAME_LEN - len(base_filename)) #for each transaction, FIR data is prefixed by filename within a 32 bytes field

    sent = 0
    error = False
    while sent < len(firm_data) and not error:
      print('Transaction %d : filename %s, fir length %d, offset %d' % (ptp_obj._transaction, base_filename, len(firm_data), sent) )
      r = ptp_obj.transaction( 0x911f, [ len(firm_data), sent ], senddata = filename + firm_data[sent:sent+FIRM_CHUNK_LEN] )
      error = r['ResponseCode'] != 0x2001
      sent += min(FIRM_CHUNK_LEN, len(firm_data)-sent)
    print('Done')  
else:
  print('Update firmware operation not supported') 
```

## References and inspirations

- MTP 1.1 : https://www.usb.org/sites/default/files/MTPv1_1.zip (official specification)
- Gphoto2 : https://github.com/gphoto/libgphoto2/tree/master/camlibs/ptp2 (more recent, active)
- chdkPTP : https://app.assembla.com/wiki/show/chdkptp (lua using ptpcam, with a GUI. Compiled for Windows, Linux x64, Raspberry)
- ptpcam/ptplib2 : https://github.com/leirf/libptp (since 2013)
- ptpcam/libptp2 : https://sourceforge.net/projects/libptp/files/libptp2/ (Mariusz Woloszyn 2001-2011)
- camlib : https://github.com/petabyt/camlib (2022, in C)
  - canon hacks : https://github.com/petabyt/camlib/blob/master/src/canon.c
- sequoia-ptp : https://github.com/Parrot-Developers/sequoia-ptpy (no maintenance, very complete)
- PTP/IP 
  - DPReview, press release by Nikon (2004) : https://www.dpreview.com/articles/9871487277/nikonptpip
  - Ptpip : https://github.com/mmattes/ptpip (Python, implemented and tested with Nikon D5300, 2017)
  - PTP/IP documentation : http://gphoto.org/doc/ptpip.php


## Official ways to drive your Camera from Canon:
- CCAPI (REST API, requires activation) : https://developers.canon-europe.com/developers/s/article/Latest-CCAPI 
- EDSDK (Camera <-> EDSDK <-> PTP) : https://developers.canon-europe.com/developers/s/article/How-to-get-access-camera 
