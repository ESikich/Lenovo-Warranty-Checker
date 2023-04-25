import csv
import os


class CSVHandler:
    @staticmethod
    def in_csv(dev_name: str, fname: str = 'warranty_info.csv') -> bool:
        """Check if a device is present in the CSV file.

        Args:
            dev_name (str): Device name to search for.
            fname (str, optional): Name of the CSV file to search in. Defaults to 'warranty_info.csv'.

        Returns:
            bool: True if the device is found, False otherwise.
        """
        with open(fname, mode='r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['device_name'] == dev_name:
                    return True
        return False

    @staticmethod
    def err_csv(dev_name: str, err_type: str, fname: str = 'errors.csv') -> None:
        """Add an error for a device to the errors CSV file.

        Args:
            dev_name (str): Name of the device.
            err_type (str): Type of the error.
            fname (str, optional): Name of the CSV file to write to. Defaults to 'errors.csv'.
        """
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
    def save_csv(warranty: tuple[str, str, str, str], fname: str = 'warranty_info.csv') -> None:
        """Save warranty information for a device to the CSV file.

        Args:
            warranty (tuple): Tuple containing the device name, IP address, serial number, and warranty information.
            fname (str, optional): Name of the CSV file to write to. Defaults to 'warranty_info.csv'.
        """
        with open(fname, mode='a', newline='') as csvfile:
            fn = ['device_name', 'ip_address', 'serial_number', 'warranty_info']
            writer = csv.DictWriter(csvfile, fieldnames=fn)

            # Unpack the necessary values from the warranty tuple
            dev_name, ip_addr, serial_num, warranty_date = warranty

            writer.writerow({
                'device_name': dev_name,
                'ip_address': ip_addr,
                'serial_number': serial_num,
                'warranty_info': warranty_date
            })

    @staticmethod
    def create() -> None:
        """Create the CSV files if they do not exist."""
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
