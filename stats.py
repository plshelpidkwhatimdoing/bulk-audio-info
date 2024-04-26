import os
import subprocess
import json
import toml
import yaml
import argparse
import datetime

def bytes_to_kilobytes(bytes_value):
    kilobytes = bytes_value / 1000
    return kilobytes

def format_duration(duration_in_seconds):
    minutes, seconds = divmod(duration_in_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    milliseconds = int((duration_in_seconds - int(duration_in_seconds)) * 1000)
    return "{:02d}:{:02d}:{:02d}:{:03d}".format(int(hours), int(minutes), int(seconds), milliseconds)

def get_audio_info(file_path):
    ffprobe_cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', file_path]
    result = subprocess.run(ffprobe_cmd, capture_output=True, text=True)
    if result.returncode == 0:
        info = json.loads(result.stdout)['format']
        bitrate_bytes = int(info.get('bit_rate', 0))
        bitrate_kilobytes = bytes_to_kilobytes(bitrate_bytes)
        info['bit_rate_kbps'] = f"{bitrate_kilobytes} kb/s"
        info['bitrate_bytes'] = f"{int(info.get('bit_rate', 0))} bytes/s"
        info['mindur'] = format_duration(float(info.get('duration')))
        return info
    else:
        return None

def main():
    parser = argparse.ArgumentParser(description="Get audio file information.")
    parser.add_argument("-j", "--json", action="store_true", help="Output in JSON format")
    parser.add_argument("-t", "--toml", action="store_true", help="Output in TOML format")
    parser.add_argument("-y", "--yaml", action="store_true", help="Output in YAML format")
    args = parser.parse_args()

    current_dir = os.getcwd()
    audio_files = [f for f in os.listdir(current_dir) if f.endswith(('.mp3', '.wav', '.flac', '.ogg', '.opus', '.m4a'))]

    audio_info = {}
    for file in audio_files:
        file_path = os.path.join(current_dir, file)
        info = get_audio_info(file_path)
        if info:
            audio_info[file] = {
                'exact_bitrate': info.get('bitrate_bytes', ''),
                'bitrate': info.get('bit_rate_kbps', ''),
                'format_name': info.get('format_name', ''),
                'exact_length': info.get('duration', ''),
                'length': info.get('mindur')
            }

    if args.json:
        print(json.dumps(audio_info, indent=4))
    elif args.yaml:
        print(yaml.dump(audio_info, default_flow_style=False))
    else:
        print(toml.dumps(audio_info))
        #to change default output just swap this one out

if __name__ == "__main__":
    main()
