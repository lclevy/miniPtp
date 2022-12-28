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