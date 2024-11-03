import logging

import streamlit as st

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

connection = None
address = None

if st.session_state.get("connection") == None and st.session_state.get("address")== None:
    st.error("Please connect to the sensor from the Home page")
else:
    connection = st.session_state.connection
    address = st.session_state.address

def save_settings():
    command_save = "77 04 {} 0A 0E".format(address)
    connection.write(convert_command(command_save)  )
    st.success("Setting Saved")

# Serial Functions
def convert_command(command):
    return bytes.fromhex(command)
#
def calculate_checksum(hex_command: list):
    command_bytes = hex_command[1:]
    # Convert strings to int
    command = [int(a, 16) for a in command_bytes]

    # Calculate the sum of bytes modulo 256 checksum
    checksum = sum(command) % 256

    # Return checksum as a hexadecimal string
    return f"{checksum:02X}"



st.subheader("Set")

def set_angle():
    set_alarm_angle = ["77", "08", address, "20"]

    set_angle_bytes = {
        "+X": "00",
        "+Y": "01",
        "-X": "02",
        "-Y": "03"
    }
    
    c1, c2 = st.columns(2)
    selected_option = c1.selectbox(
        'Alarm Angle',
        ('+X', '-X', '+Y', "-Y")
    )
    select_sign = c2.selectbox(
        "Angle Sign",
        ("Positive", "Negative")
    )

    angle_degree = st.number_input("Enter the Angle", value=000, max_value=180)
    decimal_degree = st.number_input("Enter the decimal Angle", value=00, max_value=99)
    
    col1, col2 = st.columns(2)
    if col1.button("Set"):
        process_set_command(set_alarm_angle, set_angle_bytes, selected_option, angle_degree, decimal_degree, select_sign)
    if col2.button("Save Settings"):
        save_settings()

def process_set_command(command: list, set_angle_bytes, selected_axis, angle_degree, decimal_degree, select_sign):
    logger.info(f"Setting alarm angle for {selected_axis}")
    base_set_command = []
    base_set_command = command.copy()
    sign = "0" 
    if select_sign == "Positive":
        sign = "0"
    if select_sign == "Negative":
        sign = "1"
    # zfill the angle degree
    full_angle_degree = str(angle_degree).zfill(3)
    selected_axis_byte = set_angle_bytes[selected_axis]
    axis_byte = selected_axis_byte
    angle_byte = full_angle_degree[-2:]
    signed_byte = f"{sign}{full_angle_degree[0]}"
    base_set_command.append(axis_byte)
    base_set_command.append(signed_byte)
    base_set_command.append(angle_byte)
    base_set_command.append(str(decimal_degree).zfill(2))
    # Calculate Checksum
    checksum = calculate_checksum(base_set_command)
    base_set_command.append(checksum)
    logger.info(f"Final command for {selected_axis} = {base_set_command}")
    connection.write(convert_command(" ".join(base_set_command)))



def set_angle_on_time():
    angle_on_time_command = ["77", "07", address, "23"]
    st.subheader("Delay ON Time")

    on_angle_bytes = {
        "+X": "00",
        "+Y": "04",
        "-X": "02",
        "-Y": "06"
    }
    
    c1, c2, c3 = st.columns(3)
    selected_option = c1.selectbox(
        'Alarm Angle',
        ('+X', '-X', '+Y', "-Y"),
        key="delay"
    )
    
    seconds = c2.selectbox(
        "Select Seconds",
        tuple(range(60)),
        key="delay sec"
    )
    miliseconds = c3.selectbox(
        "Select Miliseconds",
        tuple(range(60)),
        key="delay mili"
    )
    co1, co2 = st.columns(2)
    if co1.button("Set", key="set on"):
        process_on_command(
            angle_on_time_command,
            selected_option,
            on_angle_bytes,
            seconds,
            miliseconds,
        )
    if co2.button("Save Settings", key="set on save"):
        save_settings()
    
def process_on_command(command, axis, on_angle_byte, seconds, miliseconds):
    base_command = []
    base_command = command.copy()
    axis_byte = on_angle_byte[axis]
    base_command.append(axis_byte)
    base_command.append(str(seconds).zfill(2))
    base_command.append(str(miliseconds).zfill(2))
    # Calculate Checksum
    checksum = calculate_checksum(base_command)
    base_command.append(checksum)
    logger.info(f"Final command for set on delay {axis} = {base_command}")
    connection.write(convert_command(" ".join(base_command)))

def set_angle_off_time():
    angle_off_time_command = ["77", "07", address, "23"]
    st.subheader("Delay OFF Time")

    on_angle_bytes = {
        "+X": "01",
        "+Y": "05",
        "-X": "03",
        "-Y": "07"
    }
    
    c1, c2, c3 = st.columns(3)
    selected_option = c1.selectbox(
        'Alarm Angle',
        ('+X', '-X', '+Y', "-Y"),
        key="delay off"
    )
    
    seconds = c2.selectbox(
        "Select Seconds",
        tuple(range(60)),
        key="delay sec off"
    )
    miliseconds = c3.selectbox(
        "Select Miliseconds",
        tuple(range(60)),
        key="delay mili off"
    )
    co1, co2 = st.columns(2)
    if co1.button("Set", key="set off"):
        process_on_command(
            angle_off_time_command,
            selected_option,
            on_angle_bytes,
            seconds,
            miliseconds,
        )
    if co2.button("Save Settings", key="set off save"):
        save_settings()
    
def process_on_command(command, axis, on_angle_byte, seconds, miliseconds):
    base_command = []
    base_command = command.copy()
    axis_byte = on_angle_byte[axis]
    base_command.append(axis_byte)
    base_command.append(str(seconds).zfill(2))
    base_command.append(str(miliseconds).zfill(2))
    # Calculate Checksum
    checksum = calculate_checksum(base_command)
    base_command.append(checksum)
    logger.info(f"Final command for set on delay {axis} = {base_command}")
    connection.write(convert_command(" ".join(base_command)))




if connection and address:
    set_angle()
    st.divider()
    set_angle_on_time()
    st.divider()
    set_angle_off_time()
