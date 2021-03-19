import pandas as pd
import os

from scipy.io import loadmat, savemat
import numpy as np
from shutil import copytree

from pathlib import Path
import re
import random

def handle_dictionary_storage(_m_dict, _m_key, _m_val, how="append-if-exists"):

    if how == "append-if-exists":
        if _m_key in _m_dict.keys():
            _m_dict[_m_key].append(_m_val)
        else:
            _m_dict[_m_key] = [_m_val]
    elif how == "ignore":
        if _m_key in _m_dict.keys():
            return _m_dict
        else:
            _m_dict[_m_key] = [_m_val]
    else: # overwrite
        _m_dict[_m_key] = [_m_val]

    return _m_dict


def find_files_of_type(dir, suffix, return_parent=False):

    file_dict = {}

    for root, dirs, fnames in os.walk(dir):
        for fname in fnames:
            if fname.endswith(suffix):
                if return_parent:
                    full_path = root
                else:
                    full_path = os.path.join(root, fname)
                participant_id = re.search("EML1_[0-9][0-9][0-9]", full_path).group()
                handle_dictionary_storage(file_dict, participant_id, full_path, how="append-if-exists")

    return file_dict


def build_stim_channel(trigger_df, ch_len):

    m_channel = np.zeros(ch_len)
    for row in trigger_df.iterrows():
        m_channel[row[1]["SampleIndx"]] = 1
        for x in range(row[1]["Duration"]):
            m_channel[row[1]["SampleIndx"] + x] = 1

    return m_channel


def build_new_stim_array(trigger_file, ch_len):

    col_names = ["Time", "SampleIndx", "Trigger_Value", "Duration"]
    df = pd.read_csv(trigger_file, sep=",", names=col_names)

    # Check if stim stuff even makes sense.
    if df.iloc[-1]["SampleIndx"] > ch_len or df.iloc[-1]["SampleIndx"] < 0:
        print(f"Stims for {trigger_file} seem off ... aborting.")
        return np.array([])

    groups = df.groupby(["Trigger_Value"])

    stim_array = []
    for g in groups:
        print(g[0])
        stim_channel = build_stim_channel(g[1], ch_len)
        stim_array.append(stim_channel)

    return np.array(stim_array).transpose()


def save_new_nirs(nirs_file, nirs_path, root_export_dir, id):

    copytree(f"{nirs_path}/{id}", f"{root_export_dir}/{id}")
    old_nirs_f = [fname for fname in os.listdir(f"{root_export_dir}/{id}") if ".nirs" in fname][0]
    os.remove(f"{root_export_dir}/{id}/{old_nirs_f}")
    savemat(f"{root_export_dir}/{id}/{id}.nirs", nirs_file)


def find_matching_trigger(k, trigger_dir):

    return [elm for elm in os.listdir(trigger_dir) if k in elm][0]


def main():

    _this_fpath = os.path.dirname(os.path.realpath(__file__))
    ROOT_DIR = Path(f"{_this_fpath}/../data/toolbox_staging/")
    EXPORT_DIR = Path(f"{_this_fpath}/../data/test_long_stim/")
    TRIGGER_DIR = Path(f"{_this_fpath}/../data/toolbox_staging/triggers_raw_durations/")


    nirs = find_files_of_type(ROOT_DIR, ".nirs")

    for k, val in nirs.items():

        nirs_f = loadmat(val[0])
        trigger_f = find_matching_trigger(k, TRIGGER_DIR)
        print(trigger_f)

        stim_ch_len = nirs_f["s"].shape[0]

        new_stim_data = build_new_stim_array(f"{TRIGGER_DIR}/{trigger_f}", stim_ch_len)
        nirs_f["s"] = new_stim_data
        save_new_nirs(nirs_f, ROOT_DIR, EXPORT_DIR, k)


if __name__ == "__main__":
    main()
