import yaml

# Load database credentials from a YAML file
def load_db_credentials():
    with open('db_creds.yaml', 'r') as file:
        creds = yaml.load(file, Loader=yaml.FullLoader)
    return creds
