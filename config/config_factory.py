import json
import math


class ConfigFactory(object):

    def __init__(self, json_conf=None, dict_conf=None):
        if json_conf is None and dict_conf is None:
            arg_dictionnary = {}
        elif dict_conf is not None:
            arg_dictionnary = dict_conf
        else: # json_conf is not  None
            json_file = open(json_conf)
            json_str = json_file.read().replace('\n', '')
            json_file.close()
            arg_dictionnary = json.loads(json_str)

        import slicer.config.base_config as config
        for arg in arg_dictionnary:
            if hasattr(config, arg):
                setattr(config, arg, arg_dictionnary[arg])
            else:
                raise AttributeError('setting a undefined attr is not allowed')

        setattr(config,
                'crossArea',
                ((config.FILAMENT_DIAMETER/2.0)**2) * math.pi)  # 6.37939


class PrinterConfig():
    def __init__(self):
        pass
