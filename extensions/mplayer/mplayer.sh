#!/bin/sh
## See http://www.mplayerhq.hu/DOCS/tech/slave.txt for docs

## /mnt/us is the root directory when mounting the Kindle via USB
INSTALLDIR=/mnt/us/extensions/mplayer
MUSICDIR=/mnt/us/music
PLAYLIST="$INSTALLDIR/playlist"
VOLUME="$INSTALLDIR/volume"

## Value between -20 and 19, decrease in case of music lags
NICENESS="-10"

FIFO=/tmp/mplayer.fifo
#MPLAYER="nice -n$NICENESS $INSTALLDIR/mplayer -ao alsa -slave -quiet -input file=$FIFO -af volume=-15"
SHUF="$INSTALLDIR/shuf"
MPLAYER="nice -n$NICENESS $INSTALLDIR/mplayer -ao alsa -slave -quiet -input file=$FIFO"

if [ ! -e $FIFO ]; then
  mkfifo $FIFO
fi

if [ ! -f $VOLUME ]; then
    touch $VOLUME
    echo 40 > $VOLUME
fi

listmusic() {
    ## We can't allow non-valid file in the playlist because it would make prev behave weirdly
    find $MUSICDIR -type f -regex '.*\.\(3gp\|aac\|flac\|ogg\|m3u\|m4a\|mp3\|pls\|wav\|wma\)'
}

cmd() {
    if [ "x$(pidof mplayer)" = "x" ]; then
        return 1;
    fi
    echo "$@" > $FIFO
    return 0;
}

loadplaylist() {
    if ! cmd "loadlist $1"; then
        VOL=`cat $VOLUME`
        cmd "volume $VOL 1"
        nohup $MPLAYER -loop 0 -playlist $1 >/dev/null 2>&1 &
    fi
}

vol() {
    VOL=`cat $VOLUME`
    VOL=$((VOL))
	case "$1" in
		up)
		    if [ $VOL -lt 100 ]; then
			VOL=$((VOL+10))
		    fi
		;;
		dn)
		    if [ $VOL -gt 10 ]; then
			VOL=$((VOL-10))
		    fi
		;;
	esac
	echo $VOL > $VOLUME
	cmd "volume $VOL 1"
}

case "$1" in
    playall)
        listmusic > /tmp/mplayer.playlist
        loadplaylist /tmp/mplayer.playlist
        ;;
    playrand)
        listmusic | $SHUF > /tmp/mplayer.playlist
        loadplaylist /tmp/mplayer.playlist
        ;;
    playlist)
        loadplaylist $2
        ;;
    pause)
        cmd "pause"
        ;;
    stop)
	    killall mplayer
        ;;
    prev)
        cmd "pt_step -1"
        ;;
    next)
        cmd "pt_step 1"
        ;;
    volup)
	vol up
	;;
    voldn)
	vol dn
	;;
    mute)
	cmd "mute"
	;;
    *)
        echo "Usage: $0 {playall|playrand|playlist|pause|stop|prev|next|volup|voldn|mute}"
        exit 1
        ;;
esac

exit 0
