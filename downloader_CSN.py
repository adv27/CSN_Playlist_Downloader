import os
import re
import urllib.request

import requests
import wget
from bs4 import BeautifulSoup

AUTHOR = 'Vu Dinh Anh'
VERSION = '0.0.0'

DEFAULT_PATH = 'CSN_downloader'

DOWNLOAD_QUALITY = ['32kbps', '128kbps', '320kbps', '500kbps', 'Lossless']

key = ['U', 'W', 'J', 'H', 'D', 'G', 'M', 'A', 'Y', 'I', 'X', 'N', 'R', 'L', 'B', 'P', 'K']
val = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'c', 'u', 'f', 'r', '1', '1', '2']
keymap = dict(zip(key, val))


def decode_key(webkey):
    out = ""
    for k in webkey:
        if k == '-':
            out = out + "-"
        elif k not in key:
            out = out + k
        else:
            out = out + keymap[k]
    return out


def download_music_file(url):
    cwd = os.getcwd()
    file_name = url.split('/')[-1]
    file_name = urllib.request.unquote(file_name)  # get file name
    if not os.path.exists(cwd + '\\' + DEFAULT_PATH):
        os.makedirs(cwd + '\\' + DEFAULT_PATH)
    path_to_save = cwd + '\\' + DEFAULT_PATH + '\\' + file_name
    wget.download(url=url, out=path_to_save)
    print("Downloaded: " + file_name)


def decode(script):
    regex = r'decode_download_url\(\'(.*)\',(.*),(.*),(.*)\)( +)'
    m = re.search(regex, script)
    download_url = m.group(1) + decode_key(re.sub('[\s\']', '', m.group(2))) + re.sub('[\s\']', '', m.group(3))
    return download_url


def get_download_url(page):
    content = get_page(url=page)
    soup = BeautifulSoup(content, 'html.parser')
    download_div = soup.find('div', attrs={'id': 'downloadlink2'})  # div contain all download option
    scripts = download_div.find_all('script')  # scpit because 'pre load'
    download_urls = list()
    for script in scripts:
        download_url = decode(script=script.text)
        download_urls.append(download_url)
    return download_urls


def get_page(url):
    return requests.get(url=url).content


def get_all_download_pages(content):
    soup = BeautifulSoup(content, 'html.parser')
    table = soup.find('table', attrs={'border': '0', 'class': 'tbtable'})
    all_a_tags = table.find_all('a', attrs={'target': '_blank'})  # only download link has 'taget' : '_blank' attr
    download_links = list()  # for storing download_link
    for a_tag in all_a_tags:
        download_links.append(a_tag['href'])  # get download link from 'a' tag
    return download_links


def main():
    # get url
    url = input("Enter url: ")

    content = get_page(url=url)
    list_download_page = get_all_download_pages(content=content)

    # get quality
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
