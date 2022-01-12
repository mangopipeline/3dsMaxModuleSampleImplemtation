'''
Created on Jan 11, 2022

@author: carlos.anguiano
'''
import glob
import json
import os


def process_mode_files(mod_file, env_var_dic):
    mod_root = os.path.dirname(mod_file)

    with open(mod_file, 'r') as strm:
        mod_data = json.loads(strm.read())

    # where will be look for controlled directories
    if 'path' in mod_data:
        if os.path.isdir(mod_data['path']):
            mod_root = mod_data['path']
        else:
            mod_root = os.path.join(mod_root, mod_data['path'])

    folders = {'icons': 'max_icon',
               'bin': 'path',
               'plugins': 'max_plugins',
               'mxs': 'max_scripts',
               'pyhton': 'pythonpath',
               'macros': 'max_macros',
               'config': 'max_configs'}

    for folder, var in folders.items():
        test_dir = os.path.join(mod_root, folder)
        if not os.path.isdir(test_dir):
            continue

        if var not in env_var_dic:
            env_var_dic[var] = []

        env_var_dic[var].append(test_dir)


def merge_mod_environment_with_current_environment(env_var_dic):
    """
    this s where AD gets to modify the environment making sure 
    1)all AD dependencies come first, 
    2)mod dependencies come second, 
    3)and current system dependencies come last
    """
    for key, paths in env_var_dic.items():
        fval = os.pathsep.join(paths)
        if key in os.environ:
            fval = '%s%s%s' % (fval, os.pathsep, os.environ[key], )  # we add all our system mods before any current values

        print(key, '=', fval)
        os.environ[key] = fval


def max_module_setup_routine():
    r"""
    Here's where the magic happens we find all paths registered in the 3ds_Max_Modules environment variable
    AD could register a folder in the user DOCS to make it easier for small shows and individuals to download tools and pacakges

    C:\Users\carlos.anguiano\Documents\3ds Max 2022\modules

    any .mod files found here would be evaluated in bundle folders could exist parallel to the .mod files

    C:\Users\carlos.anguiano\Documents\3ds Max 2022\modules\ilm_tools.mod
    C:\Users\carlos.anguiano\Documents\3ds Max 2022\modules\ilm_tools

    content of mod would be {'name': 'ilm tools', 
                             'version': '1.0.0', 
                             'path': 'ilm_tools'}


    inside of the ilm_tools folder there would be individual folders like

    C:\Users\carlos.anguiano\Documents\3ds Max 2022\modules\ilm_tools\icons  -- would be added to the max icon path
    C:\Users\carlos.anguiano\Documents\3ds Max 2022\modules\ilm_tools\bin  --would be added to the window PATH env
    C:\Users\carlos.anguiano\Documents\3ds Max 2022\modules\ilm_tools\mxs -- would be added to the max mxs path
    C:\Users\carlos.anguiano\Documents\3ds Max 2022\modules\ilm_tools\python -- would be added to the python path 
    C:\Users\carlos.anguiano\Documents\3ds Max 2022\modules\ilm_tools\macros -- would be added to the 
    C:\Users\carlos.anguiano\Documents\3ds Max 2022\modules\ilm_tools\config -- would be added to the max configs path

    the json data in the .mod file could also hold an env var where folks could register other environment variables 

    example {'name': 'ilm tools', 
             'version': '1.0.0', 
             'path': 'ilm_tools',
             'env':{'my_lic_server':'internal_lic_server'}}


    """

    env_var_dic = {}
    env_var = '3ds_Max_Modules'

    if not env_var in os.environ:
        return

    for path in os.environ[env_var].split(os.pathsep):
        if not os.path.isdir(path):
            continue

        mod_files = glob.glob(os.path.join(path, '*.mod'))
        for mod_file in mod_files:
            process_mode_files(mod_file, env_var_dic)

    if not env_var_dic:
        return

    merge_mod_environment_with_current_environment(env_var_dic)


if __name__ == '__main__':
    os.environ['3ds_Max_Modules'] = r'c:\temp;C:\temp\test_mod'
    max_module_setup_routine()
