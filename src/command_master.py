#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CommandMaster: A utility to execute a set of commands on different devices using SSH.
The script reads a YAML file with device information and commands to execute.

Usage:
    python command_master.py --commands commands.yaml

Author: C. Ayala - ayalac@algonquincollege.com
Date: September 16th 2024
"""


import os
import sys
import yaml
import argparse
import logging
from datetime import datetime
from netmiko import ConnectHandler, NetMikoTimeoutException, NetMikoAuthenticationException


def parse_arguments():
    """Parse the command-line arguments."""
    parser = argparse.ArgumentParser(description="SSH into a device and execute commands.")
    parser.add_argument("--commands", required=True, help="File with commands to run on the device.")
    parser.add_argument("--log_dir", default="logs", help="Directory to store the command output logs.")
    return parser.parse_args()


def read_yaml_commands(commands):
    """Read devices and commands from the YAML file."""

    if not os.path.isfile(commands):
        logging.error(f"Commands file {commands} does not exist.")
        sys.exit(1)

    with open(commands, 'r') as file:
        try:
            data = yaml.safe_load(file)
        except yaml.YAMLError as exc:
            logging.error(f"Error reading YAML file: {exc}")
            sys.exit(1)

    # Extract output_file
    output_file = data.get('output_file', None)

    # Extract the device info and commands
    devices = []
    for device_entry in data.get('devices', []):
        device_info = device_entry.get('device_info')
        commands = device_entry.get('commands', [])
        devices.append((device_info, commands))

    return devices, output_file


def establish_ssh_connection(device_info):
    """Establish SSH connection to the device using netmiko."""

    try:
        logging.info(f"Connecting to {device_info['ip']}...")
        connection = ConnectHandler(**device_info)
        logging.info(f"Successfully connected to {device_info['ip']}.")
        return connection
    except NetMikoTimeoutException:
        logging.error(f"Connection timed out for {device_info['ip']}.")
    except NetMikoAuthenticationException:
        logging.error(f"Authentication failed for {device_info['ip']}.")
    except Exception as e:
        logging.error(f"An error occurred while connecting to {device_info['ip']}: {str(e)}")
        return None


def execute_commands(connection, commands, device_info):
    """Execute the list of commands on the connected device."""
    output = []
    log_file = f"{device_info['ip']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_output.log"

    with open(log_file, 'a') as file:
        for command in commands:
            logging.info(f"Executing command: {command}")
            result = connection.send_command(command)
            output.append(result)

            # Log command and output
            file.write(f"\nCommand: {command}\n")
            file.write(f"{'-' * 40}\n")
            file.write(f"{result}\n")
            file.write(f"{'-' * 40}\n")

            # Display the output to the screen
            print(f"\nCommand: {command}\n{'-' * 40}")
            print(result)
            print(f"{'-' * 40}")

    return output


def save_output(log_dir, ip, output, global_output_file=None):
    """Save the command output to a log file."""
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Determine the log file (either global output or device-specific)
    if global_output_file:
        log_file = global_output_file
    else:
        current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        log_file = os.path.join(log_dir, f"{ip}_log_{current_time}.txt")

    # Open the file for writing (overwrites if file already exists)
    with open(log_file, 'a') as file:
        # Write output with proper formatting (separation)
        file.write(f"\n--- Device: {ip} ---\n")
        for command_output in output:
            file.write(f"{command_output}\n")

    logging.info(f"Output saved to {log_file}")


def main():
    """Main function for the command_master script."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Parse arguments
    args = parse_arguments()

    # Read devices and commands from the YAML file
    devices_and_commands, output_file = read_yaml_commands(args.commands)

    # Loop through each device and execute commands
    for device_info, commands in devices_and_commands:
        # Establish SSH connection to the device
        connection = establish_ssh_connection(device_info)

        if connection:
            # Execute commands on the device
            output = execute_commands(connection, commands, device_info)

            # Save the output to the log file ( global or per device )
            save_output(args.log_dir, device_info['ip'], output, global_output_file=output_file)

            # Close the SSH connection
            connection.disconnect()
        else:
            logging.error(f"Failed to connect to {device_info['ip']}. No output generated.")


if __name__ == "__main__":
    main()
