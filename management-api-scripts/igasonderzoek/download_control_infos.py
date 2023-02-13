import yaml
import argparse
import os
import json
import requests
from datetime import datetime
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
    parser.add_argument("--since", default=None)
    parser.add_argument("--include_invited", action='store_true')
    parser.add_argument(
        "--api", help="api address")

    args = parser.parse_args()

    configs = read_yaml(args.global_config_yaml)
    user_credentials = configs["user_credentials"]
    management_api_url = configs["management_api_url"]
    participant_api_url = configs["participant_api_url"]
    use_external_idp = should_use_external_idp(configs)

    since = int(datetime.strptime(args.since, "%Y-%m-%d-%H-%M-%S").timestamp())
    include_invited = args.include_invited
    api = args.api

    client = ManagementAPIClient(management_api_url, user_credentials, use_external_idp=use_external_idp)



    r = requests.get(
            api + '/igasonderzoek/registration',
            headers=client.auth_header,
            params={
                "since": since,
                "includeInvited": "true" if include_invited else "false"
            }
            )
    if r.status_code != 200:
        raise ValueError(r.content)

    contacts = r.json()['contact']

    if len(contacts) < 1:
        print("no contact info found after {}".format(args.since))
        exit()

    sep = ','
    lines = [
        sep.join(['id', 'inviteCode', 'submittedAt', 'invited',
        'kind 1 - birthyear', 'kind 1 - birthmonth', 'kind 1 - gender',
        'kind 2 - birthyear', 'kind 2 - birthmonth', 'kind 2 - gender',
        'kind 3 - birthyear', 'kind 3 - birthmonth', 'kind 3 - gender',
        'kind 4 - birthyear', 'kind 4 - birthmonth', 'kind 4 - gender',
        'kind 5 - birthyear', 'kind 5 - birthmonth', 'kind 5 - gender',
        ])
    ]

    for c in contacts:
        c_infos = []
        for info in c['children']:
            c_infos.extend([str(info['birthyear']), str(info['birthmonth']), info['gender']])
        general = [
            c['id'],
            c['controlCode'],
            datetime.fromtimestamp(c['submittedAt']).strftime("%Y-%m-%d-%H-%M-%S"),
            datetime.fromtimestamp(c['invitedAt']).strftime("%Y-%m-%d-%H-%M-%S") if c['invitedAt'] > 0 else 'Not invited'
        ]
        line = sep.join([
            *general,
            *c_infos,
        ])
        lines.append(line)

    content = '\n'.join(lines)

    with open('igas_controls_since_{}.csv'.format(args.since), 'w') as f:
        f.write(content)
