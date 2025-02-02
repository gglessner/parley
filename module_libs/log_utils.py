import os
import datetime

def write_to_log(source_ip, source_port, dest_ip, dest_port, message):
    # Ensure the logs directory exists
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Create log directory for today if it doesn't exist
    today = datetime.date.today()
    log_dir = os.path.join('logs', today.strftime('%m-%d-%Y'))
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Construct the log file name
    log_file_name = f"{source_ip}-{source_port}-{dest_ip}-{dest_port}.log"
    log_file_path = os.path.join(log_dir, log_file_name)

    # Write the message atomically
    with open(log_file_path, 'a') as f:
        f.write(message + '\n')

# Example usage:
# write_to_log('127.0.0.1', '15334', '10.0.0.15', '80', 'This is a test message')
