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
from color_log import log
import subprocess
import os
from time import sleep


class DynamicRestart:
    """Automatically restarts namd dynamics"""

    def __init__(self, **kwargs):
        self.conf = kwargs['conf']
        self.namd = kwargs['namd']
        self.namd_exe = kwargs['namd_exe']
        self.options = kwargs['options']
        self.previous = kwargs['previous']
        self.restart = kwargs['restart']
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
        restart_files = self.search_previous()
        if not restart_files:
            return False
        sleep(1)
        self.file_name = self.get_file_name(restart_files)

        # Loads conf file in memory for editing
        self.conf_file = self.read_conf()
        if not self.conf_file:
            return False
        sleep(1)

        # Gets last stp
        restart_step = self.get_restart_step(restart_files)
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
        self.edit_run_steps()
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
            return self.conf

        log('info', 'Searching conf file.')
        cmd = 'find ' + self.previous + ' -name "*conf"'
        output = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        output = output.stdout.readlines()
        if len(output) != 1:
            log('error', 'Conf file not found! Please specify path with -c.')
            return False
        else:
            return output[0].decode('utf-8').strip()

    def search_previous(self):
        """Search restart files on previous folder"""

        log('info', 'Searching restart files.')

        cmd = 'find ' + self.previous + ' -name "*restart*" -exec du -sh {} \\;'
        output = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)

        return self.resolve_restart(output)

    def resolve_restart(self, files):
        """Check for size on restart files"""

        files = files.stdout.readlines()
        if len(files) == 0:
            log('critical', 'Restart files not found. Aborting!')
            return False

        files_size = dict()
        new_restart = list()
        old_restart = list()
        for file in files:
            file = file.decode('utf-8').strip().split('\t')

            file_name = file[1]
            files_size[file_name] = file[0]

            if file_name.endswith(".xsc") or file_name.endswith(".coor") or file_name.endswith(".vel"):
                new_restart.append(file_name)
            if file_name.endswith(".old"):
                old_restart.append(file_name)

        return self.choose_restart(files_size, new_restart, old_restart)

    def choose_restart(self, files_dic, new, old):
        """Choose restart files not empty"""
        if len(new) >= 3:
            for file in new:
                if files_dic[file] == '0':
                    break
                else:
                    return self.annotate_restart(new)

        if len(old) >= 3:
            for file in old:
                if files_dic[file] == '0':
                    break
                else:
                    log('warning', 'Restart files empty or missing, using old restart files.')
                    sleep(1)
                    return 'old', self.annotate_restart(old)

        log('critical', 'Restart files empty or missing. Aborting!')
        return False

    @staticmethod
    def annotate_restart(file_list):
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
                log('error', 'Missing restart file.')
                return False

        log('info', 'Restart files ready.')
        return annotated_files

    @staticmethod
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

        if not self.restart.endswith('/'):
            self.restart = self.restart + '/'

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

        coord_index = self.conf_file.index([line for line in self.conf_file if 'coordinates' in line][0]) + 1
        self.conf_file.insert(coord_index, '\n')

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

    @staticmethod
    def format_option(option):
        """Format options to separe argument and value"""

        option = option.split()
        if option[0].lower() == 'set':
            option = [option[0] + ' ' + option[1], *option[2:]]
        return option

    def update_conf(self, option, base_index=0):
        """Edit conf file to include/uncomment option"""

        base_index = base_index + 1
        if base_index == 1:
            base_index = len(self.conf_file) - 1

        option = self.format_option(option)

        option_index = self.search_option(option[0])
        if option_index:
            self.conf_file[option_index] = ' '.join(option) + '\n'
        else:
            self.conf_file.insert(base_index, ' '.join(option) + '\n')

    def comment_conf(self, option):
        """Edit conf file to comment option"""

        option = self.format_option(option)

        option_index = self.search_option(option[0])
        if option_index:
            if not self.conf_file[option_index].startswith('#'):
                self.conf_file[option_index] = '#' + self.conf_file[option_index]
        else:
            log('warning', 'Option "' + ' '.join(option) + '" not found. Ignoring.')
            sleep(1)

    def edit_run_steps(self):
        """Edit the number of run steps"""

        if self.run:
            log('info', 'Setting run steps to ' + self.run + '.')
            self.update_conf('run ' + self.run)

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

        cmd = [self.namd_exe, conf_file, '>', log_file]

        if self.cores != 1:
            cmd.insert(1, '+p' + str(self.cores))

        try:
            with open(log_file, 'w') as out, open(err_file, "w") as err:
                process = subprocess.Popen(cmd, stdout=out, stderr=err)
                process.wait()
                log('info', 'Dynamic finished.')
        except PermissionError:
            log('error', 'Namd exe not found! Please specify path with -e.')


if __name__ == '__main__':
    parser = make_parser()
    args = parser.parse_args()
    DynamicRestart(**vars(args))
