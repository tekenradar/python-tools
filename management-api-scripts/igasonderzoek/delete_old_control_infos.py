import yaml
import argparse
import os
import json
import requests
from influenzanet.api import ManagementAPIClient

def read_yaml(config_path):
    configs = yaml.load(
        open(config_path, 'r', encoding='UTF-8'),  Loader=yaml.FullLoader)
    return configs


def should_use_external_idp(configs):
    try:
        return configs["use_external_idp"]
    except KeyError:
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--global_config_yaml", help="global configuration file path", default=os.path.join('resources', 'config.yaml'))
    parser.add_argument(
        "--api", help="api address")

    args = parser.parse_args()

    configs = read_yaml(args.global_config_yaml)
    user_credentials = configs["user_credentials"]
    management_api_url = configs["management_api_url"]
    participant_api_url = configs["participant_api_url"]
    use_external_idp = should_use_external_idp(configs)

    api = args.api

    client = ManagementAPIClient(management_api_url, user_credentials, use_external_idp=use_external_idp)


    r = requests.delete(
            api + '/streptokids/expired-registrations',
            headers=client.auth_header)
    if r.status_code != 200:
        raise ValueError(r.content)
    try:
        print('deleted count: {}'.format(r.json()['count']))
    except Exception as e:
        print(e)



