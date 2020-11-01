CREATE TABLE parameters(
    parameter_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    device_id INTEGER,
    mode TEXT DEFAULT "None",
    lower_rate_limit INTEGER,
    upper_rate_limit INTEGER,
    atrial_amplitude INTEGER,
    atrial_pulse_width INTEGER,
    arp INTEGER,
    ventricle_amplitude INTEGER,
    ventricle_pulse_width INTEGER,
    vrp INTEGER,
    UNIQUE(username, device_id)
);