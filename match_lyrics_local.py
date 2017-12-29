import argparse
from utils import *


def qprint(*args, **kwargs):
    global argsp
    if not argsp.quiet:
        print(*args, **kwargs)


def parse_args():
    # arguments parser
    args = argparse.ArgumentParser()
    args.add_argument('path', help='Root path for Walkman')
    args.add_argument('-q', '--quiet',
                      help='Quiet mode, no prompt output and choose first search result by default.',
                      action='store_true')
    args.add_argument('-d', '--default',
                      help='Choose first search result by default.',
                      action='store_true')
    args.add_argument('-w', '--overwrite',
                      help='Overwrite existed lyrics',
                      action='store_true')
    return args.parse_args()


if __name__ == '__main__':
    argsp = parse_args()
    argsp.default |= argsp.quiet

    # list all music files
    file_list = get_file_list(argsp.path)

    # get lyrics
    for num, song in enumerate(file_list):
        qprint('======== ' + str(num / len(file_list) * 100) + '% ========')
        if has_lyrics(song) and not argsp.overwrite:
            qprint("Lyrics already exists for '%s'" % song['title'])
        else:
            # qprint(song['title'])
            lyrics = get_lyrics(qprint,
                                song_title=song['title'],
                                song_artist=song['artist'],
                                song_default=argsp.default,
                                lyric_mode=argsp.mode,
                                lyric_format=argsp.format,
                                verbose=not argsp.quiet)
            write_lyrics(song, lyrics)
            sleep(0.1)

    print('======== Done! ========')

