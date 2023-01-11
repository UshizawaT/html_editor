#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup as bsoup
import argparse
import glob
import sys
import os

argparser = argparse.ArgumentParser()


def search_desc(filename: str):
    htmlsoup: bsoup
    with open(filename, mode='r', encoding='utf-8') as htmlf:
        htmlsoup = bsoup(htmlf.read(), 'html.parser')
    desc = htmlsoup.find("meta", {"name": "description"})
    tag_robots = htmlsoup.find("meta", {"name": "robots"})
    if desc == None and tag_robots == None:
        return False
    return True


def search_keywords(filename: str):
    htmlsoup: bsoup
    with open(filename, mode='r', encoding='utf-8') as htmlf:
        htmlsoup = bsoup(htmlf.read(), 'html.parser')
    desc = htmlsoup.find("meta", {"name": "keywords"})
    tag_robots = htmlsoup.find("meta", {"name": "robots"})
    if desc == None and tag_robots == None:
        return False
    return True


def get_list_of_html_path(parent_dir_path: str):
    find_path = f'{parent_dir_path}/**/*.html'
    l_html_files = glob.glob(find_path, recursive=True)
    return l_html_files


def add_blank_desc_tag(filepath: str):
    htmlsoup: bsoup
    with open(filepath, mode='r', encoding='utf-8') as htmlf:
        htmlsoup = bsoup(htmlf.read(), 'html.parser')
    blank_desc = htmlsoup.new_tag(
        'meta', attrs={'name': 'description'}, content='')
    htmlsoup.head.insert(-2, blank_desc)
    # print(htmlsoup)
    mod_file = f'{os.path.splitext(filepath)[0]}_mod.html'
    # print(mod_file)
    with open(mod_file, mode='w', encoding='utf-8')as wfile:
        wfile.write(str(htmlsoup))


if __name__ == '__main__':
    argparser.add_argument("parents_path", help="please set me", type=str)
    argparser.add_argument("--key", help="optional", action="store_true")
    argparser.add_argument("--mod", help="optional", action="store_true")
    args = argparser.parse_args()
    if args.mod:
        add_blank_desc_tag(args.parents_path)
        sys.exit(0)
    l_html_path = get_list_of_html_path(args.parents_path)
    for path in l_html_path:
        if args.key:
            if not search_keywords(path):
                print(path)
        elif not search_desc(path):
            print(path)
