# miniPtp.py

version 27nov2022

A minimal Python PTP implementation to talk to your Camera.

Take it as an educational example for PyUsb and PTP, feel free to discover proprietary functions by exploring, such as Canon GetMacAddress...

## Installation

Tested with:
- Python 3.10 and Python 3.8
- Windows 10 + libusb-win ("libusb-win32 filter" installed with Zadig)
- Ubuntu 20.10
- Canon R6 and Ixux 180 (Elph 190)

## Requirements

- PyUSB 1.2.1

## Features

- list supported operations and properties
- list storages and files/handler
- allow to get a file (object) using his handler 

## Syntax
a la ptpcam:
```
usage: miniPtp.py [-h] [-o] [-p] [-i] [-L] [-g HANDLER]

options:
  -h, --help            show this help message and exit
  -o, --list-operations
                        list supported operations
  -p, --list-properties
                        list supported properties
  -i, --info            show device info
  -L, --list-files      list all files
  -g HANDLER, --get-file HANDLER
                        get file by given handler
```
## Example
```
>python miniPtp.py -poiL
idProduct=0x32f5
+ operations_supported
0x1001/PTP_GetDeviceInfo 0x1002/PTP_OpenSession 0x1003/PTP_CloseSession 0x1004/PTP_GetStorageIDs 0x1005/PTP_GetStorageInfo 0x1006/PTP_GetNumObjects 0x1007/PTP_GetObjectHandles 0x1008/PTP_GetObjectInfo 0x1009/PTP_GetObject 0x100a/PTP_GetThumb 0x100b/PTP_DeleteObject 0x100c/PTP_SendObjectInfo 0x100d/PTP_SendObject 0x100f/PTP_FormatStore 0x1014/PTP_GetDevicePropDesc 0x1016/PTP_SetDevicePropValue 0x101b/PTP_GetPartialObject 0x902f 0x9033/Canon_GetMacAddress 0x9050/Canon_EnableCommand 0x9051 0x905c 0x905d 0x9060 0x9068 0x9069 0x906a 0x906b 0x906c 0x906d 0x906e 0x906f 0x9077 0x9078 0x9079 0x9101 0x9102 0x9103 0x9104 0x9105 0x9106 0x9107 0x9108 0x9109 0x910a 0x910c 0x910f 0x9110 0x9114/Canon_SetRemoteMode 0x9115/Canon_SetEventMode 0x9116/Canon_GetEvent 0x9117 0x9118 0x911a 0x911b 0x911c 0x911d 0x911e 0x911f 0x9122 0x9123 0x9124 0x9127 0x9128 0x9129 0x912b 0x912c 0x912d 0x912e 0x912f 0x9130 0x9131 0x9132 0x9133 0x9134 0x9135 0x9136 0x9137 0x9138 0x9139 0x913a 0x913b 0x913c 0x913d 0x913e 0x913f 0x9140 0x9141 0x9143 0x9144 0x9145 0x9146 0x9148 0x9149 0x914a 0x914b 0x914d 0x914f 0x9150 0x9153 0x9154 0x9155 0x9157 0x9158 0x9159 0x915a 0x915b 0x915c 0x915d 0x9160 0x9166 0x916b 0x916c 0x916d 0x916e 0x916f 0x9170 0x9171 0x9172 0x9173 0x9174 0x9177 0x9178 0x9179 0x9180 0x9181 0x9182 0x9183 0x9184 0x9185 0x9186 0x9187 0x9188 0x9189 0x918a 0x91ae 0x91af 0x91b9 0x91ba 0x91d3 0x91d4 0x91d5 0x91d7 0x91d8 0x91d9 0x91da 0x91db 0x91dc 0x91dd 0x91de 0x91e1 0x91e3 0x91e6 0x91e7 0x91e8 0x91e9 0x91ec 0x91f0 0x91f1
+ device_prop_supported
0x5001/BatteryLevel 0xd303/UsedDeviceState 0xd402/DeviceFriendlyName 0xd406/SessionInitiatorVersionInfo 0xd407/PerceivedDeviceType
+ Model= Canon EOS R6
+ Device_version= 3-1.5.0
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
## Limitations (a lot, because it is mini :-)

- Only USB transport yet, but designed with IP as possible extension
- Tested with Canon R6
- Implemented : GetDeviceInfo, OpenSession, CloseSession, GetStorageIDs, GetStorageInfo, GetObjectHandles, GetObjectInfo, GetObject, GetDevicePropDesc and Canon GetMacAddress


## References and inspirations

- MTP 1.1 : https://www.usb.org/sites/default/files/MTPv1_1.zip (official specification)
- PTP, 2012 : https://people.ece.cornell.edu/land/courses/ece4760/FinalProjects/f2012/jmv87/site/files/PTP%20Protocol.pdf
- ptplib : https://github.com/leirf/libptp (the reference, in C)
- camlib : https://github.com/petabyt/camlib (simple, in C)
- sequoia-ptp : https://github.com/Parrot-Developers/sequoia-ptpy (no maintenance, very complete)
- PTP/IP 
  - DPReview, press release by Nikon (2004) : https://www.dpreview.com/articles/9871487277/nikonptpip
  - Pptip : https://github.com/mmattes/ptpip (Python, implemented and tested with Nikon D5300)
  - PTP/IP documentation : http://gphoto.org/doc/ptpip.php


