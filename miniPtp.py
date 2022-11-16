'''
miniPtp.py
'''

# https://www.usb.org/document-library/media-transfer-protocol-v11-spec-and-mtp-v11-adopters-agreement

import os
#os.environ['PYUSB_DEBUG'] = 'debug'
import usb.core
import usb.util

from struct import pack, Struct
from binascii import hexlify, unhexlify
from collections import namedtuple

PTP_CLASS_IMAGE = 6

class usb_tr:
  VENDORID_CANON = 0x04a9
  
  def __init__(self, vendor = VENDORID_CANON):
    self.device = None
    self.config = None
    self.interface = None
    self.out_ep = None
    self.in_ep = None
    self.intr_ep = None

    # simplified from https://github.com/pyusb/pyusb/blob/master/docs/tutorial.rst
    devs = usb.core.find( idVendor=vendor ) 
    if devs is None:
      raise ValueError('Device not found')
    print('idProduct=0x%x' % devs.idProduct)
    self.device = devs
    self.device.set_configuration()
    
    for self.config in self.device:
      self.interface = usb.util.find_descriptor( self.config, bInterfaceClass=PTP_CLASS_IMAGE ) 

    # get an endpoint instance
    for ep in self.interface:
      ep_type = usb.util.endpoint_type(ep.bmAttributes)
      ep_dir = usb.util.endpoint_direction(ep.bEndpointAddress)
      if ep_type == usb.util.ENDPOINT_TYPE_BULK:
        if ep_dir == usb.util.ENDPOINT_IN:
          self.in_ep = ep
        elif ep_dir == usb.util.ENDPOINT_OUT:
          self.out_ep = ep
      elif ((ep_type == usb.util.ENDPOINT_TYPE_INTR) and (ep_dir == usb.util.ENDPOINT_IN)):
          self.intr_ep = ep


class ptp:
  S_HEADER = Struct('<LHHL')
  NT_HEADER = namedtuple('ptp_header', 'len type code transaction' )

  S_DEVICE_INFO_HEADER = Struct('<HLH')

  OC_GetDeviceInfo = 0x1001 
  OC_OpenSession = 0x1002

  RC_OK = 0x2001

  PACKET_TYPE_COMMAND = 1
  PACKET_TYPE_DATA = 2
  PACKET_TYPE_RESPONSE = 3
    
  def __init__( self, trans={'usb':True} ):
    self.transaction = 0
    if 'usb' in trans:
      self.device = usb_tr()
    else:
      return None    

  def build_header( self, size, ptp_type, ptp_code ):
    return ptp.S_HEADER.pack( size, ptp_type, ptp_code, self.transaction )

  def parse_header( data ):
    return ptp.NT_HEADER( *ptp.S_HEADER.unpack_from(data, 0) )

  def parse_string( data ):
    _len = data[0]
    if _len == 0:
      return ''
    else:
      return bytes( data[ 1: 1+(_len-1)*2 ] ).decode('utf-16')    
      
  def string_len( n ): #return length of ptp string in bytes, given utf-16 len
    if n==0:
      return 1
    else:
       return 1+(n+1)*2    

  def parse_array( data ):
    len = Struct('<L').unpack_from( data, 0)[0]
    return Struct('<%dH' % len).unpack_from( data, 4 )

  #section 5.1.1
  def parse_devinfo( data ):
    dev_info = dict()
    ptr = ptp.S_HEADER.size
    
    dev_info['std_version'], dev_info['mtp_vendor_id'], dev_info['mtp_version'] = ptp.S_DEVICE_INFO_HEADER.unpack_from( data, ptr)
    ptr += ptp.S_DEVICE_INFO_HEADER.size
    
    dev_info['mtp_extensions'] = ptp.parse_string( data[ptr:] )    
    ptr += ptp.string_len( len(dev_info['mtp_extensions']) )

    dev_info['functional_mode'] = Struct('<H').unpack_from(data, ptr)[0]
    ptr += Struct('<H').size
    
    dev_info['operations_supported'] = ptp.parse_array( data[ptr: ] )
    ptr += Struct('<L').size + Struct('<H').size*len( dev_info['operations_supported'] )
    
    dev_info['events_supported'] = ptp.parse_array( data[ptr: ] )
    ptr += Struct('<L').size + Struct('<H').size*len( dev_info['events_supported'] )

    dev_info['device_prop_supported'] = ptp.parse_array( data[ptr: ] )
    ptr += Struct('<L').size + Struct('<H').size*len( dev_info['device_prop_supported'] )

    dev_info['capture_formats'] = ptp.parse_array( data[ptr: ] )
    ptr += Struct('<L').size + Struct('<H').size*len(dev_info['capture_formats'])

    dev_info['playback_formats'] = ptp.parse_array( data[ptr: ] )
    ptr += Struct('<L').size + Struct('<H').size*len( dev_info['playback_formats'] )    
 
    dev_info['manufacturer'] = ptp.parse_string( data[ptr:] )
    ptr += ptp.string_len( len(dev_info['manufacturer']) )
    
    dev_info['model'] = ptp.parse_string( data[ptr:] )
    ptr += ptp.string_len( len(dev_info['model']) )
    
    dev_info['device_version'] = ptp.parse_string( data[ptr:] )
    ptr += ptp.string_len( len(dev_info['device_version']) )

    dev_info['serial_number'] = ptp.parse_string( data[ptr:] )
    ptr += ptp.string_len( len(dev_info['serial_number']) )
        
    return dev_info 
          
  def write(self, data):
    return self.device.out_ep.write( data ) #more then 512 bytes is not tested !!!!

  def read(self):
    chunk = self.device.in_ep.read( self.device.in_ep.wMaxPacketSize )
    data = chunk
    while len(chunk) == self.device.in_ep.wMaxPacketSize and len(chunk)!=0: #to test = multiple of in_ep.wMaxPacketSize
      chunk = self.device.in_ep.read( self.device.in_ep.wMaxPacketSize )
      data += chunk
    return data

  def get_device_info( self ):
    packet = self.build_header( ptp.S_HEADER.size, ptp.PACKET_TYPE_COMMAND, ptp.OC_GetDeviceInfo )
    l = self.write( packet )
    assert l == len( packet )
    
    data = self.read()
    ptp_header = ptp.parse_header( data )
    assert ptp_header.len >= ptp.S_HEADER.size
    assert ptp_header.type == ptp.PACKET_TYPE_DATA
    assert ptp_header.code == ptp.OC_GetDeviceInfo
    assert ptp_header.transaction == self.transaction    

    dev_info = ptp.parse_devinfo( data ) 
    
    ack = ptp_obj.read()
    ptp_header = ptp.parse_header( ack )
    assert ptp_header.len == ptp.S_HEADER.size
    assert ptp_header.type == ptp.PACKET_TYPE_RESPONSE
    assert ptp_header.code == ptp.RC_OK
    assert ptp_header.transaction == self.transaction    

    return dev_info

  def open_session( self ):    
    self.session_id = 1
    self.transaction = 0
    
    packet = self.build_header( ptp.S_HEADER.size+Struct('<L').size, ptp.PACKET_TYPE_COMMAND, ptp.OC_OpenSession )
    packet += pack('<L', self.session_id)
     
    l = self.write( packet )
    assert l == len( packet )
        
    data = self.read()
    ptp_header = ptp.parse_header( data ) 
    if ptp_header.code != ptp.RC_OK:
      print('error 0x%x' % ptp_header.code)
      return
    assert ptp_header.len == ptp.S_HEADER.size
    assert ptp_header.type == ptp.PACKET_TYPE_RESPONSE
    assert ptp_header.transaction == self.transaction    
    
    self.transaction += 1

  def close_session( self ):    
    self.session_id = 1
    
    packet = self.build_header( ptp.S_HEADER.size+Struct('<L').size, ptp.PACKET_TYPE_COMMAND, 0x1003 )
    packet += pack('<L', self.session_id)
     
    l = self.write( packet )
    assert l == len( packet )
        
    data = self.read()
    ptp_header = ptp.parse_header( data ) 
    if ptp_header.code != ptp.RC_OK:
      print('error 0x%x' % ptp_header.code)
      return
    assert ptp_header.len == ptp.S_HEADER.size
    assert ptp_header.type == ptp.PACKET_TYPE_RESPONSE
    assert ptp_header.transaction == self.transaction    
    
    self.transaction += 1
  
  def get_macaddress( self ):
    packet = self.build_header( ptp.S_HEADER.size, ptp.PACKET_TYPE_COMMAND, 0x9033 )
         
    l = self.write( packet )
    assert l == len( packet )

    data = self.read()
    #print(hexlify(data))
    ptp_header = ptp.parse_header( data ) 
    assert ptp_header.len == ptp.S_HEADER.size + 6
    assert ptp_header.type == ptp.PACKET_TYPE_DATA
    assert ptp_header.code == 0x9033
    assert ptp_header.transaction == self.transaction  
    
    ack = ptp_obj.read()
    ptp_header = ptp.parse_header( ack )
    assert ptp_header.len == ptp.S_HEADER.size
    assert ptp_header.type == ptp.PACKET_TYPE_RESPONSE
    assert ptp_header.code == ptp.RC_OK
    assert ptp_header.transaction == self.transaction   

    self.transaction += 1
    return data[ptp.S_HEADER.size:] #return mac address, wifi on R6
  
ptp_obj = ptp()
#print(ptp_obj.device.device)

dev_info = ptp_obj.get_device_info() 
'''print('operations_supported')
for op in dev_info['operations_supported']:
  print('0x%x' % op, end=' ')
print()'''
print(dev_info)
  
ptp_obj.open_session()

mac_addr = ptp_obj.get_macaddress()

mac_addr = ptp_obj.get_macaddress()
print('mac_addr', hexlify(mac_addr))

ptp_obj.close_session()
