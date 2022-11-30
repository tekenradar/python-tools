import os
import argparse
import pandas as pd
from influenzanet.api import ManagementAPIClient
from utils import read_yaml, should_use_external_idp


def generate_rule_for_participant(code: str):
    return [
        {
            "name": "UPDATE_FLAG",
            "data": [
            {
                "dtype": "str",
                "str": "externalStudyCode"
            },
            {
                "dtype": "str",
                "str": code
            }
            ]
        },
        {
            "name": "ADD_MESSAGE",
            "data": [
            {
                "dtype": "str",
                "str": "invite-to-external-study"
            },
            {
                "dtype": "exp",
                "exp": {
                "name": "timestampWithOffset",
                "data": [
                    {
                    "dtype": "num",
                    "num": 0
                    }
                ]
                }
            }
            ]
        }
    ]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--global_config_yaml", help="global configuration file path", default=os.path.join('resources', 'config.yaml'))
    parser.add_argument(
        "--study_key", help="study key, the rules should be updated for", required=True)
    parser.add_argument(
        "--participants", help="for which participants should the rules applied for", required=True)

    args = parser.parse_args()

    participants = pd.read_csv(args.participants)

    configs = read_yaml(
        args.global_config_yaml)
    user_credentials = configs["user_credentials"]
    management_api_url = configs["management_api_url"]
    use_external_idp = should_use_external_idp(configs)

    study_key = args.study_key
    client = ManagementAPIClient(
        management_api_url, user_credentials, use_external_idp=use_external_idp)



    for index, row in participants.iterrows():
        rules = generate_rule_for_participant(row.code)
        pid = row.participantID

        if len(pid) < 4:
            print("unexpected participant ID: {}".format(pid))
            continue
        resp = client.run_custom_study_rules_for_single_participant(study_key, rules, pid)
        print('Applying for participant: {}'.format(pid))
        if 'participantStateChangePerRule' in resp.keys():
            for i, c in enumerate(resp['participantStateChangePerRule']):
                print('\tRule #{}: changed {} of {} participants'.format(
                    i+1, c, resp['participantCount']))
    print("Ready with all participants.")
