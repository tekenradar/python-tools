import os
import json
import argparse
from management_api import ManagementAPIClient
from utils import read_yaml, should_use_external_idp
from datetime import datetime


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


def get_birthday(item):
    try:
        return item["responses"][0]["response"]["items"][0]["value"]
    except:
        return ""


def get_gender(item):
    try:
        return item["responses"][0]["response"]["items"][0]["items"][0]["key"]
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


def get_gp_infos(item):
    gp_infos = {}
    try:
        cloze_items = item["responses"][0]["response"]["items"][0]["items"]
        for ci in cloze_items:
            if ci["key"] == "pn":
                gp_infos["gp_office"] = ci["value"]
            elif ci["key"] == "nh":
                gp_infos["gp_name"] = ci["value"]
            elif ci["key"] == "str":
                gp_infos["gp_address_street"] = ci["value"]
            elif ci["key"] == "hnr":
                gp_infos["gp_address_number"] = ci["value"]
            elif ci["key"] == "pc":
                gp_infos["gp_address_postalcode"] = ci["value"]
            elif ci["key"] == "plaats":
                gp_infos["gp_address_city"] = ci["value"]
            elif ci["key"] == "tel":
                gp_infos["gp_phone"] = ci["value"]
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
            responses[pid] = {}

        current_participant = responses[pid]

        item_key = r['key']
        if "Email" in item_key:
            current_participant["email"] = get_email(r)
        elif "Naam" in item_key:
            current_participant["firstname"] = get_first_name(r)
            current_participant["lastname"] = get_last_name(r)
        elif "GENDER" in item_key:
            current_participant["gender"] = get_gender(r)
        elif "Tel" in item_key:
            current_participant["phone"] = get_phone(r)
        elif "Birthday" in item_key:
            current_participant["birthday"] = get_birthday(r)
        elif "GP" in item_key:
            current_participant = {**current_participant, **get_gp_infos(r)}
        else:
            print("Unexpected item key: {}".format(item_key))

        responses[pid] = current_participant

    return responses


def save_as_csv(filename, data):
    keys = ["participantID", "email", "firstname", "lastname", "gender", "phone", "gp_office", "gp_name", "gp_address_street", "gp_address_number", "gp_address_postalcode", "gp_address_city", "gp_phone"]
    with open(filename, 'w') as f:
        line = ",".join(keys)
        line += '\n'
        f.write(line)

        for pID in data.keys():
            lineInfos = []
            lineInfos.append(pID)
            pData = data[pID]
            for i in range(1, len(keys)):
                k = keys[i]
                if k not in pData.keys():
                    lineInfos.append('')
                else:
                    lineInfos.append(pData[k])

            line = ",".join(lineInfos)
            line += '\n'
            f.write(line)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--global_config_yaml", help="global configuration file path", default=os.path.join('resources', 'config.yaml'))
    parser.add_argument("--study_key", type=str, required=True)
    parser.add_argument("--condition_path", type=str, required=True)
    parser.add_argument("--participants_list", type=str, required=True)
    parser.add_argument("--key_filter", type=str, default='')

    args = parser.parse_args()

    study_key = args.study_key
    key_filter = args.key_filter
    condition_path = args.condition_path
    p = args.participants_list

    condition = json.load(open(condition_path, 'r', encoding='UTF-8'))

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
        "keyFilter": key_filter,
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