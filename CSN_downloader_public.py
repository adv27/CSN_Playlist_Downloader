import io
import os
import urllib.request

import requests
from bs4 import BeautifulSoup

AUTHOR = 'Vu Dinh Anh'
VERSION = '0.0.0'

DEFAULT_PATH = 'CSN_downloader'

DOWNLOAD_QUALITY = ['32kbps', '128kbps', '320kbps', '500kbps', 'Lossless']


def download_music_file(url):
    cwd = os.getcwd()  # current working directory
    file_name = url.split('/')[-1]
    file_name = file_name[file_name.index('v5=') + 3:]
    file_name = urllib.request.unquote(file_name)  # get file name, escape from URL pattern
    if not os.path.exists(cwd + '\\' + DEFAULT_PATH):
        os.makedirs(cwd + '\\' + DEFAULT_PATH)

    path_to_save = cwd + '\\' + DEFAULT_PATH + '\\' + file_name

    r = requests.get(url)
    with io.open(path_to_save, 'wb')as f:
        f.write(r.content)

    print("Downloaded :" + file_name)


def get_download_url(page):
    content = get_page_content(url=page)
    soup = BeautifulSoup(content, 'html.parser')
    download_div = soup.find('div', attrs={'id': 'downloadlink2'})  # div contain all download option

    download_urls = list()
    anchor_tags = download_div.find_all('a')
    for anchor_tag in anchor_tags:
        download_urls.append(anchor_tag['href'])

    return download_urls


def get_page_content(url):
    return requests.get(url=url).content


def get_all_download_pages(content):
    soup = BeautifulSoup(content, 'html.parser')
    table = soup.find('table', attrs={'border': '0', 'class': 'tbtable'})
    all_anchor_tags = table.find_all('a', attrs={'target': '_blank'})  # only download link has 'taget' : '_blank' attr
    download_links = list()  # for storing download_link
    for anchor_tag in all_anchor_tags:
        download_links.append(anchor_tag['href'])  # get download link from 'a' tag
    return download_links


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
        DEFAULT_PATH += '\\' + custom_path

    for download_page in list_download_page:
        download_urls = get_download_url(page=download_page)
        if any(quality in u for u in download_urls):
            for u in download_urls:
                if (quality in u):
                    download_music_file(u)
        else:
            #if  user's quality choosen is not available for download, find  the nearest download quality
            for q in DOWNLOAD_QUALITY[DOWNLOAD_QUALITY.index(quality) - 1::-1]:
                keep_find_quality = True
                for u in download_urls:
                    if (q in u):
                        download_music_file(u)
                        keep_find_quality = False
                if keep_find_quality is False:
                    break


if __name__ == '__main__':
    main()
