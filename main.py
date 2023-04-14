import json
from csv_handler import CSVHandler
from warranty_checker import WarrantyChecker
from ad import AD

def main():
    with open('config.json') as f:
        config = json.load(f)
    ad = AD(config)

    CSVHandler.create()

    try:
        ad.connect()
        dev_pool = ad.get_dev_pool()
        warranty_checker = WarrantyChecker(config, dev_pool)
        dev_pool = warranty_checker.proc_pool()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ad.close_connection()
        

if __name__ == '__main__':
    main()
