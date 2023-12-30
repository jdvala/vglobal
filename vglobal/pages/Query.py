import streamlit as st
import time
connection = None
address = None

commands = {
    "query_alarm_angle_plus_x": "77 05 {} 21 00 26",
    "query_alarm_angle_plus_y": "77 05 {} 21 01 27",
    "query_alarm_angle_minus_x": "77 05 {} 21 02 28",
    "query_alarm_angle_minus_y": "77 05 {} 21 03 29",
    "query_alarm_delay_on_time_plus_x": "77 05 {} 24 00 29",
    "query_alarm_delay_on_time_plus_y": "77 05 {} 24 04 2D",
    "query_alarm_delay_on_time_minus_x": "77 05 {} 24 02 2B",
    "query_alarm_delay_on_time_minus_y": "77 05 {} 24 06 2F",
    "query_alarm_delay_off_time_plus_x": "77 05 {} 24 01 2A",
    "query_alarm_delay_off_time_plus_y": "77 05 {} 24 05 2E",
    "query_alarm_delay_off_time_minus_x": "77 05 {} 24 03 2C",
    "query_alarm_delay_off_time_minus_y": "77 05 {} 24 07 30",
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


def query_zero_type():
    current_command = commands["query_zero_type"].format(address)   
    converted_command = convert_command(command=current_command)
    if connection:
        connection.write(converted_command)
        time.sleep(0.1)
        zero_type = connection.read_all()
        _parse_zero_type(zero_type)

def _parse_angle(angle):
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
        if split_angle_hex[5] == "10":
            return f"-{split_angle_hex[6]} seconds"
        else:
            return f"{split_angle_hex[6]} seconds"

def query_alarm_angle():
    current_command_plus_x = commands["query_alarm_angle_plus_x"].format(address)
    current_command_minus_x = commands["query_alarm_angle_minus_x"].format(address)
    current_command_plus_y = commands["query_alarm_angle_plus_y"].format(address)
    current_command_minus_y = commands["query_alarm_angle_minus_y"].format(address)

    converted_command_plus_x = convert_command(command=current_command_plus_x)
    converted_command_minus_x = convert_command(command=current_command_minus_x)
    converted_command_plus_y = convert_command(command=current_command_plus_y)
    converted_command_minus_y = convert_command(command=current_command_minus_y)

    command_dict = {
        "Alarm Angle +X": converted_command_plus_x,
        "Alarm Angle -X": converted_command_minus_x,
        "Alarm Angle +Y": converted_command_plus_y,
        "Alarm Angle -Y": converted_command_minus_y
    }

    response = []
    if connection:
        for key, item in command_dict.items():
            connection.write(item)
            time.sleep(0.2)
            resp = connection.read_all()
            angle = _parse_angle(resp)
            st.markdown(f"**{key}**: :orange[{angle}]")



def query_alarm_delay_time():
    current_command_on_plus_x = commands["query_alarm_delay_on_time_plus_x"].format(address)
    current_command_on_minus_x = commands["query_alarm_delay_on_time_minus_x"].format(address)
    current_command_on_plus_y = commands["query_alarm_delay_on_time_plus_y"].format(address)
    current_command_on_minus_y = commands["query_alarm_delay_on_time_minus_y"].format(address)
    current_command_off_plus_x = commands["query_alarm_delay_off_time_plus_x"].format(address)
    current_command_off_minus_x = commands["query_alarm_delay_off_time_minus_x"].format(address)
    current_command_off_plus_y = commands["query_alarm_delay_off_time_plus_y"].format(address)
    current_command_off_minus_y = commands["query_alarm_delay_off_time_minus_y"].format(address)
    

    converted_command_on_plus_x = convert_command(command=current_command_on_plus_x)
    converted_command_on_minus_x = convert_command(command=current_command_on_minus_x)
    converted_command_on_plus_y = convert_command(command=current_command_on_plus_y)
    converted_command_on_minus_y = convert_command(command=current_command_on_minus_y)
    converted_command_off_plus_x = convert_command(command=current_command_off_plus_x)
    converted_command_off_minus_x = convert_command(command=current_command_off_minus_x)
    converted_command_off_plus_y = convert_command(command=current_command_off_plus_y)
    converted_command_off_minus_y = convert_command(command=current_command_off_minus_y)

    command_dict = {
        "Alarm Delay On Time +X": converted_command_on_plus_x,
        "Alarm Delay On Time -X": converted_command_on_minus_x,
        "Alarm Delay On Time +Y": converted_command_on_plus_y,
        "Alarm Delay On Time -Y": converted_command_on_minus_y,
        "Alarm Delay Off Time +X": converted_command_off_plus_x,
        "Alarm Delay Off Time -X": converted_command_off_minus_x,
        "Alarm Delay Off Time +Y": converted_command_off_plus_y,
        "Alarm Delay Off Time -Y": converted_command_off_minus_y
    }

    if connection:
        for key, item in command_dict.items():
            connection.write(item)
            time.sleep(0.2)
            resp = connection.read_all()
            angle = _parse_angle_time(resp)
            st.markdown(f"**{key}**: :green[{angle}]")





if connection and address:
    st.header("Query")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Zero Type")
        query_zero_type()
    with col2:
        st.subheader("Alarm Angle")
        query_alarm_angle()
    st.divider()
    st.subheader("Alarm Delay Time")
    query_alarm_delay_time()