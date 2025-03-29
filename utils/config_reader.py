
import configparser

def read_config(ini_file,section, key):
   config = configparser.ConfigParser()
   config.read(ini_file)
   return config[section][key]

def read_config_int(ini_file,section, key):
   config = configparser.ConfigParser()
   config.read(ini_file)
   return config.getint(section, key)

