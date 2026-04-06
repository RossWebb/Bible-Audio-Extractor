import os
import re
import subprocess
import json
import tkinter as tk
from tkinter import filedialog
from flask import Flask, render_template, request, jsonify, send_from_directory
import datetime

app = Flask(__name__)

# --- CONFIGURATION ---
SETTINGS_FILE = "settings.json"
OUTPUT_DIR = "output"

def find_aeneas():
    """Tries to find the specific Python 3.7 interpreter that has Aeneas installed."""
    paths = [
        r"C:\Python37-32\python.exe", 
        r"C:\aeneas\python.exe", 
        r"C:\Program Files (x86)\Scripture App Builder\aeneas\python.exe",
        r"C:\Program Files (x86)\aeneas\python.exe"
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return "python"

AENEAS_PYTHON = find_aeneas()

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# --- DATA MAPS ---
CANON_NUMS = {"GEN": "01", "EXO": "02", "LEV": "03", "NUM": "04", "DEU": "05", "JOS": "06", "JDG": "07", "RUT": "08", "1SA": "09", "2SA": "10", "1KI": "11", "2KI": "12", "1CH": "13", "2CH": "14", "EZR": "15", "NEH": "16", "EST": "17", "JOB": "18", "PSA": "19", "PRO": "20", "ECC": "21", "SNG": "22", "ISA": "23", "JER": "24", "LAM": "25", "EZK": "26", "DAN": "27", "HOS": "28", "JOL": "29", "AMO": "30", "OBA": "31", "JON": "32", "MIC": "33", "NAM": "34", "HAB": "35", "ZEP": "36", "HAG": "37", "ZEC": "38", "MAL": "39", "MAT": "01", "MRK": "02", "LUK": "03", "JHN": "04", "ACT": "05", "ROM": "06", "1CO": "07", "2CO": "08", "GAL": "09", "EPH": "10", "PHP": "11", "COL": "12", "1TH": "13", "2TH": "14", "1TI": "15", "2TI": "16", "TIT": "17", "PHM": "18", "HEB": "19", "JAS": "20", "1PE": "21", "2PE": "22", "1JN": "23", "2JN": "24", "3JN": "25", "JUD": "26", "REV": "27"}
BOOK_MAP = {"GEN": "Genesis", "EXO": "Exodus", "LEV": "Leviticus", "NUM": "Numbers", "DEU": "Deuteronomy", "JOS": "Joshua", "JDG": "Judges", "RUT": "Ruth", "1SA": "1 Samuel", "2SA": "2 Samuel", "1KI": "1 Kings", "2KI": "2 Kings", "1CH": "1 Chronicles", "2CH": "2 Chronicles", "EZR": "Ezra", "NEH": "Nehemiah", "EST": "Esther", "JOB": "Job", "PSA": "Psalms", "PRO": "Proverbs", "ECC": "Ecclesiastes", "SNG": "Song of Solomon", "ISA": "Isaiah", "JER": "Jeremiah", "LAM": "Lamentations", "EZK": "Ezekiel", "DAN": "Daniel", "HOS": "Hoshea", "JOL": "Joel", "AMO": "Amos", "OBA": "Obadiah", "JON": "Jonah", "MIC": "Micah", "NAM": "Nahum", "HAB": "Habakkuk", "ZEP": "Zechariah", "HAG": "Haggai", "ZEC": "Zechariah", "MAL": "Malachi", "MAT": "Matthew", "MRK": "Mark", "LUK": "Luke", "JHN": "John", "ACT": "Acts", "ROM": "Romans", "1CO": "1 Corinthians", "2CO": "2 Corinthians", "GAL": "Galatians", "EPH": "Ephesians", "PHP": "Philippians", "COL": "Colossians", "1TH": "1 Thessalonians", "2TH": "2 Thessalonians", "1TI": "1 Timothy", "2TI": "2 Timothy", "TIT": "Titus", "PHM": "Philemon", "HEB": "Hebrews", "JAS": "James", "1PE": "1 Peter", "2PE": "2 Peter", "1JN": "1 John", "2JN": "2 John", "3JN": "3 John", "JUD": "Jude", "REV": "Revelation"}
REVERSE_MAP = {v: k for k, v in BOOK_MAP.items()}
OT_CODES = ["GEN", "EXO", "LEV", "NUM", "DEU", "JOS", "JDG", "RUT", "1SA", "2SA", "1KI", "2KI", "1CH", "2CH", "EZR", "NEH", "EST", "JOB", "PSA", "PRO", "ECC", "SNG", "ISA", "JER", "LAM", "EZK", "DAN", "HOS", "JOL", "AMO", "OBA", "JON", "MIC", "NAM", "HAB", "ZEP", "HAG", "ZEC", "MAL"]

# --- SETTINGS HELPERS ---
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                d = json.load(f)
                return {
                    "project": d.get("project", ""),
                    "audio": d.get("audio", ""),
                    "gap": d.get("gap", 1.5),
                    "fades": d.get("fades", True)
                }
        except: pass
    return {"project": "", "audio": "", "gap": 1.5, "fades": True}

def save_settings(p, a, g, f_bool):
    with open(SETTINGS_FILE, "w") as f:
        json.dump({"project": p, "audio": a, "gap": g, "fades": f_bool}, f)

# Global variables for the session
settings = load_settings()
PROJECT_PATH = settings["project"]
AUDIO_PATH = settings["audio"]
CURRENT_GAP = settings["gap"]
CURRENT_FADES = settings["fades"]

# --- CORE FUNCTIONS ---
def parse_bulk_input(text_data):
    tasks = []
    lines = text_data.strip().split('\n')
    for line in lines:
        match = re.match(r"(.+?)\s+(\d+):([\d,\s-]+)", line.strip())
        if match:
            book, chap, v_string = match.groups()
            for part in v_string.split(','):
                part = part.strip()
                if '-' in part:
                    try: s, e = map(int, part.split('-'))
                    except: continue
                else:
                    try: s = e = int(part)
                    except: continue
                tasks.append({"book": book.strip(), "chap": int(chap), "v_start": s, "v_end": e})
    return tasks

def scan_sfm_file(filepath):
    structure = {}
    current_chap = 0
    if not os.path.exists(filepath): return {}
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            c_match = re.match(r'\\c\s+(\d+)', line)
            if c_match:
                current_chap = int(c_match.group(1))
                structure[current_chap] = 0
            v_match = re.match(r'\\v\s+(\d+)', line)
            if v_match and current_chap in structure:
                structure[current_chap] = max(structure[current_chap], int(v_match.group(1)))
    return structure

def get_audio_file(book_code, chap):
    canon = CANON_NUMS.get(book_code)
    prefix = "A" if book_code in OT_CODES else "B"
    target_start = f"{prefix}{canon}___"
    for f in os.listdir(AUDIO_PATH):
        if f.upper().startswith(target_start) and f"_{chap:02}_" in f:
            return os.path.join(AUDIO_PATH, f)
    return None

def get_refined_times(map_path, v_start, v_end):
    start_ts, end_ts = None, None
    if not os.path.exists(map_path): return None, None
    with open(map_path, "r") as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) < 3: continue
            s, e, identifier = parts
            v_label = identifier.split('|')[0]
            v_list = []
            if '-' in v_label:
                try:
                    v_low, v_high = map(int, v_label.split('-'))
                    v_list = list(range(v_low, v_high + 1))
                except: pass
            else:
                try: v_list = [int(v_label)]
                except: pass
            
            if v_start in v_list and start_ts is None:
                raw_s = float(s)
                start_ts = raw_s + 0.1 if v_list[0] == 1 else raw_s - 1.0
            if v_end in v_list:
                end_ts = float(e) + 0.1
    return start_ts, end_ts

# --- ROUTES ---
@app.route('/')
def index():
    curr = load_settings()
    return render_template('index.html', 
                           p_path=curr["project"], 
                           a_path=curr["audio"], 
                           gap=curr["gap"], 
                           fades=curr["fades"])

@app.route('/set_path/<ptype>')
def set_path(ptype):
    global PROJECT_PATH, AUDIO_PATH
    root = tk.Tk(); root.withdraw(); root.attributes("-topmost", True)
    path = filedialog.askdirectory(); root.destroy()
    if path:
        if ptype == 'project': PROJECT_PATH = path
        else: AUDIO_PATH = path
        save_settings(PROJECT_PATH, AUDIO_PATH, CURRENT_GAP, CURRENT_FADES)
        return jsonify({"status": "success", "path": path})
    return jsonify({"status": "error"})

@app.route('/extract_bulk', methods=['POST'])
def extract_bulk():
    global PROJECT_PATH, AUDIO_PATH, CURRENT_GAP, CURRENT_FADES
    data = request.json
    raw_refs = data.get('references', '')
    tasks = parse_bulk_input(raw_refs)
    
    CURRENT_GAP = float(data.get('gap', 1.5))
    CURRENT_FADES = data.get('fades', True)
    save_settings(PROJECT_PATH, AUDIO_PATH, CURRENT_GAP, CURRENT_FADES)

    if not tasks: return jsonify({"status": "error", "message": "No valid references found."})

    for t in tasks:
        code = REVERSE_MAP.get(t['book'])
        if not code: return jsonify({"status": "error", "message": f"Book '{t['book']}' not recognized."})
        target_sfm = next((f for f in os.listdir(PROJECT_PATH) if code in f.upper() and f.upper().endswith(".SFM")), None)
        if not target_sfm: return jsonify({"status": "error", "message": f"SFM file for {t['book']} missing."})
        struct = scan_sfm_file(os.path.join(PROJECT_PATH, target_sfm))
        if t['chap'] not in struct: return jsonify({"status": "error", "message": f"{t['book']} Ch {t['chap']} not found."})
        if t['v_end'] > struct[t['chap']]: return jsonify({"status": "error", "message": f"{t['book']} {t['chap']} max verse is {struct[t['chap']]}."})

    combined_files, labels, current_offset = [], [], 0.0
    bridge_path = os.path.join(OUTPUT_DIR, "bridge.mp3")
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"anoisesrc=d={CURRENT_GAP}:c=brown:r=44100:a=0.05", "-ac", "1", bridge_path], check=True)

    try:
        for i, t in enumerate(tasks):
            code = REVERSE_MAP.get(t['book'])
            audio_file = get_audio_file(code, t['chap'])
            map_path = os.path.join(OUTPUT_DIR, f"map_{code}_{t['chap']}.tsv")
            
            if not os.path.exists(map_path):
                target_sfm = next((f for f in os.listdir(PROJECT_PATH) if code in f.upper() and f.upper().endswith(".SFM")), None)
                sync_lines = [f"INTRO|{t['book']}", f"ANNOUNCE|Chapter {t['chap']}"]
                with open(os.path.join(PROJECT_PATH, target_sfm), 'r', encoding='utf-8', errors='ignore') as f:
                    curr_c = 0
                    for line in f:
                        c_m = re.match(r'\\c\s+(\d+)', line)
                        if c_m: curr_c = int(c_m.group(1))
                        if curr_c == t['chap']:
                            v_m = re.match(r'\\v\s+([\d-]+)\s+(.*)', line)
                            if v_m:
                                v_range, raw_text = v_m.group(1), v_m.group(2)
                                clean = re.sub(r'\\f\s+.*?\\f\*', '', raw_text)
                                clean = re.sub(r'\\x\s+.*?\\x\*', '', clean)
                                clean = re.sub(r'\\[a-z0-9-]+\*?\s?', '', clean)
                                clean = clean.replace('*', '').strip()
                                sync_lines.append(f"GAP_{v_range}|---")
                                sync_lines.append(f"{v_range}|{clean}")

                temp_sync_path = os.path.join(OUTPUT_DIR, f"temp_{i}.txt")
                with open(temp_sync_path, "w", encoding="utf-8") as f:
                    for sl in sync_lines: f.write(sl + "\n")

                cfg = "task_language=en|is_text_type=parsed|os_task_file_format=tsv|task_adjust_boundary_percent=50"
                subprocess.run([AENEAS_PYTHON, "-m", "aeneas.tools.execute_task", audio_file, temp_sync_path, cfg, map_path], check=True)

            s_ts, e_ts = get_refined_times(map_path, t['v_start'], t['v_end'])
            duration = e_ts - s_ts
            temp_seg = os.path.join(OUTPUT_DIR, f"seg_{i}.mp3")
            fade_filter = f"afade=t=in:st=0:d=0.1,afade=t=out:st={max(0, duration-0.1)}:d=0.1" if CURRENT_FADES else "anull"
            subprocess.run(["ffmpeg", "-y", "-ss", str(s_ts), "-to", str(e_ts), "-i", audio_file, "-af", fade_filter, temp_seg], check=True)

            labels.append(f"{current_offset:.6f}\t{current_offset + duration:.6f}\t{t['book']} {t['chap']}:{t['v_start']}")
            combined_files.append(temp_seg)
            if i < len(tasks) - 1:
                combined_files.append(bridge_path)
                current_offset += (duration + CURRENT_GAP)
            else:
                current_offset += duration

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        final_mp3 = f"Sequence_{timestamp}.mp3"
        list_path = os.path.join(OUTPUT_DIR, "concat_list.txt")
        with open(list_path, "w") as f:
            for fp in combined_files: f.write(f"file '{os.path.abspath(fp)}'\n")

        subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path, "-c:a", "libmp3lame", "-q:a", "2", os.path.join(OUTPUT_DIR, final_mp3)], check=True)
        label_file = f"Labels_{timestamp}.txt"
        with open(os.path.join(OUTPUT_DIR, label_file), "w") as f: f.write("\n".join(labels))

        return jsonify({"status": "success", "audio_url": f"/download/{final_mp3}", "label_url": f"/download/{label_file}", "filename": final_mp3})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(OUTPUT_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True)
