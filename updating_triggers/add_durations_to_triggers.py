import pandas as pd
import os

from scipy.io import loadmat, savemat
import numpy as np
from shutil import copytree

from pathlib import Path
import re

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


def main():

    loc_map = {"1_sent": 51,
               "2_words": 52,
               "3_jabsent": 53,
               "4_jabwords": 54}

    _this_fpath = os.path.dirname(os.path.realpath(__file__))
    ROOT_DIR = Path(f"{_this_fpath}/../data/toolbox_staging/")
    EXPORT_DIR = Path(f"{_this_fpath}/../data/toolbox_staging/triggers_raw_durations/")

    trigger_files = find_files_of_type(ROOT_DIR, ".tri")

    notes_df = pd.read_csv(Path(f"{_this_fpath}/../data/data_summaries/eml_summary_nirs.csv")).set_index('participant')

    for k, val in trigger_files.items():

        loc_order = notes_df.loc[k]['Localizer Order'][1:-1].replace("'", "").split(', ')

        df = pd.read_csv(val[0], sep=";", names=["t", "sample", "value"])

        df = df[df["value"] != 22]

        durations = []
        for i, elm in enumerate(df["sample"].tolist()):
            if i + 1 == len(df["sample"].tolist()):
                durations.append(0)
            else:
                durations.append(df["sample"].tolist()[i + 1] - elm)

        df["duration"] = durations

        # Remove task end triggers.
        df = df[df["value"] != 26]
        df = df[df["value"] != 27]

        new_val_list = []
        count = 0
        for elm in df["value"].tolist():
            if elm == 23:
                new_val_list.append(loc_map[loc_order[count]])
                count += 1
            elif elm == 24:
                new_val_list.append(loc_map[loc_order[count]])
                count += 1
            else:
                new_val_list.append(elm)

        df["value"] = new_val_list

        df.to_csv(f"{EXPORT_DIR}/{k}_RAW.tri", header=False, index=False)




if __name__ == "__main__":
    main()
