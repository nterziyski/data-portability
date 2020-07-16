import datetime
import time
import warnings
import os
import shutil
import random

from faker import Faker
import simplejson as json

import filename

DIRECTORY_ANONYMIZED = "../facebook-data-anonymous"
DIRECTORY_FACEBOOK_DATA = "../facebook-data"
DIRECTORY_DATASTRUCTURES = "../datastructures.json"

SEED_VALUE = 25

DEBUG_print_missing_key_stack = False
DEBUG_remove_old_anonymous_folder = True

# Set up faker.
# Choosing a seed value ensures the same names generate every time

fake = Faker()
# Faker.seed(SEED_VALUE)
fakes_table = {}


def main():
    # Create the empty anonymous data folder
    if os.path.exists(DIRECTORY_ANONYMIZED):
        shutil.rmtree(DIRECTORY_ANONYMIZED)
    os.makedirs(DIRECTORY_ANONYMIZED)

    for file in filename.all_files:
        print("Cleaning data for {}...".format(file))
        write_anonymized_file(file)

    for directory in os.listdir("{}/{}".format(DIRECTORY_FACEBOOK_DATA, 'messages/inbox')):
        print('Directory: {}...'.format(directory))
        write_anonymized_file('message_1.json', "{}/{}".format('messages/inbox', directory), 'messages/inbox')


def write_anonymized_file(filename, subDirectoryName=None, schema=None):
    directory = "{}/{}".format(DIRECTORY_ANONYMIZED, subDirectoryName if subDirectoryName else filename.split('/')[0])
    fileNameLocal = "{}/{}".format(subDirectoryName, filename) if subDirectoryName else filename
    fileNameLocalObscured = "{}/{}".format(subDirectoryName, filename) if subDirectoryName else filename
    output_file = "{}/{}".format(DIRECTORY_ANONYMIZED, fileNameLocalObscured)
    os.makedirs(directory, exist_ok=True)

    output_data = anonymize_file(fileNameLocal, schema)
    if output_data is None:
        return
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    # Create the directory if it does not exist in

def anonymize_file(filename, schema=None):
    filepath = "{}/{}".format(DIRECTORY_FACEBOOK_DATA, filename)
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print('No data available for file at path {}'.format(filepath))
        return None
    with open(DIRECTORY_DATASTRUCTURES, 'r') as d:
        cleaning_rules = json.load(d)[schema if schema else filename]
    cleaned_data = _apply_rules_to_json(cleaning_rules, data)
    return data


## ANONYMIZATION RULE APPLICATION METHODS

def _apply_rules_to_json(rules, data={}):
    if rules == "IGNORE":
        return data
    elif rules == "MANUAL":
        return {}
    for key in data.keys():
        if key not in rules:
            warning = "(Missing key: {})".format(key)
            if DEBUG_print_missing_key_stack:
                print(warning)
                return -1
            else:
                warnings.warn(warning)
                return
        r_val = rules[key]
        d_val = data[key]
        x = 0
        if r_val is None:
            return        
        if isinstance(d_val, dict):
            if _apply_rules_to_json(r_val, d_val) == -1:
                print(key)
                return
        elif isinstance(d_val, list):
            for i in range(len(d_val)):
                data_value = d_val[i]
                if isinstance(data_value, dict):                    
                    if _apply_rules_to_json(r_val[0], data_value) == -1:
                        print(key)
                        return
                else:
                    d_val[i] = _apply_rule_to_value(r_val[0], data_value)
        else:
            data[key] = _apply_rule_to_value(r_val, d_val)

            
def _apply_rule_to_value(rule, value):
        if rule == "NAME":
            return _fake_name(value)
        elif rule == "TIMESTAMP":
            return _fake_timestamp(value)
        elif rule == "EMAIL":
            return _fake_email(value)
        elif rule == "PHONE":
            return _fake_phone(value)
        elif rule == "TITLE":
            return _fake_title(value)
        elif rule == "TEXT":
            return _fake_text(value)
        elif rule == "URL":
            return _fake_url(value)
        elif rule == "URI":
            return "photos_and_videos/your_posts/some_local_path.jpg"
        elif rule == "IP_ADDRESS":
            return _fake_ip(value)
        elif rule == "LOCATION":
            return _fake_location(value)
        elif rule == "ADDRESS":
            return _fake_address(value)
        elif rule == "LAT":
            return _fake_latitude(value)
        elif rule == "LON":
            return _fake_longitude(value)
        elif rule == "BOOL":
            return _fake_bool()
        # Allow overriding for specific strings
        elif "CUSTOM:" in rule:
            return rule.replace('CUSTOM:','') + "**"
        # For documentation sake, write in which ones we manually tweak
        elif rule == "MANUAL":
            return "MANUAL_OVERWRITE"
        elif rule == "IGNORE":
            return
        elif rule == "EAN":
            return _fake_ean()
        elif "ONEOF:" in rule:
            optionsString = rule.replace('ONEOF:', '')
            options = optionsString.split('|')
            return random.choice(options)
        else:
            warnings.warn("Unable to handle rule '{}'".format(rule))

## ANONYMIZATION HELPER METHODS

def _fake_name(input_name=None):
    name = fake.name()
    return _fake_table_lookup(input_name, name)

def _fake_email(input_email=None):
    email = fake.simple_profile()['mail']
    return _fake_table_lookup(input_email, email)

def _fake_title(input_title=None):
    max_len = max(5, (len(input_title) * 4)/3) if input_title else 15
    title = fake.text(max_nb_chars=max_len)[:-1].title()
    return _fake_table_lookup(input_title, title)

def _fake_text(input_text=None):
    max_len = max(5, (len(input_text) * 4)/3) if input_text else 24
    text = fake.text(max_nb_chars=max_len)[:-1]
    return _fake_table_lookup(input_text, text)

def _fake_timestamp(input_datetime, end_datetime=None, start_datetime=None):
    if input_datetime == 0:
        return 0
    timestamp = int(time.mktime(fake.past_date().timetuple()))
    return _fake_table_lookup(input_datetime, timestamp)

def _fake_phone(input_phone):
    phone = fake.phone_number()
    return _fake_table_lookup(input_phone, phone)

def _fake_url(input_url):
    url = fake.url()
    return _fake_table_lookup(input_url, url)

def _fake_ip(input_ip):
    ip = fake.ipv4_public()
    return _fake_table_lookup(input_ip, ip)

def _fake_location(input_loc):
    loc = "{}, {}".format(fake.city(), fake.state())
    return _fake_table_lookup(input_loc, loc)

def _fake_address(input_addr):
    address = fake.address().replace('\n', ' ')[:-6]
    return _fake_table_lookup(input_addr, address)

def _fake_latitude(input_lat):
    lat = fake.latitude()
    return _fake_table_lookup(input_lat, lat)

def _fake_longitude(input_lon):
    lon = fake.longitude()
    return _fake_table_lookup(input_lon, lon)

def _fake_bool():
    return fake.boolean()

def _fake_ean():
    return fake.ean(length=13)

def _fake_table_lookup(key, value):
    # if key is None:
    #     return value
    # elif key not in fakes_table:
    #     fakes_table[key] = value
    # else:
    #     value = fakes_table[key]
    return value


if __name__ == '__main__':
    main()