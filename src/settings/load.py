"""
For loading default settings.
"""

from classes.info import USER_PATH
import json
from typing import TypeGuard
from classes.logger import log
import settings.defaults

DEFAULT_CONFIG_VALUES = settings.defaults.DEFAULT_CONFIG_VALUES



config_values = None

# import the config.json file
def load_config_file(file_name: str, alternate_dict: dict, num_configs_loaded_successfully):
    
    # a list containing 2 lists:
    # [0] contains a list of all the keys/values that were successfully loaded from the config file
    # [1] contains a list of all the keys that did not exist in the config file
    config_keys_loaded = [[],[]]

    # file_name could be None during start up if either:
    # 1. filepath.json file not found.
    # 2. filepath.json file found but most_recently_opened_config_file key didn't exist.
    if file_name is None:
        log.debug("Config filename is None. Using defaults instead.")
        # alternate_dict provided during start up is the DEFAULTs
        config_values = alternate_dict
        # all the key names should be in [1].  
        config_keys_loaded[1] = [key for key in DEFAULT_CONFIG_VALUES]
        return (config_values, config_keys_loaded, num_configs_loaded_successfully)

    try:
        # open, read, parse as dictionary, and close the config.json file
        with open(file_name) as json_file:
            config_values = json.load(json_file)

        log.debug("Successfully loaded a config file.")

        # check which keys exist in the loaded file, and compile a list of which exist and which don't.
        checkValuesExist(config_values, config_keys_loaded, alternate_dict)

        # if we were able to load at least 1 value from the file, then increment the count of how many config files successfully gave values.
        if len(config_keys_loaded[0]) >= 1:
            num_configs_loaded_successfully += 1

        return (config_values, config_keys_loaded, num_configs_loaded_successfully)
            
    except:
        # if can't read default settings from config.json file, then use the defaults.
        log.debug("Couldn't load settings from the config file.  Using hard-coded default settings instead.")

        # use alternate_dict provided.
        config_values = alternate_dict
        # all the key names should be in [1].  
        config_keys_loaded[1] = [key for key in DEFAULT_CONFIG_VALUES]
        return (config_values, config_keys_loaded, num_configs_loaded_successfully)



JsonValue = bool | int | float | str | list | dict | None


def is_config_number(value: JsonValue) -> TypeGuard[int | float]:
    # bool is excluded because Python treats True as the int 1.
    return not isinstance(value, bool) and isinstance(value, (int, float))


def checkValuesExist(config_values: dict, config_keys_loaded: list, alternate_dict: dict):
    # record which keys exist in the config file and which don't.
    for key in DEFAULT_CONFIG_VALUES:
        if (key in config_values) and is_config_number(config_values.get(key)):
            # if the desired key is found in the pre-existing dict, then save that key name in a list.
            # also checks that the value is an int or float (ie a valid format).
            config_keys_loaded[0].append(key)
            log.debug(f"{key} is in config_values")
        else:
            # if the desired key is not found, then save that key name to a different list, and create a key-value for it.
            config_keys_loaded[1].append(key)
            log.debug(f"{key} not in config_values")
            config_values[key] = alternate_dict.get(key)
            # Note: the keys in config_values that are not used (ie, they are misnamed), are NOT deleted.
            # they remain, but are simply not used.




    

