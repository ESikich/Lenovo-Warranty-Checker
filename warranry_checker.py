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
    def __init__(self, config, dev_pool):
        self.config = config
        self.dev_pool = dev_pool

    def setup(self):
        opts = Options()
        opts.add_argument('-headless')
        driver = webdriver.Firefox(options=opts, service=FirefoxService(executable_path=self.config['driver_location']))
        return driver

    def get_serial(self, device_info):
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
    def get_warranty(device_info):
        dev_name, ip_addr, serial_number, config = device_info
        url = config['web_url']
        opts = Options()
        opts.add_argument('-headless')
        driver = webdriver.Firefox(options=opts, service=FirefoxService(executable_path=config['driver_location']))
        driver.get(url)
        input_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, config['input_xpath'])))
        input_field.clear()
        input_field.send_keys(serial_number)
        input_field.send_keys(Keys.RETURN)
        warranty_info = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, config['warranty_xpath']))).text
        driver.quit()
        return (dev_name, ip_addr, serial_number, warranty_info)


    def proc_pool(self):
        devs = []
        for dev_name, ip_addr in self.dev_pool:
            devs.append((dev_name, ip_addr, self.config['wmi_user'], self.config['wmi_password']))

        serial_numbers = []
        for device_info in tqdm(devs, desc='Getting serial numbers'):
            serial_number = self.get_serial(device_info)
            serial_numbers.append(serial_number)

        pared_down_dev_pool = []
        for device_info, serial_number in zip(devs, serial_numbers):
            dev_name, ip_addr, _, _ = device_info
            if not serial_number:
                CSVHandler.err_csv(dev_name, 'Invalid Serial Number')
                continue

            pared_down_dev_pool.append((dev_name, ip_addr, serial_number))

        if pared_down_dev_pool:
            self.driver = self.setup()
            for dev_name, ip_addr, serial_number in tqdm(pared_down_dev_pool, desc='Checking warranty info'):
                warranty_info = self.get_warranty((dev_name, ip_addr, serial_number, self.config))
                CSVHandler.save_csv(dev_name, ip_addr, serial_number, warranty_info)
            self.driver.quit()

def process_entry(entry, config):
    comp_name = entry['name'].value
    if CSVHandler.in_csv(comp_name):
        return None
    try:
        ip_addr = NetUtil.get_ip(str(comp_name))
    except Exception as e:
        CSVHandler.err_csv(comp_name, 'DNS Error')
        return None
    if NetUtil.ping(ip_addr):
        return (comp_name, ip_addr)
    return None
