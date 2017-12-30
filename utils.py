import requests
import re
import json
import datetime
import shutil
from os import listdir, walk, path
from tinytag import TinyTag
from collections import defaultdict
from fuzzywuzzy import process


def get_file_list(file_dir, file_format=['.m4a', '.mp3']):
    file_list = []
    if path.exists(file_dir):
        for root, sub_dir, file_names in walk(file_dir):
            file_names = [x for x in file_names
                          if path.splitext(x)[1] in file_format and path.splitext(x)[0][0] != '.']
            if (file_names):
                for file_name in file_names:
                    try:
                        tags = TinyTag.get(path.join(root, file_name))
                        file_list.append({
                            'path': root,
                            'name': file_name,
                            'title': tags.title or path.splitext(file_name)[0],
                            'artist': tags.artist or ''
                        })
                    except:
                        print(file_name)
                        file_list.append({
                            'path': root,
                            'name': file_name,
                            'title': path.splitext(file_name)[0],
                            'artist': ''
                        })

        return file_list
    else:
        print('Error: target directory not exists')
        exit()


def get_lyrics(qprint, song_title='', song_artist='', song_default=False,
               lyric_mode='both', lyric_format='{orig} / {trans}', verbose=False):
    # requests settings
    search_song = 'http://music.163.com/api/search/get/web'
    search_lrc = 'http://music.163.com/api/song/lyric?lv=1&kv=1&tv=-1&id=%s'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36',
               'Referer': 'http://music.163.com/search/'}
    # get song id
    if is_simple_title(song_title):
        searchTitle = ' '.join([song_title, song_artist])
    else:
        searchTitle = song_title
    with requests.Session() as session:
        session.headers.update(headers)
        qprint('Searching: %s' % ' - '.join([song_title, song_artist]))
        res = session.post(search_song, data={
            's': searchTitle,
            'type': 1,
            'offset': 0,
            'limit': 10
        }).json()
    songs = res.get('result', {}).get('songs', '')
    if len(songs) == 0:
        qprint('No result found for \'%s\'.' % song_title)
        return ''
    elif len(songs) == 1 or not verbose or (song_default and not is_simple_title(song_title)):
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
            req = session.get(search_lrc % song).json()
        except:
            print(session.get(search_lrc % song))
            req = {}
    if req.get('lrc', None) is None or req['lrc'].get('lyric', None) is None:
        qprint('No lyrics found.')
        return ''

    # lyric mode
    has_trans = True
    if lyric_mode in ['trans', 'both']:
        if req.get('tlyric', None) is None or req['tlyric'].get('lyric', None) is None:
            qprint('No translation found, fallback to original lyrics.')
            has_trans = False
            lyric_mode = 'original'
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
            org[format_timestamp(j)] = ln['lrc'].strip()
    if has_trans:
        for i in req['tlyric']['lyric'].split('\n'):
            rm = r.match(i)
            if not rm:
                continue
            ln = rm.groupdict()
            for j in ln['tag'].split(']['):
                trans[format_timestamp(j)] = ln['lrc'].strip()
    out = []
    for i in sorted(org):
        if lyric_mode == 'original' or not trans[i].strip() or trans[i].strip() == org[i].strip():
            line = ['[{tag}]{orig}']
        elif lyric_mode == 'trans' or not org[i].strip():
            line = ['[{tag}]{trans}']
        elif lyric_mode == 'both':
            line = ['[{tag}]' + i for i in lyric_format.split('\n')]
        for l in line:
            out.append(l.format(tag=i, orig=org[i], trans=trans[i]))
    return out


def write_lyrics(song, lyrics):
    if lyrics:
        lyricsFile = path.join(song['path'],
                               path.splitext(song['name'])[0]) + '.lrc'
        with open(lyricsFile, 'w') as of:
            of.write('\n'.join(lyrics))
    else:
        pass

def copy_lyrics(song, lrc_src):
    lrc_dst = path.join(song['path'],
                        path.splitext(song['name'])[0]) + '.lrc'
    shutil.copy(lrc_src, lrc_dst)
    print('copy {} to {}'.format(lrc_src, lrc_dst))

def has_lyrics(song):
    lyricsFile = path.join(song['path'],
                           path.splitext(song['name'])[0]) + '.lrc'
    return path.exists(lyricsFile)


def format_timestamp(timestamp):
    # format timestamp xx:xx.xxx as xx:xx.xx
    if (re.findall('\d+:\d+\.\d\d\d', timestamp) != []):
        timestamp = re.findall('\d+:\d+\.\d\d\d', timestamp)[0]
        tsp = timestamp.split(':')
        return '%s:%05.2f' % (tsp[0], float(tsp[1]))
    elif (re.findall('\d+:\d+\.\d\d', timestamp) == []):
        # print(timestamp)
        pass
    return timestamp


def is_simple_title(title):
    return len(title.encode('utf-8')) <= 12


def match_lyrics(title, artist, lrc_list, ths=80):
    res = process.extractOne("{} - {}.lrc".format(title, artist), lrc_list)
    print(res)
    lrc_file = res[0] if res is not None and res[1] >= ths else None
    return lrc_file
