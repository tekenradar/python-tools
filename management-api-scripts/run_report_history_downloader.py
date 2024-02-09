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
    parser.add_argument("--report_key", type=str, default=None)
    parser.add_argument("--query_start_date", default=None)
    parser.add_argument("--query_end_date", default=None)
    parser.add_argument("--participant_id", default=None)
    parser.add_argument("--as_csv", action="store_true", default=False)

    args = parser.parse_args()

    study_key = args.study_key
    report_key = args.report_key
    participant_id = args.participant_id
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

    resp = client.get_participant_reports(
        study_key,
        report_key,
        participant_id,
        query_start_date,
        query_end_date
    )
    if resp is None:
        print("No files were generated.")
        exit()

    output_folder = "downloads"
    os.makedirs(output_folder, exist_ok=True)

    if args.as_csv:
        print("Converting to CSV")
        import pandas as pd
        import json
        flat_resp = []

        for report in resp["reports"]:
            flat_report = {}
            for k, v in report.items():
                if k != "data":
                    flat_report[k] = v
                else:
                    for entry in report["data"]:
                        flat_report[entry["key"]] = entry["value"]
            flat_resp.append(flat_report)
        df = pd.DataFrame(flat_resp)
        filename = "reports_{}_{}.csv".format(study_key, datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
        output_path = os.path.join(output_folder, filename)
        df.to_csv(output_path, index=False)
        print('Saved file at {}'.format(output_path))
        exit()
    else:
        filename = "reports_{}_{}.json".format(study_key, datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
        output_path = os.path.join(output_folder, filename)
        with open(output_path, 'w') as f:
            json.dump(resp, f)
            print('Saved file at {}'.format(output_path))
