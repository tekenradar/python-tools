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
        "--id_list", help="text file containing one id per row")
    parser.add_argument(
        "--api", help="api address")

    args = parser.parse_args()

    configs = read_yaml(args.global_config_yaml)
    user_credentials = configs["user_credentials"]
    management_api_url = configs["management_api_url"]
    participant_api_url = configs["participant_api_url"]
    use_external_idp = should_use_external_idp(configs)

    id_list_path = args.id_list
    api = args.api

    client = ManagementAPIClient(management_api_url, user_credentials, use_external_idp=use_external_idp)

    invites  = {
        "participants": []
    }
    with open(id_list_path) as f:
        for line in f.readlines():
            l = line.strip()
            if len(l) > 0:
                ref, c_ind = l.split(',')
                p_info = {
                    "reference": ref,
                    "childIndex": int(c_ind)
                }
                invites["participants"].append(p_info)


    r = requests.post(
            api + '/igasonderzoek/invite', data=json.dumps(invites),
            headers=client.auth_header)
    if r.status_code != 200:
        raise ValueError(r.content)
    try:
        print('{} messages sent / id count: {}'.format(r.json()['count'], len(invites["participants"])))
    except Exception as e:
        print(e)


