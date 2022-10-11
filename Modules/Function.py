import os
import re
import subprocess
import time

ffmpeg = ".\\bin\\ffmpeg.exe -i "


def mkdir(path):
    # mkdir 路径不存在会创建最低级路径
    # makedirs 路径不存在会创建多级完整路径
    if not os.path.exists(path):
        os.makedirs(path)


def parse_export_confing(stream_list, audio_radio, auto_aac):
    if stream_list is None:
        return "", ""
    selected_streams = [(item.data()) for item in stream_list.selectedIndexes()]
    if len(selected_streams) < 1:
        return "", ""
    default_recode_list = [': Audio: truehd', ': Audio: dts', ': Audio: flac', ': Audio: opus']
    stream_confing = ""
    audio_config = ""
    audio_index = 0
    hdmv_pgs_subtitle = False
    for item in selected_streams:
        # print(item)
        # Stream #0:0: Video: hevc (Main 10)
        # Stream #0:1(eng): Audio: truehd
        stream_confing += " -map " + re.findall(r"Stream #(\d+:\d+)[:([]", item)[0]
        if ": Audio:" in item:
            if audio_radio == 0:
                continue
            elif audio_radio == 1 and any(key in item for key in default_recode_list):
                if auto_aac and ", 7.1," in item:
                    audio_config += " -c:a:" + str(audio_index) + " aac"
                else:
                    audio_config += " -c:a:" + str(audio_index) + " ac3"
            elif audio_radio == 2:
                if auto_aac and ", 7.1," in item:
                    audio_config += " -c:a:" + str(audio_index) + " aac"
                else:
                    audio_config += " -c:a:" + str(audio_index) + " ac3"
            audio_index += 1
        elif ": Subtitle: hdmv_pgs_subtitle" in item:
            hdmv_pgs_subtitle = True

    print(stream_confing, audio_config)

    if hdmv_pgs_subtitle:
        return "", ""
    return stream_confing, audio_config


def parse_export_srt_confing(stream_list):
    if stream_list is None:
        return ""
    selected_streams = [(item.data()) for item in stream_list.selectedIndexes()]
    if len(selected_streams) != 1:
        return ""

    stream_confing = ""
    # Stream #0:2(eng): Subtitle: subrip (default)
    if ": Subtitle: subrip" in selected_streams[0]:
        stream_confing = " -map " + re.findall(r"Stream #(\d+:\d+)[:([]", selected_streams[0])[0]
    return stream_confing


def get_mp4_name(path):
    return (get_file_name(path) + "_remux.mp4") if path else ""


def get_srt_name(path):
    return (get_file_name(path) + "_remux.srt") if path else ""


def get_file_name(path):
    base_name = os.path.split(path)[1] if path else ""
    base_name = os.path.splitext(base_name)[0] if base_name else ""
    return base_name


def get_file_ext(path):
    return os.path.splitext(path)[1] if path else ""


def export_batch(mkv_path, export_dir, stream_config, audio_config):
    mkv_dir = os.path.dirname(mkv_path)
    video_ext = get_file_ext(mkv_path)
    # print(mkv_dir, mkv_name, video_ext)
    for item in os.listdir(mkv_dir):
        if item.endswith(video_ext):
            # print(item)
            mp4_name = get_mp4_name(item)
            await_exe_cmd(ffmpeg + format_path_quotes(mkv_dir + os.sep + item)
                          + stream_config + " -c:v copy -c:a copy -c:s mov_text" + audio_config + " " +
                          format_path_quotes(export_dir + os.sep + mp4_name))


def export_srt_batch(mkv_path, export_dir, stream_config):
    mkv_dir = os.path.dirname(mkv_path)
    video_ext = get_file_ext(mkv_path)
    # print(mkv_dir, mkv_name, video_ext)
    for item in os.listdir(mkv_dir):
        if item.endswith(video_ext):
            # print(item)
            srt_name = get_srt_name(item)
            await_exe_cmd(ffmpeg + format_path_quotes(mkv_dir + os.sep + item)
                          + stream_config + " " +
                          format_path_quotes(export_dir + os.sep + srt_name))


def await_exe_cmd(cmd):
    print("cmd:", cmd)
    proc = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
    while proc.poll() is None:
        # 等待执行完毕
        # print(proc.poll())
        time.sleep(1)


def exe_cmd(cmd):
    print("cmd:", cmd)
    subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)


def get_cmd_result(cmd):
    print("cmd:", cmd)
    # 标准输出和错误输出合并，只需要将stderr参数设置为subprocess.STDOUT：
    # 需设置encoding，默认为byte数组
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8")
    res = proc.stdout.readlines()
    proc.stdout.close()
    return res


def read_stream_info(path):
    res_arr = get_cmd_result(ffmpeg + format_path_quotes(path))
    stream_info = []
    for line in res_arr:
        line = line.replace('\n', '')
        print(line)
        if line.startswith("  Stream #"):
            stream_info.append(line.strip())
        if line.startswith("      title           :"):
            # 如果有title信息添加到该行末尾
            stream_info[-1] += line.strip().replace("title           :", "  --  ")
    return stream_info


def format_path_quotes(path):
    # 文件路径可能有空格需加引号
    return "\"{}\"".format(path)
