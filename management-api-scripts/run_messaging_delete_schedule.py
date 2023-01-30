import argparse
from influenzanet.api import ManagementAPIClient
from utils import read_yaml, should_use_external_idp


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--global_config_yaml", help="global configuration file path")
    args = parser.parse_args()

    configs = read_yaml(args.global_config_yaml)
    user_credentials = configs["user_credentials"]
    management_api_url = configs["management_api_url"]
    use_external_idp = should_use_external_idp(configs)


    client = ManagementAPIClient(
        management_api_url, user_credentials, use_external_idp=use_external_idp)
    existing_auto_messages = client.get_auto_messages()
    if len(existing_auto_messages) < 1:
        print('There are no "auto messages" yet, nothing to delete.')
        exit()
    else:
        print('There are existing "auto messages":')
        display_text = "\t{index}: {id} - {label}"
        for i, m in enumerate(existing_auto_messages['autoMessages']):
            label = '<No Label>'
            if 'label' in m.keys():
                label = m['label']
            print(display_text.format(index=i, id=m['id'], label=label))

        while True:
            selection = input('Enter the index of the item you want to delete? (type a number between {} and {} or "exit" to stop the process): '.format(
                0, len(existing_auto_messages['autoMessages']) - 1))
            if selection == "exit":
                exit()
            try:
                selection = int(selection)
                if 0 <= selection < len(existing_auto_messages['autoMessages']):
                    break
            except ValueError:
                continue
        id = existing_auto_messages['autoMessages'][selection]['id']
        confirm = input('Do you really want to remove the item {}? (y/n) '.format(id))

        if confirm.lower().strip() == 'y':
            resp = client.delete_auto_message(id)
        else:
            print('Exiting without further action.')
