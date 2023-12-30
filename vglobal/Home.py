import streamlit as st
import serial
import time
from serial.tools import list_ports

st.title("Vistec Tilt Program")
st.subheader("Axis Values")
address = None
connection = None

st.session_state["address"] = address
st.session_state["connection"] = connection

commands = {
    "x_axis" : "77 04 {} 01 05",
    "y_axis" : "77 04 {} 02 06",
    "x_y_axis": "77 04 {} 04 08",
    "current_address": "77 04 00 1F 23",
    "query_zero_type": "77 04 {} 0D 11",
    "set_zero_type": "77 05 {0} 05 {1} 0B"
}

# Serial Functions
def convert_command(command):
    return bytes.fromhex(command)


def get_serial_ports():
    ports = [port.device for port in list_ports.comports()]
    return tuple(ports)


def esstlish_connection(port, baud_rate):
    # This function to be called once the user presses connect.
    try:
        global connection 
        connection = serial.Serial(port, baud_rate, timeout=1)
        st.session_state.connection = connection
        st.toast("Connection Successful")
    except ValueError:
        st.error("Connection parameters are wrong!")
        return None
    except serial.SerialException:
        st.error("Physical problem with device connection or Please press connect button")
        return None 
    
    

def _parse_address_response(response):
    hex_representation = ' '.join(hex(byte)[2:].zfill(2) for byte in response)
    if hex_representation:
        try:
            return hex_representation.split(" ")[4]
        except:
            st.error("Error fetching address")
    else:
        st.error("Unable to fetch address")

def query_current_address():
    global address
    converted_command = convert_command(command=commands["current_address"])
    if connection:
        connection.write(converted_command)
        time.sleep(0.1)
        add_response = connection.read_all()
        address = _parse_address_response(add_response)
        st.session_state.address = address
        return address

def _process_x_y(raw_x, raw_y, raw_z):
    final_x = ""
    final_y = ""
    final_z = ""
    if len(raw_x) == 3 and len(raw_y) == 3  and len(raw_z):
        if raw_x[0] == "10":
            final_x = f"-{raw_x[1]}.{raw_x[2]}"
        elif raw_x[0] == "00":
            final_x = f"{raw_x[1]}.{raw_x[2]}"
        if raw_y[0] == "10":
            final_y = f"-{raw_y[1]}.{raw_y[2]}"
        elif raw_y[0] == "00":
            final_y = f"{raw_y[1]}.{raw_y[2]}"
        if raw_z[0] == "10":
            final_z = f"-{raw_z[1]}.{raw_z[2]}"
        elif raw_z[0] == "00":
            final_z = f"{raw_z[1]}.{raw_z[2]}"
    
    #print(final_x, final_y)
    return final_x, final_y, final_z

def _parse_x_y_axis(axis_vals):
    parsed_xy_vlaues = ' '.join(hex(byte)[2:].zfill(2) for byte in axis_vals)
    #breakpoint()
    if parsed_xy_vlaues:
        splited_xy_values = parsed_xy_vlaues.split(" ")
        raw_x_axis = splited_xy_values[4:7] 
        raw_y_axis = splited_xy_values[7:10]
        raw_z_axis = splited_xy_values[10:13]
        f_x, f_y, f_z = _process_x_y(raw_x_axis, raw_y_axis, raw_z_axis)
        return f_x, f_y, f_z

def query_axis():
    current_command = commands["x_y_axis"].format(address)
    converted_command = convert_command(command=current_command)
    if connection:
        connection.write(converted_command)
        time.sleep(0.1)
        x_y_axis= connection.read_all()
        f_x, f_y, f_z = _parse_x_y_axis(x_y_axis)
        return f_x, f_y, f_z

def axis_values():
    # here we will display the axis values
   
    # Create placeholders for metrics
    x_metric_placeholder = st.empty()
    y_metric_placeholder = st.empty()
    z_metric_placeholder = st.empty()

    while True:
        f_x, f_y, f_z = query_axis()
    
        x_metric_placeholder.metric(label="X-Axis", value=f_x)
        y_metric_placeholder.metric(label="Y-Axis", value=f_y)
        z_metric_placeholder.metric(label="Z-Axis", value=f_z)

# dropdown
comm_port = st.selectbox(
    "Select the Communication Port",
    get_serial_ports()
)

baud_rate = st.selectbox(
    "Select the Baud Rate",
    ("9600", "115200")
)

connection_button = st.button(
    label="Connect",
    on_click=esstlish_connection(comm_port, baud_rate)
)
if connection_button:
    address = query_current_address()
    print(address)
    st.markdown(f"""
    **Address: :red[{address}]**
    """)

if connection and address:
    axis_values()