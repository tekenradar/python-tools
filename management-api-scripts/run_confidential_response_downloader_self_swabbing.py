import os
import json
import argparse
from management_api import ManagementAPIClient
from utils import read_yaml, should_use_external_idp
from datetime import datetime
import pandas as pd


def get_email(item):
    try:
        return item["responses"][0]["response"]["items"][0]["value"]
    except:
        return ""


def get_phone(item):
    try:
        return item["responses"][0]["response"]["items"][0]["value"]
    except:
        return ""


def get_first_name(item):
    try:
        cloze_items = item["responses"][0]["response"]["items"][0]["items"]
        for ci in cloze_items:
            if ci["key"] == "vn":
                return ci["value"]
    except:
        return ""
    return ""


def get_last_name(item):
    try:
        cloze_items = item["responses"][0]["response"]["items"][0]["items"]
        for ci in cloze_items:
            if ci["key"] == "an":
                return ci["value"]
    except:
        return ""
    return ""


def get_addr_infos(item):
    gp_infos = {}
    try:
        cloze_items = item["responses"][0]["response"]["items"][0]["items"]
        for ci in cloze_items:
            if ci["key"] == "street":
                gp_infos["street"] = ci["value"]
            elif ci["key"] == "nr":
                gp_infos["nr"] = ci["value"]
            elif ci["key"] == "zip":
                gp_infos["zip"] = ci["value"]
            elif ci["key"] == "city":
                gp_infos["city"] = ci["value"]
    except:
        return gp_infos
    return gp_infos


def parse_confidential_data(data):
    if "responses" not in data.keys():
        return None

    responses = {}
    for r in data["responses"]:
        pid = r["participantId"]

        if pid not in responses.keys():
            responses[pid] = {
                "participantID": pid
            }

        current_participant = responses[pid]

        item_key = r['key']
        if "Email" in item_key:
            current_participant["email"] = get_email(r)
        elif "Name" in item_key:
            current_participant["firstname"] = get_first_name(r)
            current_participant["lastname"] = get_last_name(r)
        elif "Tel" in item_key:
            current_participant["phone"] = get_phone(r)
        elif "Addr" in item_key:
            current_participant = {**current_participant, **get_addr_infos(r)}
        else:
            print("Unexpected item key: {}".format(item_key))

        responses[pid] = current_participant

    return responses


def save_as_csv(filename, data):
    # column_names = ["participantID", "email", "firstname", "lastname", "gender", "phone", "gp_office", "gp_name", "gp_address_street", "gp_address_number", "gp_address_postalcode", "gp_address_city", "gp_phone"]
    df = []
    for pID in data.keys():
        df.append(data[pID])
    df = pd.DataFrame(df)
    df.to_csv(filename, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--global_config_yaml", help="global configuration file path", default=os.path.join('resources', 'config.yaml'))
    parser.add_argument("--study_key", type=str, required=True)
    parser.add_argument("--participants_list", type=str, required=True)

    args = parser.parse_args()

    study_key = args.study_key
    p = args.participants_list

    condition = {
        "name": "gt",
        "data": [
            {
                "dtype": "num",
                "num": 1
            },
            {
                "dtype": "num",
                "num": 0
            }
        ]
    }

    participants = [l.strip() for l in open(p, 'r', encoding='UTF-8').readlines()]

    configs = read_yaml(
        args.global_config_yaml)
    user_credentials = configs["user_credentials"]
    management_api_url = configs["management_api_url"]
    use_external_idp = should_use_external_idp(configs)

    client = ManagementAPIClient(
        management_api_url, user_credentials, use_external_idp=use_external_idp)

    query = {
        "participantIds": participants,
        "keyFilter": '',
        "condition": condition
    }

    resp = client.get_confidential_responses(
        study_key,
        query
    )
    if resp is None:
        print("No files were generated.")
        exit()

    output_folder = "downloads"
    os.makedirs(output_folder, exist_ok=True)
    filename = "confidential_responses_{}_{}.json".format(study_key, datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
    output_path = os.path.join(output_folder, filename)
    with open(output_path, 'w') as f:
        json.dump(resp, f)
        print('Saved file at {}'.format(output_path))

    filename = "confidential_responses_{}_{}.csv".format(study_key, datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
    output_path = os.path.join(output_folder, filename)
    cdata = parse_confidential_data(resp)
    save_as_csv(output_path, cdata)