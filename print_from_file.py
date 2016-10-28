import inspect
import os
import sys
sys.path.append(os.path.split(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))[0])
from slicer.config.config_factory import ConfigFactory, ConfigFactoryNextGeneration
from slicer.Print_pipeline import print_mesh


def print_from_file():
    args = sys.argv
    args = args[1:]
    stl_file_name = args[0]
    conf_file_name = args[1]

    ConfigFactory(conf_file_name)
    import slicer.config.config as config
    config.reset()

    mesh = get_stl_from_file(stl_file_name)
    print_mesh(mesh, stl_file_name)

def print_from_file_next_generation():
    args = sys.argv
    args = args[1:]
    stl_file_name = args[0]
    default_config_mp5_path = args[1]
    user_config_mp5_path = args[2]
    printer_config_mp5_path = args[3]
    filament_config_mp5_path = args[4]
    print_from_file_config_mp5_path = args[5]

    # ConfigFactory(user_config_mp5, printer_config_mp5, filament_config_mp5)

    ConfigFactoryNextGeneration(['default', 'user', 'printer', 'filament', 'print_from_file'],
                                [4, 1, 2, 3, 0],
                                default_config_mp5_path,
                                user_config_mp5_path,
                                printer_config_mp5_path,
                                filament_config_mp5_path,
                                print_from_file_config_mp5_path)

    import slicer.config.config as config
    config.reset()
    mesh = get_stl_from_file(stl_file_name)
    print_mesh(mesh, stl_file_name)

def get_stl_from_file(stl_file_name):
    from stl import mesh
    return mesh.Mesh.from_file(stl_file_name)

if __name__ == '__main__':
    print_from_file_next_generation()