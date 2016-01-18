#!/usr/bin/python

import sys
import os

def __InstallDesktopIcon(cobblr_path, icon_name):
  icon_path = os.path.join(cobblr_path, 'applications/desktop/icons')

  if os.path.exists(icon_path) is False:
    os.makedirs(icon_path)

  icon_dest = os.path.join(icon_path, icon_name)
  cp_command = "cp -r " + icon_name + " " + icon_dest
  os.system(cp_command)

  print "Icon installed on Desktop"

def __InstallModule(cobblr_path, module_name, module_files):
  install_path = os.path.join(cobblr_path, 'applications')
  module_path = os.path.join(install_path, module_name)

  if os.path.exists(module_path) is False:
    os.makedirs(module_path)

  for module_file in module_files:
    module_dest = os.path.join(module_path, module_file)
    cp_command = "cp -r " + module_file + " " + module_dest
    os.system(cp_command)

  init_file = os.path.join(module_path, '__init__.py')
  open(init_file, 'w').close()

  print "Application installed"


def Install(cobblr_path):
  all_files = os.listdir('.')
  for file_name in all_files:
    if 'module' in file_name:
      module_name = file_name.split('_')[0]
      icon_name = module_name + ".png"

  module_files = [i for i in all_files if '.png' not in i]

  try:
    os.system('./dependencies.sh')
    module_files.remove('dependencies.sh')
  except:
    pass

  try:
    module_files.remove('setup.py')
  except:
    pass

  __InstallModule(cobblr_path, module_name, module_files)
  __InstallDesktopIcon(cobblr_path, icon_name)
  print "Finished installing", module_name, "module."

if __name__ == '__main__':
  action = sys.argv[1]
  cobblr_path = sys.argv[2]

  if action == 'install':
    Install(cobblr_path)
  elif action == 'remove':
    print "I haven't implemented this yet. So much homework."
  else:
    print "setup.py doesn't know how to", action + ". But you can teach me."
