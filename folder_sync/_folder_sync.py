# coding: utf-8

"""Module implementing folder synchronisation mechanism"""

import datetime
import filecmp
import os
import shutil
import sys
from typing import List


__author__ = "Joaquim Leitão"
__email__ = "jocaleitao93@gmail.com"


def _write_to_log(log_file_path: str, message: str) -> None:
    """
    Appends a provided message to a log file in a given location.
    :param log_file_path: Path to the log file
    :param message: The messaged to the appended to the log file
    """
    with open(log_file_path, "a", encoding="utf-8") as fp:
        fp.write(f"[{datetime.datetime.now()}] {message}\n")


def _custom_print(log_file_path: str, message: str) -> None:
    """
    Custom implementation of a print function, making sure that the desired message is not only
    printed to the console output, but also to the provided log file
    :param log_file_path: Path to the log file
    :param message: The message to be printed and logged to the file
    """
    print(message)
    _write_to_log(log_file_path, message)


def _copy_new_modified_files(
        source_folder_path: str,
        replica_folder_path: str,
        paths_list: List[str],
        log_file_path: str
) -> bool:
    """
    Copies both (i) new files/folders added to the source folder, and (ii) files modified in the
    source folder, since the last synchronisation, to the replica folder. If any copy operation
    fails, it is appropriately logged in the provided log file.
    :param source_folder_path: The path to the source folder
    :param replica_folder_path: The path to the replica folder
    :param paths_list: List of names of the newly created or modified files and folders, in the
                       source folder
    :param log_file_path: Path to a file where the logs of the aforementioned operations will be
                          carried out
    :return: True, if all the actions were performed successfully, otherwise False
    """
    return_val = True
    for path_name in paths_list:
        try:
            source_path = os.path.join(source_folder_path, path_name)
            replica_path = os.path.join(replica_folder_path, path_name)

            # Copy from "source_path" to "replica_path"
            if os.path.isdir(source_path):
                # If "source_path" corresponds to a directory, then this will be the relative path
                # to a newly created directory, which does not exist in the replica folder (only
                # modified files appear in dircmp.diff_files, and those will be processed in the
                # else statement). Nevertheless, if indeed a case occurs where the folder already
                # exists in the replica folder, then the version from the source folder should be
                # kept, hence calling shutil.copytree with "dirs_exist_ok=True"
                _custom_print(log_file_path, f"Copying folder from {source_path} to {replica_path}")
                shutil.copytree(source_path, replica_path, dirs_exist_ok=True)
            else:
                _custom_print(log_file_path, f"Copying file from {source_path} to {replica_path}")
                shutil.copy2(source_path, replica_path)
        except (FileNotFoundError, OSError, PermissionError, shutil.SameFileError) as e:
            _custom_print(
                log_file_path,
                f"Exception while copying modified file/folder {path_name}: {e}"
            )
            return_val = False

    return return_val


def _delete_locations(
        folder_root_path: str,
        sub_folder_names: List[str],
        log_file_path: str
) -> bool:
    """
    Deletes a specified set of files/folders, which are all contained inside a given root
    folder. These correspond to files/folders deleted in the source folder since the last
    synchronisation, and which, therefore, must also be deleted on the replica folder.
    For each folder deleted, a new line in the provided log file is added, documenting the action
    performed. If any deletion fails, it is appropriately logged in the provided log file.
    :param folder_root_path: Path to the root location of all the folders to be deleted
    :param sub_folder_names: List with the names of the folders to be deleted
    :param log_file_path: Path to a file where the log of the aforementioned folder deletion
                          actions will be carried out
    :return: True, if all the actions were performed successfully, otherwise False
    """
    # Delete each folder only on the replica/target folder
    return_val = True
    for sub_folder_name in sub_folder_names:
        try:
            curr_subfolder_name = os.path.join(folder_root_path, sub_folder_name)
            if os.path.isdir(curr_subfolder_name):
                _custom_print(log_file_path, f"Deleting folder {curr_subfolder_name}")
                shutil.rmtree(curr_subfolder_name)
            else:
                _custom_print(log_file_path, f"Deleting file {curr_subfolder_name}")
                os.remove(curr_subfolder_name)
        except (FileNotFoundError, OSError, PermissionError, shutil.SameFileError) as e:
            _custom_print(
                log_file_path,
                f"Exception during file/folder deletion {sub_folder_name}: {e}"
            )
            return_val = False
    return return_val


def _folder_sync(source_folder_path: str, replica_folder_path: str, log_file_path: str) -> None:
    """
    Synchronizes the contents of two folders - source folder and replica folder - such that the
    replica folder is an exact match of the source folder, once the synchronisation is completed.
    This synchronisation includes deleting files and folders removed from the source folder, as
    well as newly added ones, and files and folders modified in the source folder.
    :param source_folder_path: The path to the source folder
    :param replica_folder_path: The path to the replica folder
    :param log_file_path: Path to a file where the log of the operations carried out during the
                          synchronisation will be carried out
    :raises:
        FileNotFoundError: If the source folder cannot be found at the path provided in the
                           <source_folder_path> argument
    """

    # Get absolute paths for source and replica folders, in case relative paths are provided
    source_folder_path = os.path.abspath(source_folder_path)
    replica_folder_path = os.path.abspath(replica_folder_path)

    if not os.path.exists(source_folder_path):
        message = f"Could not find the source folder at the provided path: {source_folder_path}"
        _write_to_log(log_file_path, f"EXCEPTION: {message}")
        raise FileNotFoundError(message)

    if not os.path.exists(replica_folder_path):
        # Replica folder does not exist, copy it and return
        message = f"Replica folder not found at path {replica_folder_path}. "\
                  f"Copying entire source folder from path {source_folder_path}"
        _custom_print(log_file_path, message)

        shutil.copytree(source_folder_path, replica_folder_path)
        return

    comparison_result = filecmp.dircmp(source_folder_path, replica_folder_path)

    # Must copy files in "left_only" and "diff_files" from source to replica
    _return_val  =_copy_new_modified_files(
        source_folder_path,
        replica_folder_path,
        comparison_result.left_only + comparison_result.diff_files,
        log_file_path
    )
    if not _return_val:
        # Error while copying new files to replica folder!
        # Stop execution (already logged the folder/file which failed to copy)
        return

    # Must delete files/folders in "right_only"
    _return_val = _delete_locations(
        replica_folder_path,
        comparison_result.right_only,
        log_file_path
    )
    if not _return_val:
        # Error during deletion! Stop execution (already logged the folder which failed to delete)
        return

    # Need to do similar process for each folder in "common_dirs"
    for sub_folder_name in comparison_result.common_dirs:
        _folder_sync(
            os.path.join(source_folder_path, sub_folder_name),
            os.path.join(replica_folder_path, sub_folder_name),
            log_file_path
        )


if __name__ == "__main__":
    if len(sys.argv) < 4:
        raise ValueError(
            f"Not enough arguments provided!\n"
            f"Expected usage: python {os.path.basename(__file__)} <source folder path> "
            f"<replica folder path> <log file path>"
        )
    if len(sys.argv) > 4:
        print(
            f"Additional (unexpected) command line arguments specified!\n"
            f"Expected usage: python {os.path.basename(__file__)} <source folder path> "
            f"<replica folder path> <log file path>"
            f"The following arguments will be ignored: {sys.argv[4:]}"
        )

    _source_folder_path = sys.argv[1]
    _replica_folder_path = sys.argv[2]
    _log_file = sys.argv[3]

    _folder_sync(_source_folder_path, _replica_folder_path, _log_file)
