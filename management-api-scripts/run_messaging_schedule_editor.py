import os
import json
import argparse
from influenzanet.api import ManagementAPIClient
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

    now = datetime.now()
    nextTime = now.replace(
        hour=email_config['sendingTime']['hour'], minute=email_config['sendingTime']['minute'])
    del email_config['sendingTime']

    translationsDefs = email_config['translations']

    headerOverrides = None
    try:
        headerOverrides = email_config["headerOverrides"]
    except KeyError:
        pass

    auto_message = {
        "type": email_config["sendTo"],
        "studyKey": email_config["studyKey"],
        "label": email_config["label"],
        "nextTime": int(nextTime.timestamp()),
        "period": email_config["period"],
        "until": email_config["until"],
        "condition": email_config["condition"],
        "template": {
            "headerOverrides": headerOverrides,
            "messageType": email_config["messageType"],
            "defaultLanguage": email_config["defaultLanguage"],
            "translations":  []
        }
    }

    for tr in email_config['translations']:
        auto_message['template']['translations'].append({
            'lang': tr['lang'],
            'subject': tr['subject'],
            'templateDef': read_and_convert_html(
                os.path.join(email_folder, tr['lang'] + '.html')
            )
        })

    mode = None
    selection = None

    client = ManagementAPIClient(
        management_api_url, user_credentials, use_external_idp=use_external_idp)
    existing_auto_messages = client.get_auto_messages()
    if len(existing_auto_messages) < 1:
        print('There are no "auto messages" yet. This will be added as a new entry.')
        mode = "create"
    else:
        print('There are existing "auto messages":')
        display_text = "\t{index}: {id} - {label}"
        for i, m in enumerate(existing_auto_messages['autoMessages']):
            label = '<No Label>'
            if 'label' in m.keys():
                label = m['label']
            print(display_text.format(index=i, id=m['id'], label=label))

        while True:
            mode = input(
                'Do you want to create a new entry or update one of these? (type here "create", "update" or "exit" to stop): ')
            if mode == "exit":
                exit()
            if mode in ["create", "update"]:
                break
        if mode == "update":
            while True:
                selection = input('Enter the index of the item you want to modify? (type a number between {} and {} or "exit" to stop the process): '.format(
                    0, len(existing_auto_messages['autoMessages']) - 1))
                if selection == "exit":
                    exit()
                try:
                    selection = int(selection)
                    if 0 <= selection < len(existing_auto_messages['autoMessages']):
                        break
                except ValueError:
                    continue

    if mode == 'update':
        id = existing_auto_messages['autoMessages'][selection]['id']
        auto_message['id'] = id

    client.save_auto_message({
        "autoMessage": auto_message
    })
