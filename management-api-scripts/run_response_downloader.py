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
    parser.add_argument("--page_size", default=None)
    parser.add_argument("--page", default=None)
    args = parser.parse_args()

    study_key = args.study_key
    survey_key = args.survey_key
    survey_info_lang = args.survey_info_lang
    survey_info_format = args.survey_info_format
    response_format = args.response_format
    short_keys = args.short_keys
    key_separator = args.key_separator
    page_size = args.page_size
    page = args.page

    with_meta_infos = {
        "withPositions": "true" if args.meta_pos else "false",
        "withInitTimes": "true" if args.meta_init else "false",
        "withDisplayTimes": "true" if args.meta_disp else "false",
        "withResponseTimes": "true" if args.meta_resp else "false",
    }

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

    resp = client.get_response_csv(
        study_key, survey_key,
        key_separator,
        response_format,
        short_keys,
        with_meta_infos,
        query_start_date, query_end_date, 
        page_size, page,
    )
    if resp is None:
        print("No files were generated.")
        exit()

    output_folder = "export_" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    os.makedirs(output_folder)

    query_range_text = ""
    if args.query_start_date is not None:
        query_range_text += "_" + args.query_start_date
    if args.query_end_date is not None:
        query_range_text += "_" + args.query_end_date

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
