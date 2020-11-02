#! /usr/bin/env python3
# coding: utf-8
# Copyright (c) 2020 oatsu
"""
USTファイルを対象に、UTAUプラグインを実行させるツール。
大量に処理したい、複数のプラグインを連続で実行したいとかに使えそう。

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

import utaupy as up
from tqdm import tqdm

# from pprint import pprint


PATH_TEMPORARY_PLUGIN_TXT = './temp_utauplugin_wrapper.txt'


def generate_plugintxt_from_ustobj(ust, path_txt_out):
    """
    ust         : utaupy.ust.Ust オブジェクト
    path_txt_out: UTAUプラグイン用テキストファイルのPATH

    USTファイルを読み取り、
    UTAUプラグイン用のテキストファイルとして保存する。
    """
    # 元のUstオブジェクトを壊さないために複製
    ust_deepcopied = deepcopy(ust)
    # [#TRACKEND] に対応するノートを削除
    if ust_deepcopied[-1].tag == '[#TRACKEND]':
        del ust_deepcopied[-1]
    else:
        raise ValueError('入力USTの最終エントリが [#TRACKEND] じゃないです。')
    # UTAUプラグイン用のテキストファイルを出力
    ust_deepcopied.write(path_txt_out)


def run_external_utauplugin(path_utauplugin_exe, path_plugintxt):
    """
    入出力パスを指定し、全体の処理を実行する。
    path_utauplugin_exe: UTAUプラグインのパス
    path_plugintxt: UTAUプラグイン用一時ファイルのPATH
    """
    # UTAUプラグインを起動して処理させる
    subprocess.run((path_utauplugin_exe, path_plugintxt), check=True)


def update_ustobj_with_plugintxt(ust, path_plugintxt):
    """
    もとのUstと、プラグインが出力したUstっぽいファイルを比較して、
    もとのUstオブジェクトのパラメータを上書きする。
    """
    # [#TRACKEND] を追加
    with open(path_plugintxt, 'a') as f:
        f.write('[#TRACKEND]\n')
    # UTAUプラグインが出力したファイルをUstオブジェクトとして読み取る
    processed_ust = up.ust.load(path_plugintxt)

    # ノートのパラメータ差分を更新
    notes = ust.notes
    for idx, note in enumerate(tqdm(processed_ust.notes)):
        if note.tag == '[#INSERT]':
            notes.insert(idx, note)
        else:
            notes[idx].update(note)
    ust.notes = notes


def main():
    """
    処理対象ファイルのPATHを指定して処理を実行
    """
    # UTAUプラグインを指定
    path_utauplugin_exe = input('path_utauplugin_exe: ').strip('"')
    # 処理したいUSTファイルを指定
    path_ust_in = input('path_ust_in: ').strip('"')
    # USTファイルの出力先
    path_ust_out = splitext(basename(path_ust_in))[0] + '_result.ust'
    # USTファイルをutaupy.ust.Ustオブジェクト化
    ust = up.ust.load(path_ust_in)
    # UTAUプラグイン用の一時ファイルを生成
    generate_plugintxt_from_ustobj(ust, PATH_TEMPORARY_PLUGIN_TXT)
    # UTAUプラグインを呼び出して処理を実行
    run_external_utauplugin(path_utauplugin_exe, PATH_TEMPORARY_PLUGIN_TXT)
    # UTAUプラグイン用の一時ファイルを読み取ってUstオブジェクトに差分を反映
    update_ustobj_with_plugintxt(ust, PATH_TEMPORARY_PLUGIN_TXT)
    # UstオブジェクトをUSTファイル出力
    ust.write(path_ust_out)


if __name__ == '__main__':
    main()
    input('できた')
