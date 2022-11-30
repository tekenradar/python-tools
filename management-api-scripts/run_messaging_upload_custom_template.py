import argparse
import os
import base64
from influenzanet.api import ManagementAPIClient
from utils import read_yaml, should_use_external_idp


def read_and_endcode_template(path):
    content = open(path, 'r', encoding='UTF-8').read()
    return base64.b64encode(content.encode()).decode()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--global_config_yaml", help="global configuration file path", default=os.path.join('resources', 'config.yaml'))
    parser.add_argument(
        "--email_template_folder", help="folder containing the email template")

    args = parser.parse_args()

    configs = read_yaml(args.global_config_yaml)
    user_credentials = configs["user_credentials"]
    management_api_url = configs["management_api_url"]
    participant_api_url = configs["participant_api_url"]
    use_external_idp = should_use_external_idp(configs)

    email_template_folder = args.email_template_folder

    client = ManagementAPIClient(management_api_url, user_credentials, use_external_idp=use_external_idp)


    email_config = read_yaml(os.path.join(email_template_folder, 'email-props.yaml'))

    payload = {
        "messageType": email_config["messageType"],
        "studyKey": email_config["studyKey"],
        "defaultLanguage": email_config["defaultLanguage"]
    }

    if 'headerOverrides' in email_config.keys():
        payload['headerOverrides'] = email_config["headerOverrides"]

    payload["translations"] = []
    for code, subject in email_config["subjects"].items():
        current_translation = {
            "lang": code,
            "subject": subject,
        }
        current_translation["templateDef"] = read_and_endcode_template(os.path.join(email_template_folder, code + '.html'))
        payload["translations"].append(current_translation)

    try:
        r = client.save_email_template(payload)
    except Exception as e:
        print('template for ' + email_config["messageType"] + ' cannot be saved:')
        print(e)
    else:
        print('saved templates for: ' + email_config["messageType"])
