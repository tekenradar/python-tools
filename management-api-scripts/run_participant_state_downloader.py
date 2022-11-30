import os
import json
import argparse
from influenzanet.api import ManagementAPIClient
from utils import read_yaml, should_use_external_idp
from datetime import datetime

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--global_config_yaml", help="global configuration file path", default=os.path.join('resources', 'config.yaml'))
    parser.add_argument("--study_key", type=str, required=True)
    parser.add_argument("--status", type=str, required=False, default=None)

    args = parser.parse_args()

    study_key = args.study_key
    status = args.status

    configs = read_yaml(
        args.global_config_yaml)
    user_credentials = configs["user_credentials"]
    management_api_url = configs["management_api_url"]
    use_external_idp = should_use_external_idp(configs)

    client = ManagementAPIClient(
        management_api_url, user_credentials, use_external_idp=use_external_idp)

    resp = client.get_participant_states(
        study_key, status,
    )
    if resp is None:
        print("No files were generated.")
        exit()

    output_folder = "downloads"
    os.makedirs(output_folder, exist_ok=True)
    filename = "participant_states_{}_{}.json".format(study_key, datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
    output_path = os.path.join(output_folder, filename)
    with open(output_path, 'w') as f:
        json.dump(resp, f)
        print('Saved file at {}'.format(output_path))
