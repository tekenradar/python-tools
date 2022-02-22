import os
import json
import argparse
from management_api import ManagementAPIClient
from utils import read_yaml, should_use_external_idp
import base64
from datetime import datetime


def read_and_convert_html(path):
    content = open(path, 'r', encoding='UTF-8').read()
    return base64.b64encode(content.encode()).decode()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--global_config_yaml", help="global configuration file path", default=os.path.join('resources/longcovid', 'config.yaml'))
    parser.add_argument(
        "--email_folder", help="Folder to the email config", required=True)

    args = parser.parse_args()

    configs = read_yaml(args.global_config_yaml)
    user_credentials = configs["user_credentials"]
    management_api_url = configs["management_api_url"]
    use_external_idp = should_use_external_idp(configs)

    email_folder = args.email_folder
    email_config = json.load(open(os.path.join(email_folder, 'config.json')))

    del email_config['sendingTime']

    translationsDefs = email_config['translations']

    headerOverrides = None
    try:
        headerOverrides = email_config["headerOverrides"]
    except KeyError:
        pass

    message_config = {
        "type": email_config["sendTo"],
        "studyKey": email_config["studyKey"],
        "label": email_config["label"],
        "period": email_config["period"],
        "condition": email_config["condition"],
        "template": {
            "headerOverrides": headerOverrides,
            "messageType": email_config["messageType"],
            "defaultLanguage": email_config["defaultLanguage"],
            "translations":  []
        }
    }

    for tr in email_config['translations']:
        message_config['template']['translations'].append({
            'lang': tr['lang'],
            'subject': tr['subject'],
            'templateDef': read_and_convert_html(
                os.path.join(email_folder, tr['lang'] + '.html')
            )
        })

    client = ManagementAPIClient(
        management_api_url, user_credentials, use_external_idp=use_external_idp)

    client.send_message_to_study_participants(email_config["studyKey"], email_config["condition"], message_config["template"], True)
