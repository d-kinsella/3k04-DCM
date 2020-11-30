import json
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import serial
import database as db
import utils
#import serial_utils
import dummy_serial_utils as serial_utils

parameter_ranges = {
    'lower_rate_limit': {"range": [50, 90], "type": int},
    'atrial_amplitude': {"range": [65, 75], "type": int},
    'atrial_pulse_width': {"range": [1, 30], "type": int},  # ms
    'atrial_sensitivity': {"range": [25, 100], "type": float},
    'arp': {"range": [150, 500], "type": int},
    'ventricle_amplitude': {"range": [65, 75], "type": int},
    'ventricle_pulse_width': {"range": [1, 30], "type": int},
    'ventricle_sensitivity': {"range": [25, 100], "type": float},
    'vrp': {"range": [150, 500], "type": int},
    'max_sens_rate': {"range": [50, 175], "type": int},
    'activity_threshold': {"range": [0, 200], "type": int},
    'reaction_time': {"range": [0, 200], "type": int},
    'response_factor': {"range": [1, 20], "type": int},
    'recovery_time': {"range": [0, 200], "type": int},
    'fixed_av_delay': {'range': [70, 300], "type": int}
}

# Set up the server
app = Flask(__name__)
app.secret_key = b'!@#$RFBNKOI*&^%RESXCVBNKLOI*&^%ESXCVBNK<BVCDERTYHJ'
app.config['DATABASE'] = '.\\data\\db.sql'
db.init_db(app)

# Set up the serial output, port isn't set
# so that the user can input it later
ser = serial.Serial()
ser.baudrate = 115200


# Redirect to the login page
@app.route('/')
def landing_page():
    return redirect(url_for('login'))


# Add a new user and add them to the database
# If database is full or the user already exists then the registration will fail
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "GET":
        return render_template('signup.html', signup_failed=False)

    if request.method == "POST":
        if db.get_num_users() >= 10:
            return render_template('signup.html', signup_failed=True, error_msg="too many users registered")
        if request.form['username'] and request.form['password']:
            try:
                db.create_user((request.form['username'], request.form['password']))
                return redirect(url_for('login'))
            except sqlite3.IntegrityError as e:
                print(e)
                return render_template('signup.html', signup_failed=True,
                                       error_msg="unsuccessful registration, try again")
        return render_template('signup.html', signup_failed=True, error_msg="no username or password entered")


# If user navigates to /login (method == get), serve the login
# page. If user is already logged in, redirect to /dcm

# If user submits their login information (method == post),
# check if the user's information is valid. If valid, send to the dcm page.
# If not, send them back to the login page with a notification
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        if "user" not in session:
            return render_template('index.html',
                                   login_failed=
                                   False if 'login_failed' not in request.args
                                   else request.args['login_failed']
                                   )
        else:
            return redirect(url_for("dcm_view"))

    if request.method == 'POST':

        # check if login input is valid
        user = utils.check_credentials(request.form['username'], request.form['password'])

        if user:
            session["device_id"] = 0
            session["user"] = user
            return redirect(url_for("dcm_view"))
        else:
            return redirect(url_for('login', login_failed=True))


@app.route('/logout', methods=['POST'])
def logout():
    session.pop("user")
    session.pop("device_id")
    return redirect("/")


@app.route('/connection_update', methods=['POST'])
def connect():
    session["serial_port"] = request.form["serial_port"]
    ser.port = session["serial_port"]
    try:
        session['device_id'] = serial_utils.get_device_id(ser)
    except serial.serialutil.SerialException:
        session['device_id'] = None
        session["serial_port"] = "Failed To Connect"
    return redirect("/dcm")


# Show the user the page with dcm settings. Clicking a different mode
# shows a different submission form with the valid parameters (see dcm.html)
@app.route('/dcm', methods=['GET'])
def dcm_view():
    if "user" not in session:
        return redirect(url_for("landing_page"))
    else:
        device_id = None if "device_id" not in session else session["device_id"]
        user_stored_params = db.get_user_params(session["user"], device_id)
        submission_success = None if 'submission_success' not in request.args else request.args['submission_success']
        invalid_parameters = None if 'invalid_parameters' not in request.args else request.args['invalid_parameters']
        serial_port = "None" if "serial_port" not in session else session["serial_port"]
        return render_template('dcm.html',
                               device_id=device_id,
                               user=session["user"],
                               stored_params=user_stored_params,
                               submission_success=submission_success,
                               invalid_parameters=invalid_parameters,
                               serial_port=serial_port,
                               parameter_ranges=parameter_ranges
                               )


# After submitting a form on the dcm page, the results are posted here.
# The parameters are checked if they are within predefined valid ranges, and
# if they are not, send the user a message with which parameters are out of the range.

# TODO: Add serial communication to send the parameters sent to this method to simulink using ser.write()
# TODO: Parameters are accessed with request.form[parameter]
@app.route('/submit-params/<mode>', methods=['POST'])
def submit_params(mode):
    invalid_parameters = utils.check_invalid_parameters(request.form, mode, parameter_ranges)
    print("invalid_parameters")
    print(invalid_parameters)
    if invalid_parameters or not session['device_id']:
        return redirect(url_for("dcm_view",
                                submission_success=False,
                                invalid_parameters=invalid_parameters)
                        )
    (parameters, parameter_dict) = utils.build_parameters(mode, request.form)
    db.create_parameters(parameters, session['user'], session['device_id'])

    try:
        if not serial_utils.set_device_params(ser, parameter_dict):
            raise serial.serialutil.SerialException
    except serial.serialutil.SerialException:
        session['device_id'] = None
        return redirect(url_for("dcm_view",
                                submission_success=False,
                                invalid_parameters=invalid_parameters)
                        )
    # TODO: This is where to put the serial communication
    print(request.form)

    return redirect(url_for("dcm_view",
                            submission_success=True,
                            invalid_parameters=invalid_parameters)
                    )


@app.route('/get_egram_data', methods=['GET'])
def get_egram_data():
    egram_data = 0
    try:
        egram_data = serial_utils.receive_egram_transmission(ser)
        serial_success = 200
    except serial.serialutil.SerialException:
        serial_success = 500
    return app.response_class(
        response=json.dumps(
            {'status': serial_success, 'atrium': egram_data['atrium'], 'ventricle': egram_data['ventricle']}),
        mimetype='application/json'
    )


if __name__ == '__main__':
    app.run(debug=True)
