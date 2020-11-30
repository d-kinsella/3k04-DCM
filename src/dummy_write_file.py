import random
import struct


def get_device_id(ser):
    bytes_out = b'\x16\x22' + b'\00' * 40
    ser.open()
    ser.write(bytes_out)
    bytes_in = ser.read(58)
    device_id = int.from_bytes(bytes_in[24:25], byteorder="little")
    ser.close()
    return device_id


def set_device_params(ser, params):
    return True


def receive_egram_transmission(ser):
    bytes_out = b'\x16\x22' + b'\00' * 40
    ser.open()
    ser.write(bytes_out)
    bytes_in = ser.read(58)
    print(bytes_in[-8:])
    print(bytes_in[-16:-8])

    print(struct.unpack(bytes_in[-8:]))
    print(struct.unpack(bytes_in[-16:-8]))
    egram_data = {'atrium': struct.unpack('<d', bytes_in[-8:]),
                  'ventricle': struct.unpack('<d', bytes_in[-16:])}
    ser.close()
    return egram_data
