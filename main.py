# coding: utf-8


"""Execution start point. Allows the job to be added or removed from the user's crontab"""

import os
import sys

from folder_sync import add_job_to_crontab, del_job_from_crontab


_MODE_ADD = "add"
_MODE_DEL = "del"


if __name__ == "__main__":
    if len(sys.argv) < 6:
        raise ValueError(
            f"Not enough arguments provided!\n"
            f"Expected usage: python {os.path.basename(__file__)} <source folder path> "
            f"<replica folder path> <synchronisation interval (minutes)> <log file path> "
            f"<mode>"
        )
    if len(sys.argv) > 6:
        print(
            f"Additional (unexpected) command line arguments specified!\n"
            f"Expected usage: python {os.path.basename(__file__)} <source folder path> "
            f"<replica folder path> <synchronisation interval (minutes)> <log file path> "
            f"<mode>\nThe following arguments will be ignored: {sys.argv[6:]}"
        )

    _source_folder_path = sys.argv[1]
    _replica_folder_path = sys.argv[2]
    _sync_interval = sys.argv[3]
    _log_file = sys.argv[4]
    _mode = sys.argv[5]

    curr_file_root_folder = os.path.dirname(__file__)
    file_to_run = os.path.join(curr_file_root_folder, "folder_sync/_folder_sync.py")

    curr_root_folder_python = os.path.join(curr_file_root_folder, "venv/bin/python")
    PYTHON_EXEC = curr_root_folder_python if os.path.exists(curr_root_folder_python) else "python"

    command_to_add = f"cd {curr_file_root_folder};"\
        f"{PYTHON_EXEC} {file_to_run} {_source_folder_path} {_replica_folder_path} {_log_file}"

    if _mode.lower() == _MODE_ADD:
        add_job_to_crontab(command_to_add, _sync_interval)
    elif _mode.lower() == _MODE_DEL:
        del_job_from_crontab(command_to_add)
    raise ValueError(
        f"Invalid value assigned to <mode> argument! Expected {_MODE_ADD} or {_MODE_DEL}, "
        f"but found: {_mode}"
    )
