#!/usr/bin/env python3
"""Generates VLC playlist for tape recording based on input with total duration checks"""
# pylint: disable=import-error,line-too-long
import argparse
import logging
import pathlib
import sys
from glob import glob
from os import path

import xspf_lib as xspf
from mutagen.flac import FLAC
from mutagen.mp3 import MP3


def process_track(args, side, audio):
    """Process track and return xspf.Track list"""
    result = []
    track_number = audio.get("tracknumber", ["-"])[0]
    track_title = audio.get("title", [pathlib.Path(audio.filename).stem])[0]
    if args.debug:
        print(f"{side:<10}{track_number:<5}{track_title:<60}{audio.info.length / 60:.0f}m{audio.info.length % 60:.0f}s")
    result.append(xspf.Track(location=audio.filename, title=track_title, duration=audio.info.length))
    if args.pause > 0:  # if pause enabled, add it between tracks
        result.append(xspf.Track(location=f"vlc://pause:{args.pause}", title=f"----------pause {args.pause}s----------", duration=args.pause))
    return result


def process_playlist(args, title, tracks, playlist_file):
    """Create and save playlist from track list"""
    playlist = xspf.Playlist(title=title, trackList=tracks)
    playlist.write(playlist_file)
    duration = sum(i.duration for i in tracks)
    print(
        f"""---
{title} playlist generated at: '{playlist_file}'
Tracks count: {len(tracks)/2 if args.pause > 0 else len(tracks)}, Duration: {duration / 60:.0f}m{duration % 60:.0f}s"""
    )


def main():
    """main handler"""
    logging.basicConfig(format="%(asctime)s %(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--album", help="Path to album")
    parser.add_argument("-f", "--format", default="mp3", help="Album format, mp3/flac supported")
    parser.add_argument("-l", "--length", default=90, help="Tape length, total minutes", type=int)
    parser.add_argument("-p", "--pause", default=2, help="Pause duration between tracks", type=int)
    parser.add_argument("-d", "--debug", action=argparse.BooleanOptionalAction, help="Output debug information")
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 0.1")
    args = parser.parse_args()
    logging.warning("Starting with parameters: %s", args)

    if not args.album:
        logging.error("Please provide path to album in cmdline, exit...")
        sys.exit(1)

    # get sorted list of files from album directory
    files = sorted(glob(path.join(args.album, f"*.{args.format}")))
    if not files:
        logging.error(
            "No media found in folder '%s' with '%s' format, exit...",
            args.album,
            args.format,
        )
        sys.exit(1)

    # estimate duration and create xspf playlists per cassette side (A/B)
    duration = 0
    tracks_a = []
    tracks_b = []
    for file in files:
        if args.format == "mp3":
            audio = MP3(file)
        elif args.format == "flac":
            audio = FLAC(file)
        else:
            logging.error("Unsupported format: %s, exit...", args.format)
            sys.exit(1)

        duration += audio.info.length
        if duration < args.length * 60 / 2:  # Until total duration less than 1/2 of tape length, add them to Side A
            tracks_a.extend(process_track(args, "Side A", audio))
        elif duration < args.length * 60:  # Add next tracks to Side B until tape length
            tracks_b.extend(process_track(args, "Side B", audio))
        else:
            logging.error("Tracks duration: %.0d min is longer than tape length: %.0d min, exit...", duration / 60, args.length)
            sys.exit(1)

    process_playlist(args, "Side A", tracks_a, path.join(args.album, "Side A.xspf"))
    if tracks_b:  # if there're enough tracks for side B
        process_playlist(args, "Side B", tracks_a, path.join(args.album, "Side B.xspf"))


if __name__ == "__main__":
    main()
