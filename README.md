# veeam-folder-sync
Simple folder synchronisation package

Python package that implements synchronisation of two folders. It maintains a full, identical copy of the source folder at the replica folder.

**Usage**: The package relies on crontab to schedule periodic synchronisation between the folders.
- To add a new synchronisation job run *python main.py <PATH_TO_SOURCE_FOLDER> <PATH_TO_REPLICA_FOLDER> <SYNC_INTERVAL_MIN> <LOG_FILE_PATH> ADD*.
- To remove a previously added synchronisation job run *python main.py <PATH_TO_SOURCE_FOLDER> <PATH_TO_REPLICA_FOLDER> <SYNC_INTERVAL_MIN> <LOG_FILE_PATH> DEL*
