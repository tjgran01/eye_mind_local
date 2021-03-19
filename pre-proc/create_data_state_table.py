import pandas as pd
import os
import re

from pathlib import Path

def get_reading_order(trial_fnames):

    read_order = {}

    for k, val in trial_fnames.items():
        df = pd.read_csv(val[0], skiprows=1, names=["time_info", "event", "val"], sep="\t")
        condition_list = df[df['val'] == 7]["event"].tolist()
        condition_list = [elm[:-1] for elm in condition_list]

        # Preserve the order and get rid of repeats
        _cond_list = []
        for elm in condition_list:
            if elm not in _cond_list:
                _cond_list.append(elm)

        read_order[k] = _cond_list

    return read_order


def get_localizer_order(trial_fnames):

    loc_order = {}
    possible_vals = ["4_jabwords", "3_jabsent", "2_words", "1_sent"]

    for k, val in trial_fnames.items():
        df = pd.read_csv(val[0], skiprows=1, names=["time_info", "event", "val"], sep="\t")
        condition_list = df[df['val'] == 23]["event"].tolist()
        condition_list = [elm.split(" ")[-1] for elm in condition_list]

        missing = list_diff(possible_vals, condition_list)
        if len(missing) == 1:
            condition_list.insert(0, missing[0])
            loc_order[k] = condition_list
        else:
            loc_order[k] = []

    return loc_order


def validate_triggers(trigger_fnames):

    localizer_triggers = [25, 27, 24, 22, 23, 26]

    triggers_valid = {}

    for k, val in trigger_fnames.items():
        df = pd.DataFrame()
        for v in val:
            df = df.append(pd.read_csv(v, sep=";", names=["t", "sample", "val"]), ignore_index=True)

        if df.shape[0] == 226:
            triggers_valid[k] = "LSL Triggers Look Good For Whole Study"
        elif df.shape[0] > 226:
            triggers_valid[k] = f"There are {df.shape[0] - 226} more triggers than expected."
        elif df[df["val"].isin(localizer_triggers)].shape[0] == 86:
            triggers_valid[k] = f"LSL Triggers Look Good for Localizer / Resting State, but are {226 - df.shape[0]} triggers short of whole study."
        else:
            triggers_valid[k] = f"Missing: {86 - df[df['val'].isin(localizer_triggers)].shape[0]} in the Localizer / Resting State Task."

    return triggers_valid


def list_diff(li1, li2):
    return (list(list(set(li1)-set(li2)) + list(set(li2)-set(li1))))


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

    _this_fpath = os.path.dirname(os.path.realpath(__file__))

    ROOT_DIR = Path(f"{_this_fpath}/../data/unzipped/")

    nirs_fnames = find_files_of_type(ROOT_DIR, ".nirs")
    trigger_fnames = find_files_of_type(ROOT_DIR, ".tri")
    trial_sheet_fnames = find_files_of_type(ROOT_DIR, "Trials.txt")
    nirs_dir_fpaths = find_files_of_type(ROOT_DIR, ".nirs", return_parent=True)

    # Start getting info about the data
    valid_triggers_dict = validate_triggers(trigger_fnames)
    localizer_order_dict = get_localizer_order(trial_sheet_fnames)
    reading_order_dict = get_reading_order(trial_sheet_fnames)

    df = pd.DataFrame([nirs_fnames, trigger_fnames, nirs_dir_fpaths,
                       trial_sheet_fnames, valid_triggers_dict,
                       localizer_order_dict, reading_order_dict]).transpose()
    df.index.name = 'participant'
    df.columns = ["NIRS fPath", "Trigger fPath", "nirs_dir",
                  "Trial Sheet fPath", "Trigger Notes",
                  "Localizer Order", "Reading Order"]
    df.to_csv(Path(f"{ROOT_DIR}/../data_summaries/eml_summary_nirs.csv"))


if __name__ == "__main__":
    main()
