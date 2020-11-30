import random


def get_device_id(ser):
    return 1


def set_device_params(ser, params):
    return True


def receive_egram_transmission(ser):
    egram_data = {'atrium': random.random() * 5, 'ventricle': random.random() * 5}
    return egram_data
