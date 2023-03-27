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
                    "childIndex": int(c_ind) - 1
                }
                invites["participants"].append(p_info)

    batch_size = 5

    print(len(invites["participants"]))
    batch_count = -(len(invites["participants"]) // -batch_size)
    print('Total batches: {}'.format(batch_count))

    current_batch = 0
    total_sent = 0
    for i in range(0, len(invites["participants"]), batch_size):
        batch = invites["participants"][i:i+batch_size]
        current_batch += 1
        r = requests.post(
            api + '/igasonderzoek/invite', data=json.dumps({"participants": batch}),
            headers=client.auth_header)
        if r.status_code != 200:
            raise ValueError(r.content)
        try:
            total_sent += r.json()['count']
            print('Batch #{}: {} messages sent / id count: {}'.format(current_batch, r.json()['count'], len(batch)))
        except Exception as e:
            print(e)
        if current_batch > 0 and current_batch % 50 == 0:
            client.renew_token()

    print('Total sent: {}'.format(total_sent))


