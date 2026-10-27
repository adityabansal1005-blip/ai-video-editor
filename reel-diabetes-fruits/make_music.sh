#!/usr/bin/env bash
# Regenerates assets/music.wav: a calm C-Am-F-G pad, 4 s per chord, looped to 66 s.
set -euo pipefail
cd "$(dirname "$0")/assets"
chord(){ ffmpeg -v error -y -f lavfi -i "sine=f=$1:d=4" -f lavfi -i "sine=f=$2:d=4" -f lavfi -i "sine=f=$3:d=4" -f lavfi -i "sine=f=$4:d=4" -filter_complex "amix=inputs=4:normalize=1,afade=t=in:d=0.6,afade=t=out:st=3.2:d=0.8" -ar 48000 "$5"; }
chord 130.81 261.63 329.63 392.00 c1.wav
chord 110.00 220.00 261.63 329.63 c2.wav
chord 87.31 174.61 220.00 261.63 c3.wav
chord 98.00 196.00 246.94 293.66 c4.wav
printf "file c1.wav\nfile c2.wav\nfile c3.wav\nfile c4.wav\n" > chords.txt
ffmpeg -v error -y -f concat -i chords.txt -c copy loop16.wav
ffmpeg -v error -y -stream_loop 4 -i loop16.wav -t 66 -af "tremolo=f=0.25:d=0.25,lowpass=f=1400,aecho=0.8:0.6:180|340:0.25|0.15,afade=t=in:d=2,afade=t=out:st=63:d=3,volume=0.9" -ar 48000 -ac 2 music.wav
rm c1.wav c2.wav c3.wav c4.wav chords.txt loop16.wav
echo "wrote assets/music.wav"
