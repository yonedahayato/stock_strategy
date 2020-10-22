"""multiprocessing.py

    Section20

"""
import datetime as dt
import numpy as np
import multiprocessing as mp
import os
import pandas as pd
import sys
import time

ABSPATH = os.path.abspath(__file__)
BASEDIR = os.path.dirname(ABSPATH)
PARENTDIR = os.path.dirname(BASEDIR)
PPARENTDIR = os.path.dirname(PARENTDIR)
PPPARENTDIR = os.path.dirname(PPARENTDIR)

sys.path.append(PARENTDIR)
sys.path.append(PPPARENTDIR)

from helper.log import logger

def lin_parts(num_atoms, num_threads):
    """lin_parts func

    タスクの分割
    スニペット 20.5

    Args:
        num_atoms(int): タスクの総数
        num_threads(int): スレッドの数(ここではコア数)

    """
    # 単一ループによる原子の分割
    num_partition = min(num_threads, num_atoms) + 1
    parts = np.linspace(start = 0, stop = num_atoms, num = num_partition)
    parts = np.ceil(parts).astype(int)

    return parts

def nested_parts(num_atoms, num_threads, upper_triang=False):
    """nested_parts func

    タスクの分割
    スニペット 20.6

    Args:
        num_atoms(int): タスクの総数
        num_threads(int): スレッドの数(ここではコア数)
        upper_triang(bool): xxx

    """

    # 内側のループでの分子の分割
    parts, num_threads_tmp = [0], min(num_threads, num_atoms)
    for num in range(num_threads_tmp):
        part = 1 + 4 * (parts[-1] ** 2 + parts[-1] + num_atoms * (num_atoms + 1.0) / num_threads_tmp)
        part = (-1 + part ** 0.5) / 2
        parts.append(part)

    parts = np.round(parts).astype(int)

    if upper_triang: # 最初の行が最も重い
        parts = np.cumsum(np.diff(parts)[::-1])
        parts = np.append(np.array([0]), parts)

    return parts

def expand_call(kargs):
    """expand_call func

    コールバック関数へのジョブ（分子）の引き渡し
    スニペット 20.10

    Args:
        kargs(dict): コールバック関数の情報とその引数

    """
    func = kargs["func"]
    del kargs["func"]
    out = func(**kargs)
    return out

def process_jobs_single(jobs):
    """process_jobs_single func

    デバッグのためのシングルスレッド実行
    スニペット 20.8

    Args:
        jobs(list): タスクのリスト

    """
    out = []
    for job in jobs:
        out_tmp = expand_call(job)
        out.append(out_tmp)

    return out

def report_progress(job_num, num_jons, time0, task):
    """report_progress func

    非同期ジョブが完了したときに進行状況を報告

    Args:
        job_num(int): 完了したジョブ番号
        num_jons(int): すべてのジョブ数
        time0(xxx): 開始時刻
        task(xxx): xxx

    """
    msg = [float(job_num) / num_jons, (time.time() - time0) / 60.0]
    msg.append(msg[1] * (1 / msg[0] - 1))

    time_stamp = str(dt.datetime.fromtimestamp(time.time()))
    msg = "{} {}% {} done after {} minutes. Remaining {} minutes".format(time_stamp,
                             str(round(msg[0] * 100, 2)),
                             task,
                             str(round(msg[1], 2)),
                             str(round(msg[2], 2))
                             )

    if job_num < num_jons:
        sys.stderr.write(msg + "\r")
    else:
        sys.stderr.write(msg + "\n")

def process_jobs(jobs, task=None, num_threads=24):
    """process_jobs func

    並行しての処理の実行
    スニペット 20.9

    Note:
        expand_call の場合、ジョブには func: コールバックを含める必要がある

    """
    if task is None:
        task = jobs[0]["func"].__name__

    pool = mp.Pool(processes=num_threads)
    outputs, out, time0 = pool.imap_unordered(expand_call, jobs), [], time.time()

    # 非同期出力を処理し、進行状況を報告
    for i, out_tmp in enumerate(outputs, 1):
        out.append(out_tmp)
        report_progress(i, len(jobs), time0, task)

    pool.close()
    pool.join()

    return out

def mp_pandas_obj(func, pd_obj, num_threads=24, mp_batches=1, lin_mols=True, **kargs):
    """mp_pandas_obj func

    ジョブを並列化し、DataFrame または Series を返す
    スニペット 20.7

    Args:
        func(function): 並列して実行されるコールバック関数
        pd_obj(tuple): 次のものを含む要素の組み
            [0]: 分子をコールバック関数に渡すために使用される引数の名前
            [1]: 分子にグループ分けされる分割不能なタスク（原子）のリスト
        num_threads(int): スレッドの数(ここではコア数)
        mp_batches(int): 並列バッチ数（コア当たりのジョブ数）
        lin_mols(bool): パーティションが線形か二重ネストなのか
        kargs(dict): func に必要なキーワード引数

    Note:
        1. タスク分割ためのインデックスを作成 (parts)
            ex: 0 ~ 10のタスクを part=[ 0  5  7  9 10]のようにインデックスわけ

        2. parts を使用して 分割されたindex を作成 (job)

    """
    if lin_mols:
        parts = lin_parts(num_atoms=len(pd_obj[1]), num_threads=num_threads * mp_batches)
    else:
        parts = nested_parts(num_atoms=len(pd_obj[1]), num_threads=num_threads * mp_batches)

    jobs = []
    for sub_set_index in range(1, len(parts)):
        sub_set_start_index = parts[sub_set_index - 1]
        sub_set_end_index = parts[sub_set_index]

        job = {pd_obj[0]: pd_obj[1][sub_set_start_index:sub_set_end_index],
               "func": func}
        job.update(kargs)
        jobs.append(job)

    if num_threads == 1:
        out = process_jobs_single(jobs)
    else:
        out = process_jobs(jobs, num_threads=num_threads)

    if len(out) == 0:
        logger.warn("結果の件数が0です。確認してください。")
        return out

    if isinstance(out[0], pd.DataFrame):
        df0 = pd.DataFrame()
    elif isinstance(out[0], pd.Series):
        df0 = pd.Series()
    else:
        return out

    for i in out:
        df0 = df0.append(i)


    return df0.sort_index()
