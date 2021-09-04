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

def watch(filename, queue):
    log_file = open(filename, 'r')
    log_file.seek(0,2) # Go to the end of the file
    while True:
        line = log_file.readline()
        if line:
            queue.put(line)
        else:
            time.sleep(0.1) # Sleep briefly

def sendReport(report):
    logger = DiscordLogger(webhook_url=settings['web_url'], **options)
    logger.construct(title=str("Last " + str(settings['interval']) + " Seconds of Logs"), description=report)

    response = logger.send()

def main():
    
    multiprocessing.freeze_support()
    log_files = settings['log_files']
    log_processes = {}
    log_queues = {}
    for file in log_files:
        log_queues[file] = multiprocessing.Queue()
        log_processes[file] = multiprocessing.Process(target = watch, args=(file, log_queues[file]))
        log_processes[file].start()

    while True:
        time.sleep(settings['interval'])

        output = ""
        for file in log_files:
            output += str("**" + file + "**\n\n")
            num_in_queue = log_queues[file].qsize()
            for x in range(num_in_queue):
                output += log_queues[file].get()
            output += '\n'

        print(output)

        sendReport(output)

if __name__ == '__main__':
    main()






