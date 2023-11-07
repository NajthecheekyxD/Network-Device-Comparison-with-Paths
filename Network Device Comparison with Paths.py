import netmiko
import difflib
from getpass import getpass

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

# Retrieve current running configuration from the device
current_config = device_connection.send_command("show running-config")

# Retrieve startup configuration from the device
startup_config = device_connection.send_command("show startup-config")

# Save current running configuration to a file
with open("current_config.txt", "w") as f:
    f.write(current_config)

# Save startup configuration to a file
with open("startup_config.txt", "w") as f:
    f.write(startup_config)

# Use difflib to compare the current running configuration with the startup configuration
differences = difflib.ndiff(current_config.splitlines(keepends=True), startup_config.splitlines(keepends=True))

# Print the differences
print("Differences between the current running configuration and the startup configuration:")
print(''.join(differences))