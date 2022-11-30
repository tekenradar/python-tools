import os
import argparse
from influenzanet.api import ManagementAPIClient
from utils import read_yaml, should_use_external_idp

def print_subs(subs):
    if "subscriptions" not in subs.keys():
        print("\tNo subscription for this study yet.")
        return
    for i, sub in enumerate(subs["subscriptions"]):
        print("\t[{}] - '{}' - '{}'".format(i, sub["messageType"], sub["email"]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--global_config_yaml", help="global configuration file path", default=os.path.join('resources', 'config.yaml'))
    parser.add_argument(
        "--study_key", help="key of the study, the user should be added to or removed from", required=True)

    args = parser.parse_args()

    configs = read_yaml(
        args.global_config_yaml)
    user_credentials = configs["user_credentials"]
    management_api_url = configs["management_api_url"]
    participant_api_url = configs["participant_api_url"]
    use_external_idp = should_use_external_idp(configs)

    study_key = args.study_key

    client = ManagementAPIClient(
        management_api_url, user_credentials, participant_api_url=participant_api_url, use_external_idp=use_external_idp)

    subs_on_server = client.get_study_notification_subs(study_key)

    print("Subscriptions fetched:")
    print_subs(subs_on_server)

    action = input("Please type what actions you want to perform ['add' or 'remove']: ").lower()

    subs = []
    if "subscriptions" in subs_on_server.keys():
        subs = subs_on_server["subscriptions"]

    if action == "add":
        messageType = input("Enter the message type: ")
        email = input("Enter the email address: ").lower()
        subs.append( {
            "messageType": messageType,
            "email": email
        })
    elif action == "remove":
        if len(subs) < 1:
            print("list was already empty - exiting")
            exit()

        ind = int(input("Enter the index of the item to delete [0 - {}]: ".format(len(subs)-1)))
        del subs[ind]
    else:
        print("unknown action - exiting")
        exit()

    subs_on_server = client.update_study_notification_subs(study_key, subs)
    print("Updated subscriptions list:")
    print_subs(subs_on_server)