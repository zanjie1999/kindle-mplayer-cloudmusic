# -*- encoding:utf-8 -*-

# 网易云音乐 mplayer playlist生成器
# 版本: 7.0
import platform
import sys
import codecs
import hashlib
import json
import os
import urllib.request, urllib.parse, urllib.error
import gzip
import signal
from sys import argv
from io import StringIO


if len(argv) < 2:
    print("请传入歌单id")
    sys.exit()

# 歌单id设置 设置为 argv[1] 将使用 " python make_lrc_music_m3u.py 歌单id " 这种方式传入
playlistId = argv[1]

# 播放列表存放位置
playlistName = '/mnt/us/extensions/mplayer/playlist/' + playlistId + ".playlist"

# Ctrl + C 退出
def signal_handler(signal, frame):
   print('Ctrl + C, exit now...')
   sys.exit(1)

signal.signal(signal.SIGINT, signal_handler)

# 加载头部 防ban
opener = urllib.request.build_opener()
opener.addheaders = [
    ('Host', 'music.163.com'),
    ('Connection', 'keep-alive'),
    ('Cache-Control', 'max-age=0'),
    ('Upgrade-Insecure-Requests', '1'),
    ('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'),
    ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'),
    ('Accept-Encoding', 'gzip, deflate'),
    ('Accept-Language', 'zh-CN,zh-TW;q=0.9,zh;q=0.8,en-GB;q=0.7,en;q=0.6')
]
urllib.request.install_opener(opener)


# 发送请求
def urlGetJsonLoad(url):
    """ 发送请求并解析json
    """

    gzdata = ''
    try:
        gzdata = urllib.request.urlopen(url)
    except Exception as e:
        print('connect error: ', url)
        return {'code': ''}
    try:
        if gzdata.info().get('Content-Encoding') == 'gzip':
            gziper = gzip.GzipFile(fileobj=gzdata)
            return json.loads(gziper.read().decode('utf-8'))
        else:
            return json.loads(gzdata.read().decode('utf-8'))
    except Exception as e:
        print('decode error: ', url)
        return {'code': ''}


# 写出文件
def writeToFile(name, text):
    try:
        print('Write to file: ' + name)
    except:
        print('Write to file: ')
    try:
        file = codecs.open(name, "w", "utf-8")
        file.write(text)
        file.close()
    except:
        print('error')


# 生成播放列表
playlistText = ""
def addPlaylist(id):
    global playlistText
    playlistText += "http://music.163.com/song/media/outer/url?id=" + str(id) + ".mp3\n"


# 获取歌单
url = 'http://music.163.com/api/playlist/detail?id=' + playlistId
dataL = urlGetJsonLoad(url)
if dataL['code'] != 200:
    ecode = str(dataL['code'])
    print('errorCode: ' + ecode)
else:
    # 循环歌单
    for tracks in dataL['result']['tracks']:
        addPlaylist(tracks['id'])

    # 写播放列表文件
    writeToFile(playlistName, playlistText)

if len(argv) > 2:
    # 使用mplayer播放
    os.system("/mnt/us/extensions/mplayer/mplayer.sh playlist " + playlistName)
