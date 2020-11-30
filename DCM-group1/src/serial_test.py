import time

import serial
import serial_utils
import struct

ser = serial.Serial()
ser.port = input("Enter Serial Port: ")
ser.baudrate = 115200
ser.timeout = 2


## TEST GET_DEVICE_ID ##
def test_get_device_id():
    return serial_utils.get_device_id(ser)


## TEST SET_DEVICE_PARAMS ##
def test_set_device_params():
    param_inputs = {
        'lower_rate_limit': 2,
        'atrial_pulse_width': 3,
        'ventricle_pulse_width': 4,
        'arp': 5,
        'vrp': 6,
        'atrial_amplitude': 7,
        'ventricle_amplitude': 8,
        'response_factor': 10,
        'max_sens_rate': 11,
        'av_delay': 12,
        'activity_threshold': 13,
        'mode': "DOOR",
        'ventricle_sensitivity': 1.5,
        'atrial_sensitivity': 1.6
    }

    return serial_utils.set_device_params(ser, param_inputs), expected_echo


## TEST START_EGRAM_TRANSMISSION FOR BOTH ##
def test_recieve_egram_transmission_data():
    egram_data = serial_utils.receive_egram_transmission(ser)

    return egram_data


## TEST START_EGRAM_TRANSMISSION FOR BOTH ##
def test_receive_rapid_egram_transmission_data():
    results = []
    for i in range(50):
        results.push = serial_utils.receive_egram_transmission(ser)
        time.sleep(25 / 1000)
    return results


if __name__ == '__main__':
    print("Test 1: Get Device Id")
    device_id = test_get_device_id()
    print("Device Id: " + str(device_id))
    print("Passed" if device_id == 11 else "Failed")

    print("Test 2: Set Device Params")
    device_params, expected_params = test_set_device_params()
    print("Echoed params:")
    print(device_params)
    print("Passed" if device_params == expected_params else "Failed")

    print("Test 3: Receive  Egram")
    transmission = test_recieve_egram_transmission_data()
    print("Passed" if type(transmission["atrium"]) == float and type(transmission["ventricle"]) == float else "Failed")

    print("Test 4: Receive  Rapid Egram")
    rapid_results = test_receive_rapid_egram_transmission_data()
    print("Passed" if len(rapid_results) == 50 else "Failed")
