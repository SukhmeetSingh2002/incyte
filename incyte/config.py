import os
import json

def load_custom_config():
    config_file_path = os.path.expanduser("~/.config/incyte/config.json")
    
    if os.path.exists(config_file_path):
        with open(config_file_path, 'r') as config_file:
            return json.load(config_file)
    else:
        # Create the config file
        os.makedirs(os.path.dirname(config_file_path), exist_ok=True)

        # Create the default config based on the user's OS. Also based on language (C++ or Python)
        default_config = {"python": {}, "cpp": {}, "other": {}}
        if os.name == 'nt':
            default_config['cpp']['build_command'] = "g++ -o a.exe"
            default_config['cpp']['run_command'] = "a.exe"
        else:
            default_config['cpp']['build_command'] = "g++ -o a.out"
            default_config['cpp']['run_command'] = "./a.out"
        
        # for python check if the user has python3 installed
        if os.system("python3 --version") == 0:
            default_config['python'] = "python3"
        else:
            default_config['python'] = "python"

        with open(config_file_path, 'w') as config_file:
            json.dump(default_config, config_file)


        return default_config

def store_custom_config(custom_config):
    config_file_path = os.path.expanduser("~/.codeCompare/config.json")
    with open(config_file_path, 'w') as config_file:
        json.dump(custom_config, config_file)

def get_build_command(args, custom_config):
    return custom_config.get('build_command', None)

def get_run_command(args, custom_config):
    return custom_config.get('run_command', None)
