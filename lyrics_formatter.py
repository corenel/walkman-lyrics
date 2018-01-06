import argparse
import os
from utils import format_lyrics

def qprint(*args, **kwargs):
    global argsp
    if not argsp.quiet:
        print(*args, **kwargs)


def parse_args():
    # arguments parser
    args = argparse.ArgumentParser()
    args.add_argument('lrc_path', help='Path to lyrics folder')
    args.add_argument(
        '-q',
        '--quiet',
        help='Quiet mode, no prompt output and choose first search result.',
        action='store_true')
    args.add_argument(
        "--output",
        type=str,
        default="formatted",
        help="Path to store formatted lyrics files")
    return args.parse_args()


if __name__ == '__main__':
    argsp = parse_args()

    # list all music files
    LRC_LIST = [l for l in os.listdir(argsp.lrc_path) if os.path.splitext(l)[1] == '.lrc']
    LRC_OUTPATH = os.path.join(argsp.lrc_path, argsp.output)
    if not os.path.exists(LRC_OUTPATH):
        os.makedirs(LRC_OUTPATH)

    # get lyrics
    for idx, lrc_file in enumerate(LRC_LIST):
        qprint('======== ' + str(idx / len(LRC_LIST) * 100) + '% ========')
        qprint(lrc_file)
        formatted = format_lyrics(os.path.join(argsp.lrc_path, lrc_file))
        outpath = os.path.join(LRC_OUTPATH, lrc_file)
        with open(outpath, 'w') as f:
            f.write('\n'.join(formatted))
        qprint('save formatted lyrics to {}'.format(outpath))

    print('======== Done! ========')
