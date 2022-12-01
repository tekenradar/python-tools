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
    parser.add_argument("--file_type", default=None)
    parser.add_argument("--participant", default=None)
    parser.add_argument("--query_start_date", default=None)
    parser.add_argument("--query_end_date", default=None)
    args = parser.parse_args()

    study_key = args.study_key
    file_type = args.file_type
    participant = args.participant
    query_start_date = args.query_start_date
    query_end_date = args.query_end_date
    if query_start_date is not None:
        query_start_date = datetime.strptime(
            query_start_date, "%Y-%m-%d-%H-%M-%S").timestamp()

    if query_end_date is not None:
        query_end_date = datetime.strptime(
            query_end_date, "%Y-%m-%d-%H-%M-%S").timestamp()

    configs = read_yaml(
        args.global_config_yaml)
    user_credentials = configs["user_credentials"]
    management_api_url = configs["management_api_url"]
    use_external_idp = should_use_external_idp(configs)

    client = ManagementAPIClient(
        management_api_url, user_credentials, use_external_idp=use_external_idp)

    resp = client.get_file_infos(
        study_key, file_type,
        participant,
        query_start_date, query_end_date
    )
    if resp is None:
        print("No files were generated.")
        exit()

    output_folder = 'downloads'
    os.makedirs(output_folder, exist_ok=True)

    query_range_text = ""
    if args.query_start_date is not None:
        query_range_text += "_" + args.query_start_date
    if args.query_end_date is not None:
        query_range_text += "_" + args.query_end_date

    info_file_name = os.path.join(output_folder, "{}_file_infos{}.json".format(study_key, query_range_text))
    json.dump(resp, open(info_file_name, 'w', encoding='utf-8'))
    print("File generated at: {}".format(info_file_name))
