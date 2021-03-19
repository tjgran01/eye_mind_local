import zipfile
import os

def main():

    root_dir = "../data/zipped/"
    unzipped_dir = "../data/unzipped/"

    if not os.path.exists(unzipped_dir):
        os.mkdir(unzipped_dir)

    for zipfname in os.listdir(root_dir):
        with zipfile.ZipFile(f"{root_dir}{zipfname}", "r") as zip_r:
            print(f"Extracting {zipfname} to location: {unzipped_dir}{zipfname[:-4]}")
            zip_r.extractall(f"{unzipped_dir}{zipfname[:-4]}")




if __name__ == "__main__":
    main()
