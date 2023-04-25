from typing import Dict, List, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from csv_handler import CSVHandler
from net_util import NetUtil
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import winrm


class WarrantyChecker:
    def __init__(self, config: Dict[str, str], dev_pool: List[Tuple[str, str]]) -> None:
        self.config = config
        self.dev_pool = dev_pool
        self.driver: Optional[webdriver.Firefox] = None

    def setup(self) -> webdriver.Firefox:
        """Set up the Firefox driver with headless mode enabled and return it."""
        opts = Options()
        opts.add_argument('-headless')
        driver = webdriver.Firefox(options=opts, service=FirefoxService(executable_path=self.config['driver_location']))
        return driver

    def get_serial(self, device_info: Tuple[str, str, str, str]) -> Optional[str]:
        """Get the serial number of a device using Windows Management Instrumentation (WMI).

        Args:
            device_info: A tuple containing device name, IP address, WMI username, and WMI password.

        Returns:
            The serial number of the device, or None if an error occurs.
        """
        dev_name, ip_addr, wmi_user, wmi_password = device_info
        session = winrm.Session(dev_name, auth=(wmi_user, wmi_password), transport='ntlm')
        try:
            result = session.run_ps('Get-WmiObject Win32_BIOS | Select-Object SerialNumber')
        except Exception as e:
            CSVHandler.err_csv(dev_name, 'WMI Error')
            return None

        if result.status_code != 0:
            CSVHandler.err_csv(dev_name, 'WMI Error 2?')
            return None

        try:
            serial_number = result.std_out.decode('utf-8').strip().split('\r\n')[-1].split()[-1]
        except Exception as e:
            CSVHandler.err_csv(dev_name, 'UTF-8 Error')
            return None

        if not (serial_number and (len(serial_number) == 8 or len(serial_number) == 7)):
            CSVHandler.err_csv(dev_name, 'Invalid Serial Number')
            return None

        return serial_number

    @staticmethod
    def get_warranty(device_info: Tuple[str, str, str, Dict[str, str]]) -> Tuple[str, str, str, str]:
        """Get the warranty information of a device using its serial number.

        Args:
            device_info: A tuple containing device name, IP address, serial number, and configuration parameters.

        Returns:
            A tuple containing device name, IP address, serial number, and warranty information.
        """
        dev_name, ip_addr, serial_number, config = device_info
        url = config['web_url']

        # Set up the Firefox driver with headless mode enabled
        opts = Options()
        opts.add_argument('-headless')
        driver = webdriver.Firefox(options=opts, service=FirefoxService(executable_path=config['driver_location']))

        # Navigate to the web page and enter the serial number
        driver.get(url)
        input_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, config['input_xpath'])))
        input_field.clear()
        input_field.send_keys(serial_number)
        input_field.send_keys(Keys.RETURN)

        # Get the warranty information and quit the driver
        warranty_info = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, config['warranty_xpath']))).text
        driver.quit()

        return (dev_name, ip_addr, serial_number, warranty_info)


def proc_pool(self) -> None:
    """Process the device pool, get the serial numbers, and check the warranties."""
    devs = []
    for dev_name, ip_addr in self.dev_pool:
        devs.append((dev_name, ip_addr, self.config['wmi_user'], self.config['wmi_password']))

    # Use process_map() to get the serial numbers in parallel
    serial_numbers = process_map(self.get_serial, devs, desc='Getting serial numbers', max_workers=4)

    pared_down_dev_pool = []
    for device_info, serial_number in zip(devs, serial_numbers):
        dev_name, ip_addr, _, _ = device_info
        if not serial_number:
            CSVHandler.err_csv(dev_name, 'Invalid Serial Number')
            continue

        pared_down_dev_pool.append((dev_name, ip_addr, serial_number))

    if pared_down_dev_pool:
        self.driver = self.setup()

    # Use process_map() to check the warranties in parallel
    warranty_infos = process_map(self.get_warranty, [(dev_name, ip_addr, serial_number, self.config) for dev_name, ip_addr, serial_number in pared_down_dev_pool], desc='Checking warranties', max_workers=4)

    # Save the warranty information to a CSV file
    CSVHandler.write_csv(warranty_infos)

    # Close the driver
    if self.driver:
        self.driver.quit()
