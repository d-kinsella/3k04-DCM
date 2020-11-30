import serial
import time
import struct
import utils

def get_device_id(ser):
    bytes_out = b'\x16\x22' + b'\00' * 40
    ser.open()
    ser.write(bytes_out)
    bytes_in = ser.read(58)
    device_id = int.from_bytes(bytes_in[24:25], byteorder="little")
    ser.close()
    return device_id


def set_device_params(ser, params):
    print(params)
    bytes_header = b'\x16\x55'
    bytes_out = b'\x00' + utils.get_mode_bytes(params['mode'])
    bytes_out += params['lower_rate_limit'].to_bytes(2, byteorder='big')
    bytes_out += params['atrial_pulse_width'].to_bytes(2, byteorder='big')
    bytes_out += params['ventricle_pulse_width'].to_bytes(2, byteorder='big')
    bytes_out += params['arp'].to_bytes(2, byteorder='big')
    bytes_out += params['vrp'].to_bytes(2, byteorder='big')
    bytes_out += params['atrial_amplitude'].to_bytes(2, byteorder='big')
    bytes_out += params['ventricle_amplitude'].to_bytes(2, byteorder='big')
    bytes_out += params['response_factor'].to_bytes(2, byteorder='big')
    bytes_out += params['max_sens_rate'].to_bytes(2, byteorder='big')
    bytes_out += params['fixed_av_delay'].to_bytes(2, byteorder='big')
    bytes_out += (1).to_bytes(2, byteorder='big')
    bytes_out += struct.pack('!d', params["ventricle_sensitivity"])
    bytes_out += struct.pack('!d', params["atrial_sensitivity"])

    expected_echo = b''
    for param in params:
        if param != "mode" and "sensitivity" not in param:
            expected_echo += params[param].to_bytes(2, byteorder='big')
        elif "sensitivity" in param:
            expected_echo += struct.pack('!f', params[param])
        else:
            expected_echo += b'\x00' + utils.get_mode_bytes(params[param])

    ser.open()
    ser.write(bytes_header + bytes_out)
    echoed_params = ser.read(58)
    ser.close()
    print(echoed_params)
    return echoed_params == echoed_params


def receive_egram_transmission(ser):
    bytes_out = b'\x16\x22' + b'\00' * 40
    ser.open()
    ser.write(bytes_out)
    bytes_in = ser.read(58)
    print(bytes_in)
    egram_data = {'atrium': struct.unpack('!d', bytes_in[-8:])[0],
                  'ventricle': struct.unpack('!d', bytes_in[-16:])[-8]}
    ser.close()
    return egram_data



