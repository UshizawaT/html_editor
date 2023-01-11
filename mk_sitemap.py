#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import argparse
import glob
import os
import datetime
import json

argparser = argparse.ArgumentParser()
homepage_root: str = 'https://my-remainder0fstudies.com/'
d_settings: dict[str:any] = {}


def get_list_of_html_path(parent_dir_path: str):
    find_path = f'{parent_dir_path}/**/*.html'
    l_html_files = glob.glob(find_path, recursive=True)
    return l_html_files


def load_json_list():
    global d_settings
    with open('sitemap_setting.json', mode='r', encoding='utf-8') as jsf:
        d_settings = json.load(jsf)


def depth_to_priority(path_str: str, parents: str):
    parent_depth: int = len(parents.split('/'))
    return 1-(len(path_str.split('/'))-parent_depth)*0.1


def transform_url_path(html_file_list: list[str], parent_path: str):
    url_path: list[str] = ['']*len(html_file_list)
    update_times: list[str] = ['']*len(html_file_list)
    priorities: list[float] = ['']*len(html_file_list)
    for i, html_path in enumerate(html_file_list):
        dt = datetime.datetime.fromtimestamp((os.stat(html_path)).st_mtime)
        update_times[i] = dt.strftime('%Y-%m-%d')
        priorities[i] = depth_to_priority(html_path, parent_path)
        url_path[i] = html_path.replace(parent_path, homepage_root)
    return url_path, update_times, priorities


def xml_sitemap(url_list: list[str], update_date_list: list[str], priority_list: list[float], parentpath: str):
    l_ignore: list[str] = d_settings['ignore']
    urlset = ET.Element('urlset')
    urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
    tree = ET.ElementTree(element=urlset)
    for url, udate, pri in zip(url_list, update_date_list, priority_list):
        if url in l_ignore:
            print(f'ignored: {url}')
            continue
        url_element = ET.SubElement(urlset, 'url')
        loc = ET.SubElement(url_element, 'loc')
        if url == f'{homepage_root}index.html':
            loc.text = homepage_root
        else:
            loc.text = url
        priority = ET.SubElement(url_element, 'priority')
        priority.text = f'{pri}'
        lastmod = ET.SubElement(url_element, 'lastmod')
        lastmod.text = udate
    tree.write(f'{parentpath}sitemap.xml',
               encoding='utf-8', xml_declaration=True)


if __name__ == '__main__':
    argparser.add_argument("parent_path", help="please set me", type=str)
    args = argparser.parse_args()
    load_json_list()
    l_htmls = get_list_of_html_path(args.parent_path)
    print(f'html files: {len(l_htmls)}')
    urls, utimes, priorities = transform_url_path(l_htmls, args.parent_path)
    xml_sitemap(urls, utimes, priorities, args.parent_path)
