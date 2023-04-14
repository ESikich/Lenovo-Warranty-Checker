# Warranty Checker

Warranty Checker is a Python-based tool designed to retrieve the warranty information for devices in an Active Directory domain. It does this by first retrieving the serial number of each device using WinRM and then uses Selenium to scrape the warranty information from the device manufacturer's website. The results are then saved to a CSV file for future reference.

## Dependencies

This tool requires the following Python libraries:

- `ldap3`
- `winrm`
- `Selenium`
- `tqdm`

## Files

### ad.py

The `AD` class in this file is responsible for connecting to the Active Directory domain and retrieving a list of devices. The `get_dev_pool` method uses `process_map` to retrieve the list of devices in parallel. Each device is processed by the `process_entry` function in `warranty_checker.py`. The `AD` class uses the `ldap3` library to connect to the Active Directory domain and retrieve device information.

### csv_handler.py

This file contains the `CSVHandler` class, which is responsible for reading from and writing to the CSV files. The `in_csv`, `save_csv`, and `err_csv` methods are used to read and write data to the `warranty_info.csv` and `errors.csv` files. The `create` method is used to create the CSV files if they don't already exist.

### warranty_checker.py

This file contains the `WarrantyChecker` class, which is responsible for retrieving the serial number and warranty information for each device. The `setup` method initializes the Firefox driver with a headless option, and the `get_serial` and `get_warranty` methods use WinRM and Selenium, respectively, to retrieve the necessary information. The `proc_pool` method uses `tqdm` to display progress bars while processing each device. The `WarrantyChecker` class uses the `winrm` library to connect to devices using WinRM.

### main.py

This file is the entry point for the application. It reads the configuration file (`config.json`), creates the CSV files if necessary, retrieves the list of devices from Active Directory using the `AD` class, and then processes the devices using the `WarrantyChecker` class.

## Configuration

The `config.json` file contains the following options:

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

To use Warranty Checker, first ensure that all dependencies are installed. Then, create a `config.json` file in the project root directory with the necessary configuration options. Finally, run the following command:

```
python main.py
```

This will retrieve the list of devices from Active Directory, process each device, and save the results to the CSV files. The tool uses parallel processing to speed up the process of retrieving warranty information.

## Troubleshooting

If you encounter any issues with this tool, try the following:

- Ensure that all dependencies are installed.
- Ensure that the `config.json` file contains the correct options.
- Ensure that the Firefox driver executable is installed in the correct location.
- Ensure that the `wmi_user` and `wmi_password` options in `config.json` are correct.
- Check the log files (`warranty_info.csv` and `errors.csv`) for any issues.

If you continue to have issues, please consult the documentation for each library used in this tool:

- [ldap3](https://ldap3.readthedocs.io/)
- [winrm](https://github.com/diyan/pywinrm)
- [Selenium](https://selenium-python.readthedocs.io/)
- [tqdm](https://tqdm.github.io/)
- [multiprocessing](https://docs.python.org/3/library/multiprocessing.html)

If you are still unable to resolve the issue, please open an issue on the GitHub repository for this tool. We will do our best to help you resolve the issue as soon as possible.
