import argparse
import os
from utils import (get_file_list, has_lyrics, match_lyrics,
                   copy_lyrics)


def qprint(*args, **kwargs):
    global argsp
    if not argsp.quiet:
        print(*args, **kwargs)


def parse_args():
    # arguments parser
    args = argparse.ArgumentParser()
    args.add_argument('music_path', help='Path to MUSIC folder of Walkman')
    args.add_argument('lrc_path', help='Path to lyrics folder')
    args.add_argument(
        '-q',
        '--quiet',
        help='Quiet mode, no prompt output and choose first search result.',
        action='store_true')
    args.add_argument(
        '-d',
        '--default',
        help='Choose first match result by default.',
        action='store_true')
    args.add_argument(
        '-w',
        '--overwrite',
        help='Overwrite existed lyrics',
        action='store_true')
    return args.parse_args()


if __name__ == '__main__':
    argsp = parse_args()
    argsp.default |= argsp.quiet

    # list all music files
    SONG_LIST = get_file_list(argsp.music_path)
    LRC_LIST = os.listdir(argsp.lrc_path)

    # get lyrics
    for num, song in enumerate(SONG_LIST):
        qprint('======== ' + str(num / len(SONG_LIST) * 100) + '% ========')
        if has_lyrics(song) and not argsp.overwrite:
            qprint("Lyrics already exists for '%s'" % song['title'])
        else:
            qprint(song['title'])
            lrc_file = match_lyrics(song['title'], song['artist'], LRC_LIST)
            if lrc_file:
                copy_lyrics(song, os.path.join(argsp.lrc_path, lrc_file))

    print('======== Done! ========')
