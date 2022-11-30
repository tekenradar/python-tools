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
        "--survey_list", help="path to the text file containing the list of survey json paths", required=True)

    args = parser.parse_args()

    configs = read_yaml(
        args.global_config_yaml)
    user_credentials = configs["user_credentials"]
    management_api_url = configs["management_api_url"]
    use_external_idp = should_use_external_idp(configs)

    study_key = args.study_key
    survey_list = args.survey_list

    client = ManagementAPIClient(
        management_api_url, user_credentials, use_external_idp=use_external_idp)

    surveys = []
    with open(survey_list, 'r', encoding='utf-8') as f:
        paths = f.readlines()
        for p in paths:
            p = p.strip()
            if not os.path.exists(p):
                print("WARNING: file at path '{}' does not exist".format(p))
                continue
            surveys.append(p)

    if len(surveys) < 1:
        print("No surveys found. Please ensure the survey list contains valid content.")
        exit()

    for survey_path in surveys:
        survey_def = read_survey_json(survey_path)
        survey_key = survey_def['survey']['surveyDefinition']['key']
        try:
            resp = client.save_survey_to_study(study_key, survey_def)
            print("Survey '{}' saved.".format(survey_key))
        except:
            continue


