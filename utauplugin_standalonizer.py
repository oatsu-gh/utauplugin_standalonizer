#! /usr/bin/env python3
# coding: utf-8
# Copyright (c) 2020 oatsu
"""
# 入力
- ustファイルを読み取ってUstオブジェクトにする。
- UstオブジェクトをUtauPluginオブジェクトに変換する。
- UTAUプラグインへの入力用txtファイルに出力する。
  - ノートを全選択したときのスクリプトと一致するようにする。
# プラグイン実行
- UTAUプラグインを起動してtxtファイルを渡す。
- UTAUプラグインが終了したのを検知。
- UTAUプラグインが上書きしたtxtファイルを取得。
# 出力
- UTAUプラグインが出力したファイルを読み取るってUtauPluginオブジェクトにする。
- もとのUtauPluginオブジェクトのパラメーターと比較し、変更部分を上書きする。
- 加工済みUtauPluginオブジェクトをもとのUstオブジェクトと比較し、Ustオブジェクトに変換する。
- Ustオブジェクトをustファイルとして出力する。
"""

# from time import sleep
import subprocess
from copy import deepcopy
from os.path import basename, splitext
from pprint import pprint

import utaupy as up
from tqdm import tqdm

PATH_TEMPORARY_PLUGINTXT = './temp_utauplugin_wrapper.txt'


def run_external_utauplugin(path_utauplugin_exe, path_ust_in):
    """
    入出力パスを指定し、全体の処理を実行する。
    """
    # 処理したいUSTファイルを読み取る
    original_ust = up.ust.load(path_ust_in)
    # [#TRACKEND] を取り除く
    original_ust_for_plugin = deepcopy(original_ust)
    # UTAUプラグイン用のテキストファイルを出力
    path_plugintxt = PATH_TEMPORARY_PLUGINTXT
    original_ust_for_plugin.write(path_plugintxt.replace('.txt', '_in.txt'))
    original_ust_for_plugin.write(path_plugintxt)
    # UTAUプラグインを起動して処理させる
    subprocess.run((path_utauplugin_exe, path_plugintxt), check=True)
    # [#TRACKEND] を追加してから、UTAUプラグインが出力したファイルを取得する
    with open(path_plugintxt, 'a') as f:
        f.write('[#TRACKEND]\n')
    processed_ust = up.ust.load(path_plugintxt)

    # 変更点を元のUSTに反映
    notes = original_ust.notes
    for idx, note in enumerate(tqdm(processed_ust.notes)):
        if note.tag == '[#INSERT]':
            notes.insert(idx, note)
        else:
            # データ差分を更新
            notes[idx].update(note)
    # ustファイルを出力
    path_ust_out=splitext(basename(path_ust_in))[0] + '_updated.ust'
    original_ust.notes = notes
    original_ust.write(path_ust_out)


def main():
    path_utauplugin_exe=input('path_utauplugin_exe: ').strip('"')
    path_ust_in=input('path_ust_in: ').strip('"')
    run_external_utauplugin(path_utauplugin_exe, path_ust_in)
    input('できた')


if __name__ == '__main__':
    main()
