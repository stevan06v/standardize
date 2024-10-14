import csv
import os
import phonenumbers
import logging
from phonenumbers import NumberParseException

logging.basicConfig(filename='phone_standardization.log', level=logging.INFO, format='%(asctime)s - %(message)s')

prefix_region_dict = {
    '49': 'DE',   # Germany
    '43': 'AT',   # Austria
    '1': 'US',    # USA/Canada
    '44': 'GB',   # UK
    '33': 'FR',   # France
    '39': 'IT',   # Italy
    '385': 'CRO', # Croatia
    '34': 'ES',   # Spain
    '45': 'DK',   # Denmark
    '46': 'SE',   # Sweden
    '47': 'NO',   # Norway
    '31': 'NL',   # Netherlands
    '32': 'BE',   # Belgium
    '30': 'GR',   # Greece
    '48': 'PL',   # Poland
    '351': 'PT',  # Portugal
    '41': 'CH',   # Switzerland
    '36': 'HU',   # Hungary
    '420': 'CZ',  # Czech Republic
    '421': 'SK',  # Slovakia
    '386': 'SI',  # Slovenia
    '371': 'LV',  # Latvia
    '370': 'LT',  # Lithuania
    '372': 'EE',  # Estonia
    '380': 'UA',  # Ukraine
    '7': 'RU',    # Russia
    '90': 'TR',   # Turkey
    '91': 'IN',   # India
    '86': 'CN',   # China
    '81': 'JP',   # Japan
    '61': 'AU',   # Australia
    '64': 'NZ',   # New Zealand
    '60': 'MY',   # Malaysia
    '65': 'SG',   # Singapore
    '62': 'ID',   # Indonesia
    '27': 'ZA',   # South Africa
    '55': 'BR',   # Brazil
    '52': 'MX',   # Mexico
    '56': 'CL',   # Chile
    '54': 'AR',   # Argentina
    '51': 'PE',   # Peru
    '57': 'CO',   # Colombia
    '53': 'CU',   # Cuba
    '58': 'VE',   # Venezuela
}

DEFAULT_REGION = "AT"

DELIMITER = ","
PHONE_NUMBER_FIELD = 'tel'


def clean_phone_number(phone_number):
    return ''.join(filter(lambda x: x.isdigit() or x == '+', phone_number))


def standardize_phone_number(phone_number):
    phone_number = clean_phone_number(phone_number)

    if phone_number.startswith('+'):
        try:
            parsed_number = phonenumbers.parse(phone_number, None)
            standardized_phone = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
            return standardized_phone
        except NumberParseException:
            logging.warning(f"Could not parse phone number: {phone_number}")
            return "unknown"

    has_country_code = False
    for prefix in prefix_region_dict.keys():
        if phone_number.startswith(prefix):
            has_country_code = True
            phone_number = '+' + phone_number.lstrip('0')
            break

    if not has_country_code:
        country_code = phonenumbers.country_code_for_region(DEFAULT_REGION)
        phone_number = f"+{country_code}{phone_number.lstrip('0')}"

    try:
        parsed_number = phonenumbers.parse(phone_number, DEFAULT_REGION)
        standardized_phone = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        return standardized_phone
    except NumberParseException:
        logging.warning(f"Could not parse phone number: {phone_number}")
        return "unknown"


def parse_and_standardize(input_file, output_file):
    try:
        with open(input_file, mode='r', newline='', encoding='utf-8') as infile, \
                open(output_file, mode='w', newline='', encoding='utf-8') as outfile:

            reader = csv.DictReader(infile, delimiter=DELIMITER)
            fieldnames = ['Name', 'Handynummer', 'Gezeichnet']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                firma = row.get('Firma', '')
                weitere_vornamen = row.get('Weitere Vornamen', '')
                nachname = row.get('Nachname', '')

                name = nachname if nachname else weitere_vornamen if weitere_vornamen else firma

                mobil = row.get(PHONE_NUMBER_FIELD, '')
                if mobil:
                    phone_numbers = mobil.split(',')
                    for number in phone_numbers:
                        number = number.strip()
                        standardized_phone = standardize_phone_number(number)
                        writer.writerow({'Name': name, 'Handynummer': standardized_phone, 'Gezeichnet': '0'})
                        logging.info(f"{name}: Standardized phone number to {standardized_phone}")
                else:
                    logging.info(f"{name}: No phone number found.")
    except Exception as e:
        logging.error(f"Error processing file {input_file}: {str(e)}")


def process_files(non_standardized_dir_path, standardized_dir_path):
    filelist = []

    for root, dirs, files in os.walk(non_standardized_dir_path):
        for file in files:
            filelist.append(os.path.join(root, file))

    for file_path in filelist:
        file_name = os.path.basename(file_path)
        standardized_output_path = os.path.join(standardized_dir_path, file_name)

        print(f"Processing file: {file_name}")
        parse_and_standardize(file_path, standardized_output_path)


non_standardized_dir_path = "./non-standardized-list"
standardized_dir_path = "./standardized-list"

process_files(non_standardized_dir_path, standardized_dir_path)
