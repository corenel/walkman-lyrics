"""Copy music file and lyrics by playlist."""

import argparse
import os
import shutil


def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(
        description="Script to copy music file and lyrics by playlist.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("filepath", help="path for playlist file",
                        type=str, default=None)
    parser.add_argument("-o", "--output", help="path for output folder",
                        type=str, default=".")
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    # reaf playlist
    with open(args.filepath, "r") as f:
        filelist = f.readlines()
    root = os.path.normpath(os.path.join(os.path.dirname(args.filepath), ".."))
    filelist = [os.path.join(root, "/".join(item.strip().split("\\")[1:]))
                for item in filelist]

    # check output directory
    if not os.path.exists(args.output):
        os.makedirs(args.output)

    # copy musci and lyrics file
    for item in filelist:
        if os.path.exists(item):
            shutil.copy(item, args.output)
            print("copy {} to {}".format(item, args.output))
        lrc = os.path.splitext(item)[0] + '.lrc'
        if os.path.exists(lrc):
            shutil.copy(lrc, args.output)
            print("copy {} to {}".format(lrc, args.output))
