#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup as bsoup
import argparse
import glob
from typing import overload
import json
from copy import deepcopy

argparser = argparse.ArgumentParser()

outside_tag: list[str] = ['<head>', '</head>']
before_tag: str = '<meta charset="utf-8">'
input_tag: str = '<meta name="keywords" content="Arduino, Arduino IDE">'


def get_index_on_partial_match(searchlist: list[str], reference: str, n_index: int = 0) -> int:
    for i, l in enumerate(searchlist):
        if reference in l and i > n_index:
            return i
    return -1


def get_indexlist_on_partial_match(searchlist: list[str], reference: str, n_index: int = 0) -> int:
    l_out: list[int] = [i for i, l in enumerate(
        searchlist) if reference in l and i > n_index]
    return l_out


def load_as_txt(filename: str) -> str:
    list_lines: list[str]
    with open(filename, mode='r', encoding='utf-8')as file:
        list_lines = file.read().split('\n')
    return list_lines


def get_index_of_outer_tags(rawlines: list[str], outer_tag: list[str], start_index: int = 0) -> tuple[int, int]:
    i_begin = get_index_on_partial_match(rawlines, outer_tag[0], start_index)
    i_end = get_index_on_partial_match(rawlines, outer_tag[1], i_begin)
    return i_begin, i_end


def is_tag_inside(rawlines: list[str], outer_tag: list[str], candidate_tag: str, target_from_ctag: int, start_index: int = 0) -> int:
    i_otag_st, i_otag_en = get_index_of_outer_tags(
        rawlines, outer_tag, start_index)
    i_ctag = get_index_on_partial_match(rawlines, candidate_tag, start_index)
    if i_ctag < 0 or i_otag_st < 0 or i_otag_en < 0:
        return -1
    _i_mod = i_ctag+target_from_ctag
    if i_otag_st <= _i_mod <= i_otag_en:
        print(f'inside from {i_otag_st} to {i_otag_en}')
        return _i_mod
    elif i_otag_en < _i_mod <= len(rawlines):
        while True:
            i_otag_st2, i_otag_en2 = get_index_of_outer_tags(
                rawlines, outer_tag, i_otag_en)
            if i_otag_st2 <= _i_mod <= i_otag_en2:
                print(f'inside from {i_otag_st2} to {i_otag_en2}')
                return _i_mod
    return -1


def insert_before_candidate_tag(rawlines: list[str], outer_tag: list[str], candidate_tag: str, input: str):
    list_out: list[str] = deepcopy(rawlines)
    i_otag_st, i_otag_en = get_index_of_outer_tags(rawlines, outer_tag)
    i_btag = get_index_on_partial_match(rawlines, candidate_tag)
    print(f'input tag before {i_btag}')
    if i_otag_st <= i_btag-1 <= i_otag_en:
        list_out.insert(i_btag, input)
    return list_out


def insert_after_candidate_tag(rawlines: list[str], outer_tag: list[str], candidate_tag: str, input: str):
    list_out: list[str] = deepcopy(rawlines)
    i_otag_st, i_otag_en = get_index_of_outer_tags(rawlines, outer_tag)
    i_atag = get_index_on_partial_match(rawlines, candidate_tag)
    print(f'input tag after {i_atag}')
    if i_otag_st <= (i_atag+1) <= i_otag_en:
        list_out.insert(i_atag+1, input)
    return list_out


def insert_cr_after_span(input: str) -> list[str]:
    outputlist: list[str] = [f'{input[:22]}']
    outputlist.append(f'{input[22:46]}')
    pre_index: int = 0
    index: int = input.find('</span>')
    l_span: int = len('</span>')
    print(f'span index: {index}, span length: {l_span}')
    i: int = 0
    while index != -1 and pre_index < index:
        if i == 0:
            outputlist.append(f'{input[46:(index+l_span)]}')
        else:
            outputlist.append(f'{input[(pre_index+l_span):(index+l_span)]}')
        pre_index = index
        index = input.find('</span>', index+l_span)
        print(f'span index: {index}')
        i += 1
    outputlist.append(f'{input[(pre_index+l_span):]}')
    return outputlist


def replace_tag(rawlines: list[str], outer_tag: list[str], candidate_tag: str, input: str):
    list_out: list[str] = deepcopy(rawlines)
    i_mod = is_tag_inside(rawlines, outer_tag, candidate_tag, 0)
    inserttxt: list[str] = insert_cr_after_span(input)
    print(inserttxt)
    if i_mod < 0:
        return None, False
    while i_mod >= 0:
        list_out[i_mod:i_mod+1] = inserttxt
        i_mod = is_tag_inside(rawlines, outer_tag, candidate_tag, 0, i_mod)
    return list_out, True


def load_json_list():
    with open('edit_tag_list.json', mode='r', encoding='utf-8') as jsf:
        return json.load(jsf)


def file_io(filepath: str, f_insert: bool, f_replace: bool):
    d_json = load_json_list()
    #wfilename: str = f'{os.path.splitext(filepath)[0]}_edit.html'
    l_txt: list[str] = load_as_txt(filepath)
    o_tag: list[str] = d_json['outer_tag']
    c_tag: str = d_json['marked_tag']
    f_sucsess: bool = False
    print(f'outer_tag: {o_tag}')
    print(f'candidated_tag: {c_tag}')
    if f_insert:
        if d_json['insert_flag'] == 'upper':
            print('insert upper')
            l_wtxt = insert_before_candidate_tag(
                l_txt, o_tag, c_tag, d_json['insert_tag'])
        elif d_json['insert_flag'] == 'bottom':
            print('insert bottom')
            l_wtxt = insert_after_candidate_tag(
                l_txt, o_tag, c_tag, d_json['insert_tag'])
        f_sucsess = (len(l_wtxt) > 0)
    elif f_replace:
        print('start replacement!')
        l_wtxt, f_sucsess = replace_tag(
            l_txt, o_tag, c_tag, d_json['replace_tag'])
    if not f_sucsess:
        return False
    with open(filepath, mode='w', encoding='utf-8') as wfile:
        wtxt: str = '\n'.join(l_wtxt)
        wfile.write(wtxt)
    return True


def get_list_of_html_path(parent_dir_path: str):
    find_path = f'{parent_dir_path}/**/*.html'
    l_html_files = glob.glob(find_path, recursive=True)
    return l_html_files


if __name__ == '__main__':
    argparser.add_argument("file_path", help="please set me", type=str)
    argparser.add_argument("--insert", help="optional", action="store_true")
    argparser.add_argument("--replace", help="optional", action="store_true")
    args = argparser.parse_args()
    # file_io(args.file_path)
    l_file = get_list_of_html_path(args.file_path)
    for file in l_file:
        if not file_io(file, args.insert, args.replace):
            print(f'did not change {file}')
