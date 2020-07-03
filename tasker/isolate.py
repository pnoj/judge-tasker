import subprocess
import shutil
import os
import sys

def get_box_id():
    return int(os.environ['ISOLATE_BOX_ID'])

def execute_command_subprocess(command, time_limit=None, stdin="", check=True, verbose=False):
    if verbose:
        print(' '.join(command))
    subprocess_result = subprocess.run(command, capture_output=True, timeout=time_limit, input=stdin, text=True, check=False)
    if check:
        print(subprocess_result.stdout)
        print(subprocess_result.stderr)
        subprocess_result.check_returncode()
    return subprocess_result

def setup():
    execute_command_subprocess(['isolate', '--cg', '--init', f'--box-id', f'{get_box_id()}'])

def cleanup():
    execute_command_subprocess(['isolate', '--cleanup', f'--box-id', f'{get_box_id()}'])

def execute_command(command, real_directory, virtual_directory, stdin="", verbose=False, check=True):
    command[0] = shutil.which(command[0])
    process_result = execute_command_subprocess(['isolate', f'--dir={virtual_directory}={real_directory}:rw', '--cg', '--stderr-to-stdout', '--share-net', f'--box-id', f'{get_box_id()}', '--run', '--'] + command, stdin=stdin, check=check, verbose=verbose)
    if verbose:
        print(process_result.stdout)
    return process_result.stdout
