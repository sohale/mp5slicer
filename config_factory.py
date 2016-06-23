import math
import json

class config_factory:

    def __init__(self, json_conf):
        json_file = open(json_conf)
        json_str = json_file.read().replace('\n', '')
        json_file.close()
        arg_dictionnary = json.loads(json_str)

        import slicer.base_config as config
        for arg in arg_dictionnary:
            setattr(config,arg,arg_dictionnary[arg])
        setattr(config, "crossArea" ,((config.filamentDiameter/2.0)**2) * math.pi) #6.37939





class Printer_config():
    def __init__(self):
        import slicer.printer_config as printer_config
