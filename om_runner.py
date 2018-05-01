# -*- coding: utf-8 -*-
"""
Created on Sun Apr 29 13:53:45 2018

@author: rober
"""

import os

def add_om_extension(file):
    #Assume that any file without a .om extension has no extension at all
    if not file[:-3] == '.om':
        return file + '.om' 
    return file

def run_file(file, shell):
    text = ''
    with open(file) as f:
        for line in f:
            line = line.strip()
            if len(line) > 0 and not line[0] in ['#', '@']: #Remove imports and comments
                text += line + ' '
#    print('running:')
#    print(text)
#    print('********')
    return shell.interpret(text, return_nodes=True)

def run_om_project(folder, shell):
    files = []
#    ext = folder + '\\'
    #Walk through the folder, collecting all files
    main = ''
    
    paths_from_names = {}
    for (dirpath, dirnames, filenames) in os.walk(folder):
#        print(filenames)
        for file in filenames:
#            paths_from_names[file] = dirpath + '\\' + file
            paths_from_names[file] = os.path.join(dirpath, file)
        paths = [paths_from_names[f] for f in filenames]
        if 'main.om' in filenames:
#            main = dirpath + '\\main.om'
            main = os.path.join(dirpath, 'main.om')
        files.extend(paths)
    
    #Only keep .om files
    files = [file for file in files if os.path.splitext(file)[1] == '.om']
    
    imports = {} #A map from files to files they import
    #Find what files each file needs
    
#    main = ''
#    for file in files:
#        if file [-7:] == 'main.om':
#            main = file
            
    for file in files:
        with open(file) as f:
            
            for line in f:
                to_add = []
                line = line.strip()
#                print(line)
                if len(line) > 0 and line[0] == '@':
#                    print(line)
                    line = line [1:]
                    names = line.split()
                    names = [add_om_extension(name) for name in names]
                    names = [paths_from_names[name] for name in names]
#                    print(names)
                    to_add.extend(names)
                imports[file] = imports.get(file, []) + to_add
#    print('imports:')
#    print(imports)
#    print('********')
    #Find which files main.om needs directly or indirectly
    needed = {} #A map a file to all the files that file needs, directly or indirectly
    for file in imports:
        needed[file] = imports[file]
    #Repeatedly, for each file, add the needed files of the files it imports to its needed files
    going = True
    while going:
        going = False
        for file in files:
            add = []
            for imported in imports[file]:
                add.extend(needed.get(imported, []))
            prev = needed.get(file, [])
            new = prev[:]
            new.extend(add)
            new = list(set(new))
            if set(prev) != set(new):
                going = True
            
            needed[file] = new
    
#    print('needed:')
#    print(needed)
#    print('*******')
    
    #Check for circularity
    to_check = [main] + needed[main]
    for file in to_check:
        if file in needed[file]:
            raise AssertionError('Circular dependency at ' + file)
    
    to_run = needed[main]
    run = []
    while to_run:
        for file in to_run:
            if not [file for file in needed[file] if not file in run]:
                run_file(file, shell)
                run.append(file)
                to_run.remove(file)
                
    return run_file(main, shell)