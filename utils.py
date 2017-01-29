import requests
import re
import json
import datetime
from os import listdir, walk, path
from tinytag import TinyTag
from collections import defaultdict


def getFileList(fileDir):
    fileFormat = ['.m4a', '.mp3']
    fileList = []
    if path.exists(fileDir):
        for root, subFolders, fileNames in walk(fileDir):
            fileNames = [x for x in fileNames
                         if path.splitext(x)[1] in fileFormat]
            if (fileNames):
                for fileName in fileNames:
                    try:
                        tags = TinyTag.get(path.join(root, fileName))
                        fileList.append({
                            'path': root,
                            'name': fileName,
                            'title': tags.title or path.splitext(fileName)[0],
                            'artist': tags.artist or ''
                        })
                    except:
                        print(fileName)
                        fileList.append({
                            'path': root,
                            'name': fileName,
                            'title': path.splitext(fileName)[0],
                            'artist': ''
                        })

        return fileList
    else:
        print('Error: target directory not exists')
        exit()


def getLyrics(qprint, songTitle='', songArtist='', songDefault=False,
              lyricMode='both', lyricFormat='{orig} / {trans}', verbose=False):
    # requests settings
    search = 'http://music.163.com/api/search/get/web'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36',
               'Referer': 'http://music.163.com/search/'}
    # get song id
    if isSimpleTitle(songTitle):
        searchTitle = ' '.join([songTitle, songArtist])
    else:
        searchTitle = songTitle
    with requests.Session() as session:
        session.headers.update(headers)
        qprint('Searching: %s' % ' - '.join([songTitle, songArtist]))
        res = session.post(search, data={
            's': searchTitle,
            'type': 1,
            'offset': 0,
            'limit': 10
        }).json()
    songs = res.get('result', {}).get('songs', '')
    if len(songs) == 0:
        qprint('No result found for \'%s\'.' % songTitle)
        return ''
    elif len(songs) == 1 or (songDefault and not isSimpleTitle(songTitle)):
        song = songs[0]['id']
        sid = 0
    else:
        qprint('Choose a song to download lyrics, or -1 to exit.\n')
        for i, s in enumerate(songs):
            qprint('%-5s\x1b[1m%s\x1b[0m \x1b[2m(%d)\x1b[0m' % ('%s.' % i, s['name'], s['id']))
            qprint('     \x1b[0m%s | \x1b[3m%s\x1b[0m' %
                   ('; '.join([j['name'] for j in s['artists']]), s['album']['name']))
            qprint()
        sid = input('Song ID: ')
        while not sid.isdecimal() or int(sid) < 0 or int(sid) >= len(songs):
            if sid == '-1':
                return ''
            if sid == '':
                sid = 0
                break
            qprint('%s is invalid. Please enter a integer between 0 and %s.' % (sid, len(songs)))
            sid = input('Song ID: ')
        sid = int(sid)
        song = songs[int(sid)]['id']

    # get song info
    songinfo = [songs[sid]['name'], '; '.join([j['name'] for j in songs[sid]['artists']]), songs[sid]['album']['name']]
    songstr = '     \x1b[1m%s\x1b[0m \x1b[2m(%d)\x1b[0m\n' % (songinfo[0], songs[sid]['id'])
    songstr += '     \x1b[0m%s | \x1b[3m%s\x1b[0m\n' % (songinfo[1], songinfo[2])
    qprint()
    qprint('Trying to download lyrics for song %s:' % song)
    qprint(songstr)

    # get lyrics
    with requests.Session() as session:
        session.headers.update(headers)
        try:
            req = session.get('http://music.163.com/api/song/lyric?lv=1&kv=1&tv=-1&id=%s' % song).json()
        except:
            print(session.get('http://music.163.com/api/song/lyric?lv=1&kv=1&tv=-1&id=%s' % song))
            req = {}
    if req.get('lrc', None) is None or req['lrc'].get('lyric', None) is None:
        qprint('No lyrics found.')
        return ''

    # lyric mode
    has_trans = True
    if lyricMode in ['trans', 'both']:
        if req.get('tlyric', None) is None or req['tlyric'].get('lyric', None) is None:
            qprint('No translation found, fallback to original lyrics.')
            has_trans = False
            lyricMode = 'original'
    else:
        has_trans = False

    # reformat lyrics
    org = defaultdict(str)
    trans = defaultdict(str)
    r = re.compile(r'\[(?P<tag>[0-9:.\]\[]+)\](?P<lrc>.*)')
    for i in req['lrc']['lyric'].split('\n'):
        rm = r.match(i)
        if not rm:
            continue
        ln = rm.groupdict()
        for j in ln['tag'].split(']['):
            org[formatTimestamp(j)] = ln['lrc'].strip()
    if has_trans:
        for i in req['tlyric']['lyric'].split('\n'):
            rm = r.match(i)
            if not rm:
                continue
            ln = rm.groupdict()
            for j in ln['tag'].split(']['):
                trans[formatTimestamp(j)] = ln['lrc'].strip()
    out = []
    for i in sorted(org):
        if lyricMode == 'original' or not trans[i].strip() or trans[i].strip() == org[i].strip():
            line = ['[{tag}]{orig}']
        elif lyricMode == 'trans' or not org[i].strip():
            line = ['[{tag}]{trans}']
        elif lyricMode == 'both':
            line = ['[{tag}]' + i for i in lyricFormat.split('\n')]
        for l in line:
            out.append(l.format(tag=i, orig=org[i], trans=trans[i]))
    return out


def writeLyrics(song, lyrics):
    if lyrics:
        lyricsFile = path.join(song['path'],
                               path.splitext(song['name'])[0]) + '.lrc'
        with open(lyricsFile, 'w') as of:
            of.write('\n'.join(lyrics))
    else:
        pass


def hasLyrics(song):
    lyricsFile = path.join(song['path'],
                           path.splitext(song['name'])[0]) + '.lrc'
    return path.exists(lyricsFile)


def formatTimestamp(timestamp):
    # format timestamp xx:xx.xxx as xx:xx.xx
    if (re.findall('\d+:\d+\.\d\d\d', timestamp) != []):
        timestamp = re.findall('\d+:\d+\.\d\d\d', timestamp)[0]
        tsp = timestamp.split(':')
        return '%s:%05.2f' % (tsp[0], float(tsp[1]))
    elif (re.findall('\d+:\d+\.\d\d', timestamp) == []):
        # print(timestamp)
        pass
    return timestamp


def isSimpleTitle(title):
    return len(title.encode('utf-8')) <= 12
