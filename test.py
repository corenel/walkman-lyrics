import argparse
from utils import *
from time import sleep


def qprint(*args, **kwargs):
    global argsp
    if not argsp.quiet:
        print(*args, **kwargs)


if __name__ == '__main__':
    # arguments parser
    args = argparse.ArgumentParser()
    args.add_argument('path', help='Root path for Walkman')
    args.add_argument('-m', '--mode',
                      help='Mode of LRC file',
                      choices=['trans', 'original', 'both'],
                      default='both')
    args.add_argument('-f', '--format',
                      help='Format to combine both types of lyrics\n'
                           'Default: \'{orig} / {trans}\'',
                      default='{orig} / {trans}')
    args.add_argument('-q', '--quiet',
                      help='Quiet mode, no prompt output and choose first search result by default.',
                      action='store_true')
    args.add_argument('-d', '--default',
                      help='Choose first search result by default.',
                      action='store_true')
    args.add_argument('-w', '--overwrite',
                      help='Overwrite existed lyrics',
                      action='store_true')
    argsp = args.parse_args()
    argsp.default |= argsp.quiet

    # list all music files
    fileList = get_file_list(argsp.path)

    # get lyrics
    for num, song in enumerate(fileList):
        qprint('======== ' + str(num / len(fileList) * 100) + '% ========')
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
