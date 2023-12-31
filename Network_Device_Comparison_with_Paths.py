import netmiko
import difflib
from getpass import getpass
import re

def compare_configs(startup_config, current_config):
    differences = difflib.ndiff(startup_config.splitlines(keepends=True), current_config.splitlines(keepends=True))
    return ''.join(differences)

def extract_config_commands(config):
    config_commands = {}
    lines = config.splitlines()
    for line in lines:
        match = re.match(r"^(.*?)\s{1,}(.*)$", line)
        if match:
            config_commands[match.group(1)] = match.group(2)
    return config_commands

try:
    # Ask for device information
    device_ip = input("Enter device IP: ") #192.168.56.101
    device_username = input("Enter username: ") #cisco
    device_password = getpass("Enter password: ")#cisco123!

    # Create SSH connection to the device
    device_connection = netmiko.ConnectHandler(
        host=device_ip,
        username=device_username,
        password=device_password,
        device_type="cisco_ios"
    )
    # Retrieve startup configuration from the device
    startup_config = device_connection.send_command("show startup-config")

    # Write current running configuration to a file
    with open("startup_config.txt", "w") as f:
        f.write(startup_config)

    # Retrieve current running configuration from the device
    current_config = device_connection.send_command("show running-config")

    # Write current running configuration to a file
    with open("current_config.txt", "w") as f:
        device_connection.send_command("Terminal Length 0")
        f.write(current_config)

    # Load Cisco device hardening device
    cisco_hardening_device_filename = "cisco_device_hardening_device.txt"
    try:
        with open(cisco_hardening_device_filename, "r") as f:
            cisco_hardening_device = f.read()
    except FileNotFoundError:
        print(f"Error: {cisco_hardening_device_filename} not found.")
        exit(1)
    except PermissionError:
        print(f"Error: Insufficient permissions to read {cisco_hardening_device_filename}.")
        exit(1)

    # Extract configuration commands from startup configuration and Cisco device hardening device
    current_config_commands = extract_config_commands(current_config)
    cisco_hardening_device_commands = extract_config_commands(cisco_hardening_device)

    # Compare current running configuration and Cisco device hardening device
    cisco_hardening_device_differences = compare_configs(current_config, cisco_hardening_device)

    # Print the differences
    print('-'*50)
    print("\nDifferences between the running configuration and the startup configuration:")
    print("\nDifferences between the current running configuration and the Cisco device hardening advice:")
    print('-'*50)
    print(cisco_device_hardening_device_differences)

finally:
    # Close SSH connection
    if 'device_connection' in locals() or 'device_connection' in globals():
        device_connection.disconnect()