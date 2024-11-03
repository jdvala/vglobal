import logging
import time

import streamlit as st

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

connection = None
address = None

commands = {
   "query_zero_type": "77 04 {} 0D 11",
}

if st.session_state.get("connection") == None and st.session_state.get("address")== None:
    st.error("Please connect to the sensor from the Home page")
else:
    connection = st.session_state.connection
    address = st.session_state.address

# Serial Functions
def convert_command(command):
    return bytes.fromhex(command)

def _parse_zero_type(bytes):
    zero_type_response = ""
    zero_type_response = ' '.join(hex(byte)[2:].zfill(2) for byte in bytes)
    if zero_type_response:
        zero_type_response_splited = zero_type_response.split(" ")
        final_zero_type_num = zero_type_response_splited[-2]
        if final_zero_type_num == "00":
            st.markdown(f"**Zero Type**: :green[Absolute]")
        elif final_zero_type_num == "FF".lower():
            st.markdown(f"**Zero Type**: :red[Relative]")

def calculate_checksum(hex_command: list):
    command_bytes = hex_command[1:]
    # Convert strings to int
    command = [int(a, 16) for a in command_bytes]

    # Calculate the sum of bytes modulo 256 checksum
    checksum = sum(command) % 256

    # Return checksum as a hexadecimal string
    return f"{checksum:02X}"


def query_zero_type():
    current_command = commands["query_zero_type"].format(address)   
    converted_command = convert_command(command=current_command)
    if connection:
        connection.write(converted_command)
        time.sleep(0.1)
        zero_type = connection.read_all()
        _parse_zero_type(zero_type)

def parse_angle(angle):
    angle_hex = ' '.join(hex(byte)[2:].zfill(2) for byte in angle)
    split_angle_hex = angle_hex.split(" ")
    if split_angle_hex:
        if split_angle_hex[5] == "10":
            return f"-{split_angle_hex[6]}&deg;"
        else:
            return f"{split_angle_hex[6]}&deg;"
        
def _parse_angle_time(angle):
    angle_hex = ' '.join(hex(byte)[2:].zfill(2) for byte in angle)
    split_angle_hex = angle_hex.split(" ")
    if split_angle_hex:
        return f"{split_angle_hex[5]} seconds {split_angle_hex[6]} miliseconds"

base_alarm_angle_command = ["77", "05", address, "21"]

angle_bytes = {
    "+X": "00",
    "+Y": "01",
    "-X": "02",
    "-Y": "03"
}

def process_alarm_angle_command(base_alarm_command: list, angle_value: str, angle_byte: str):
    logger.info(f"Base command found for {angle_value}: {base_alarm_command}")
    tmp_command = []
    tmp_command = base_alarm_command.copy()
    tmp_command.append(angle_byte)
    checksum = calculate_checksum(tmp_command)
    tmp_command.append(checksum)
    final_command = " ".join(tmp_command)
    logger.info(f"Final command {angle_value} = {final_command}")
    connection.write(convert_command(final_command))
    time.sleep(0.1)
    resp = connection.readall()
    logger.info(f"Final reponse for {angle_value} is {resp.hex()}")
    return resp

def query_alarm_angle():  
    for key, value in angle_bytes.items():
        response = process_alarm_angle_command(base_alarm_angle_command, key, value)
        angle = parse_angle(response)
        st.markdown(f"**{key}**: :orange[{angle}]")

delay_on_time_base_command = ["77", "05", address, "24"]

delay_on_axis = {
    "+X": "00",
    "-X": "02",
    "+Y": "04",
    "-Y": "06"
}

delay_off_axis = {
    "+X": "01",
    "-X": "03",
    "+Y": "05",
    "-Y": "07"
}


def process_delay_time(command_int, axis, axis_value):
    command = []
    command = command_int.copy()
    command.append(axis_value)
    checksum = calculate_checksum(command)
    command.append(checksum)
    final_command = " ".join(command)
    logger.info(f"Final command {axis} = {final_command}")
    connection.write(convert_command(final_command))
    time.sleep(0.1)
    resp = connection.readall()
    logger.info(f"Final reponse for delay_on_time {axis} is {resp.hex()}")
    return resp

def query_alarm_delay_on_time():
    if connection:
        for key, value in delay_on_axis.items():
            resp = process_delay_time(delay_on_time_base_command, key, value)
            angle = _parse_angle_time(resp)
            st.markdown(f"**{key}**: :green[{angle}]")
        

def query_alarm_delay_off_time():
    if connection:
        for key, value in delay_off_axis.items():
            resp = process_delay_time(delay_on_time_base_command, key, value)
            angle = _parse_angle_time(resp)
            st.markdown(f"**{key}**: :green[{angle}]")
        




if connection and address:
    st.header("Query")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Zero Type")
        if col1.button("Query Zero Type", key="query zero type"):
            query_zero_type()
    with col2:
        st.subheader("Alarm Angle")
        if col2.button("Query Alarm Angle", key="query alarm angle"):
            query_alarm_angle()
    st.divider()
    
    st.subheader("Alarm Delay ON Time")
    if st.button("Query Alarm Delay On Time", key="query delay on time"):
        query_alarm_delay_on_time()
    
    st.subheader("Alarm Delay OFF Time")
    
    if st.button("Query Alarm Delay Off Time", key="query delay off time"):
        query_alarm_delay_off_time()
