import streamlit as st
import time
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

def calculate_modulo256_checksum(hex_command):
    hex_command = " ".join(hex_command.split(" ")[1:])
    
    # Remove spaces from the hex command
    hex_command = hex_command.replace(" ", "")
    
    # Convert hex string to a list of integers
    command_bytes = [int(hex_command[i:i+2], 16) for i in range(0, len(hex_command), 2)]

    # Calculate the sum of bytes modulo 256 checksum
    checksum = sum(command_bytes) % 256

    # Return checksum as a hexadecimal string
    return f"{checksum:02X}"

def set_alarm_angle():
    st.subheader("Set Alarm Angle")
    local_command = ["77", "08", address, "20"]
    selected_option = st.selectbox(
    'Alarm Angle',
    ('+X', '-X', '+Y', "-Y"))

    angle_degree = st.number_input("Enter the Angle", max_value=180, value=None)
    decimal_degree = st.number_input("Enter the decimal Angle", max_value=99, value=None)
    if selected_option == "+X":
        D = "00"
        S = "00"
    elif selected_option == "-X":
        D = "00"
        S = "01"
    elif selected_option == "+Y":
        D = "01"
        S = "00"
    elif selected_option == "-Y":
        D = "01"
        S = "01"
    else:
        st.error("Invalid selected option")
    

    col1, col2 = st.columns(2)
    set_button = col1.button("Set") 
    if set_button:
        local_command.append(D)
        local_command.append(S)
        local_command.append(str(angle_degree).zfill(2))
        local_command.append(str(decimal_degree).zfill(2))
        # calculate checksum
        checksum = calculate_modulo256_checksum(" ".join(local_command))
        local_command.append(checksum)

        command_to_send = " ".join(local_command)
        print(command_to_send)
        connection.write(convert_command(command_to_send))

    save_button = col2.button("Save Settings")
    if save_button:
        save_settings()

# calculate hex value on the fly and delay and set zero type.

def set_zero_type():
    command = ["77", "05", address, "05"]
    st.divider()
    st.subheader("Set Zero Type")
    
    opt = st.selectbox(
        "Zero type",
        ("Absolute", "Relative")
    )
    if opt == "Absolute":
        data = "00"
    else:
        data = "01"
    
    if opt:
        command.append(data)
    
        # Calculate checksum
        _checksum = calculate_modulo256_checksum(" ".join(command))
        command.append(_checksum)
        print(convert_command(" ".join(command)))
        connection.write(convert_command(" ".join(command)))

    if st.button("Save Setting"):
        save_settings()
    


if connection and address:
    set_alarm_angle()
    set_zero_type()