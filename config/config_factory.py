import sys
import os
import inspect
sys.path.append(os.path.split(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))[0])


from mp5slicer.config.config import ConfigurationError
import json
import math


printer_files_dict = {'Ultimaker Origin': 'mp5slicer/config/config_0.mp5',
                      'Ultimaker 2': 'mp5slicer/config/config_1.mp5'}
filament_files_dict = {'PLA': 'mp5slicer/config/filament.mp5',
                       'ABS': 'mp5slicer/config/filament.mp5'}
default_files_dict = {0: 'mp5slicer/config/default.mp5'}


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
                raise AttributeError('setting a undefined attr {} is not allowed ; {} is not in base_config'.format(arg,arg))

        setattr(config,
                'crossArea',
                ((config.FILAMENT_DIAMETER/2.0)**2) * math.pi)  # 6.37939


class ConfigFactoryNextGeneration(object):

    def __init__(self, config_names, config_priority, *configs_paths_or_dicts):
        self.config_names = config_names
        self.config_priority = config_priority
        self.config_paths_or_dicts = configs_paths_or_dicts
        self.config_priority_list = self.get_config_priority()
        self.merged_config_dict = self.merge_config_dict()


        self.set_config_attributes()


    def get_config_priority(self):

        def make_prioritsed_config_names(config_names, config_priority):
            prioritised_config_names = [None] * len(config_priority)
            for config_name, config_rank in zip(config_names, config_priority):
                prioritised_config_names[config_rank] = config_name
            return prioritised_config_names

        len_config_names = len(self.config_names)

        if self.config_priority is None:
            len_config_priority = 0

            if (self.config_names[0] == 'default') & \
               (self.config_names[1] == 'user') & \
               (self.config_names[2] == 'printer') & \
               (self.config_names[3] == 'filament'):

                self.config_priority = [None] * len_config_names

                config_start = 3

                for i in range(len(self.config_names)):
                    if i == 0:
                        self.config_priority[i] = len_config_names - 1
                    elif i == 1:
                        self.config_priority[i] = 0
                    elif i == 2:
                        self.config_priority[i] = 2
                    elif i == 3:
                        self.config_priority[i] = 1
                    else:
                        self.config_priority[i] = config_start
                        config_start += 1

            else:
                raise ConfigurationError("Unknown configuration please supply a config_priority.  \n \
                                            config_names = ['default', 'user', 'printer', 'filament', ...]")

        else: # config_priority not None

            len_config_priority = len(self.config_priority)

            if len_config_names <= 3:
                raise ConfigurationError("config_names should have length at least 3.\
                    since config_names = ['default', 'user', 'printer', 'filament', ...]")
            elif len_config_priority != len(set(self.config_priority)):
                raise ConfigurationError("config_priority has duplicates.")
            elif len_config_priority == len_config_names:
                return make_prioritsed_config_names(self.config_names, self.config_priority)
            elif len_config_priority > len_config_names:
                raise ConfigurationError('length of config_priority should always be smaller \
                                  and equals to length of config names')
            elif len_config_priority < len_config_names:
                raise ConfigurationError('length of config_priority is larger than the length \
                                  of config_priority')
            else:
                raise ConfigurationError

    def merge_config_dict(self):

        config_dicts = {}

        counter = 0
        for each_config_path_or_dict in self.config_paths_or_dicts:
            current_config_name = self.config_names[counter]
            if isinstance(each_config_path_or_dict, dict):
                if 'printerSettings' in each_config_path_or_dict:
                    config_dicts[current_config_name] = each_config_path_or_dict['printerSettings']
                else:
                    config_dicts[current_config_name] = each_config_path_or_dict
            else:
                with open(each_config_path_or_dict) as data_file:
                    config_dicts[current_config_name] = json.load(data_file)['printerSettings']
            counter += 1

        merged_config_dict = {}
        for config_dict_name in self.config_priority_list:
            current_config_dict = config_dicts[config_dict_name]
            for key in current_config_dict:
                if key not in merged_config_dict:
                    merged_config_dict[key] = current_config_dict[key]

        return merged_config_dict

    def set_config_attributes(self):
        # set config attributes
        import mp5slicer.config.base_config as base_config
        import mp5slicer.config.config as config

        for arg in self.merged_config_dict:
            if hasattr(config, arg):
                setattr(base_config, arg, self.merged_config_dict[arg])
            else:
                raise ConfigurationError('Try to set a unknown configuration {}.'.format(arg))


        # move this to somewhere else
        setattr(base_config,
                'crossArea',
                ((base_config.FILAMENT_DIAMETER/2.0)**2) * math.pi)  # 6.37939

        pass

def run_ConfigFactory_on_MP5_file(mp5_file, to_file):
    
    printer_file_path = printer_files_dict[mp5_file['printerSettings']['PRINTER']]
    filament_file_path = filament_files_dict[mp5_file['printerSettings']['FILAMENT']]
    default_file_path = default_files_dict[mp5_file['printerSettings']['DEFAULT']]

    printer_setting_dict = mp5_file['printerSettings']
    cleaned_printer_setting_dict = {
        i:printer_setting_dict[i] for i in printer_setting_dict if i not in
        ['PRINTER', 'FILAMENT', 'DEFAULT']
        }

    ConfigFactoryNextGeneration(['default', 'user', 'printer', 'filament', 'print_from_file'],
                            [4, 1, 2, 3, 0],
                            default_file_path,
                            cleaned_printer_setting_dict,
                            printer_file_path,
                            filament_file_path,
                            {'TO_FILE': to_file})




# def main():
#     ConfigFactoryNextGeneration(['default', 'user', 'printer', 'filament'],
#                                 [3, 0, 1, 2],
#                                 'slicer/config/default.mp5',
#                                 {'OUTER_BOUNDARY_COAST_AT_END_LENGTH':23},
#                                 'slicer/config/config_0.mp5',
#                                 'slicer/config/filament.mp5')

    # print(get_config_priority(['default', 'user', 'printer', 'filament'], [3, 0, 1, 2]))

if __name__ == '__main__':
    main()