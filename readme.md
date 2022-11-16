# miniPtp.py

A minimal Python PTP implementation to talk to your Camera.

Take it as an educational example for PyUsb and PTP, feel free to discovered proprietary functions by exploring, such as Canon GetMacAddress...

## Installation

Tested with:
- Python 3.10 and Python 3.8
- Windows 10 + libusb-win (installed with Zadig)
- Ubuntu 20.10

## Requirements

- PyUSB 1.2.1

## Example
```
>python  miniPtp.py
idProduct=0x32f5
{'std_version': 100, 'mtp_vendor_id': 6, 'mtp_version': 100, 'mtp_extensions': '', 'functional_mode': 0, 'operations_supported': (4098, 4099, 4097, 4100, 37121, 4101, 37122, 4102, 4103, 4104, 37123, 37232, 4105, 37124, 37233, 4106, 4111, 37126, 4116, 4118, 4123, 4108, 4109, 37127, 37234, 37164, 37236, 37140, 37141, 37142, 37143, 37129, 37235, 37130, 37170, 36915, 36968, 36969, 36970, 36971, 37146, 37149, 37150, 37151, 37154, 37155, 37156, 37169, 37171, 37172, 37173, 37180, 37182, 37183, 37184, 37204, 37205, 37207, 37208, 37209, 37210, 37211, 37216, 36972, 36973, 36974, 36975, 37222, 37128, 37136, 37163, 37168, 37181, 37212, 37213, 37147, 37148, 37203, 37160, 37161, 36911, 37132, 37360, 37159, 37361, 37345, 37347, 37350, 37351, 37352, 37353, 37356, 37188, 37189, 37331, 37332, 37174, 37175, 37190, 37227, 37228, 37192, 37193, 37194, 37135, 37195, 37185, 37187, 4107, 37125, 37165, 37166, 37167, 37177, 37178, 37179, 37335, 37336, 37337, 37338, 37339, 37340, 37341, 37342, 37333, 37254, 37255, 37256, 37248, 37249, 37250, 37251, 37252, 37253, 37257, 37258, 37176, 37144, 37197, 37199, 37200, 37231, 37230, 37229, 37239, 37294, 37295, 37305, 37306, 36983, 36984, 36985, 37240, 37241, 36944, 36945, 36956, 36957, 36960), 'events_supported': (49537, 16387, 49539, 49540, 49541, 49542, 49543, 49544, 49545, 49546, 49547, 49549, 49550, 49551, 49552, 49553, 49568, 49569, 16393), 'device_prop_supported': (54274, 54279, 54278, 54019, 20481), 'capture_formats': (14337,), 'playback_formats': (12289, 12290, 12294, 12298, 12296, 14337, 45313, 45315, 48898, 14336, 45316, 45317), 'manufacturer': 'Canon.Inc', 'model': 'Canon EOS R6', 'device_version': '3-1.5.0', 'serial_number': '[redacted]'}
mac_addr b'74bfc0xxxxxx'
```
## limitations (a lot, because it is mini :-)

- Only USB transport yet, but designed with IP as possible extension
- Tested only with Canon R6
- Implemented only GetDeviceInfo, OpenSession, CloseSession and Canon GetMacAddress


## References and inspirations

- MTP 1.1 : https://www.usb.org/sites/default/files/MTPv1_1.zip (official specification)
- ptplib : https://github.com/leirf/libptp (the reference, in C)
- camlib : https://github.com/petabyt/camlib (simple, in C)
- sequoia-ptp : https://github.com/Parrot-Developers/sequoia-ptpy (no maintenance, very complete)
