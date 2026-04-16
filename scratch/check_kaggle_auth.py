import os
import kaggle
try:
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    print(f"Checking credentials...")
    api.authenticate()
    print(f"Authenticated as: {api.config_values['username']}")
except Exception as e:
    print(f"Auth Error: {e}")
    print(f"Env Username: {os.getenv('KAGGLE_USERNAME')}")
    print(f"Config File path: {os.path.join(os.path.expanduser('~'), '.kaggle', 'kaggle.json')}")
