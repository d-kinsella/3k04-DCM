import sqlite3
from flask import current_app, g


def get_num_users():
    cursor = get_db().execute('SELECT COUNT(*) FROM users')
    result = cursor.fetchone()
    cursor.close()
    print('Number of users: %s' % result[0])
    return result[0]


def get_user_params(user):
    cursor = get_db().execute('SELECT * FROM parameters WHERE id=(SELECT id FROM users WHERE username=?)', (user,))
    result = cursor.fetchone()
    cursor.close()
    return result


def query_user(user):
    cursor = get_db().execute('SELECT * FROM users WHERE username=?', (user,))
    result = cursor.fetchone()
    cursor.close()
    return result


def create_parameters(parameter_data, user):
    db = get_db()
    cursor = db.cursor()

    sql_query = '''UPDATE parameters
                SET mode=?,
                lower_rate_limit=?,
                upper_rate_limit=?,
                atrial_amplitude=?,
                atrial_pulse_width=?,
                arp=?,
                ventricle_amplitude=?,
                ventricle_pulse_width=?,
                vrp=?
                WHERE id=(SELECT id FROM users WHERE username=?)'''
    parameters = parameter_data + (user,)
    cursor.execute(sql_query, parameters)
    db.commit()


def create_user(user_data):
    db = get_db()
    sql_query = 'INSERT INTO users(' \
                'username,password' \
                ')VALUES(?,?)'
    cursor = db.cursor()
    cursor.execute(sql_query, user_data)
    db.commit()

    db = get_db()
    sql_query = 'INSERT INTO parameters(' \
                'mode,lower_rate_limit,upper_rate_limit,atrial_amplitude,' \
                'atrial_pulse_width,arp,ventricle_amplitude,ventricle_pulse_width,vrp' \
                ')VALUES(?,?,?,?,?,?,?,?,?)'
    cursor = db.cursor()
    cursor.execute(sql_query, ("", "", "", "", "", "", "", "", ""))

    db.commit()


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def init_db(app):
    with app.app_context():
        db = get_db()

        with app.open_resource('./schema.sql') as schema:
            try:
                db.executescript(schema.read().decode('utf8'))
            except sqlite3.OperationalError as e:
                print(e)
        db.commit()
