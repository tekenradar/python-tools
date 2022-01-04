import os
import json
import argparse
from management_api import ManagementAPIClient
from utils import read_yaml, should_use_external_idp
import base64


def yaml_obj_to_loc_object(obj):
    loc_obj = []
    for k in obj.keys():
        loc_obj.append({
            "code": k,
            "parts": [{
                "str": obj[k]
            }]
        })
    return loc_obj


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--global_config_yaml", help="global configuration file path", default=os.path.join('resources', 'config.yaml'))
    parser.add_argument(
        "--study_def_path", help="folder with study def yaml and rules json", required=True)

    args = parser.parse_args()

    configs = read_yaml(args.global_config_yaml)
    user_credentials = configs["user_credentials"]
    management_api_url = configs["management_api_url"]
    use_external_idp = should_use_external_idp(configs)

    study_path = args.study_def_path
    print(study_path)

    study_def = read_yaml(os.path.join(study_path, "props.yaml"))
    rules = json.load(
        open(os.path.join(study_path, "study_rules.json"), 'r', encoding='UTF-8'))

    study_obj = {
        "study": {
            "key": study_def["studyKey"],
            "status": study_def["status"],
            "secretKey": study_def["secretKey"],
            "props": {
                "systemDefaultStudy": study_def["props"]["systemDefaultStudy"],
                "startDate": study_def["props"]["startDate"],
                "name": yaml_obj_to_loc_object(study_def["props"]["name"]),
                "description": yaml_obj_to_loc_object(study_def["props"]["name"]),
                "tags": [{"label": yaml_obj_to_loc_object(t)} for t in study_def["props"]["tags"]]
            },
            "rules": rules
        }
    }

    if "configs" in study_def.keys():
        allowParticipantFiles = study_def["configs"]["allowParticipantFiles"]
        idMappingMethod = study_def["configs"]["idMappingMethod"]
        study_obj["study"]["configs"] = {
            "participantFileUploadRule": {
                "name": "gt",
                "data": [
                    { "dtype": "num", "num": 1},
                    { "dtype": "num", "num": 0 if allowParticipantFiles == True else 2 }
                ]
            },
            "idMappingMethod": idMappingMethod
        }

    client = ManagementAPIClient(
        management_api_url, user_credentials, use_external_idp=use_external_idp)
    client.create_study(study_obj)
