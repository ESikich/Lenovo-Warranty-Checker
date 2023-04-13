import csv
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from ldap3 import Server, Connection, ALL, SUBTREE
import winrm
import json
import socket
import ldap3


def trace_calls(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}...")
        result = func(*args, **kwargs)
        print(f"Finished {func.__name__}")
        return result
    return wrapper

def save_error_to_csv(device_name, error_type):
    with open('errors.csv', mode='a', newline='') as csvfile:
        fieldnames = ['device_name', 'error_type']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writerow({
            'device_name': device_name,
            'error_type': error_type
        })

def get_ip_address(hostname):
    try:
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except Exception as e:
        print(f"{hostname}... It was DNS.")
        raise


def is_device_online(ip_address, port=445, timeout=1):
    try:
        with socket.create_connection((ip_address, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


class WarrantyChecker:
    def __init__(self, config):
        self.config = config
        self.driver = self.setup_driver()

    def setup_driver(self):
        options = Options()
        driver = webdriver.Firefox(options=options, service=FirefoxService(executable_path=self.config['driver_location']))
        return driver

    def navigate_to_website(self, url):
        self.driver.get(url)

    def submit_serial_number(self, serial_number):
        input_field = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, self.config['input_xpath'])))
        input_field.clear()
        input_field.send_keys(serial_number)
        input_field.send_keys(Keys.RETURN)

    def extract_warranty_info(self):
        warranty_info = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, self.config['warranty_xpath'])))
        return warranty_info.text

    def quit_driver(self):
        self.driver.quit()


class AD:
    def __init__(self, config):
        self.config = config
        self.server = Server(self.config['ldap_server'], use_ssl=True, get_info=ALL)
        self.conn = None

    @trace_calls
    def connect(self):
        self.conn = Connection(self.server, self.config['ad_user'], self.config['ad_password'], auto_bind=True, client_strategy=ldap3.RESTARTABLE)

    def close_connection(self):
        if self.conn:
            self.conn.unbind()

    @trace_calls
    def get_serial_numbers(self):
        self.conn.search(search_base=self.config['search_base'], search_filter='(objectClass=computer)', attributes=['name'], search_scope=SUBTREE)

        for entry in self.conn.entries:
            computer_name = entry['name'].value
            try:
                ip_address = get_ip_address(str(computer_name))
            except Exception as e:
                print(f"Error resolving IP address for {computer_name}: {e}")
                save_error_to_csv(computer_name, 'DNS Error')
                continue
            if is_device_online(ip_address):
                session = winrm.Session(computer_name, auth=(self.config['wmi_user'], self.config['wmi_password']), transport='ntlm')
            else:
                print(f"{computer_name} is offline")
                save_error_to_csv(computer_name, 'Offline')

            try:
                result = session.run_ps('Get-WmiObject Win32_BIOS | Select-Object SerialNumber')
            except Exception as e:
                print(f"{computer_name}... WMI: {e}")
                save_error_to_csv(computer_name, 'WMI Error')
                continue
            if result.status_code == 0:
                serial_number = result.std_out.decode('utf-8').strip().split('\r\n')[-1].split()[-1]
                if serial_number and (len(serial_number) == 8 or len(serial_number) == 7):
                    get_warranty_info(self.config, computer_name, ip_address, serial_number)
            else:
                print(f"Some kind WMI deal with {computer_name} over here...")
                save_error_to_csv(computer_name, 'WMI Error')
@trace_calls
def get_warranty_info(config, device_name, ip_address, serial_number):
    warranty_checker = WarrantyChecker(config)
    url = config['web_url']
    warranty_checker.navigate_to_website(url)
    warranty_checker.submit_serial_number(serial_number)
    warranty_info = warranty_checker.extract_warranty_info()

    print(f'Device Name: {device_name}')
    print(f'IP Address: {ip_address}')
    print(f'Serial Number: {serial_number}')
    print(f'Warranty Information: {warranty_info}')
    print('-------------------------------------------')

    warranty_checker.quit_driver()

    save_to_csv(device_name, ip_address, serial_number, warranty_info)

def save_to_csv(device_name, ip_address, serial_number, warranty_info):
    with open('warranty_info.csv', mode='a', newline='') as csvfile:
        fieldnames = ['device_name', 'ip_address', 'serial_number', 'warranty_info']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writerow({
            'device_name': device_name,
            'ip_address': ip_address,
            'serial_number': serial_number,
            'warranty_info': warranty_info
        })

def close_connections(ad, warranty_checker=None):
    if ad:
        ad.close_connection()
    if warranty_checker:
        warranty_checker.quit_driver()

def main():
    with open('config.json') as f:
        config = json.load(f)

    # Create the CSV files with headers if they don't exist
    if not os.path.exists('warranty_info.csv'):
        with open('warranty_info.csv', mode='w', newline='') as csvfile:
            fieldnames = ['device_name', 'ip_address', 'serial_number', 'warranty_info']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

    if not os.path.exists('errors.csv'):
        with open('errors.csv', mode='w', newline='') as csvfile:
            fieldnames = ['device_name', 'error_type']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

    ad = AD(config)
    warranty_checker = None
    try:
        ad.connect()
        ad.get_serial_numbers()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        close_connections(ad, warranty_checker)

if __name__ == '__main__':
    main()
