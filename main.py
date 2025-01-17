import threading
import requests
import random
import string
import os
import json

from ui import Logger

logger = Logger()
os.makedirs("output", exist_ok=True)

val = "output/valid.txt"
inv = "output/invalid.txt"
err = "output/error.txt"

with open("config.json", "r") as file:
    config = json.load(file)
    num = config.get("num")
    threads_count = config.get("threads")

def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def check_paste_status(random_string):
    url = f"https://paste.ee/r/{random_string}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            logger.debug(f"Valid Paste: {url}")
            with open(val, "a") as valid_file:
                valid_file.write(f"{url}\n")
        elif response.status_code == 404:
            logger.error(f"Invalid Paste: {url}")
            with open(inv, "a") as invalid_file:
                invalid_file.write(f"{url}\n")
        else:
            logger.warn(f"Ratelimited: {url}")
            with open(err, "a") as error_file:
                error_file.write(f"{url}\n")
    except requests.RequestException as e:
        logger.error(f"Error checking URL {url}: {e}")
        with open(err, "a") as error_file:  # Save the URL to the error file
            error_file.write(f"{url} - Error: {e}\n")

def worker(thread_id):
    while True:
        random_string = generate_random_string(num)
        check_paste_status(random_string)

if __name__ == "__main__":

    threads = []
    for i in range(threads_count):
        thread = threading.Thread(target=worker, args=(i,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    logger.info("Task Completed")
