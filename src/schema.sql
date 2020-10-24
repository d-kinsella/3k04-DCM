CREATE TABLE users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE parameters(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mode TEXT DEFAULT "None",
    lower_rate_limit INTEGER,
    upper_rate_limit INTEGER,
    atrial_amplitude INTEGER,
    atrial_pulse_width INTEGER,
    arp INTEGER,
    ventricle_amplitude INTEGER,
    ventricle_pulse_width INTEGER,
    vrp INTEGER
)