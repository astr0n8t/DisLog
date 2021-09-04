#!/usr/bin/env python3

from discord_logger import DiscordLogger
import json
import time
import multiprocessing

# read file
with open('options.json', 'r') as options:
    options_data=options.read()

# parse file
settings = json.loads(options_data)

options = {
    "application_name": settings['hostname'],
    "service_name": settings['service_name'],
    "service_environment": settings['environment'],
    "display_hostname": True,
    "default_level": "debug",
}

log_files = settings['log_files']

def watch(syslog_file):
    syslog_file.seek(0,2) # Go to the end of the file
    while True:
        line = syslog_file.readline()
        if not line:
            time.sleep(0.1) # Sleep briefly
            continue
        yield line

def logFile(filename):
    with open(filename, 'r') as log_file:
        log_file_output = watch(log_file)

        for output in log_file_output:

            logger = DiscordLogger(webhook_url=settings['web_url'], **options)
            logger.construct(title=filename, description=output)

            response = logger.send()

def startLog(filename):
    log_process = multiprocessing.Process(target = logFile, args=([filename]))
    log_process.start()
    return log_process

if __name__ == '__main__':
    multiprocessing.freeze_support()
    log_processes = {}
    for file in log_files:
        log_processes[file] = startLog(file)






