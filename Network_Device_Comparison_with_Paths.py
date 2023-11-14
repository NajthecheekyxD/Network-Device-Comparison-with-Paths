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
    device_ip = input("Enter device IP: ")
    device_username = input("Enter username: ")
    device_password = getpass("Enter password: ")

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
        f.write(current_config)

    # Load Cisco device hardening advice
    try:
        with open("cisco_device_hardening_advice.txt", "r") as f:
            cisco_device_hardening_device = f.read()
    except FileNotFoundError:
        print("Error: cisco_device_hardening_device.txt not found.")
        exit(1)
    except PermissionError:
        print("Error: Insufficient permissions to read cisco_device_hardening_device.txt.")
        exit(1)

    # Extract configuration commands from startup configuration and Cisco device hardening device
    current_config_commands = extract_config_commands(current_config)
    cisco_device_hardening_advice_commands = extract_config_commands(cisco_device_hardening_device)

    # Compare current running configuration and Cisco device hardening device
    cisco_device_hardening_advice_differences = compare_configs(current_config, cisco_device_hardening_device)

    # Print the differences
    print('-'*50)
    print("\nDifferences between the running configuration and the startup configuration:")
    print("\nDifferences between the current running configuration and the Cisco device hardening advice:")
    print('-'*50)
    print(cisco_device_hardening_advice_differences)

finally:
    # Close SSH connection
    if 'device_connection' in locals() or 'device_connection' in globals():
        device_connection.disconnect()
