from urllib.parse import urlparse, urljoin
from threading import Lock, Thread
import os
import shutil
import time
import requests
import html2text
from bs4 import BeautifulSoup
from backend import utils
from backend.pdf import process_pdf

mutex = Lock()

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
    "referer": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
}


def get_link_from_path(link_path):
    with open(link_path, "r", encoding="utf-8") as f:
        link = f.read()

    link = [i.replace("\xa0", " ") for i in link.split("\n") if i != ""]
    return link


def create_result_folder():
    try:
        os.mkdir("result")
        print("Current dir in : " + os.getcwd())
    except:
        shutil.rmtree("result")
        print("Result folder exist, removed existing result folder")
        os.mkdir("result")
        print("Created result folder")


def find_base_url(url):
    o = urlparse(url)
    return o.scheme + "://" + o.netloc


def lk_to_file(lk, fail_link, file_name, file_lk_map, timeout):
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_images = True

    if lk.lower().endswith(".pdf"):
        txt = process_pdf(lk)
        if txt:
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(txt)
            mutex.acquire()
            file_lk_map[file_name] = lk
            mutex.release()
            return
        else:
            mutex.acquire()
            fail_link.append(lk)
            mutex.release()
            return

    if (
        lk.lower().endswith(".png")
        or lk.lower().endswith(".jpk")
        or lk.lower().endswith(".img")
        or lk.lower().endswith(".png")
        or lk.lower().endswith(".doc")
        or lk.lower().endswith(".docx")
        or lk.lower().endswith(".csv")
    ):
        print(f"Can't parse None HTML content, link is {lk}\n")
        mutex.acquire()
        fail_link.append(lk)
        mutex.release()
        return
    # check time out
    try:
        r = requests.get(lk, headers=headers, timeout=timeout)
    except (requests.exceptions.RequestException, ValueError) as e:
        print(f"Link {lk} time out in {timeout} seconds")
        mutex.acquire()
        fail_link.append(lk)
        mutex.release()
        return

    if r.status_code != 200:
        print(
            f"Fail to parse {lk}, status code is {r.status_code}\n, forbidden to request"
        )
        mutex.acquire()
        fail_link.append(lk)
        mutex.release()
    else:
        txt = r.text
        try:
            html_raw = h.handle(txt)
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(html_raw)
            #         print(f"Write {lk} to {file_name}")
            mutex.acquire()
            file_lk_map[file_name] = lk
            mutex.release()
        except:
            print(f"Wrong parsing {lk} to {file_name}...")
            print(txt)

    time.sleep(1)


def write_to_files(link_lst, deep_dive=False, level=1, timeout=30):
    file_lk_map = {}
    fail_link = []
    child_threads = []

    create_result_folder()

    for index in range(1, len(link_lst) + 1):
        lk = link_lst[index - 1]
        file_name = f"./result/{index}.txt"
        t = Thread(
            target=lk_to_file, args=([lk, fail_link, file_name, file_lk_map, timeout])
        )
        t.start()
        # check if the link is not a html
        child_threads.append(t)

    for t in child_threads:
        t.join()
    return file_lk_map, fail_link
