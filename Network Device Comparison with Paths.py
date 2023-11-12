from netmiko import ConnectHandler
import re
import getpass
import difflib

def compare_configs(config1, config2):
    differences = difflib.ndiff(config1.splitlines(keepends=True), config2.splitlines(keepends=True))
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
    device_connection = ConnectHandler(
        host=device_ip,
        username=device_username,
        password=device_password,
        device_type="cisco_ios",
    )

    # Retrieve device's running configuration
    current_config = device_connection.send_command("show running-config")

    # Retrieve the local offline configuration
    with open("local_offline_config.txt", "r") as f:
        local_offline_config = f.read()

    # Retrieve the Cisco device hardening advice
    with open("cisco_device_hardening_advice.txt", "r") as f:
        cisco_device_hardening_advice = f.read()

    # Extract configuration commands from current running configuration and local offline configuration
    current_config_commands = extract_config_commands(current_config)
    local_offline_config_commands = extract_config_commands(local_offline_config)
    cisco_device_hardening_advice_commands = extract_config_commands(cisco_device_hardening_advice)

    # Compare current running configuration with local offline configuration and Cisco device hardening advice
    local_offline_differences = compare_configs(current_config, local_offline_config)
    cisco_device_hardening_advice_differences = compare_configs(current_config, cisco_device_hardening_advice)

    # Print the differences
    print("\nDifferences between the current running configuration and the local offline configuration:")
    print(local_offline_differences)

    print("\nDifferences between the current running configuration and the Cisco device hardening advice:")
    print(cisco_device_hardening_advice_differences)

    # Enable syslog
    device_connection.send_config_set(["logging host 192.168.1.1"])
    device_connection.save_config()

except FileNotFoundError:
    print("Error: local_offline_config.txt not found.")
except PermissionError:
    print("Error: Insufficient permissions to read local_offline_config.txt.")
except getpass.GetPassWarning:
    print("Error: Invalid password.")
except Exception as e:
    print(f"Error: {e}")
