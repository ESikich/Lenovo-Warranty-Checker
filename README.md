# Warranty Checker

This project is designed to check the warranty status of devices in an Active Directory domain. It uses WinRM to retrieve the serial number of each device and then uses Selenium to scrape the warranty information from the device manufacturer's website. The results are saved to a CSV file for future reference.

## Dependencies

This project requires Python 3.7 or later and the following libraries:

- ldap3
- selenium
- tqdm
- winrm

The `tqdm.contrib.concurrent` and `tqdm.contrib.concurrent.process_map` libraries are also used to enable parallel processing.

## Files

### ad.py

This file contains the `AD` class, which is responsible for connecting to the Active Directory domain and retrieving a list of devices. The `get_dev_pool` method uses `process_map` to retrieve the list of devices in parallel. Each device is processed by the `process_entry` function in `warranty_checker.py`.

### csv_handler.py

This file contains the `CSVHandler` class, which is responsible for reading from and writing to the CSV files. It also contains a `create` method that creates the CSV files if they don't already exist.

### warranty_checker.py

This file contains the `WarrantyChecker` class, which is responsible for retrieving the serial number and warranty information for each device. The `setup` method initializes the Firefox driver with a headless option, and the `get_serial` and `get_warranty` methods use WinRM and Selenium, respectively, to retrieve the necessary information. The `proc_pool` method uses `tqdm` to display progress bars while processing each device.

### main.py

This file is the entry point for the application. It reads the configuration file (`config.json`), creates the CSV files if necessary, retrieves the list of devices from Active Directory using the `AD` class, and then processes the devices using the `WarrantyChecker` class.

## Configuration

The configuration file (`config.json`) contains the following options:

- `ldap_server`: The hostname or IP address of the Active Directory server.
- `search_base`: The LDAP search base for the device search.
- `ad_user`: The username to connect to Active Directory.
- `ad_password`: The password to connect to Active Directory.
- `wmi_user`: The username to connect to devices using WinRM.
- `wmi_password`: The password to connect to devices using WinRM.
- `web_url`: The URL of the website to retrieve warranty information from.
- `driver_location`: The path to the Firefox driver executable.
- `input_xpath`: The XPath of the input field for the serial number on the warranty information website.
- `warranty_xpath`: The XPath of the warranty information on the warranty information website.

## Usage

To use this tool, first ensure that all dependencies are installed. Then, create a `config.json` file in the project root directory with the necessary configuration options. Finally, run the following command:

```
python main.py
```

This will retrieve the list of devices from Active Directory, process each device, and save the results to the CSV files.

## Troubleshooting

If you encounter any issues with this tool, try the following:

- Ensure that all dependencies are installed.
- Ensure that the `config.json` file contains the correct options.
- Ensure that the Firefox driver executable is installed in the correct location.
- Ensure that the `wmi_user` and `wmi_password` options in `config.json` are correct.
- Check the `errors.csv` file for any errors that may have occurred during processing.
- If you encounter any other issues, feel free to contact the project maintainers.
