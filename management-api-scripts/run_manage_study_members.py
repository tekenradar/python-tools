import os
import argparse
from influenzanet.api import ManagementAPIClient
from utils import read_yaml, should_use_external_idp


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--global_config_yaml", help="global configuration file path", default=os.path.join('resources', 'config.yaml'))
    parser.add_argument(
        "--action", help="ADD or REMOVE", default='ADD')
    parser.add_argument(
        "--study_key", help="key of the study, the user should be added to or removed from", required=True)
    parser.add_argument(
        "--user_id", help="user id of the RESEARCHER user to be added", required=True)
    parser.add_argument(
        "--user_name", help="user name of the RESEARCHER user", required=True)

    args = parser.parse_args()

    configs = read_yaml(
        args.global_config_yaml)
    user_credentials = configs["user_credentials"]
    management_api_url = configs["management_api_url"]
    participant_api_url = configs["participant_api_url"]
    use_external_idp = should_use_external_idp(configs)

    action = args.action
    study_key = args.study_key
    user_id = args.user_id
    user_name = args.user_name

    client = ManagementAPIClient(
        management_api_url, user_credentials, participant_api_url=participant_api_url, use_external_idp=use_external_idp)

    if action == 'ADD':
        client.add_study_member(study_key, user_id, user_name)
    elif action == 'REMOVE':
        client.remove_study_member(study_key, user_id)
    else:
        raise('unknown action: ' + action)
