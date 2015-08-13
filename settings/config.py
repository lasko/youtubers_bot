# encoding: UTF-8
import yaml

def read_yaml_config(yml_file):
    with open(yml_file, 'r') as ymlfile:
        data = yaml.load(ymlfile)
    return data
