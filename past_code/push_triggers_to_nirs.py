import pandas as pd
import os

from scipy.io import loadmat, savemat
import numpy as np
from shutil import copytree

from pathlib import Path

def find_files_of_type(root, type):

    fpaths = {}
    for root, dirs, fnames in os.walk(root):
        for fname in fnames:
            if fname.endswith(type):
                full_path = os.path.join(root, fname)
                fpaths[full_path.split("/")[2][:6]] = full_path

    return fpaths


def build_stim_channel(trigger_df, ch_len):

    m_channel = np.zeros(ch_len)
    for row in trigger_df.iterrows():
        m_channel[row[1]["SampleIndx"]] = 1

    return m_channel


def build_new_stim_array(trigger_file, ch_len):

    col_names = ["Time", "SampleIndx", "Trigger_Value"]
    df = pd.read_csv(trigger_file, sep=";", names=col_names)

    print(trigger_file)

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

    # Fix sloppy copying.
    fname = nirs_path[nirs_path.rfind("\\")+1:-5]
    path_without_file = nirs_path[:nirs_path.rfind("\\")+1]
    new_dir_path = f"{root_export_dir}{id}/"

    copytree(path_without_file, new_dir_path)
    savemat(f"{new_dir_path}{fname}.nirs", nirs_file)


def main():

    root_data_dir = "../data/"
    root_export_dir = "./rewritten_nirs_stims/"

    trigger_files = find_files_of_type(root_data_dir ,"_new.tri")
    nirs_files = find_files_of_type(root_data_dir ,".nirs")

    missing_dotNIRS = trigger_files.keys() - nirs_files.keys()

    print(missing_dotNIRS)

    print(f"DOT NIRS FILES IN DIRS: {len(nirs_files)}")
    print(f"TRIGGER TILES IN DIRS: {len(trigger_files)}")


    for participant, nirs_path in nirs_files.items():
        nirs_file = loadmat(nirs_path)
        stim_ch_len = nirs_file["s"].shape[0]

        try:
            new_stim_data = build_new_stim_array(trigger_files[participant], stim_ch_len)
        except KeyError:
            print(f"Key Error for {participant}: no trigger file found")
        if new_stim_data.any():
            if stim_ch_len == new_stim_data.shape[0]:
                nirs_file["s"] = new_stim_data
                # save_new_nirs(nirs_file, nirs_path, root_export_dir, participant)
        else:
            print("Something went wrong")
            print(participant)



if __name__ == "__main__":
    main()
