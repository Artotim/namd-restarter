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


def format_option(option):
    """Format options to separate argument and value"""

    option = option.split()
    if option[0].lower() == 'set':
        option = [option[0] + ' ' + option[1], *option[2:]]
    return option


def write_backup(file):
    """Write the backups on file"""

    import shutil

    if file.endswith('old'):
        new_file = file.replace('old', 'bak')
    else:
        new_file = file + '.bak'

    shutil.copy(file, new_file)


def finish_dynamic(err):
    """Check for errors on dynamic end"""

    with open(err, 'r') as err_file:
        err_message = err_file.read()

        if len(err_message) > 1:
            log('error', 'Dynamic ended with error status:')
            print(err_message)
        else:
            log('info', 'Dynamic finished.')
