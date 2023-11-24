from netmiko import ConnectHandler
import time
import difflib
import getpass

# Define the device parameters for SSH connection
ssh_device = {
    'device_type': 'cisco_ios',
    'ip': '192.168.56.101',
}

def login_to_device():
    # Get username, password, and enable secret from the user
    username = input("Enter your username: ")  # prne
    password = getpass.getpass("Enter your password: ")  # cisco123!
    secret = getpass.getpass("Enter your enable secret: ")  # class123!

    # Add the entered credentials to the device dictionary
    ssh_device['username'] = username
    ssh_device['password'] = password
    ssh_device['secret'] = secret

    while True:
        try:
            ssh_conn = ConnectHandler(**ssh_device)
            ssh_conn.enable()
            return ssh_conn
        except ValueError as e:
            print(f"Error: {e}")
            print("Retrying...")
            time.sleep(5)

def ssh_menu():
    # Establish the connection once at the beginning
    ssh_conn = login_to_device()

    print("------------------SSH Menu-------------------")
    print("1. Change Device Hostname")
    print("2. Save Running Configuration")
    print("3. Compare Running Configuration with Startup Configuration")
    print("4. Compare Running Configuration with Local Version")
    print("5. Compare Running Configuration with Cisco Hardening Device")
    print("6. Configure Syslog")
    print("7. Configure ACL (Access Control List)")
    print("8. Configure IPSec")
    print("9. Exiting SSH Menu")

    choice = input("Enter your choice (1/2/3/4/5/6/7/8/9): ")

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
        configure_acl(ssh_conn)
    elif choice == "8":
        configure_ipsec()
    elif choice == "9":
        print("Exiting SSH Menu")
        ssh_conn.disconnect()
    else:
        print("Invalid choice. Please enter 1, 2, 3, 4, 5, 6, 7, 8, or 9.")
        ssh_menu()

def change_hostname():
    new_hostname = input("Enter the new hostname: ")

    while True:
        try:
            ssh_conn = ConnectHandler(**ssh_device)
            ssh_conn.enable()
            ssh_conn.config_mode()
            ssh_conn.send_command('hostname ' + new_hostname)
            ssh_conn.exit_config_mode()
            ssh_conn.send_command('write memory')
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
            ssh_conn = ConnectHandler(**ssh_device)
            ssh_conn.enable()
            running_config = ssh_conn.send_command('show running-config')
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

    diff_startup = difflib.unified_diff(show_running_config.splitlines(), startup_config.splitlines(), lineterm='')

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

    diff_local = difflib.unified_diff(show_running_config.splitlines(), local_offline_version.splitlines(),
                                      lineterm='')

    print('-' * 50)
    print("\nDifferences between the current running configuration and the local offline version")
    print('-' * 50)
    print('\n'.join(diff_local))

def compare_with_hardening_device(show_running_config):
    try:
        with open("cisco_hardening_device.txt", "r") as f:
            cisco_hardening_device = f.read()
    except FileNotFoundError:
        print("Error: cisco_hardening_device.txt not found")
        exit(1)
    except PermissionError:
        print("Error: Insufficient permissions to read cisco_hardening_device.txt")
        exit(1)

    diff = difflib.unified_diff(show_running_config.splitlines(), cisco_hardening_device.splitlines(),
                                lineterm='')

    print('-' * 50)
    print("\nDifferences between the current running configuration and the cisco hardening device")
    print('-' * 50)
    print('\n'.join(diff))

def configure_syslog():
    with open('syslog_commands.txt', 'r') as f:
        syslog_commands = f.readlines()
        while True:
            try:
                ssh_conn = ConnectHandler(**ssh_device)
                ssh_conn.enable()
                for command in syslog_commands:
                    ssh_conn.send_command(command.strip())

                ssh_conn.send_command('write memory')
                ssh_conn.disconnect()
                break
            except ValueError as e:
                print(f"Error: {e}")
                print(f"Retrying...")
                time.sleep(5)

    print("Syslog configuration complete")

def configure_acl(ssh_conn):
    print("Enter ACL Configuration. Type 'exit' to finish.")
    try:
        # Manually enter enable mode
        enable_command = input("R1>")
        if enable_command.lower() == 'enable':
            ssh_conn.send_command_timing('enable')
        else:
            print("Invalid command. Exiting ACL configuration.")
            return

        # Manually enter configuration terminal mode
        config_command = input("R1# configure terminal")
        if config_command.lower() == 'configure terminal':
            ssh_conn.send_command_timing(config_command)
        else:
            print("Invalid command. Exiting ACL configuration.")
            return

        prompt = ssh_conn.find_prompt()

        # Apply user-entered ACL configuration commands
        acl_commands = []
        while True:
            acl_command = input(f"{prompt} (config)# ")
            if acl_command.lower() == 'exit':
                break
            acl_commands.append(acl_command)

            # Check if 'interface' command is entered
            if acl_command.strip().lower().startswith('interface'):
                prompt = ssh_conn.find_prompt(config_mode=True)

        # Join ACL commands into a single string
        acl_config = "\n".join(acl_commands)

        # Use send_config_set to send the ACL configuration
        output = ssh_conn.send_config_set([acl_config])

        # Save the configuration
        output += ssh_conn.send_command_timing('write memory')
        print(output)

        print("ACL configuration complete")
    except ValueError as e:
        print(f"Error configuring ACL: {e}")

def configure_ipsec():
    print("Enter IPSec configuration. Type 'exit' on a new line to finish.")
    ipsec_commands = []
    while True:
        ipsec = input("R1> ")
        ipsec = input("R1# ")
        ipsec = input("R1(config)# ")
        if command.lower() == 'exit':
            break
        ipsec_commands.append(command)

    ssh_conn = None

    try:
        ssh_conn = ConnectHandler(**ssh_device)
        ssh_conn.enable()

        ssh_conn.config_mode()

        for command in ipsec_commands:
            ssh_conn.send_command(command)

        ssh_conn.exit_config_mode()
        ssh_conn.send_command('write memory')

        print("IPSec configuration complete")
    except ValueError as e:
        print(f"Error configuring IPSec: {e}")
    finally:
        if ssh_conn:
            ssh_conn.disconnect()

if __name__ == "__main__":
    ssh_menu()  # Call the ssh_menu() once
