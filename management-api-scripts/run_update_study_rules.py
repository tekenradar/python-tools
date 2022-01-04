import os
import json
import argparse
from management_api import ManagementAPIClient
from utils import read_yaml, should_use_external_idp


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--global_config_yaml", help="global configuration file path", default=os.path.join('resources', 'config.yaml'))
    parser.add_argument(
        "--rules_json_path", help="file path to the survey rules json", required=True)
    parser.add_argument(
        "--study_key", help="study key, the rules should be updated for", required=True)

    args = parser.parse_args()

    configs = read_yaml(args.global_config_yaml)
    user_credentials = configs["user_credentials"]
    management_api_url = configs["management_api_url"]
    use_external_idp = should_use_external_idp(configs)

    study_key = args.study_key
    rules_path = args.rules_json_path

    client = ManagementAPIClient(
        management_api_url, user_credentials, use_external_idp=use_external_idp)

    rules = json.load(open(rules_path, 'r', encoding='UTF-8'))
    client.update_study_rules(study_key, rules)
