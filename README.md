# Namd Restarter
Created by Artotim.   

Namd restarter is a program to automatically restart a previous NAMD dynamic run. It follows the instructions on [this post](https://www.ks.uiuc.edu/Research/namd/mailing_list/namd-l.2007-2008/1211.html) to restart/continue from an old .conf along with the files from the last run.  

This program is licensed under the [GPL-3.0 License](https://github.com/Artotim/namd-restarter/blob/main/LICENSE).

## Installation
First download the program with the command: 

    wget https://github.com/Artotim/namd-restarter/raw/main/namd_restart  
       
Then give it executable permissions:

    chmod +x namd_restart


## Usage  
You can set the program to your path or simply run it with `./namd_restart`  

	Basic usage: namd_restart -i <path/to/previous_run/> -o <path/to/restart_output/>

	Required parameters:
	    -i , --input           Previous dynamic folder
	    -o , --output          Restart output folder

	Optional parameters:
	    -h, --help             Show help message and exit
	    -c , --conf            Path to previous .conf file
	    -f , --file-name       Set output files name
	    -r , --run             Set run steps number (default is get from last run)
	    -a , --add-options     Additional options to include in .conf file (e.g., <margin 3>)
	    -e , --namd-exe        Path to namd executable
	    -N, --no-namd          Disable automatically running namd after end
	    -B, --backup           Save backups for restart files while running namd
	    -t , --threads         Number of cores to run namd when automatically running (default: 1)
                       
### Disclaimer
This product comes with no warranty whatsoever.  
This product its not an official NAMD release or have any affiliation to it.