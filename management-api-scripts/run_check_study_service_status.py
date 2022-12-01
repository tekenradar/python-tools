import os
import argparse
from influenzanet.api import ManagementAPIClient
from utils import read_yaml


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--global_config_yaml", help="global configuration file path", default=os.path.join('resources', 'config.yaml'))

    args = parser.parse_args()

    configs = read_yaml(
        args.global_config_yaml)
    user_credentials = configs["user_credentials"]
    management_api_url = configs["management_api_url"]
    participant_api_url = configs["participant_api_url"]

    client = ManagementAPIClient(management_api_url, user_credentials, participant_api_url=participant_api_url, use_no_login=True)
    client.check_study_service_status()