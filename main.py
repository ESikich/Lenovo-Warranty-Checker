import json
from csv_handler import CSVHandler
from warranty_checker import WarrantyChecker
from ad import AD


def main() -> None:
    # Load configuration from a JSON file
    with open('config.json') as f:
        config = json.load(f)

    # Initialize AD object with the configuration
    ad = AD(config)

    # Create a CSV file using the CSVHandler module
    CSVHandler.create()

    try:
        # Connect to the Active Directory server
        ad.connect()

        # Get a list of devices from the device pool
        dev_pool = ad.get_dev_pool()

        # Initialize WarrantyChecker object with configuration and device pool
        warranty_checker = WarrantyChecker(config, dev_pool)

        # Process the device pool to check warranties
        dev_pool = warranty_checker.proc_pool()

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Close the connection to the Active Directory server
        ad.close_connection()


if __name__ == '__main__':
    main()
