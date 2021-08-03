import i18n
import yaml


def i18n_set_file(file):
    """Set the translation of the required file"""
    with open(f"translation/{file}.yaml", "r") as stream:
        dictionary = yaml.load(stream, Loader=yaml.FullLoader)
        for key, value in dictionary.items():
            i18n.add_translation(str(key), str(value))
