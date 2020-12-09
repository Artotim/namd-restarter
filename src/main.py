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

from arguments_parser import make_parser
from prepare_dynamic import format_option, finish_dynamic, write_backup
from resolve_restart import search_previous, get_restart_step
from color_log import log
import os
from time import sleep
import subprocess


class DynamicRestart:
    """Automatically restarts namd dynamics"""

    def __init__(self, **kwargs):
        self.conf = kwargs['conf']
        self.backup = kwargs['backup']
        self.namd = kwargs['namd']
        self.namd_exe = kwargs['namd_exe']
        self.options = kwargs['options']
        self.previous = os.path.abspath(kwargs['previous']) + '/'
        self.restart = os.path.abspath(kwargs['restart']) + '/'
        self.run = kwargs['run']
        self.cores = kwargs['threads']
        self.file_name = kwargs['file_name']

        self.conf_file = None

        try:
            self.main()
        except KeyboardInterrupt:
            log('error', 'Interrupted by user.')

    def main(self):
        """Main routine"""

        # Gets conf file
        self.conf = self.search_conf()
        if not self.conf:
            return False
        sleep(1)

        # Prepares restart files
        restart_files = search_previous(self.previous)
        if not restart_files:
            return False
        sleep(1)
        self.file_name = self.get_file_name(restart_files)

        # Loads conf file in memory for editing
        self.conf_file = self.read_conf()
        if not self.conf_file:
            return False
        sleep(1)

        # Gets last step
        restart_step = get_restart_step(restart_files)
        if not restart_step:
            return False
        sleep(1)

        # Analyze restart folder
        self.prepare_restart()
        sleep(1)

        # Make basic edits on conf file
        self.configure_restart(restart_step, restart_files)
        sleep(1)

        # Edit optional arguments on conf file
        self.configure_optional()
        self.save_conf()
        sleep(1)

        # Run namd when enabled
        if self.namd:
            self.run_namd()
        else:
            log('info', 'Done.')

    def search_conf(self):
        """Search conf files archive"""

        if self.conf is not None:
            if self.conf.endswith('.conf'):
                return self.conf
            else:
                log('error', 'Please provide a valid .conf file.')
                return False

        log('info', 'Searching conf file.')
        cmd = 'find ' + self.previous + ' -name "*conf"'
        output = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        output = output.stdout.readlines()
        if len(output) != 1:
            log('error', 'Conf file not found! Please specify path with -c.')
            return False
        else:
            return output[0].decode('utf-8').strip()

    def read_conf(self):
        """Read conf file to list"""

        with open(self.conf) as conf:
            conf_file = conf.readlines()

            if len(conf_file) == 0:
                log('error', 'Could not open .conf file.')
                return False

            return conf_file

    def get_file_name(self, files):
        """Gets file name if not passed"""

        if self.file_name:
            return self.file_name
        pathless_file = files['xsc'].split('/')[-1]
        return pathless_file.split('.restart.xsc')[0]

    def prepare_restart(self):
        """Check if output folder exists and is empty"""

        if not os.path.exists(self.restart):
            os.makedirs(self.restart)
        else:
            if len(os.listdir(self.restart)) != 0:
                log('warning', 'Output folder not empty. Subscribing.')
                sleep(1)

    def configure_restart(self, restart_step, restart_files):
        """Make basic edits on conf file"""

        log('info', 'Preparing .conf file.')

        restart_insert = ['set outputname ' + self.restart + self.file_name,
                          'bincoordinates ' + restart_files['coor'],
                          'binvelocities ' + restart_files['vel'],
                          'extendedSystem ' + restart_files['xsc'],
                          'firsttimestep ' + restart_step]
        restart_comment = ['temperature', 'minimize', 'reinitvels']

        coord_index = self.search_option('coordinates') + 1
        self.conf_file.insert(coord_index, '\n')

        self.edit_run_steps(restart_step)

        for option in restart_insert:
            self.update_conf(option, coord_index)

        for option in restart_comment:
            self.comment_conf(option)

    def search_option(self, option):
        """Search an option index on conf file"""

        for line in self.conf_file:
            if line.startswith(option) or line.startswith('#' + option):
                return self.conf_file.index(line)
        return False

    def update_conf(self, option, base_index=0):
        """Edit conf file to include/uncomment option"""

        base_index = base_index + 1
        if base_index == 1:
            base_index = len(self.conf_file) - 1

        option = format_option(option)

        option_index = self.search_option(option[0])
        if option_index:
            self.conf_file[option_index] = ' '.join(option) + '\n'
        else:
            self.conf_file.insert(base_index, ' '.join(option) + '\n')

    def comment_conf(self, option):
        """Edit conf file to comment option"""

        option = format_option(option)

        option_index = self.search_option(option[0])
        if option_index:
            if not self.conf_file[option_index].startswith('#'):
                self.conf_file[option_index] = '#' + self.conf_file[option_index]
        else:
            log('warning', 'Option "' + ' '.join(option) + '" not found. Ignoring.')
            sleep(1)

    def edit_run_steps(self, restart_step):
        """Edit the number of run steps"""

        if self.run:
            log('info', 'Setting run steps to ' + self.run + '.')
            self.update_conf('run ' + self.run)
        else:
            steps = self.get_remaining_steps(restart_step)

            log('info', 'Setting run steps to ' + steps + '.')
            self.update_conf('run ' + steps)

    def get_remaining_steps(self, restart_step):
        """Get number of remaining steps to complete dynamic"""

        previous_line = self.conf_file[self.search_option('run')]
        previous_step = previous_line.strip().split()[1]

        next_time_step = int(previous_step) - int(restart_step)
        next_time_step = next_time_step if next_time_step != 0 else restart_step

        return str(next_time_step)

    def configure_optional(self):
        """Make additional edits on conf file"""

        for item in self.options:
            log('info', 'Setting parameter "' + ' '.join(item) + '".')
            self.update_conf(' '.join(item))

    def save_conf(self):
        """Save conf file"""

        log('info', 'Saving .conf file at ' + self.restart)
        conf = self.restart + self.file_name + '.conf'
        with open(conf, 'w') as file:
            for line in self.conf_file:
                file.write(line)

    def run_namd(self):
        """Runs namd executable with # cores"""

        log('info', 'Running namd with ' + str(self.cores) + ' cores.')

        conf_file = self.restart + self.file_name + '.conf'
        log_file = self.restart + self.file_name + '.log'
        err_file = self.restart + self.file_name + '.err'

        cmd = [self.namd_exe, conf_file]

        if self.cores != 1:
            cmd.insert(1, '+p' + str(self.cores))

        try:
            with open(log_file, 'w') as out, open(err_file, "w") as err:
                process = subprocess.Popen(cmd, stdout=out, stderr=err)

                while process.poll() is None:
                    if self.backup:
                        self.backup_restart()
                    sleep(300)

                else:
                    finish_dynamic(err_file)

        except (PermissionError, FileNotFoundError):
            log('error', 'Namd exe not found! Please specify path with -e.')

    def backup_restart(self):
        """Checks to create backups file for restarting"""

        restart_files = search_previous(self.restart, silent=True)
        if not restart_files or restart_files['xsc'].endswith('bak'):
            return

        for file in restart_files:
            try:
                write_backup(restart_files[file])
            except FileNotFoundError:
                break


if __name__ == '__main__':
    parser = make_parser()
    args = parser.parse_args()
    DynamicRestart(**vars(args))
