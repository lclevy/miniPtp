# miniPtp.py

version 16jan2023

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
>python miniPtp.py -Lodip
+ operations_supported
0x1001/PTP_GetDeviceInfo 0x1002/PTP_OpenSession 0x1003/PTP_CloseSession 0x1004/PTP_GetStorageIDs 0x1005/PTP_GetStorageInfo 0x1006/PTP_GetNumObjects 0x1007/PTP_GetObjectHandles 0x1008/PTP_GetObjectInfo 0x1009/PTP_GetObject 0x100a/PTP_GetThumb 0x100b/PTP_DeleteObject 0x100c/PTP_SendObjectInfo 0x100d/PTP_SendObject 0x100f/PTP_FormatStore 0x1014/PTP_GetDevicePropDesc 0x1016/PTP_SetDevicePropValue 0x101b/PTP_GetPartialObject 0x902f 0x9033/Canon_GetMacAddress 0x9050/Canon_InitiateEventProc_50 0x9051/Canon_TerminateEventProc_51 0x905c/Canon_InitiateEventProc_5c 0x905d/Canon_TerminateEventProc_5d 0x9060/Canon_IsNeoKabotanProcMode 0x9068/Canon_GetWebServiceSpec 0x9069/Canon_GetWebServiceData 0x906a/Canon_SetWebServiceData 0x906b/Canon_DeleteWebServiceData 0x906c/Canon_GetRootCertificateSpec 0x906d/Canon_GetRootCertificateData 0x906e/Canon_SetRootCertificateData 0x906f/Canon_DeleteRootCertificateData 0x9077/Canon_GetTranscodeApproxSize 0x9078/Canon_RequestTranscodeStart 0x9079/Canon_RequestTranscodeCancel  0x9101/EOS_GetStorageIDs 0x9102/EOS_GetStorageInfo 0x9103/EOS_GetObjectInfo 0x9104/EOS_GetObject 0x9105/EOS_DeleteObject 0x9106/EOS_FormatStore 0x9107/EOS_GetPartialObject 0x9108/EOS_GetDeviceInfoEx 0x9109/EOS_GetObjectInfoEx 0x910a/EOS_GetThumbEx 0x910c/EOS_SetObjectAttributes 0x910f/EOS_Remote_Release 0x9110/EOS_SetDevicePropValueEx 0x9114/EOS_SetRemoteMode 0x9115/EOS_SetEventMode 0x9116/EOS_GetEvent 0x9117/EOS_TransferComplete 0x9118/EOS_CancelTransfer 0x911a/EOS_PCHDDCapacity 0x911b/EOS_SetUILock 0x911c/EOS_ResetUILock 0x911d/EOS_KeepDeviceOn 0x911e 0x911f/EOS_UpdateFirmware 0x9122 0x9123 0x9124 0x9127 0x9128/EOS_RemoteReleaseOn 0x9129/EOS_RemoteReleaseOff 0x912b 0x912c/EOS_GetPartialObjectEx 0x912d 0x912e 0x912f 0x9130 0x9131 0x9132/EOS_EndGetPartialObjectEx 0x9133 0x9134 0x9135/EOS_GetCTGInfo 0x9136/EOS_GetLensAdjust 0x9137 0x9138 0x9139 0x913a 0x913b 0x913c 0x913d/EOS_SetRequestOLCInfoGroup 0x913e 0x913f/EOS_GetCameraSupport 0x9140 0x9141/EOS_RequestInnerDevelopStart 0x9143/EOS_RequestInnerDevelopEnd 0x9144/EOS_GetGpsLoggingData 0x9145/EOS_GetGpsLogCurrentHandle 0x9146/EOS_SetImageRecoveryData 0x9148/EOS_FormatRecoveryData 0x9149/EOS_GetPresetLensAdjustParam 0x914a/EOS_GetRawDispImage 0x914b/EOS_SaveImageRecoveryData 0x914d/EOS_DrivePowerZoom 0x914f/EOS_GetIptcData 0x9150/EOS_SetIptcData 0x9153/EOS_GetViewFinderData 0x9154/EOS_DoAutoFocus 0x9155/EOS_DriveLens 0x9157/Canon_ClickWB 0x9158/Canon_Zoom 0x9159/Canon_ZoomPosition 0x915a/Canon_SetLiveAFFrame 0x915b/Canon_TouchAfPosition 0x915c/Canon_SetLvPcFlavoreditMode 0x915d/Canon_SetLvPcFlavoreditParam 0x9160/Canon_AFCancel 0x9166 0x916b/Canon_SetImageRecoveryDataEx 0x916c/Canon_GetImageRecoveryListEx 0x916d/Canon_CompleteAutoSendImages 0x916e/Canon_NotifyAutoTransferStatus 0x916f/Canon_GetReducedObject 0x9170/Canon_GetObjectInfo64 0x9171/Canon_GetObject64 0x9172/Canon_GetPartialObject64 0x9173/Canon_GetObjectInfoEx64 0x9174/Canon_GetPartialObjectEx64 0x9177/Canon_NotifySaveComplete 0x9178/Canon_GetTranscodedBlock 0x9179/Canon_TransferCompleteTranscodedBlock 0x9180 0x9181 0x9182/Canon_NotifyEstimateNumberofImport 0x9183/Canon_NotifyNumberofImported 0x9184/Canon_NotifySizeOfPartialDataTransfer 0x9185/Canon_NotifyFinish 0x9186/EOS_GetWftData 0x9187/EOS_SetWftData 0x9188/EOS_ChangeWftSettingNum 0x9189/EOS_GetPictureStylePCFlavorParam 0x918a 0x91ae 0x91af 0x91b9/Canon_SetFELock 0x91ba/EOS_DeleteWftSettingNum 0x91d3 0x91d4/Canon_SendCertData 0x91d5 0x91d7/Canon_DistinctionRTC 0x91d8/Canon_NotifyGpsTimeSyncStatus 0x91d9 0x91da 0x91db 0x91dc 0x91dd 0x91de 0x91e1 0x91e3 0x91e6/Canon_NotifyAdapterStatus 0x91e7 0x91e8/Canon_ceresNotifyNetworkError 0x91e9/Canon_AdapterTransferProgress 0x91ec/Canon_ceresSEndWpsPinCode 0x91f0/Canon_TransferComplete2 0x91f1/Canon_CancelTransfer2
+ device_prop_supported
0x5001/BatteryLevel 0xd303/UsedDeviceState 0xd402/DeviceFriendlyName 0xd406/SessionInitiatorVersionInfo 0xd407/PerceivedDeviceType
+ Model= Canon EOS R6
+ Device_version= 3-1.5.0
+ Opening session
Connected
+ Model_id: 0x80000453
LensName b'RF24-105mm F4 L IS USM'
hostname b'EOSR6_xxxxxx'
+ Mac_addr b'74bfc0xxxxxx'
+ properties supported
property_code: 0x5001/BatteryLevel, datatype: 0x2/uint8, current: 16
property_code: 0xd303/UsedDeviceState, datatype: 0x2/uint8, current: 1
property_code: 0xd402/DeviceFriendlyName, datatype: 0xffff/str, current: Canon EOS R6
property_code: 0xd406/SessionInitiatorVersionInfo, datatype: 0xffff/str, current: Windows/10.0.19045 MTPClassDriver/10.0.19041.0
property_code: 0xd407/PerceivedDeviceType, datatype: 0x6/uint32, current: 1
+ Storage_IDs
0
{'storage_type': 4, 'filesystem_type': 3, 'access_capability': 0, 'max_capacity': 0, 'free_space_bytes': 0, 'free_space_objects': 4294967295, 'storage_description': 'SD1', 'volume_identifier': ''}
2
{'storage_type': 4, 'filesystem_type': 3, 'access_capability': 0, 'max_capacity': 15923150848, 'free_space_bytes': 15420555264, 'free_space_objects': 4294967295, 'storage_description': 'SD2', 'volume_identifier': ''}
  90000000 00020001 00000000 3001 1        0 DCIM
    91900000 00020001 90000000 3001 1        0 100CANON
      9190d321 00020001 91900000 b108 0 21662294 2U4A3378.CR3
      9190d381 00020001 91900000 b108 0 18202710 2U4A3384.CR3
...
      9190d4f1 00020001 91900000 b108 0 18219606 2U4A3407.CR3
    91940000 00020001 90000000 3001 1        0 101CNOOO
      9194d501 00020001 91940000 b108 0 24550486 2U4A3408.CR3
  a0080000 00020001 00000000 3001 1        0 MISC

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

- MTP 1.1 : https://www.usb.org/sites/default/files/MTPv1_1.zip (2011, official specification)
- Gphoto2 : https://github.com/gphoto/libgphoto2/tree/master/camlibs/ptp2 (since 2002, Marcus Meissner and co. Active)
- chdkPTP : https://app.assembla.com/wiki/show/chdkptp (since 2011, Reyalp, lua using ptpcam, with a GUI. Compiled for Windows, Linux x64, Raspberry)
- ptpcam/ptplib2 : https://github.com/leirf/libptp (since 2013)
- ptpcam/libptp2 : https://sourceforge.net/projects/libptp/files/libptp2/ (Mariusz Woloszyn 2001-2011)
- camlib : https://github.com/petabyt/camlib (2022, Petabyte, in C)
  - canon hacks : https://github.com/petabyt/camlib/blob/master/src/canon.c
- sequoia-ptp : https://github.com/Parrot-Developers/sequoia-ptpy (no maintenance, very complete)
- PTP/IP 
  - DPReview, press release by Nikon (2004) : https://www.dpreview.com/articles/9871487277/nikonptpip
  - Ptpip : https://github.com/mmattes/ptpip (Python, implemented and tested with Nikon D5300, 2017)
  - PTP/IP documentation : http://gphoto.org/doc/ptpip.php


## Official ways to drive your Camera from Canon:
- CCAPI (REST API, requires activation) : https://developers.canon-europe.com/developers/s/article/Latest-CCAPI 
- EDSDK (Camera <-> EDSDK <-> PTP) : https://developers.canon-europe.com/developers/s/article/How-to-get-access-camera 
