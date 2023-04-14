import csv
import os

class CSVHandler:

    @staticmethod
    def in_csv(dev_name, fname='warranty_info.csv'):
        with open(fname, mode='r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['device_name'] == dev_name:
                    return True
        return False

    @staticmethod
    def err_csv(dev_name, err_type, fname='errors.csv'):
        errs = set()
        with open(fname, mode='r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            errs = set((row['device_name'], row['error_type']) for row in reader)

        if (dev_name, err_type) not in errs:
            with open(fname, mode='a', newline='') as csvfile:
                fn = ['device_name', 'error_type']
                writer = csv.DictWriter(csvfile, fieldnames=fn)

                writer.writerow({
                    'device_name': dev_name,
                    'error_type': err_type
                })

    @staticmethod
    def save_csv(dev_name, ip_addr, serial_num, warranty, fname='warranty_info.csv'):
        with open(fname, mode='a', newline='') as csvfile:
            fn = ['device_name', 'ip_address', 'serial_number', 'warranty_info']
            writer = csv.DictWriter(csvfile, fieldnames=fn)

            writer.writerow({
                'device_name': dev_name,
                'ip_address': ip_addr,
                'serial_number': serial_num,
                'warranty_info': warranty
            })

    @staticmethod
    def create():
        if not os.path.exists('warranty_info.csv'):
            with open('warranty_info.csv', mode='w', newline='') as csvfile:
                fn = ['device_name', 'ip_address', 'serial_number', 'warranty_info']
                writer = csv.DictWriter(csvfile, fieldnames=fn)
                writer.writeheader()

        if not os.path.exists('errors.csv'):
            with open('errors.csv', mode='w', newline='') as csvfile:
                fn = ['device_name', 'error_type']
                writer = csv.DictWriter(csvfile, fieldnames=fn)
                writer.writeheader()
