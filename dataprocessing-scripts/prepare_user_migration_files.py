import json
import argparse
import pandas as pd
from datetime import datetime

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True)
    args = parser.parse_args()

    input_filename = args.input

    orig_data = pd.read_csv(input_filename, index_col=0)

    unique_emails = orig_data['accountId'].unique()

    new_users = []

    for email in unique_emails:
        user_orig_data = orig_data[orig_data['accountId'] == email]

        new_user = {
            "accountId": email,
            "oldParticipantIDs": [],
            "profileNames": [],
            "preferredLanguage": "nl",
            "studies": [
                "tekenradar"
            ],
            "use2FA": True,
            "accountConfirmedAt": 10,
            "createdAt": 0,
            "reports": []
        }

        profile_ids = user_orig_data['oldParticipantIDs'].unique()

        for old_pid in profile_ids:
            profile_data = user_orig_data[user_orig_data['oldParticipantIDs'] == old_pid]

            new_user["oldParticipantIDs"].append(str(old_pid))
            new_user["profileNames"].append(profile_data["profileNames"].values[0])

            for _, report_row in profile_data[profile_data["key"].notna()].iterrows():
                ts = int(datetime.strptime(report_row['timestamp'], "%Y-%m-%d %H:%M:%S").timestamp())

                report = {
                    "key": report_row['key'],
                    "profile_id": str(old_pid),
                    "study_key": "tekenradar",
                    "timestamp": ts,
                    "data": [
                        {
                            "key": "icon",
                            "value": report_row['key'],
                        },
                    ]
                }
                if report_row['key'] == "TB":

                    # handle count:
                    if pd.notnull(report_row["count"]):
                        report["data"].append({
                            "key": "count",
                            "value": str(int(report_row["count"])),
                            "dtype": "int"
                        })

                    # handle activity:
                    if pd.notnull(report_row["activity"]):
                        report["data"].append({
                            "key": "activity",
                            "value": str(report_row["activity"]),
                            "dtype": "keyList"
                        })

                    # handle environment:
                    if pd.notnull(report_row["environment"]):
                        report["data"].append({
                            "key": "environment",
                            "value": str(report_row["environment"]),
                            "dtype": "keyList"
                        })

                    # handle location:
                    if pd.notnull(report_row["location"]):
                        report["data"].append({
                            "key": "location",
                            "value": str(report_row["location"]),
                            "dtype": "string"
                        })
                new_user["reports"].append(report)

        new_users.append(new_user)


    json.dump(new_users, open(input_filename.split('.')[0] + '.json', 'w', encoding='utf-8'))