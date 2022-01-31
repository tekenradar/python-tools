import os
import yaml
import json
import argparse
from management_api import ManagementAPIClient
from utils import read_yaml, should_use_external_idp
from datetime import datetime


if __name__ == "__main__":



    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--global_config_yaml", help="global configuration file path", default=os.path.join('resources', 'config.yaml'))
    parser.add_argument(
        "--query", help="path the the yaml file with the query config", required=True)
    """
    parser.add_argument("--study_key", type=str, required=True)
    parser.add_argument("--survey_key", type=str, required=True)
    parser.add_argument("--survey_info_lang", type=str, required=True)
    parser.add_argument("--survey_info_format",
                        choices=["csv", "json"], default="json")
    parser.add_argument("--response_format",
                        choices=["long", "wide", "json"], default="wide")
    parser.add_argument("--key_separator", default="-")
    parser.add_argument("--query_start_date", default=None)
    parser.add_argument("--query_end_date", default=None)
    parser.add_argument("--short_keys", action='store_true')
    parser.add_argument("--with_meta_positions",
                        dest='meta_pos', action='store_true')
    parser.add_argument("--with_meta_init_times",
                        dest='meta_init', action='store_true')
    parser.add_argument("--with_meta_response_times",
                        dest='meta_resp', action='store_true')
    parser.add_argument("--with_meta_display_times",
                        dest='meta_disp', action='store_true')
    parser.add_argument("--with_meta_item_versions",
                        dest='meta_version', action='store_true')
    """
    args = parser.parse_args()

    query = read_yaml(args.query)
    study_key = query["study_key"]
    survey_keys = query["survey_keys"]
    survey_info_lang = query["survey_info_lang"]
    survey_info_format = query["survey_info_format"]
    response_format = query["response_format"]
    short_keys = query["short_keys"]
    key_separator = query["key_separator"]
    print(query)

    with_meta_infos = {
        "withPositions": query["metaInfos"]["position"],
        "withItemVersions": query["metaInfos"]["itemVersion"],
        "withInitTimes": query["metaInfos"]["initTimes"],
        "withDisplayTimes": query["metaInfos"]["displayTimes"],
        "withResponseTimes": query["metaInfos"]["responseTimes"],
    }

    query_start_date = query["query_start"]
    query_end_date = query["query_end"]

    if query_start_date is not None:
        query_start_date = datetime.strptime(
            query_start_date, "%Y-%m-%d-%H-%M-%S").timestamp()

    if query_end_date is not None:
        query_end_date = datetime.strptime(
            query_end_date, "%Y-%m-%d-%H-%M-%S").timestamp()

    configs = read_yaml(args.global_config_yaml)
    user_credentials = configs["user_credentials"]
    management_api_url = configs["management_api_url"]
    use_external_idp = should_use_external_idp(configs)

    client = ManagementAPIClient(
        management_api_url, user_credentials, use_external_idp=use_external_idp)

    output_folder = "export_" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    os.makedirs(output_folder)

    for survey_key in survey_keys:
        print("Downloading responses for {}".format(survey_key))

        resp = client.get_response_csv(
            study_key, survey_key,
            key_separator,
            response_format,
            short_keys,
            with_meta_infos,
            query_start_date, query_end_date
        )
        if resp is None:
            print("No files were generated.")
            continue

        query_range_text = ""
        if query["query_start"] is not None:
            query_range_text += "_" + query["query_start"]
        if query["query_end"] is not None:
            query_range_text += "_" + query["query_end"]

        ext = 'csv'
        if response_format == 'json':
            ext = 'json'

        response_file_name = os.path.join(
            output_folder,
            "{}_{}_responses{}.{}".format(study_key, survey_key, query_range_text, ext)
        )
        with open(response_file_name, 'w', encoding='utf-8') as f:
            f.write(resp)
        print("File generated at: {}".format(response_file_name))

        survey_info_text = ""
        if survey_info_format == "csv":
            survey_info_text = client.get_survey_info_preview_csv(
                study_key, survey_key, survey_info_lang, short_keys
            )
        else:
            survey_infos = client.get_survey_info_preview(
                study_key, survey_key, survey_info_lang, short_keys
            )
            if survey_infos is not None:
                survey_info_text = json.dumps(survey_infos, indent=2)

        info_file_name = os.path.join(
            output_folder,
            "{}_{}_survey_info.{}".format(
                study_key, survey_key, survey_info_format)
        )
        with open(info_file_name, 'w', encoding='utf-8') as f:
            f.write(survey_info_text)
        print("File generated at: {}".format(info_file_name))


