from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import serial
import database as db

# Placeholder parameter ranges
parameter_ranges = {
    "lower_rate_limit": [0, 200],
    "upper_rate_limit": [0, 200],
    "atrial_amplitude": [0, 200],
    "atrial_pulse_width": [0, 200],
    "arp": [0, 200],
    "ventricle_amplitude": [0, 200],
    "ventricle_pulse_width": [0, 200],
    "vrp": [0, 200]
}

# Placeholder device id
dummy_device_id = 100000

# Set up the server
app = Flask(__name__)
app.secret_key = b'!@#$RFBNKOI*&^%RESXCVBNKLOI*&^%ESXCVBNK<BVCDERTYHJ'
app.config['DATABASE'] = '.\\data\\db.sql'
db.init_db(app)

# Set up the serial output, port isn't set
# so that the user can input it later
ser = serial.Serial()
ser.baudrate = 19200


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
                return render_template('signup.html', signup_failed=True, error_msg="user already exists, try with a different username")
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
        user = check_credentials(request.form['username'], request.form['password'])

        if user:
            session["user"] = user
            return redirect(url_for("dcm_view"))
        else:
            return redirect(url_for('login', login_failed=True))


def check_credentials(username, password):
    check_username = db.query_user(username)
    if check_username and check_username['password'] == password:
        return username
    else:
        return False


@app.route('/logout', methods=['POST'])
def logout():
    session.pop("user")
    session.pop("device_id")
    return redirect("/")


# Show the user the page with dcm settings. Clicking a different mode
# shows a different submission form with the valid parameters (see dcm.html)
@app.route('/dcm', methods=['GET'])
def dcm_view():
    if "user" not in session:
        return redirect(url_for("landing_page"))
    else:
        session['device_id'] = get_device_id()
        user_stored_params = db.get_user_params(session["user"], session["device_id"])
        submission_success = None if 'submission_success' not in request.args else request.args['submission_success']
        invalid_parameters = None if 'invalid_parameters' not in request.args else request.args['invalid_parameters']
        return render_template('dcm.html',
                               device_id=session['device_id'],
                               user=session["user"],
                               stored_params=user_stored_params,
                               submission_success=submission_success,
                               invalid_parameters=invalid_parameters
                               )


def get_device_id():
    # TODO Serial identification of connected device
    return dummy_device_id


# After submitting a form on the dcm page, the results are posted here.
# The parameters are checked if they are within predefined valid ranges, and
# if they are not, send the user a message with which parameters are out of the range.

# TODO: Add serial communication to send the parameters sent to this method to simulink using ser.write()
# TODO: Parameters are accessed with request.form[parameter]
@app.route('/submit-params/<mode>', methods=['POST'])
def submit_params(mode):
    invalid_parameters = check_invalid_parameters(request.form, mode)
    print("invalid_parameters")
    print(invalid_parameters)
    if invalid_parameters or not session['device_id']:
        return redirect(url_for("dcm_view",
                                submission_success=False,
                                invalid_parameters=invalid_parameters)
                        )
    if mode[0] == 'A':
        parameters = (
            mode,
            request.form['lower_rate_limit'],
            request.form['upper_rate_limit'],
            request.form['atrial_amplitude'],
            request.form['atrial_pulse_width'],
            request.form['arp'],
            '',
            '',
            ''
        )
    elif mode[0] == 'V':
        parameters = (
            mode,
            request.form['lower_rate_limit'],
            request.form['upper_rate_limit'],
            '',
            '',
            '',
            request.form['ventricle_amplitude'],
            request.form['ventricle_pulse_width'],
            request.form['vrp']
        )
    db.create_parameters(parameters, session['user'], session['device_id'])

    # TODO: This is where to put the serial communication
    print(request.form)
    ser.port = request.form['serial_port']

    return redirect(url_for("dcm_view",
                            submission_success=True,
                            invalid_parameters=invalid_parameters)
                    )


def check_invalid_parameters(parameters, mode):
    invalid_parameters = ""
    parameters_to_check = []
    if mode in ["AOO", 'AAI']:
        parameters_to_check = \
            ["lower_rate_limit", "upper_rate_limit",
             "atrial_amplitude", "atrial_pulse_width",
             "arp"]
    elif mode in ["VOO", 'VVI']:
        parameters_to_check = \
            ["lower_rate_limit", "upper_rate_limit",
             "ventricle_amplitude", "ventricle_pulse_width",
             "vrp"]

    for param in parameters_to_check:
        if parameters[param] == "" or not parameters[param].isdecimal() or \
                (int(parameters[param]) < parameter_ranges[param][0] or
                 int(parameters[param]) > parameter_ranges[param][1]):
            invalid_parameters += param.replace('_', ' ') + ', '
    return invalid_parameters[:-2]


if __name__ == '__main__':
    app.run(debug=True)
