import database as db


def check_credentials(username, password):
    check_username = db.query_user(username)
    if check_username and check_username['password'] == password:
        return username
    else:
        return False


def check_invalid_parameters(parameters, mode, parameter_ranges):
    invalid_parameters = ""

    for param in parameters:
        try:
            param_num = float(parameters[param])
        except ValueError:
            invalid_parameters += param.replace('_', ' ') + ', '
            continue

        if parameters[param] == "" or \
                (param_num < parameter_ranges[param]['range'][0] or
                 param_num > parameter_ranges[param]['range'][1]):
            invalid_parameters += param.replace('_', ' ') + ', '
    return invalid_parameters[:-2]


def get_mode_bytes(mode):
    mode_byte_out = b''
    if "AOO" in mode:
        mode_byte_out = b'\x01'
    elif "AAI" in mode:
        mode_byte_out = b'\x03'

    elif "VOO" in mode:
        mode_byte_out = b'\x00'

    elif "VVI" in mode:
        mode_byte_out = b'\x02'

    elif "DOO" in mode:
        mode_byte_out = b'\x04'

    if "R" in mode:
        mode_byte_out = bytes([int.from_bytes(mode_byte_out, byteorder='big') + 5])
    return mode_byte_out


def build_parameters(mode, form):
    print(form)
    parameters = (mode, form['lower_rate_limit'], '')
    parameter_dict = {"mode": mode}
    if "AOO" in mode:
        parameters = parameters + (form['atrial_amplitude'], form['atrial_pulse_width'], '', '', '', '', '', '', '',
                                   '', '', '', '', '', '', '', '')
    elif "AAI" in mode:
        parameters = parameters + \
                     (form['atrial_amplitude'], form['atrial_pulse_width'], form['atrial_sensitivity'], form['arp'],
                      '', '', '', '', '', '', '', '', '', '', '', '', '')
    elif "VOO" in mode:
        parameters = parameters + \
                     ('', '', '', '', '', form['ventricle_amplitude'], form['ventricle_pulse_width'], '', '', '', '',
                      '', '', '', '', '', '')
    elif "VVI" in mode:
        parameters = parameters + \
                     ('', '', '', '', '', form['ventricle_amplitude'], form['ventricle_pulse_width'],
                      form['ventricle_sensitivity'], form['vrp'], '', '',
                      '', '', '', '', '', '')
    elif "DOO" in mode:
        parameters = parameters + \
                     (form['atrial_amplitude'], form['atrial_pulse_width'], '', '', '', form['ventricle_amplitude'],
                      form['ventricle_pulse_width'], '', '', '', '', '', form['fixed_av_delay'], '', '', '', '')
    if "R" in mode:
        parameters = parameters + (form['max_sens_rate'], '', '',
                                   form['response_factor'], '')
    else:
        parameters = parameters + ('', '', '', '', '')

    parameter_mapping = ("lower_rate_limit", "upper_rate_limit", 'atrial_amplitude', 'atrial_pulse_width',
                         'atrial_sensitivity', 'arp', 'pvarp', 'ventricle_amplitude', 'ventricle_pulse_width',
                         'ventricle_sensitivity', 'vrp', 'pvarp_ext', 'hysteresis', 'rate_smoothing', 'fixed_av_delay',
                         'dynamic_av_delay', 'atr_duration', 'atr_fall_mode', 'atr_fall_time', 'max_sens_rate',
                         'activity_threshold', 'reaction_time', 'response_factor', 'recovery_time')
    for i in range(1, len(parameters) - 1):
        param_num = 0
        if parameters[i] != "":
            try:
                param_num = int(parameters[i])
            except ValueError:
                param_num = float(parameters[i])
        parameter_dict[parameter_mapping[i - 1]] = param_num if parameters[i] != "" else 0
    return parameters, parameter_dict
