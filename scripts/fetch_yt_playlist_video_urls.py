import argparse
import subprocess
import json


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Extract video URLs from a YouTube playlist"
    )
    parser.add_argument("playlist", help="URL or ID of the YouTube playlist")
    return parser.parse_args()


def get_playlist_url(playlist):
    if "youtube.com" in playlist or "youtu.be" in playlist:
        return playlist
    return f"https://www.youtube.com/playlist?list={playlist}"


def extract_video_ids(playlist_url):
    result = subprocess.run(
        ["yt-dlp", "-j", "--flat-playlist", playlist_url],
        capture_output=True,
        text=True,
    )
    return [json.loads(line)["id"] for line in result.stdout.strip().split("\n")]


def generate_video_urls(video_ids):
    return [f"https://www.youtube.com/watch?v={video_id}" for video_id in video_ids]


def print_video_urls(video_urls):
    for index, url in enumerate(video_urls):
        print(f"{index + 1}\t{url}")


def main():
    args = parse_arguments()
    playlist_url = get_playlist_url(args.playlist)
    video_ids = extract_video_ids(playlist_url)
    video_urls = generate_video_urls(video_ids)
    print_video_urls(video_urls)


if __name__ == "__main__":
    main()
