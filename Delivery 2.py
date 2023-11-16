from netmiko import ConnectHandler
import time
import difflib

# Define the device parameters for SSH connection
ssh_device = {
    'device_type': 'cisco_ios',
    'ip': '192.168.56.101',
    'username': 'prne',
    'password': 'cisco123!',
    'secret': 'class123!',  # Enable secret password
}

def ssh_menu():
    print("SSH Menu")
    print("1. Change Device Hostname")
    print("2. Save Running Configuration")
    print("3. Compare Running Configuration with Startup Configuration")
    print("4. Compare Running Configuration with Local Version")
    print("5. Compare Running Configuration with Cisco Hardening Device")
    print("6. Configure Syslog")
    print("7. Exiting SSH Menu")

    choice = input("Enter your choice (1/2/3/4/5/6/7): ")

    if choice == "1":
        change_hostname()
    elif choice == "2":
        save_running_config()
    elif choice == "3":
        show_running_config = compare_running_config()
        compare_running_with_startup_config(show_running_config)
    elif choice == "4":
        show_running_config = compare_running_config()
        compare_running_with_local_version(show_running_config)
    elif choice == "5":
        show_running_config = compare_running_config()
        compare_with_hardening_device(show_running_config)
    elif choice == "6":
        configure_syslog()
    elif choice == "7":
        print("Exiting SSH Menu")
        return  # Added to stop the ssh_menu() function from being called again
    else:
        print("Invalid choice. Please enter 1, 2, 3, 4, 5, 6, or 7.")
        ssh_menu()

def change_hostname():
    new_hostname = input("Enter the new hostname: ")

    while True:
        try:
            ssh_conn = ConnectHandler(**ssh_device)  # Corrected here
            ssh_conn.enable()  # Enter enable mode
            ssh_conn.config_mode()  # Enter global configuration mode
            ssh_conn.send_command('hostname ' + new_hostname)
            ssh_conn.exit_config_mode()  # Exit configuration mode
            ssh_conn.send_command('write memory')  # Save configuration
            ssh_conn.disconnect()
            break
        except ValueError as e:
            print(f"Error: {e}")
            print("Retrying...")
            time.sleep(5)

    print(f"Device hostname changed to {new_hostname}")

def save_running_config():
    while True:
        try:
            ssh_conn = ConnectHandler(**ssh_device)  # Corrected here
            ssh_conn.enable()  # Enter enable mode
            running_config = ssh_conn.send_command('show running-config')  # Capture the output
            ssh_conn.disconnect()
            break
        except ValueError as e:
            print(f"Error: {e}")
            print("Retrying...")
            time.sleep(5)

    with open('running_config.txt', 'w') as f:
        f.write(running_config)

    print("Running configuration saved to running_config.txt")

def compare_running_config():
    while True:
        try:
            ssh_conn = ConnectHandler(**ssh_device)
            ssh_conn.enable()
            show_running_config = ssh_conn.send_command('show running-config')
            ssh_conn.disconnect()
            break
        except ValueError as e:
            print(f"Error: {e}")
            print(f"Retrying...")
            time.sleep(5)
    return show_running_config

def compare_running_with_startup_config(show_running_config):
    while True:
        try:
            ssh_conn = ConnectHandler(**ssh_device)
            ssh_conn.enable()
            startup_config = ssh_conn.send_command('show startup-config')
            ssh_conn.disconnect()
            break
        except ValueError as e:
            print(f"Error: {e}")
            print(f"Retrying...")
            time.sleep(5)

    # Compare current running configuration with startup configuration
    diff_startup = difflib.unified_diff(show_running_config.splitlines(), startup_config.splitlines(), lineterm='')

    # Print the differences
    print('-' * 50)
    print("\nDifferences between the current running configuration and the startup configuration")
    print('-' * 50)
    print('\n'.join(diff_startup))

def compare_running_with_local_version(show_running_config):
    try:
        with open("local_offline_version.txt", "r") as f:
            local_offline_version = f.read()
    except FileNotFoundError:
        print("Error: local_offline_version.txt not found")
        exit(1)
    except PermissionError:
        print("Error: Insufficient permissions to read local_offline_version.txt")
        exit(1)

    # Compare current running configuration with local offline version
    diff_local = difflib.unified_diff(show_running_config.splitlines(), local_offline_version.splitlines(),
                                      lineterm='')

    # Print the differences
    print('-' * 50)
    print("\nDifferences between the current running configuration and the local offline version")
    print('-' * 50)
    print('\n'.join(diff_local))

def compare_with_hardening_device(show_running_config):
    # Load Cisco Hardening device
    try:
        with open("cisco_hardening_device.txt", "r") as f:
            cisco_hardening_device = f.read()
    except FileNotFoundError:
        print("Error: cisco_hardening_device.txt not found")
        exit(1)
    except PermissionError:
        print("Error: Insufficient permissions to read cisco_hardening_device.txt")
        exit(1)

    # Compare current running configuration and Cisco Hardening Device
    diff = difflib.unified_diff(show_running_config.splitlines(), cisco_hardening_device.splitlines(),
                                lineterm='')

    # Print the differences
    print('-' * 50)
    print("\nDifferences between the current running configuration and the cisco hardening device")
    print('-' * 50)
    print('\n'.join(diff))

def configure_syslog():
    # Open and read the syslog commands from a file
    with open('syslog_commands.txt', 'r') as f:
        syslog_commands = f.readlines()
        while True:
            try:
                ssh_conn = ConnectHandler(**ssh_device)
                ssh_conn.enable()
                for command in syslog_commands:
                    ssh_conn.send_command(command.strip())

                ssh_conn.send_command('write memory')  # Save configuration
                ssh_conn.disconnect()
                break
            except ValueError as e:
                print(f"Error: {e}")
                print(f"Retrying...")
                time.sleep(5)

    print("Syslog configuration complete")

if __name__ == "__main__":
    ssh_menu()  # Call the ssh_menu() once
