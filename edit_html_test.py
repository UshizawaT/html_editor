#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup as bsoup
import argparse
import glob
import sys
import os
import json
from copy import deepcopy

argparser = argparse.ArgumentParser()

outside_tag: list[str] = ['<head>', '</head>']
before_tag: str = '<meta charset="utf-8">'
input_tag: str = '<meta name="keywords" content="Arduino, Arduino IDE">'


def get_index_on_partial_match(searchlist: list[str], reference: str) -> int:
    for i, l in enumerate(searchlist):
        if reference in l:
            return i
    return -1


def load_as_txt(filename: str) -> str:
    list_lines: list[str]
    with open(filename, mode='r', encoding='utf-8')as file:
        list_lines = file.read().split('\n')
    return list_lines


def insert_before_candidate_tag(rawlines: list[str], outer_tag: list[str], candidate_tag: str, input: str):
    list_out: list[str] = deepcopy(rawlines)
    i_otag_st = get_index_on_partial_match(rawlines, outer_tag[0])
    i_otag_en = get_index_on_partial_match(rawlines, outer_tag[1])
    print(f'insede from {i_otag_st} to {i_otag_en}')
    i_btag = get_index_on_partial_match(rawlines, candidate_tag)
    print(f'input tag after {i_btag}')
    if i_otag_st <= i_btag-1 <= i_otag_en:
        list_out.insert(i_btag, input)
    return list_out


def insert_after_candidate_tag(rawlines: list[str], outer_tag: list[str], candidate_tag: str, input: str):
    list_out: list[str] = deepcopy(rawlines)
    i_otag_st = get_index_on_partial_match(rawlines, outer_tag[0])
    i_otag_en = get_index_on_partial_match(rawlines, outer_tag[1])
    print(f'insede from {i_otag_st} to {i_otag_en}')
    i_btag = get_index_on_partial_match(rawlines, candidate_tag)
    print(f'input tag after {i_btag}')
    if i_otag_st <= (i_btag+1) <= i_otag_en:
        list_out.insert(i_btag+1, input)
    return list_out
    #wfilename: str = f'{os.path.splitext(filename)[0]}_edit.html'
    # with open(wfilename, mode='w', encoding='utf-8') as wfile:
    #    for i, l in enumerate(list_lines):
    #        if i == (i_btag+1) and i_otag_st <= i <= i_otag_en:
    #            wfile.write(f'{input_tag}\n')
    #        wfile.write(f'{l}\n')


def load_json_list():
    with open('edit_tag_list.json', mode='r', encoding='utf-8') as jsf:
        return json.load(jsf)


def file_io(filepath: str):
    d_json = load_json_list()
    #wfilename: str = f'{os.path.splitext(filepath)[0]}_edit.html'
    l_txt: list[str] = load_as_txt(filepath)
    if d_json['insert_flag'] == 'upper':
        print('insert upper')
        l_wtxt = insert_before_candidate_tag(
            l_txt, d_json['outer_tag'], d_json['marked_tag'], d_json['insert_tag'])
    elif d_json['insert_flag'] == 'bottom':
        print('insert bottom')
        l_wtxt = insert_after_candidate_tag(
            l_txt, d_json['outer_tag'], d_json['marked_tag'], d_json['insert_tag'])
    with open(filepath, mode='w', encoding='utf-8') as wfile:
        wtxt: str = '\n'.join(l_wtxt)
        wfile.write(wtxt)


def get_list_of_html_path(parent_dir_path: str):
    find_path = f'{parent_dir_path}/**/*.html'
    l_html_files = glob.glob(find_path, recursive=True)
    return l_html_files


if __name__ == '__main__':
    argparser.add_argument("file_path", help="please set me", type=str)
    args = argparser.parse_args()
    # file_io(args.file_path)
    l_file = get_list_of_html_path(args.file_path)
    for file in l_file:
        file_io(file)
