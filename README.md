# Warranty Checker

This program is a warranty checker tool that retrieves warranty information for devices connected to an Active Directory (AD) environment. The tool first queries the AD for computer objects and their associated IP addresses. It then checks if each device is online and retrieves its serial number using Windows Management Instrumentation (WMI). The serial number is used to query a manufacturer's website for warranty information, which is then saved to a CSV file.

## Dependencies

- Python 3.7+
- Selenium
- ldap3
- winrm

You will also need the appropriate driver for Selenium to use with your preferred web browser (e.g., Firefox, Chrome). Download the correct driver for your browser and add the path to the driver in the config file.

## Configuration

You will need to create a `config.json` file with the following format:

```json
{
    "ldap_server": "your_ldap_server",
    "ad_user": "your_ad_username",
    "ad_password": "your_ad_password",
    "search_base": "your_search_base",
    "wmi_user": "your_wmi_username",
    "wmi_password": "your_wmi_password",
    "driver_location": "path_to_your_browser_driver",
    "web_url": "url_of_manufacturer_warranty_check",
    "input_xpath": "xpath_of_input_field_on_warranty_website",
    "warranty_xpath": "xpath_of_warranty_info_on_warranty_website"
}
```

Replace the placeholders with your actual information.

## Usage

1. Install the required dependencies using pip:

```bash
pip install selenium ldap3 winrm
```

2. Update the `config.json` file with the appropriate information.

3. Run the script:

```bash
python warranty_checker.py
```

The script will output the warranty information for each device to a CSV file called `warranty_info.csv`. If any errors occur during execution, they will be logged in an `errors.csv` file.

## Output

The output CSV file (`warranty_info.csv`) will have the following columns:

- device_name
- ip_address
- serial_number
- warranty_info

The error CSV file (`errors.csv`) will have the following columns:

- device_name
- error_type
