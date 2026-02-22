import urllib.request
import xml.etree.ElementTree as ET
import re
import math
import os
import json
import subprocess
import shutil
import sys
import time


class Color:
    BOLD = "\033[1m"
    BLUE = "\033[34m"
    CYAN = "\033[96m"
    END = "\033[0m"
    GRAY = "\033[90m"
    GREEN = "\033[92m"
    MAGENTA = "\033[35m"
    RED = "\033[91m"
    WHITE = "\033[97m"
    YELLOW = "\033[93m"


def get_quality_label(width, height, original_label=None):
    qualities = {
        "7680x4320": "8K Ultra HD",
        "3840x2160": "4K Ultra HD (2160p)",
        "2560x1440": "2K / Quad HD (1440p)",
        "1920x1080": "Full HD (1080p)",
        "1440x1080": "Full HD 4:3 (1080p)",
        "1280x720": "HD (720p)",
        "960x720": "HD 4:3 (720p)",
        "1024x576": "Alta Definició (576p)",
        "768x576": "Qualitat TV Clàssica (576p 4:3)",
        "854x480": "Qualitat DVD (480p)",
        "768x432": "Qualitat Mitjana (432p)",
        "640x360": "Qualitat Estàndard (360p)",
        "512x288": "Qualitat Baixa (288p)",
        "384x216": "Mòbil / Estalvi de dades (216p)",
    }

    if width and height:
        res_key = f"{width}x{height}"
        return qualities.get(res_key, f"Resolució personalitzada ({res_key})")

    if original_label:
        clean_val = str(original_label).lower().replace("p", "").strip()
        for res, label in qualities.items():
            if res.endswith(f"x{clean_val}"):
                return label
        return f"Qualitat {original_label}"

    return "Qualitat desconeguda"


def get_terminal_width():
    return shutil.get_terminal_size((60, 20)).columns


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_header():
    clear_screen()
    width = min(get_terminal_width(), 75)

    logo = [
        r"  ____   ____        _     ",
        r" |___ / / ___|  __ _| |_   ",
        r"   |_ \| |     / _` | __|  ",
        r"  ___) | |___ | (_| | |_   ",
        r" |____/ \____| \__,_|\__|  ",
    ]

    print(Color.RED)
    for line in logo:
        padding = (width - len(line)) // 2
        print(f"{' ' * padding}{line}")

    title_text = "3Cat Media Downloader (CLI)"
    title_padding = (width - len(title_text)) // 2
    print(
        f"{' ' * title_padding}{Color.BOLD}{Color.RED}3Cat {Color.WHITE}Media Downloader (CLI){Color.END}"
    )

    print(f"{Color.GRAY}{'━' * width}{Color.END}")

    ffmpeg_available = shutil.which("ffmpeg") is not None
    status_label = "FFmpeg: "
    status_value = (
        "Disponible"
        if ffmpeg_available
        else "No trobat. Descàrregues de vídeos DASH desactivades."
    )

    total_status_len = len(status_label) + len(status_value)
    status_padding = (width - total_status_len) // 2
    status_color = Color.GREEN if ffmpeg_available else Color.RED

    print(
        f"{' ' * status_padding}{Color.BOLD}{status_label}{status_color}{status_value}{Color.END}"
    )

    print(f"{Color.GRAY}{'━' * width}{Color.END}\n")


def print_exit_message():
    width = min(get_terminal_width(), 75)

    line1_text = "S'està sortint de 3Cat Media Downloader (CLI)."
    line2_text = "Gràcies per fer servir l'eina. Adeu!"

    line1_padding = (width - len(line1_text)) // 2
    line2_padding = (width - len(line2_text)) // 2

    print(f"\n{Color.GRAY}{'━' * width}{Color.END}")

    print(
        f"{' ' * line1_padding}{Color.BOLD}S'està sortint de {Color.RED}3Cat {Color.WHITE}Media Downloader (CLI){Color.END}."
    )

    print(f"{' ' * line2_padding}{Color.GRAY}{line2_text}{Color.END}")

    print(f"{Color.GRAY}{'━' * width}{Color.END}\n")


def check_ffmpeg():
    return shutil.which("ffmpeg") is not None


def get_media_data(web_url):
    is_audio = "/audio/" in web_url
    media_type = "audio" if is_audio else "video"

    match = re.search(r"/(?:video|audio)/(\d+)/", web_url)
    if not match:
        raise Exception("URL no vàlida. No s'ha trobat l'ID.")
    media_id = match.group(1)

    api_url = f"https://api-media.3cat.cat/pvideo/media.jsp?media={media_type}&versio=vast&idint={media_id}&profile=pc_3cat&format=dm"
    headers = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(api_url, headers=headers)

    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode("utf-8"))
        info = data.get("informacio", {})
        titol = info.get("titol", f"{media_type}_{media_id}")
        titol = re.sub(r"[^\w\s-]", "", titol).strip()
        duracion_seg = info.get("durada", {}).get("milisegons", 0) / 1000

        sources = data.get("media", {}).get("url", [])
        if isinstance(sources, str):
            sources = [{"file": sources, "label": "MP3"}]

        variants = data.get("variants", [])
        subtitols = data.get("subtitols", [])

        return media_id, titol, duracion_seg, sources, subtitols, variants, media_type


def download_segments(base_url, template_node, total_duration, temp_filename):
    media_pattern = template_node.get("media")
    init_path = template_node.get("initialization")
    duration = int(template_node.get("duration"))
    timescale = int(template_node.get("timescale"))

    total_segments = math.ceil(total_duration / (duration / timescale))
    MAX_RETRIES = 3
    TIMEOUT = 10

    print(f"\n{Color.YELLOW}   [*] Descarregant segments: {temp_filename}{Color.END}")

    try:
        with open(temp_filename, "wb") as out_file:
            init_url = base_url + init_path
            success_init = False
            for attempt in range(MAX_RETRIES):
                try:
                    with urllib.request.urlopen(init_url, timeout=TIMEOUT) as resp:
                        out_file.write(resp.read())
                        success_init = True
                        break
                except Exception:
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(3)

            if not success_init:
                raise Exception("No s'ha pogut descarregar la capçalera.")

            for i in range(total_segments):
                seg_url = base_url + media_pattern.replace("$Number$", str(i))
                success_seg = False

                for attempt in range(MAX_RETRIES):
                    try:
                        with urllib.request.urlopen(seg_url, timeout=TIMEOUT) as resp:
                            out_file.write(resp.read())
                            success_seg = True
                            break
                    except Exception as e:
                        current_attempt = attempt + 1
                        print(
                            f"\r\033[K{Color.RED}       [!] Tall detectat al segment {i}. Intent {current_attempt}/{MAX_RETRIES}...{Color.END}",
                            end="",
                        )
                        sys.stdout.flush()

                        if attempt < MAX_RETRIES - 1:
                            time.sleep(3)
                        else:
                            print()
                            raise Exception(
                                f"Connexió perduda descarregant el segment {i}: {e}\n"
                            )

                if success_seg:
                    prog = ((i + 1) / total_segments) * 100
                    bar_size = 30
                    filled = int(prog / 100 * bar_size)
                    bar = "█" * filled + "░" * (bar_size - filled)
                    print(f"\r\033[K       |{bar}| {prog:.1f}%", end="")
                    sys.stdout.flush()

        print(f"\n       {Color.GREEN}✔ Segments completats.{Color.END}")

    except Exception as e:
        print(f"\n{Color.RED}   [!] Error: {e}{Color.END}")
        if "out_file" in locals() and not out_file.closed:
            out_file.close()
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        sys.exit(1)


def download_file(url, filename):
    MAX_RETRIES = 3
    TIMEOUT = 10
    print(f"\n{Color.YELLOW}   [*] Descarregant fitxer: {filename}{Color.END}")

    for attempt in range(MAX_RETRIES):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
                total_size = int(response.info().get("Content-Length", 0))
                downloaded = 0
                block_size = 8192

                with open(filename, "wb") as out_file:
                    while True:
                        buffer = response.read(block_size)
                        if not buffer:
                            break

                        downloaded += len(buffer)
                        out_file.write(buffer)

                        if total_size > 0:
                            prog = (downloaded / total_size) * 100
                            bar_size = 30
                            filled = int(prog / 100 * bar_size)
                            bar = "█" * filled + "░" * (bar_size - filled)
                            print(f"\r\033[K       |{bar}| {prog:.1f}%", end="")
                            sys.stdout.flush()

                print(f"\n       {Color.GREEN}✔ Descàrrega completada.{Color.END}")
                return

        except Exception as e:
            current_attempt = attempt + 1
            print(
                f"\r\033[K{Color.RED}       [!] Tall detectat. Intent {current_attempt}/{MAX_RETRIES}...{Color.END}",
                end="",
            )
            sys.stdout.flush()

            if attempt < MAX_RETRIES - 1:
                time.sleep(3)
            else:
                print(
                    f"\n\n{Color.RED}   [!] Error: Connexió perduda ({e}).{Color.END}\n"
                )
                if os.path.exists(filename):
                    os.remove(filename)
                sys.exit(1)


def vtt_to_srt(vtt_path):
    srt_path = vtt_path.replace(".vtt", ".srt")
    try:
        with open(vtt_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        final_srt = []
        counter = 1
        for i in range(len(lines)):
            line = lines[i].strip()
            if " --> " in line:
                t = re.findall(r"(\d{0,2}:?\d{2}:\d{2}[\.,]\d{3})", line)
                if len(t) >= 2:
                    start, end = t[0].replace(".", ","), t[1].replace(".", ",")
                    if start.count(":") == 1:
                        start = f"00:{start}"
                    if end.count(":") == 1:
                        end = f"00:{end}"

                    text_lines = []
                    for j in range(i + 1, min(i + 4, len(lines))):
                        nxt = lines[j].strip()
                        if not nxt or " --> " in nxt or nxt.startswith("Region:"):
                            break
                        clean = re.sub(r"<[^>]+>", "", nxt)
                        if clean and not clean.isdigit():
                            text_lines.append(clean)

                    if text_lines:
                        final_srt.append(
                            f"{counter}\n{start} --> {end}\n"
                            + "\n".join(text_lines)
                            + "\n\n"
                        )
                        counter += 1

        if final_srt:
            with open(srt_path, "w", encoding="utf-8", newline="\n") as f:
                f.writelines(final_srt)
            if os.path.exists(vtt_path):
                os.remove(vtt_path)
            print(
                f"       {Color.GREEN}✔ Subtítols SRT generats correctament.{Color.END}"
            )
            return True
        return False
    except Exception:
        return False


def main():
    ffmpeg_disponible = check_ffmpeg()

    while True:
        print_header()

        print(
            f"   {Color.BOLD}Introduïu la URL del contingut (o 's' per sortir):{Color.END}"
        )
        web_url = input(f"\n   {Color.GREEN}URL > {Color.END}").strip()

        if web_url.lower() == "s":
            print_exit_message()
            break
        if not web_url:
            continue

        try:
            media_id, titol, total_sec, sources, subtitols, variants, m_type = (
                get_media_data(web_url)
            )

            while True:
                print_header()
                print(
                    f"   {Color.BOLD}Contingut:{Color.END} {Color.YELLOW}{titol}{Color.END}"
                )

                available_options = []
                for s in sources:
                    if s.get("label") == "DASH":
                        mpd_url = s.get("file")
                        xml_data = urllib.request.urlopen(mpd_url).read()
                        root = ET.fromstring(xml_data)
                        ns = {"dash": "urn:mpeg:dash:schema:mpd:2011"}

                        if ffmpeg_disponible:
                            videos = root.findall(
                                './/dash:AdaptationSet[@mimeType="video/mp4"]/dash:Representation',
                                ns,
                            )
                            for v in videos:
                                q_label = get_quality_label(
                                    v.get("width"), v.get("height")
                                )
                                available_options.append(
                                    {
                                        "type": "DASH_VIDEO",
                                        "label": f"Vídeo - {q_label}",
                                        "tag": f"{Color.CYAN}[Descàrrega DASH]{Color.END}",
                                        "url": mpd_url,
                                        "v_rep": v,
                                        "root": root,
                                        "ns": ns,
                                    }
                                )

                        a_rep = root.find(
                            './/dash:AdaptationSet[@mimeType="audio/mp4"]/dash:Representation',
                            ns,
                        )
                        if a_rep is not None:
                            available_options.append(
                                {
                                    "type": "DASH_AUDIO",
                                    "label": "Àudio",
                                    "tag": f"{Color.GREEN}[Descàrrega DASH]{Color.END}",
                                    "url": mpd_url,
                                    "a_rep": a_rep,
                                    "ns": ns,
                                }
                            )

                    elif s.get("label") != "DASH":
                        q_label = get_quality_label(None, None, s.get("label"))
                        tag_color = Color.GREEN if m_type == "audio" else Color.BLUE
                        available_options.append(
                            {
                                "type": "DIRECT",
                                "label": f"{'Àudio' if m_type == 'audio' else 'Vídeo'} - {q_label}",
                                "tag": f"{tag_color}[Descàrrega directa]{Color.END}",
                                "url": s.get("file"),
                            }
                        )

                for v in variants:
                    label = v.get("label", "Variant")
                    v_type_name = v.get("nom", "Variant")
                    v_sources = v.get("media", {}).get("url", [])
                    for vs in v_sources:
                        if vs.get("label") != "DASH":
                            q_label = get_quality_label(None, None, vs.get("label"))
                            available_options.append(
                                {
                                    "type": "DIRECT",
                                    "label": f"{v_type_name} - {q_label}",
                                    "tag": f"{Color.MAGENTA}[{label}]{Color.END}",
                                    "url": vs.get("file"),
                                    "suffix": f" ({v_type_name})",
                                }
                            )

                for sub in subtitols:
                    available_options.append(
                        {
                            "type": "SUB",
                            "label": f"{sub.get('text')}",
                            "tag": f"{Color.BOLD}[Subtítols]{Color.END}",
                            "url": sub.get("url"),
                            "lang": sub.get("iso", "ca"),
                        }
                    )

                print(
                    f"\n   {Color.BOLD}Seleccioneu una opció de descàrrega:{Color.END}\n"
                )
                for i, opt in enumerate(available_options, start=1):
                    print(f"    {i:2}. {opt['tag']} {opt['label']}")

                new_search_idx = len(available_options) + 1
                exit_idx = len(available_options) + 2
                print(f"    {new_search_idx:2}. {Color.YELLOW}[Nova cerca]{Color.END}")
                print(f"    {exit_idx:2}. {Color.RED}[Sortir del programa]{Color.END}")

                try:
                    choice_str = input(
                        f"\n   {Color.GREEN}Opció (1-{exit_idx}) > {Color.END}"
                    )
                    if not choice_str:
                        continue
                    choice = int(choice_str)
                except ValueError:
                    continue

                if choice == exit_idx:
                    print_exit_message()
                    return

                if choice == new_search_idx:
                    break

                selected = available_options[choice - 1]

                if selected["type"] == "SUB":
                    output = f"{titol}.{selected['lang']}.vtt"
                    download_file(selected["url"], output)
                    vtt_to_srt(output)

                elif selected["type"] == "DIRECT":
                    ext = ".mp3" if m_type == "audio" else ".mp4"
                    output = f"{titol}{selected.get('suffix', '')}{ext}"
                    download_file(selected["url"], output)

                elif selected["type"] == "DASH_AUDIO":
                    output = f"{titol}.m4a"
                    base_url = selected["url"].rsplit("/", 1)[0] + "/"
                    download_segments(
                        base_url,
                        selected["a_rep"].find("dash:SegmentTemplate", selected["ns"]),
                        total_sec,
                        output,
                    )

                elif selected["type"] == "DASH_VIDEO":
                    output = f"{titol}.mp4"
                    base_url = selected["url"].rsplit("/", 1)[0] + "/"
                    v_temp, a_temp = f"v_{media_id}.tmp", f"a_{media_id}.tmp"
                    a_rep = selected["root"].find(
                        './/dash:AdaptationSet[@mimeType="audio/mp4"]/dash:Representation',
                        selected["ns"],
                    )
                    download_segments(
                        base_url,
                        selected["v_rep"].find("dash:SegmentTemplate", selected["ns"]),
                        total_sec,
                        v_temp,
                    )
                    download_segments(
                        base_url,
                        a_rep.find("dash:SegmentTemplate", selected["ns"]),
                        total_sec,
                        a_temp,
                    )
                    print(
                        f"\n   {Color.YELLOW}[*] Combinant pistes amb FFmpeg...{Color.END}"
                    )
                    subprocess.run(
                        [
                            "ffmpeg",
                            "-y",
                            "-i",
                            v_temp,
                            "-i",
                            a_temp,
                            "-c",
                            "copy",
                            output,
                        ],
                        check=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.STDOUT,
                    )
                    os.remove(v_temp)
                    os.remove(a_temp)
                    print(f"   {Color.GREEN}✔ Vídeo finalitzat amb èxit.{Color.END}")

                input(f"\n   {Color.BOLD}Premeu INTRO per tornar al menú...{Color.END}")

        except Exception as e:
            print(f"\n   {Color.RED}[!] Error: {e}{Color.END}")
            input("\n   Premeu INTRO per tornar-ho a provar...")


if __name__ == "__main__":
    main()
