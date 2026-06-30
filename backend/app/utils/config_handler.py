import yaml

def loader_config(
        config_path: str,
        encoding: str ='utf-8'
) -> dict:
    with open(config_path, 'r', encoding=encoding) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        return config