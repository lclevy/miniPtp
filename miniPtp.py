'''
miniPtp.py

a simple and portable PTP implementation

Laurent Clevy
'''

import os
import sys
import argparse

#os.environ['PYUSB_DEBUG'] = 'debug'
#os.environ['LIBUSB_DEBUG'] = '4'
import usb.core
import usb.util

from struct import pack, Struct, unpack
from binascii import hexlify, unhexlify
from collections import namedtuple
import yaml

PTP_CLASS_IMAGE = 6

'''
USB transport layer
'''

class usb_tr:
  VENDORID_CANON = 0x04a9
  
  def __init__(self, vendor = VENDORID_CANON): #default vendor id is Canon
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
    #print('idProduct=0x%x' % devs.idProduct)
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

  OC_GetDeviceInfo = 0x1001 
  OC_OpenSession = 0x1002

  RC_OK = 0x2001

  PACKET_TYPE_COMMAND = 1
  PACKET_TYPE_DATA = 2
  PACKET_TYPE_RESPONSE = 3
  
  ptp_dict = dict()
  try:
    stream = open("ptp.yml", 'r')
    ptp_dict = yaml.safe_load(stream)   
  except FileNotFoundError:
      print('file ptp.yml is missing')     

  
  def __init__( self, usb=True, vendor=usb_tr.VENDORID_CANON ):
    self._transaction = 0
    self.vendor = vendor  
    
    if usb:
      self.device = usb_tr( vendor )
    else: # USB is the only transport supported yet
      return None    


  '''
  Parsing Functions
  '''
  def parse_header( data ):
    return ptp.NT_HEADER( *ptp.S_HEADER.unpack_from(data, 0) )

  def parse_string( data ):
    _len = data[0]
    if _len == 0:
      return '', 1
    else:
      return bytes( data[ 1: 1+(_len-1)*2 ] ).decode('utf-16'), 1+_len*2    
      
  def string_len( n ): #return length of ptp string in bytes, given utf-16 len
    if n==0:
      return 1
    else:
       return 1+(n+1)*2    

  def parse_array( data, _type ):
    _len = Struct('<L').unpack_from( data, 0)[0]
    return list( Struct('<%d%s' % (_len, _type)).unpack_from( data, 4 ) ), Struct('<L').size + _len*Struct('%s'%_type).size


  S_DEVICE_INFO_HEADER = Struct('<HLH')

  #section 5.1.1
  def parse_devinfo( data ):
    dev_info = dict()
    ptr = ptp.S_HEADER.size
    
    dev_info['std_version'], dev_info['mtp_vendor_id'], dev_info['mtp_version'] = ptp.S_DEVICE_INFO_HEADER.unpack_from( data, ptr)
    ptr += ptp.S_DEVICE_INFO_HEADER.size
    
    dev_info['mtp_extensions'], size = ptp.parse_string( data[ptr:] )    
    ptr += size

    dev_info['functional_mode'] = Struct('<H').unpack_from(data, ptr)[0]
    ptr += Struct('H').size
    
    dev_info['operations_supported'], size = ptp.parse_array( data[ptr: ], 'H' )
    ptr += size
    
    dev_info['events_supported'], size = ptp.parse_array( data[ptr: ], 'H' )
    ptr += size

    dev_info['device_prop_supported'], size = ptp.parse_array( data[ptr: ], 'H' )
    ptr += size

    dev_info['capture_formats'], size = ptp.parse_array( data[ptr: ], 'H' )
    ptr += size

    dev_info['playback_formats'], size = ptp.parse_array( data[ptr: ], 'H' )
    ptr += size    
 
    dev_info['manufacturer'], size = ptp.parse_string( data[ptr:] )
    ptr += size
    
    dev_info['model'], size = ptp.parse_string( data[ptr:] )
    ptr += size
    
    dev_info['device_version'], size = ptp.parse_string( data[ptr:] )
    ptr += size

    dev_info['serial_number'], size = ptp.parse_string( data[ptr:] )
    ptr += size
        
    return dev_info 


  S_STORAGE_INFO = Struct('<HHHQQL')
  
  def parse_storage_info( data ):
    storage_info = dict()
    
    ptr = ptp.S_HEADER.size
    #header = ptp.S_STORAGE_INFO.unpack_from( data, ptr) 
    for a, b in zip( ptp.S_STORAGE_INFO.unpack_from( data, ptr), [ 'storage_type', 'filesystem_type', 'access_capability', 'max_capacity', 
      'free_space_bytes', 'free_space_objects' ] ):
      storage_info[ b ] = a

    ptr += ptp.S_STORAGE_INFO.size
    storage_info['storage_description'], size = ptp.parse_string( data[ptr: ] )
    ptr +=  ptp.string_len( len(storage_info['storage_description']) )
    
    storage_info['volume_identifier'], size = ptp.parse_string( data[ptr: ] )
    return storage_info


  S_OBJECT_INFO = Struct('<LHHLHLLLLLLLHLL')

  def parse_object_info( data ):
    object_info = dict()
    ptr = ptp.S_HEADER.size
    for a,b in zip( ptp.S_OBJECT_INFO.unpack_from( data, ptr), 
      ['storage_id', 'object_format', 'protection_status', 'object_compr_size', 'thumb_format', 'thumb_compr_size','thumb_pix_w','thumb_pix_h',
      'image_pix_w', 'image_pix_h', 'image_bit_depth', 'parent_obj', 'association_type', 'association_desc', 'seq_number' ] ):
      object_info[ b ] = a
    ptr += ptp.S_OBJECT_INFO.size
    object_info ['filename'], size = ptp.parse_string( data[ptr: ] )
    ptr += size
    object_info ['date_created'], size = ptp.parse_string( data[ptr: ] )
    ptr += size
    object_info ['date_modified'], size = ptp.parse_string( data[ptr: ] )
    ptr += size
    object_info ['keywords'], size = ptp.parse_string( data[ptr: ] )
    #print(object_info)  
    return object_info   
    
    
  S_DEVICE_PROP_DESC = Struct('<HHB')
  
  def parse_property_desc( data ):
    device_prop_desc = dict()
    ptr = ptp.S_HEADER.size
    for a,b in zip( ptp.S_DEVICE_PROP_DESC.unpack_from( data, ptr), 
      ['property_code', 'datatype', 'get_set' ] ):
      device_prop_desc[ b ] = a
    
    ptr += ptp.S_DEVICE_PROP_DESC.size
    if device_prop_desc['datatype']==2: #uint8
      device_prop_desc['default'] = int(data[ptr])
      device_prop_desc['current'] = int(data[ptr+1])
      ptr += 2
    elif device_prop_desc['datatype']==0xffff: #string
      device_prop_desc['default'], size = ptp.parse_string( data[ptr:] )
      ptr += size
      device_prop_desc['current'], size = ptp.parse_string( data[ptr:] )
      ptr += size
    elif device_prop_desc['datatype']==4: #uint16
      device_prop_desc['default'],  device_prop_desc['current'] = Struct('<HH').unpack( data[ptr:ptr+4] )
      ptr += Struct('<HH').size
    elif device_prop_desc['datatype']==6: #uint32
      device_prop_desc['default'],  device_prop_desc['current'] = Struct('<LL').unpack( data[ptr:ptr+8] )
      ptr += Struct('<LL').size
    else:
      return device_prop_desc #ignore end of structure
      
    device_prop_desc['form'] = int(data[ptr])
    return device_prop_desc  

  def print_prop_desc( prop ):
    #{'property_code': 20481, 'datatype': 2, 'get_set': 0, 'default': 17, 'current': 17, 'form': 2}
    #print(prop)
    prop_name = ptp.ptp_dict['property_codes'].get( prop['property_code'], '?' )
    prop_type = ptp.ptp_dict['property_types'].get( prop['datatype'], '?' )
    print( 'property_code: 0x%x/%s,' % (prop['property_code'], prop_name), 'datatype: 0x%x/%s,' % (prop['datatype'],prop_type), 'current:', prop.get('current','n/a') )

  def parse_events( data ):
    ptr = ptp.S_HEADER.size
    
    size, event_code = Struct('<LL').unpack_from(data, ptr)
    events = dict()
    while event_code!=0:
      size, event_code, property_code = Struct('<LLL').unpack_from(data, ptr)
      if event_code not in events:
        events[event_code] = dict()     
      events[event_code][property_code] = (size, event_code, property_code, bytes(data[ptr+12:ptr+size]) )
      #print('%x %x %x %s' % (size, event_code, property_code, bytes(data[ptr+12:ptr+size])) )
      ptr += size
      size, event_code = Struct('<LL').unpack_from(data, ptr)
    return events

    
  def encode_str( s ):
    if len(s)==0:
      return b'\x00'
    else:  
      return pack('B', len(s)) + s.encode('UTF-16LE')  
  
  def zeroterm_str( data ):
    index = data.find(b'\x00')
    if index>=0 :
      return data[:index]
    else:
      return data 
  
  '''
  I/O functions
  '''
  def write(self, data):
    total_sent = 0  
    #print(self.device.in_ep.wMaxPacketSize)
    while total_sent < len(data):
      sent = self.device.out_ep.write( data[total_sent:] )
      total_sent += sent
      #print('sent %x' % sent )
    return total_sent

  def read(self):
    chunk = self.device.in_ep.read( self.device.in_ep.wMaxPacketSize )
    data = chunk
    while len(chunk) == self.device.in_ep.wMaxPacketSize and len(chunk)!=0: #to test = multiple of in_ep.wMaxPacketSize
      chunk = self.device.in_ep.read( self.device.in_ep.wMaxPacketSize )
      data += chunk
    return data

  def get_resp_params( ptp_header, resp ):
    paramLen = (ptp_header.len-ptp.S_HEADER.size) / Struct('<L').size 
    return list ( unpack('<%dL' % paramLen, resp[ptp.S_HEADER.size:] ) )

  '''
  PTP transaction
  '''
  def transaction(self, code, req_params, data_phase=True, senddata=None):

    #request
    _len = ptp.S_HEADER.size + len(req_params)*Struct('<L').size       
    packet = pack( '<L', _len ) + pack('<H', ptp.PACKET_TYPE_COMMAND) + pack('<H', code) + pack('<L', self._transaction)
    parameters = b''.join( [ pack('<L', p) for p in req_params ] )
    l = self.write( packet + parameters)
    assert l == _len

    data = b'' 
    if data_phase:
      if not senddata:
        data = self.read()
        ptp_header = ptp.parse_header( data )
        #print('len=%2x type=%x code=%x trans=%d' %(ptp_header.len, ptp_header.type, ptp_header.code, ptp_header.transaction) )
        assert ptp_header.len >= ptp.S_HEADER.size 
        if ptp_header.type == 3:
          print('Unexpected Response len=0x%02x,' % ptp_header.len, end=' ')
          if ptp_header.code == 0x2001:
            print('Looks like there is no dataphase')
            respParams = ptp.get_resp_params( ptp_header, data )
            return { 'ResponseCode': ptp_header.code, 'Data':bytes(data), 'Parameter':respParams }
          else:  
            ptp.check_rc( ptp_header.code )
            return {}
        else:
          assert ptp_header.code == code

        assert ptp_header.transaction == self._transaction   
      else:  #senddata      
        packet = pack( '<L', ptp.S_HEADER.size+len(senddata) ) + pack('<H', ptp.PACKET_TYPE_DATA) + pack('<H', code) + pack('<L', self._transaction)
        l = self.write( packet + senddata )                 
    
    #response
    #try: 
    response = self.read()
    '''except usb.core.USBError as e:
      print(e)
      self._transaction += 1
      return { 'ResponseCode': 0x2000, 'Data':None, 'Parameter':None }
      '''
    ptp_header = ptp.parse_header( response )
    #print('len=%2x type=%x code=%x trans=%d' %(ptp_header.len, ptp_header.type, ptp_header.code, ptp_header.transaction) )
    assert ptp_header.len >= ptp.S_HEADER.size
    assert ptp_header.type == ptp.PACKET_TYPE_RESPONSE
    assert ptp_header.transaction == self._transaction
    #if ptp_header.len >= ptp.S_HEADER.size: #section 4.7.3 in MTP doc
    respParams = ptp.get_resp_params( ptp_header, response )
    
    self._transaction += 1

    return { 'ResponseCode': ptp_header.code, 'Data':bytes(data), 'Parameter':respParams }
  
  def check_rc( rc ) :
    if rc != 0x2001:
      if rc in ptp.ptp_dict['response_code']:
        print('0x%x' % rc, ptp.ptp_dict['response_code'][rc])
      else:  
        print('0x%x' % rc)          
    return rc == 0x2001
  
  def check_result(resp, respCodeOnly=True):
    rc = resp['ResponseCode']
    ptp.check_rc( rc )
    if not respCodeOnly:
      print('ResponseCode:0x%x,' % rc, 'Data:%s,' % hexlify(resp['Data'][ptp.S_HEADER.size:]), 'Parameter:', [ '0x%x' % p for p in resp['Parameter'] ] )
  
  '''
  PTP commands
  '''  

  def get_device_info( self ):
    data = self.transaction( ptp.OC_GetDeviceInfo, [] )['Data']
    return ptp.parse_devinfo( data ) 

  def open_session( self ):    
    self.session_id = 1
    self._transaction = 0
    
    return self.transaction( ptp.OC_OpenSession, [ self.session_id ], False )

  def close_session( self ):    
    self.session_id = 1
    self.transaction( 0x1003, [ self.session_id ], False )
  
  def get_macaddress( self ):
    res = self.transaction( 0x9033, [] )
    ptp.check_result( res )
    data = res['Data']
    return data[ptp.S_HEADER.size:] #return mac address, wifi on R6

  def get_storage_ids( self ):
    data = self.transaction( 0x1004, [] )['Data']

    _len = Struct('<L').unpack_from(data, ptp.S_HEADER.size)
    return Struct('<%dL' % _len).unpack_from(data, ptp.S_HEADER.size+Struct('<L').size)

    
  def get_storage_info( self, storage_id ):
    data = self.transaction( 0x1005, [ storage_id ], True )['Data']
    return ptp.parse_storage_info( data )

  #only on storage ?
  def get_num_objects( self, storage_id, object_format=0, association=0xffffffff ):
    data = self.transaction( 0x1006, [ storage_id, object_format, association ], False )['Parameter'] # all_formats, all_handles
    return data[0]

  def get_object_handles( self, storage_id, object_format=0, association=0xffffffff ):
    data = self.transaction( 0x1007, [ storage_id, object_format, association ], True )['Data']
    return ptp.parse_array( data[ptp.S_HEADER.size: ], 'L')[0] #only the list

  def get_object_info( self, handle ): 
    data = self.transaction( 0x1008, [ handle ], True )['Data']
    return ptp.parse_object_info( data )

  def get_object( self, handle ): 
    data = self.transaction( 0x1009, [ handle ], True )['Data']
    return data[ptp.S_HEADER.size: ]


  def get_device_prop_desc( self, prop ): 
    data = self.transaction( 0x1014, [ prop ], True )['Data']
    return ptp.parse_property_desc( data )

  def set_prop_device_value( self, prop, value ): 
    res = self.transaction( 0x1016, [ prop ], senddata=value )
    #print(res['ResponseCode'])

  def get_events( self ): 
    self.transaction( 0x9115, [ 1 ], False ) #Canon_SetEventMode
    data = self.transaction( 0x9116, [ 1 ] )['Data'] #Canon_GetEvent
    return ptp.parse_events( data )
   
  def print_operations( ops ): 
    for op in sorted( ops ):
      if op in ptp.ptp_dict['operations_codes']:
        print('0x%x/%s' % (op,ptp.ptp_dict['operations_codes'][op]), end=' ')  
      else:
        print('0x%x' % op, end=' ')
    print()
    
  def print_obj( h, obj, level ):
    print('%s%08x %08x %08x %04x %d %8d %s' % (level*'  ', h, obj['storage_id'], obj['parent_obj'], obj['object_format'], obj['protection_status'], obj['object_compr_size'],obj['filename']) )

  def ls_r( self, storage_id, _handles, level=0 ):
    for h in _handles:
      obj = self.get_object_info( h )
      #print(obj)
      ptp.print_obj( h, obj, level )
      if obj['association_type']==1:
        handles = self.get_object_handles( storage_id, association=h )
        self.ls_r( storage_id, handles, level+1 )

      
if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("-o", "--list-operations", help="list supported operations", action="store_true")
  parser.add_argument("-p", "--list-properties", help="list supported properties", action="store_true")
  parser.add_argument("-d", "--list-properties-description", help="list supported properties", action="store_true")
  parser.add_argument("-i", "--info", help="show device info", action="store_true")
  parser.add_argument("-L", "--list-files", help="list all files", action="store_true")
  parser.add_argument("-g", "--get-file", help="get file by given handler", dest="handler")
  parser.add_argument("-u", "--upload", help="upload file. storage,filename", dest="upload")

  args = parser.parse_args()
    
  try:
    ptp_obj = ptp()
  except ValueError as e:
    print(e)
    sys.exit()    
  #print(ptp_obj.device.device)

  dev_info = ptp_obj.get_device_info() 

  if args.list_operations:
    print('+ operations_supported')
    ptp.print_operations( sorted(dev_info['operations_supported']) )

  if args.list_properties:
    print('+ device_prop_supported')
    for prop in sorted(dev_info['device_prop_supported']):
      if prop in ptp.ptp_dict['property_codes']:
        print('0x%x/%s' % (prop,ptp.ptp_dict['property_codes'][prop]), end=' ')  
      else:
        print('0x%x' % prop, end=' ')
    print()
  print( '+ Model=', dev_info['model'] )
  print( '+ Device_version=', dev_info['device_version'] )

  #print(dev_info)
  print('+ Opening session')
  r = ptp_obj.open_session()
  ptp.check_result(r)
  if r['ResponseCode']!=ptp.RC_OK:
    print('error %x' % r['ResponseCode'])
  else:
    print('Connected') 
      
  #ptp_obj.transaction( 0x9114, [ 1 ], False ) #Canon_SetRemoteMode
  if 0x9116 in dev_info['operations_supported']: #Canon_GetEvent
    events = ptp_obj.get_events()
    print('+ Model_id: 0x%x' % unpack('<L', events[0xc189][0xd116][3] ) )
    if 0xd1d8 in events[0xc189]: print('LensName', ptp.zeroterm_str(events[0xc189][0xd1d8][3]) ) #LensName
    if 0xd125 in events[0xc189]: print('hostname', ptp.zeroterm_str(events[0xc189][0xd125][3]) ) #hostname

  ptp_obj.set_prop_device_value( 0xd406, b'/'+'Windows/10.0.19045 MTPClassDriver/10.0.19041.0\x00'.encode('UTF-16LE') )
  
  '''
  # PTP_SetObjectProtection
  r = ptp_obj.transaction( 0x1012, [ 0x01a0aee1, 0 ], False ) #[handle, new_protection]. 0 = no protection, 1 = read only. Worked on Ixus 180
  print( r, r['ResponseCode']==0x2001 )
  '''

  if args.upload: #-u 0x00010001,ssdp.txt
    s, filename = args.upload.split(',')
    storage = int(s, 16)
    parent = 0 # MUST be 0, instead we have error 0x2006 = ParameterNotSupported
    storage = 0 # optional, can be 0
    object_format = 0xbf01 # firmware file .FI2, mandatory to avoid 0x200f =  'access denied' !
    print('Try to upload', filename)   

    obj_data = open(filename, 'rb').read()
    base_filename = os.path.basename(filename)
    base_filename += '\x00'
    # PTP_SendObjectInfo    
    obj_info = ptp.S_OBJECT_INFO.pack( storage, object_format, 0, len(obj_data), 0, 0, 0, 0, 0, 0, 0, parent, 0, 0, 0) + ptp.encode_str(base_filename) + ptp.encode_str('')+ptp.encode_str('')+ptp.encode_str('')
    r = ptp_obj.transaction( 0x100c, [ storage, parent  ], senddata=obj_info ) 
    if r['ResponseCode']!=ptp.RC_OK:
      print('error %x' % r['ResponseCode']) #sometimes, we've got 0x2006 when overwriting existing files. reboot Camera fixes this
    else:  
      storage, parent_handle, new_handle = r['Parameter'] # [ storage, 0, handle ]   
      print( 'PTP_SendObjectInfo returned:', 'storage = 0x%x'% storage, 'and', 'handle = 0x%x' % new_handle)
      #after we should use SendObject  
      r = ptp_obj.transaction( 0x100d, [ ], senddata=obj_data ) #PTP_SendObject 
      if r['ResponseCode']!=0x2001:
        print('error %x' % r['ResponseCode'])
      else:
        print('Done')
        
  if 0x9033 in dev_info['operations_supported']: #GetMacAddress
    mac_addr = ptp_obj.get_macaddress()
    print('+ Mac_addr', hexlify(mac_addr))
    
  if args.list_properties_description:
    print('+ properties supported')
    for desc in sorted(dev_info['device_prop_supported']):
      #print( ptp_obj.get_device_prop_desc( desc ) )
      ptp.print_prop_desc( ptp_obj.get_device_prop_desc( desc ) )
  
  if args.list_files:   
    print('+ Storage_IDs')
    storage_ids = ptp_obj.get_storage_ids()
    for id in storage_ids:
      print( ptp_obj.get_num_objects( id ) ) 
      storage_info = ptp_obj.get_storage_info( id )
      print( storage_info )
      handles = ptp_obj.get_object_handles( id )
      ptp_obj.ls_r( id, handles, 1 )  

  if args.handler:
    obj = ptp_obj.get_object_info( int(args.handler, 16) )
    #print(obj)
    print('transfering %s (%d bytes)...' % (obj['filename'], obj['object_compr_size']))
    data = ptp_obj.get_object( int(args.handler, 16) )
    with open( obj['filename'], 'wb' ) as file:
      file.write(data)
      print('done')

  ptp_obj.close_session()
