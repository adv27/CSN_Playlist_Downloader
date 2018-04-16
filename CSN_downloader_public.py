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
VERSION = '0.0.3'

DEFAULT_PATH = 'CSN_downloader'

DOWNLOAD_QUALITY = ['32kbps', '128kbps', '320kbps', '500kbps', 'Lossless']


def download_music_file(url, save_at):
    cwd = os.getcwd()  # current working directory
    # get file name, escape from URL pattern
    file_name = url.split('/')[-1]
    file_name = urllib.request.unquote(file_name)
    # checking if the save folder is exist or not, if not then create one
    if not os.path.exists(os.path.join(cwd, save_at)):
        os.makedirs(os.path.join(cwd, save_at))

    path_to_save = os.path.join(cwd, save_at, file_name)

    r = requests.get(url, stream=True)
    total_length = r.headers.get('content-length')

    with io.open(path_to_save, 'wb') as f:
        shutil.copyfileobj(r.raw, f)
    print("Downloaded: {0:70} | {1:.2f}mb".
        format(
            file_name,
            float(total_length) / 1048576 # bytes to mb
        ),end='\n')


def get_page_content(url):
    return requests.get(url=url).content


def get_all_download_pages(content):
    soup = BeautifulSoup(content, 'html.parser')
    table = soup.find('table', attrs={'border': '0', 'class': 'tbtable'})
    # only download link has 'taget' : '_blank' attr
    anchor_tags = table.find_all('a',attrs={'target':'_blank'})  
    download_links = list(map(lambda a: a['href'], anchor_tags))
    return download_links


def get_download_urls(page):
    content = get_page_content(url=page)
    soup = BeautifulSoup(content, 'html.parser')

    # div contain all download option
    download_div = soup.find('div', attrs={'id':'downloadlink2'})  

    anchor_tags = download_div.find_all('a')
    download_urls = list(map(lambda a: a['href'], anchor_tags))

    return download_urls


def get_download_url(download_page: str, quality):
    download_urls = get_download_urls(page=download_page)
    if any(quality in u for u in download_urls):
        for u in list(filter(lambda x: quality in x, download_urls)):
            return u
    else:
        # if  user's quality choosen is not available for download, find  the nearest download quality
        index = DOWNLOAD_QUALITY.index(quality) - 1
        for q in DOWNLOAD_QUALITY[index::-1]:
            for u in download_urls:
                if q in u:
                    return u


def main():
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
        DEFAULT_PATH = os.path.join(DEFAULT_PATH,custom_path)

    # using multiprocessing for downloading
    download_urls = list(map(lambda p: get_download_url(p,quality),list_download_page))
    save_at = DEFAULT_PATH
    for url in download_urls:
        download_music_file(url,save_at)
    # with Pool(25) as pool:
    #     pool.starmap(download_music_file, zip(download_urls,repeat(save_at)))


if __name__ == '__main__':
    main()
