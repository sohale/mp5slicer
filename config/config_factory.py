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
                raise AttributeError('setting a undefined attr {} is not allowed'.format(arg))

        setattr(config,
                'crossArea',
                ((config.FILAMENT_DIAMETER/2.0)**2) * math.pi)  # 6.37939


class ConfigFactoryNextGeneration(object):

    def __init__(self,
                 user_config_mp5,
                 printer_config_mp5,
                 filament_config_mp5,
                 base_config_mp5="?"):

        # proritise from left to tight

        with open(user_config_mp5) as data_file:
            user_config_dict = json.load(data_file)['printerSettings']
        with open(filament_config_mp5) as data_file:
            filament_config_dict = json.load(data_file)['printerSettings']
        with open(printer_config_mp5) as data_file:
            printer_config_dict = json.load(data_file)['printerSettings']

        priority_config_order = [user_config_dict,
                                 filament_config_dict,
                                 printer_config_dict]

        for each_dict in reversed(priority_config_order):
            try:
                for key, value in each_dict
                arg_dictionnary = printer_config_dict


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

        # move this to somewhere else
        setattr(config,
                'crossArea',
                ((config.FILAMENT_DIAMETER/2.0)**2) * math.pi)  # 6.37939


class PrinterConfig():
    def __init__(self):
        pass
