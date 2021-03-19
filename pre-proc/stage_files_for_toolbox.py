import os
import shutil

import pandas as pd
import subprocess

from pathlib import Path

def clean_df_of_sketchy_sessions(df):

    # Only move files whose triggers are all there for localizer.
    # Drop any row where a file is missing.
    df.dropna(inplace=True)
    # Drop any row where triggers are missing FOR LOCALIZER.
    df[["is_missing", "junk"]] = df["Trigger Notes"].str.split(":", expand=True)
    df = df[df["is_missing"] != "Missing"]
    df.drop(["is_missing", "junk"], axis=1, inplace=True)

    df.reset_index(inplace=True)

    return df


def main():

    _this_fpath = os.path.dirname(os.path.realpath(__file__))
    ROOT_DIR = Path(f"{_this_fpath}/../data/unzipped/")
    STAGING_DIR = Path(f"{_this_fpath}/../data/toolbox_staging/")

    # If data state table not created, run it.
    if not os.path.exists(f"{_this_fpath}/../data/data_summaries/eml_summary_nirs.csv"):
        subprocess.call(['python', 'create_data_state_table.py'])

    df = pd.read_csv(f"{_this_fpath}/../data/data_summaries/eml_summary_nirs.csv")
    df = clean_df_of_sketchy_sessions(df)

    for row in df.iterrows():
        print(f"Moving NIRS files from: {row[1]['nirs_dir']}, to: {STAGING_DIR}/{row[1]['participant']}/")
        shutil.copytree(Path(row[1]["nirs_dir"][2:-2]), f"{STAGING_DIR}/{row[1]['participant']}/")


if __name__ == "__main__":
    main()
