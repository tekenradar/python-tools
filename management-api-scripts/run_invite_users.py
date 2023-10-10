import os
import json
import argparse
import random
import string
from time import sleep

from influenzanet.api import ManagementAPIClient
from utils import read_yaml, should_use_external_idp


def get_random_password_string(length):
    numbers = string.digits
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    symbols = string.punctuation

    password = [
        random.choice(numbers),
        random.choice(lowercase),
        random.choice(uppercase),
        random.choice(symbols)
    ]

    password += random.choices(numbers + lowercase + uppercase + symbols, k=length)

    random.shuffle(password)
    return ''.join(password)


def log_migration_events(type, users_impacted, log_file_path):
    if len(users_impacted) > 0:
        batchname = os.path.basename(log_file_path).split('.')[0]
        new_filename = batchname + '_' + str(type) + '.json'
        json.dump(users_impacted, open(new_filename, 'w', encoding='utf-8'))
        print(str(type) + ' users saved into: ', new_filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--global_config_yaml", help="global configuration file path", default=os.path.join('resources', 'config.yaml'))
    parser.add_argument(
        "--sleep", type=float, help="delay in seconds", default=0.5)
    parser.add_argument(
        "--user_list", help="JSON file with the exported list of email addresses and old participant IDs", required=True)

    args = parser.parse_args()

    configs = read_yaml(
        args.global_config_yaml)
    user_credentials = configs["user_credentials"]
    management_api_url = configs["management_api_url"]
    participant_api_url = configs["participant_api_url"]
    use_external_idp = should_use_external_idp(configs)
    sleep_delay = args.sleep

    client = ManagementAPIClient(
        management_api_url, user_credentials, participant_api_url=participant_api_url, use_external_idp=use_external_idp)

    user_batch_path = args.user_list
    new_users = json.load(open(user_batch_path, 'r', encoding='utf-8'))
    skipped_users = []
    failed_users = []
    client.renew_token()

    for i, u in enumerate(new_users):
        if u['oldParticipantIDs'] == []:
            skipped_users.append({
                'email': u['email'],
                'oldParticipantIDs': '',
                'error': 'Empty profiles'
            })
            continue
        user_object = u
        user_object['initialPassword'] = get_random_password_string(15)

        if i > 0 and i % 20 == 0:
            client.renew_token()
        print('Processing ', i + 1, ' of ', len(new_users))
        try:
            client.migrate_user(user_object)
        except ValueError as err:
            failed_users.append({
                'email': user_object['accountId'],
                'oldParticipantIDs': user_object['oldParticipantIDs'],
                'error': str(err)
            })
        sleep(sleep_delay)

    print(len(new_users) - len(failed_users) - len(skipped_users),
          ' out of ', len(new_users), 'users created')
    print(len(failed_users),
          ' out of ', len(new_users), 'users failed')
    print(len(skipped_users),
          ' out of ', len(new_users), 'users skipped')
    log_migration_events('failed', failed_users, user_batch_path)
    log_migration_events('skipped', skipped_users, user_batch_path)
