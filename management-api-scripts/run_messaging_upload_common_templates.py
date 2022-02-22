import argparse
import os
import base64
import yaml
from management_api import ManagementAPIClient
from utils import read_yaml, should_use_external_idp

########  PARAMETERS #############
message_types = [
    'registration',
    'invitation',
    'verify-email',
    'verification-code',
    'password-reset',
    'password-changed',
    'account-id-changed',  # email address changed
    'account-deleted'
]


def find_template_file(m_type, folder_with_templates):
    c = [f for f in os.listdir(folder_with_templates)
         if f.split('.')[0] == m_type]
    if len(c) != 1:
        raise ValueError("no template file found to message type: " + m_type)
    return os.path.join(folder_with_templates, c[0])


def read_and_endcode_template(path):
    content = open(path, 'r', encoding='UTF-8').read()
    return base64.b64encode(content.encode()).decode()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--global_config_yaml", help="global configuration file path", default=os.path.join('resources', 'config.yaml'))
    parser.add_argument(
        "--default_language", help="default language of the messaging", default='en')
    parser.add_argument(
        "--email_template_folder", help="folder containing the email templates", default='resources/email_templates')

    args = parser.parse_args()

    configs = read_yaml(
        args.global_config_yaml)
    user_credentials = configs["user_credentials"]
    management_api_url = configs["management_api_url"]
    participant_api_url = configs["participant_api_url"]
    use_external_idp = should_use_external_idp(configs)

    email_template_folder = args.email_template_folder
    default_language = args.default_language

    client = ManagementAPIClient(
        management_api_url, user_credentials, use_external_idp=use_external_idp)

    # Automatically extract languages:
    languages = [{"code": d, "path": os.path.join(email_template_folder, d)} for d in os.listdir(
        email_template_folder) if os.path.isdir(os.path.join(email_template_folder, d))]

    try:
        headerOverrides = read_yaml(os.path.join(
            email_template_folder, 'header-overrides.yaml'))
    except:
        headerOverrides = None

    for m_type in message_types:
        template_def = {
            'messageType': m_type,
            'defaultLanguage': default_language,
            'translations': [],
        }

        if headerOverrides is not None:
            currentHeaderOverrides = headerOverrides[m_type]
            if currentHeaderOverrides is not None:
                template_def['headerOverrides'] = currentHeaderOverrides

        for lang in languages:
            translated_template = find_template_file(m_type, lang["path"])
            subject_lines = yaml.load(
                open(os.path.join(lang["path"], 'subjects.yaml'), 'r', encoding='UTF-8'), Loader=yaml.FullLoader)

            template_def["translations"].append(
                {
                    "lang": lang["code"],
                    "subject": subject_lines[m_type],
                    "templateDef": read_and_endcode_template(translated_template)
                }
            )

        r = client.save_email_template(template_def)
        print('saved templates for: ' + m_type)
