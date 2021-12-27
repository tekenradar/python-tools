import yaml


def read_yaml(config_path):
    configs = yaml.load(
        open(config_path, 'r', encoding='UTF-8'),  Loader=yaml.FullLoader)
    return configs


def should_use_external_idp(configs):
    try:
        return configs["use_external_idp"]
    except KeyError:
        return False
