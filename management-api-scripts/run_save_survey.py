import os
import json
import argparse
from datetime import datetime
from influenzanet.api import ManagementAPIClient
from utils import read_yaml, should_use_external_idp


def read_survey_json(path):
    survey_def = json.load(open(path, 'r', encoding='UTF-8'))
    return survey_def


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--global_config_yaml", help="global configuration file path", default=os.path.join('resources', 'config.yaml'))
    parser.add_argument(
        "--study_key", help="study key to which study the survey should be saved", required=True)
    parser.add_argument(
        "--survey_json", help="path to the survey json", required=True)

    args = parser.parse_args()

    configs = read_yaml(
        args.global_config_yaml)
    user_credentials = configs["user_credentials"]
    management_api_url = configs["management_api_url"]
    use_external_idp = should_use_external_idp(configs)

    study_key = args.study_key
    survey_path = args.survey_json

    client = ManagementAPIClient(
        management_api_url, user_credentials, use_external_idp=use_external_idp)

    survey_def = read_survey_json(survey_path)

    resp = client.save_survey_to_study(study_key, survey_def)
    print('survey saved succcessfully')

