# coding: utf-8

"""Manages the folder synchronisation command in the user's crontab"""


from typing import Any

from crontab import CronTab



def add_job_to_crontab(command: str, interval: Any) -> None:
    """
    Adds a cron job with the specified command from the current user's crontab.
    :param command: The command of the cron job to be removed
    :param interval: The frequency, in minutes, with which the command should be executed
    """
    # Create a new cron object for the current user
    cron = CronTab(user=True)

    # Check if the job already exists
    found_jobs = [job for job in cron if job.command == command]

    if len(found_jobs) == 0:
        # Create a new job and set it to the desired interval
        job = cron.new(command=command)
        job.minute.every(interval)

        # Write the job to the crontab
        cron.write()

        print(f"Cron job {command} added with frequency every {interval} minutes!")
    else:
        # Change the execution frequency to all the found jobs
        for job in found_jobs:
            job.minute.every(interval)

        # Write the job to the crontab
        cron.write()

        print(f"Cron job already exists, modifying frequency to every {interval} minutes!")


def del_job_from_crontab(command: str) -> None:
    """
    Remove a cron job with the specified command from the current user's crontab.
    :param command: The command of the cron job to be removed
    """
    # Create a new cron object for the current user
    cron = CronTab(user=True)

    # Check if the job already exists
    jobs_to_remove = [job for job in cron if job.command == command]

    if len(jobs_to_remove) > 0:
        # Remove all found jobs
        for job in jobs_to_remove:
            cron.remove(job)

        # Write the changes to the crontab
        cron.write()
        print(f"Cron job(s) with command {command} removed.")
    else:
        print(f"No matching cron job found for command {command}")
