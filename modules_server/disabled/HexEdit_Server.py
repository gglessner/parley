# Module: Hex Edit Server Data
from datetime import datetime
import os
import tempfile
import subprocess
import shutil
from log_utils import write_to_log

module_description = "Allow hex editing of server data before sending"

def module_function(message_num, source_ip, source_port, dest_ip, dest_port, message_data):
    # Check if hexedit is installed
    if not shutil.which('hexedit'):
        print("hexedit is not installed. Sending original message.")
        return message_data

    # Create a temporary file
    fd, temp_file_path = tempfile.mkstemp()
    try:
        # Write message_data to the temp file
        with os.fdopen(fd, 'wb') as temp_file:
            temp_file.write(message_data)
       
        # Launch hexedit on the temp file
        print(f"Opening hexedit for message {message_num}. Edit and save to proceed.")
        subprocess.run(['hexedit', temp_file_path])
       
        # Read the modified data back
        with open(temp_file_path, 'rb') as temp_file:
            modified_data = temp_file.read()
       
        # Log if the message was modified
        if modified_data != message_data:
            log_message = f"Message {message_num} was modified via hex editor."
            write_to_log(dest_ip, dest_port, source_ip, source_port, log_message)
            print(log_message)
        else:
            print(f"Message {message_num} was not modified.")
       
        # Return the modified data
        return modified_data
    finally:
        # Delete the temporary file
        try:
            os.remove(temp_file_path)
        except OSError as e:
            print(f"Error deleting temp file: {e}")
