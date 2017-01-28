import argparse
from utils import *


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
                      help='Quiet mode, no prompt output to STDOUT, choose first search result by default.',
                      action='store_true')
    args.add_argument('-d', '--default',
                      help='Choose first search result by default.',
                      action='store_true')
    args.add_argument('-o', '--overwrite',
                      help='Overwrite existed lyrics',
                      action='store_true')
    argsp = args.parse_args()
    argsp.default |= argsp.quiet

    # list all music files
    fileList = getFileList(argsp.path)

    # get lyrics
    for song in fileList:
        if hasLyrics(song) and not argsp.overwrite:
            qprint("Lyrics already exists for '%s'" % song['title'])
        else:
            qprint(song['title'])
            # lyric = getLyrics(songTitle=song['title'],
            #                          songDefault=argsp.default,
            #                          lyricMode=argsp.mode,
            #                          verbose=not argsp.quiet)
            # writeLyrics(filePath=song['path'],
            #             fileName=song['name'],
            #             lyrics="aaaaa")
    qprint('Done!')
