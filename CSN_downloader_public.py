import io
import os
import platform
import shutil
import urllib.request
from builtins import filter
from itertools import repeat
from multiprocessing import Pool

import requests
from bs4 import BeautifulSoup

AUTHOR = 'Vu Dinh Anh'
VERSION = '0.0.2'

DEFAULT_PATH = 'CSN_downloader'

DOWNLOAD_QUALITY = ['32kbps', '128kbps', '320kbps', '500kbps', 'Lossless']

SLASH = ''
_backslashe = '\\'
_forwardslashe = '/'


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def get_system_platform():
    _system = platform.system().lower()
    global SLASH
    if _system == 'windows':
        SLASH = _backslashe
    elif _system == 'linux':
        SLASH = _forwardslashe


def download_music_file(url):
    cwd = os.getcwd()  # current working directory
    file_name = url.split('/')[-1]
    file_name = urllib.request.unquote(file_name)  # get file name, escape from URL pattern
    if not os.path.exists(cwd + '\\' + DEFAULT_PATH):
        os.makedirs(cwd + '\\' + DEFAULT_PATH)

    path_to_save = cwd + '\\' + DEFAULT_PATH + '\\' + file_name

    r = requests.get(url, stream=True)
    total_length = r.headers.get('content-length')

    print("{0}Downloading: {1:70} | {2:.2f}mb{3}".
          format(bcolors.OKBLUE,
                 file_name,
                 float(total_length) / 1048576,  # bytes to mb
                 bcolors.ENDC),
          end='\n')
    with io.open(path_to_save, 'wb')as f:
        shutil.copyfileobj(r.raw, f)
    print("{0}Downloaded:  {1}{2}".
          format(bcolors.OKGREEN,
                 file_name,
                 bcolors.ENDC),
          end='\n')


def get_download_url(page):
    content = get_page_content(url=page)
    soup = BeautifulSoup(content, 'html.parser')
    download_div = soup.find('div', attrs={'id': 'downloadlink2'})  # div contain all download option

    anchor_tags = download_div.find_all('a')
    download_urls = list(map(lambda a: a['href'], anchor_tags))

    return download_urls


def get_page_content(url):
    return requests.get(url=url).content


def get_all_download_pages(content):
    soup = BeautifulSoup(content, 'html.parser')
    table = soup.find('table', attrs={'border': '0', 'class': 'tbtable'})
    anchor_tags = table.find_all('a', attrs={'target': '_blank'})  # only download link has 'taget' : '_blank' attr
    download_links = list(map(lambda a: a['href'], anchor_tags))
    return download_links


def download(download_page: str, quality):
    download_urls = get_download_url(page=download_page)
    if any(quality in u for u in download_urls):
        # for u in download_urls:
        #     if (quality in u):
        for u in list(filter(lambda x: quality in x, download_urls)):
            download_music_file(u)
    else:
        # if  user's quality choosen is not available for download, find  the nearest download quality
        for q in DOWNLOAD_QUALITY[DOWNLOAD_QUALITY.index(quality) - 1::-1]:
            keep_find_quality = True
            for u in download_urls:
                if q in u:
                    download_music_file(u)
                    keep_find_quality = False
            if keep_find_quality is False:
                break


def main():
    # get system platform
    get_system_platform()

    # get url
    url = input("Enter url: ")

    content = get_page_content(url=url)
    list_download_page = get_all_download_pages(content=content)

    # get quality
    print(DOWNLOAD_QUALITY)
    quality = input("Enter download quality: ")
    while quality not in DOWNLOAD_QUALITY:
        print("Invalid input. Please try again.")
        quality = input("Enter download quality: ")

    custom_path = input('Enter folder to save (Enter to skip): ')
    if custom_path is not '':
        global DEFAULT_PATH
        DEFAULT_PATH += SLASH + custom_path

    # using multiprocessing for downloading
    with Pool(15) as pool:
        pool.starmap(download, zip(list_download_page, repeat(quality)))


if __name__ == '__main__':
    main()
