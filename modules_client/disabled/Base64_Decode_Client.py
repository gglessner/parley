# Module: Base64 Decoder
from datetime import datetime
import re
import base64
from log_utils import write_to_log

# Description of the module's purpose
module_description = "Identify and decode Base64 strings in binary data for display and logging"

def module_function(message_num, source_ip, source_port, dest_ip, dest_port, message_data):

    # Define a regex pattern for Base64 strings
    base64_pattern = r'(?:[A-Za-z0-9+/]{4})+(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?'
    
    # Convert binary data to string for regex search (assuming ASCII-compatible)
    try:
        data_str = message_data.decode('ascii', errors='ignore')
    except UnicodeDecodeError:
        data_str = ''  # If decoding fails, skip string operations

    # Find all potential Base64 strings
    potential_base64 = re.findall(base64_pattern, data_str)

    # Prepare output
    output = []
    output.append(f"[{source_ip}:{source_port}->{dest_ip}:{dest_port}] {datetime.now().isoformat()} ------- Base64 Decoded Data ({message_num}) -------")

    for b64_str in potential_base64:
        try:
            # Attempt to decode the Base64 string
            decoded_bytes = base64.b64decode(b64_str)
            # Attempt to decode bytes to string for readability
            try:
                decoded_str = decoded_bytes.decode('utf-8')
            except UnicodeDecodeError:
                decoded_str = decoded_bytes.hex()  # Fallback to hex if not UTF-8
            output.append(f"Base64: {b64_str}")
            output.append(f"Decoded: {decoded_str}")
        except (base64.binascii.Error, ValueError):
            # Skip invalid Base64 strings
            continue

    # Join all lines with newline characters
    full_output = '\n'.join(output)

    # Atomic writes to screen and log file
    print(full_output)
    write_to_log(source_ip, source_port, dest_ip, dest_port, full_output)

    return message_data
