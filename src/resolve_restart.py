"""
    Namd Restarter - Automatically restart namd dynamics
    Copyright (C) 2020  Arthur Pereira da Fonseca

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

    Mail: arthurpfonseca3k@gmail.com
"""

from color_log import log
import subprocess
from time import sleep


def search_previous(path, silent=False):
    """Search restart files on previous folder"""

    if not silent:
        log('info', 'Searching restart files.')

    cmd = 'find ' + path + ' -name "*restart*" -exec du -sh {} \\;'
    output = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)

    return resolve_restart(output, silent)


def resolve_restart(files, silent):
    """Check for size on restart files"""

    files = files.stdout.readlines()
    if len(files) == 0:
        if not silent:
            log('critical', 'Restart files not found. Aborting!')
        return False

    files_size = dict()
    new_restart = list()
    old_restart = list()
    backup_restart = list()

    for file in files:
        file = file.decode('utf-8').strip().split('\t')

        file_name = file[1]
        files_size[file_name] = file[0]

        if file_name.endswith(".xsc") or file_name.endswith(".coor") or file_name.endswith(".vel"):
            new_restart.append(file_name)
        if file_name.endswith(".old"):
            old_restart.append(file_name)
        if file_name.endswith(".bak"):
            backup_restart.append(file_name)

    return choose_restart(files_size, new_restart, old_restart, backup_restart, silent)


def choose_restart(files_dic, new, old, back, silent):
    """Choose restart files not empty"""

    if len(new) >= 3:
        for file in new:
            if files_dic[file] == '0':
                break
            else:
                return annotate_restart(new, silent)

    if len(old) >= 3:
        for file in old:
            if files_dic[file] == '0':
                break
            else:
                if not silent:
                    log('warning', 'Restart files empty or missing, using old restart files.')
                sleep(1)
                return annotate_restart(old, silent)

    if len(back) >= 3:
        for file in back:
            if files_dic[file] == '0':
                break
            else:
                if not silent:
                    log('warning', 'Restart files empty or missing, using backup restart files.')
                sleep(1)
                return annotate_restart(back, silent)

    if not silent:
        log('critical', 'Restart files empty or missing. Aborting!')
    return False


def annotate_restart(file_list, silent):
    """Create dict with restart files"""

    annotated_files = dict()
    for file in file_list:
        if '.restart.xsc' in file:
            annotated_files['xsc'] = file
        elif '.restart.coor' in file:
            annotated_files['coor'] = file
        elif '.restart.vel' in file:
            annotated_files['vel'] = file
        else:
            if not silent:
                log('error', 'Missing restart file.')
            return False

    if not silent:
        log('info', 'Restart files ready.')

    return annotated_files


def get_restart_step(restart_files):
    """Get last step on xsc file"""

    with open(restart_files['xsc']) as xsc:
        step = xsc.readlines()

        if len(step) == 0:
            log('error', 'Could not open .xsc file.')
            return False

        step = step[2].split(' ')[0]
        log('info', 'Using restart step ' + step + '.')
        return step
