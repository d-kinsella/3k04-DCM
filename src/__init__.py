from flask import Flask, render_template, request, redirect, url_for, session
import serial

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

# Set up the server
app = Flask(__name__)
app.secret_key = b'!@#$RFBNKOI*&^%RESXCVBNKLOI*&^%ESXCVBNK<BVCDERTYHJ'

# Set up the serial output, port isn't set
# so that the user can input it later
ser = serial.Serial()
ser.baudrate = 19200


# Redirect to the login page
@app.route('/')
def landing_page():
    return redirect(url_for('login'))


# If user navigates to /login (method == get), serve the login
# page. If user is already logged in, redirect to /dcm

# If user submits their login information (method == post),
# check if the user's information is valid. If valid, send to the dcm page.
# If not, send them back to the login page with a notification
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        if "user" not in session:
            return render_template('index.html', failed=False)
        else:
            return redirect(url_for("dcm_landing"))

    if request.method == 'POST':

        # check if login input is valid
        user = check_credentials(request.form['username'], request.form['password'])

        if user:
            session["user"] = user
            return redirect('dcm/')
        else:
            return redirect(url_for('login_failed'))


def check_credentials(username, password):
    # temporary user list until database is implemented
    users = {
        'username': 'password'
    }

    if username in users and users[username] == password:
        return username
    else:
        return False


@app.route('/login/failed', methods=['GET'])
def login_failed():
    return render_template('index.html', failed=True)


@app.route('/logout', methods=['POST'])
def logout():
    session.pop("user")
    return redirect(url_for("landing_page"))


# Show the user the page with dcm settings. Clicking a different mode
# shows a different submission form with the valid parameters (see dcm_home.html)
@app.route('/dcm/', methods=['GET'])
def dcm_landing():
    if "user" not in session:
        return redirect(url_for("landing_page"))
    else:
        return render_template('dcm_home.html', user=session["user"])


# After submitting a form on the dcm page, the results are posted here.
# The parameters are checked if they are within predefined valid ranges, and
# if they are not, send the user a message with which parameters are out of the range.

# TODO: Add serial communication to send the parameters sent to this method to simulink using ser.write()
# TODO: Parameters are accessed with request.form[parameter]
@app.route('/submit-params/<mode>', methods=['POST'])
def submit_params(mode):
    invalid_parameters = check_invalid_parameters(request.form, mode)
    print(invalid_parameters)
    if invalid_parameters:
        return redirect(url_for("submit_status",
                                success_status=False,
                                invalid_parameters=invalid_parameters)
                        )
    # TODO: This is where to put the serial stuff
    print(request.form)
    ser.port = request.form['serial_port']

    return redirect(url_for("submit_status",
                            success_status=True,
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
        if parameters[param] == "" or (int(parameters[param]) < parameter_ranges[param][0] \
                                       or int(parameters[param]) > parameter_ranges[param][1]):
            invalid_parameters += param.replace('_', ' ') + ', '
    return invalid_parameters[:-2]


# Confirm if the user's submission is valid or not
@app.route('/submit-params/result', methods=['GET'])
def submit_status():
    return render_template('dcm_home.html',
                           user=session["user"],
                           success=request.args['success_status'],
                           invalid_parameters=request.args['invalid_parameters'])


if __name__ == '__main__':
    app.run(debug=True)
