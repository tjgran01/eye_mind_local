import pandas as pd
import os
import datetime
import csv

import shutil


def find_all_files_of_type(root, type):

    fpaths = {}
    for root, dirs, fnames in os.walk(root):
        for fname in fnames:
            if fname.endswith(type):
                full_path = os.path.join(root, fname)
                # Sets participant ID as key.
                fpaths[full_path.split("/")[2][:6]] = full_path

    return fpaths

def get_fnirs_time_data(fpath):

    f = open(fpath, "r")
    lines = f.readlines()
    sampling_rate = float(lines[6].split("=")[1])
    time = lines[3].split("=")[1]
    start_time = time.replace(" ", "T")
    start_time = start_time.strip()
    return [start_time, sampling_rate]


def convert_to_dt(m_str, ms=False):

    if not ms:
        conv_str = "%Y-%m-%dT%H:%M:%S"
    else:
        conv_str = "%Y-%m-%dT%H:%M:%S.%f"
    return datetime.datetime.strptime(m_str, conv_str)


def convert_from_dt(m_str, ms=False):

    conv_str = "%Y-%m-%dT%H:%M:%S.%f"
    return m_str.strftime(conv_str)


def convert_to_samples(start, total_start, s_rate):

    start = start + datetime.timedelta(hours=7)
    time_diff = start - total_start
    samples = round(time_diff.total_seconds() * s_rate)
    return samples


def create_export_file(id):

    with open(id, "w") as out_csv:
        writer = csv.writer(out_csv, delimiter=";")


def write_file_line(id, line):

    with open(id, "a") as out_csv:
        writer = csv.writer(out_csv, delimiter=";")

        writer.writerow(line)


def main():

    valid_shapes = ["Green_Tri", "Red_Tri", "Blue_Tri"
                    "Green_Circle", "Red_Circle", "Blue_Circle",
                    "Green_Square", "Red_Square", "Blue_Square"]

    key_map = {
               "WM_Low_AL_Low_VL_Low": 51,
               "WM_High_AL_Low_VL_Low": 52,
               "WM_Low_AL_High_VL_Low": 53,
               "WM_Low_AL_Low_VL_High": 54,
               "WM_High_AL_High_VL_Low": 55,
               "MW_High_AL_Low_VL_High": 56,
               "MW_Low_AL_High_VL_High": 57,
               "WM_High_AL_High_VL_High": 58
              }

    couldnt_find_header = []

    high_aud_load_strings = ["WM_Low_AL_High_VL_Low", "WM_High_AL_High_VL_Low",
                             "WM_Low_AL_High_VL_High", "WM_High_AL_High_VL_High"]

    epoch_subtract = 62135625600

    #### Get Bevhaioral Data

    root_data_dir = "../single/"
    valid_ids = check_for_user_data_dir(root_data_dir)
    data_dict = find_experimental_files(valid_ids, root_data_dir)

    #### Get fNIRS header files.

    header_files = find_all_files_of_type(root_data_dir, "config.hdr")

    for elm, val in data_dict.items():
        try:
            header = header_files[elm]
        except KeyError:
            couldnt_find_header.append(elm)
            continue

        fnirs_start, sampling_rate = get_fnirs_time_data(header)
        fnirs_start = convert_to_dt(fnirs_start, ms=True)

        print(fnirs_start)

        val[0] = make_block_column(val[0])

        group = val[0].groupby(["Block Number"])

        ex_fname = (f"{header_files[elm][:-10]}_new.tri")

        create_export_file(ex_fname)

        for g in group:

            first_shape = g[1][g[1]["Selected Shape"] != "ANY -- Target Audio Prompt"]
            first_shape = g[1][g[1]["Selected Shape"] != "ANY -- Distractor Audio Prompt"]
            first_row = first_shape.iloc[0]


            time_offset = 45.0 - first_row["Time Left"]
            condition = first_row["Block Condition"]
            event_time = first_row["Bin Chosen Timestamp"] - epoch_subtract
            dt_event_time = datetime.datetime.fromtimestamp(event_time)
            block_start_time = (dt_event_time - datetime.timedelta(seconds=time_offset))
            print(block_start_time)
            print(sampling_rate)
            block_start_time_str = convert_from_dt(block_start_time)
            num_samples = convert_to_samples(block_start_time, fnirs_start, sampling_rate)

            write_file_line(ex_fname, [block_start_time_str, num_samples, key_map[condition]])
            block_start_time = block_start_time + datetime.timedelta(seconds=45)
            block_start_time_str = convert_from_dt(block_start_time)
            num_samples = num_samples + round(45 * sampling_rate)
            write_file_line(ex_fname, [block_start_time_str, num_samples, 1])

    if couldnt_find_header:
        print(f"NO HEADER FILE FOR PARTICIPANT: {couldnt_find_header}")


if __name__ == "__main__":
    main()
