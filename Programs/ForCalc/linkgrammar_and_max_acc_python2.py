# -*- coding: utf-8 -*-

'''
PyTorchのモデル関連
linkgrammarを用いた文法チェックを行い，エラーの無い選択肢のみファイルを作成
もし選択肢全てにエラーが出た場合は，全ての選択肢を残す

※ linkgrammarはubuntu16.04だとpython3に対応してないっぽい？ので
他のプログラムと異なりpython2.7で実行する


'''

from __future__ import print_function

import os
import re
import random
import locale
from linkgrammar import Sentence, ParseOptions, Dictionary

locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
po = ParseOptions()

def is_grammar_OK(text):
    sent = Sentence(text, Dictionary(), po)
    linkages = sent.parse()

    if sent.null_count() >0:
        return False

    return True


#ペアじゃなくて単独で読み取るやつ
def read_rawData(file):
    #print("Reading data...")
    data=[]
    with open(file, encoding='utf-8') as f:
        for line in f:
            data.append(line.strip())

    return data



def get_cloze(line):
    line=re.sub(r'.*{ ', '', line)
    line=re.sub(r' }.*', '', line)

    return line


def get_choices_from_raw_data(file_name):
    #print("Reading data...")
    choices=[]
    with open(file_name, encoding='utf-8') as f:
        for line in f:
            line=get_cloze(line.strip())
            choices.append(line.split(' ### '))     #選択肢を区切る文字列

    return choices


def randamOK(ans, OKchoices):
    ans_word=get_cloze(line)
    rand_choi=random.choice(OKchoices)
    if ans_word==rand_choi:
        return 1

    return 0

def check_grammar_and_calc_baseline_acc(ans, choices):
    OKchoices=[]
    before=re.sub(r'{.*', '', ans)
    after=re.sub(r'.*}', '', ans)

    for choice in choices:
        tmp=before + choice + after
        if is_grammer_OK(tmp.strip()):
            OKchoices.append(choice)

    if not OKchoices:
        #pythonではlistが空だとFalseになることを利用
        #どの選択肢も文法エラーの場合は全て使う
        OKchoices=choices

    flag=randamOK(ans, OKchoices)

    before_with_cloze=re.sub(r'{.*', '{ ', ans)
    after_with_cloze=re.sub(r'.*}', ' }', ans)

    mid=' ### '.join(OKchoices)
    output_line=before_with_cloze+mid+after_with_cloze

    return OKchoices, flag, output_line



def make_choices_file_and_calc_baseline_acc(ans_path, choi_path, output_path):
    all_choices=get_choices_from_raw_data(choi_path)
    ans_sents=read_rawData()
    line_num=0
    baseline_OK=0
    #ここまでは空所の記号ついたまま
    with open(output_path, 'w') as f:
        for ans, choices in zip(ans_sents, all_choices):
            OKchoices, flag, output_line=check_grammar_and_calc_baseline_acc(ans, choices)
            baseline_OK+=flag
            f.write(output_line+'\n')

    print('baseline: ',1.0*baseline_OK/line_num*100)



#----- いわゆるmain部みたいなの -----

file_path='../../../pytorch_data/'
git_data_path='../../Data/'

center_ans=git_data_path+'center_ans.txt'
center_choi=git_data_path+'center_choices.txt'
MS_ans=git_data_path+'microsoft_ans.txt'
MS_choi=git_data_path+'microsoft_choices.txt'

output_center_choi=git_data_path+'center_choices_linkgrammar.txt'
output_MS_choi=git_data_path+'microsoft_choices_linkgrammar.txt'


make_choices_file_and_calc_baseline_acc(center_ans, center_choi, output_center_choi)
make_choices_file_and_calc_baseline_acc(MS_ans, MS_choi, output_MS_choi)
