# Bible Audio Segment Extractor

A Flask-based web tool designed to synchronize Bible text (SFM) with audio files using **aeneas**, allowing users to extract specific verse ranges into a single sequence with customizable gaps and fades.
It takes a list of Bible references/ranges from available in a project on Paratext installation and extracts available audio downloaded from Bible.is for the language in question.

# Bible Audio Segment Extractor

A Flask-based web tool designed to synchronize Bible text (SFM) with audio files using **aeneas**. This tool allows users to extract specific verse ranges into a single MP3 sequence with customizable gaps and fades, complete with an Audacity Label track.

## 🛠 Prerequisites & Installation

To run this tool, you must set up the **Aeneas Engine** and a **Python 3** environment.

### Step 1: Install Aeneas (The Sync Engine)
We recommend the **Sillsdev Aeneas Installer**, as it is pre-configured for the Scripture App Builder community and bundles Python 3.7, eSpeak, and FFmpeg.

1. **Download:** [Aeneas Installer v1.7.3.0_2 (Sillsdev)](https://github.com/sillsdev/aeneas-installer/releases/tag/v1.7.3.0_2)
2. **Critical:** You **MUST** right-click the installer and select **"Run as Administrator"**. Failure to do so often prevents the components from registering correctly in Windows.
3. **FFmpeg:** This installer includes FFmpeg. The app will attempt to locate it automatically within the Aeneas directory.

### Step 2: Install Python (The Web Interface)
You need a modern version of Python (3.10 or newer) to run the Flask web application.
1. **Download:** [Python.org Downloads](https://www.python.org/downloads/)
2. **Note:** During installation, ensure you check the box **"Add Python to PATH"**.

---

## 🚀 Setup Routine

1. **Download the Project**: Download this repository as a ZIP file and extract it to a folder on your computer.
2. **Install Web Requirements**: Open a command prompt (CMD) in the project folder and run:
   ```bash
   pip install flask
3. **Run the App**: 
   ```bash
   python app.py
4. **Access the Interface**: Open your web browser and go to `http://127.0.0.1:5000`.
 
 ---

## 📖 How to Use

1. **Configure Paths**: Use the "Set Folder" buttons to select:
   * **SFM Folder**: The directory containing your Paratext `.SFM` files.
   * **Audio Folder**: The directory containing your full-chapter MP3 files.
2. **Input References**: Paste your references into the text box (one per line). 
   * *Example:* `John 3:16`
   * *Example:* `Exodus 1:1-5, 8-10`
3. **Adjust Timing**: Set the "Gap" (seconds of brown noise between clips) and toggle "Micro-Fades" to prevent audio pops.
4. **Build**: Click **"Build Audacity Project"**. 
5. **Import to Audacity**: 
   * Drag the generated MP3 into Audacity.
   * Go to `File > Import > Labels` and select the generated Labels file to see your verse markers.

---

## 📂 Technical Details
* **Persistence**: Your folder paths and preferences are saved in a local `settings.json` file so you don't have to re-enter them.
* **Aeneas Detection**: The script automatically scans for Aeneas in `C:\aeneas`, `C:\Python37-32`, and standard SAB install locations.
* **Privacy Note**: Your personal folder paths and generated audio files are automatically kept on your computer. They are never uploaded to GitHub or shared with others.

  ---

  ### ⏳ Timing & Padding Logic

To ensure the extracted audio clips feel natural and provide a seamless listening experience, the script applies specific offsets during the timestamp refinement process. These adjustments prevent "choppy" starts and "clipped" ends.

#### **Adjustment Parameters**

| Event | Logic | Offset | Rationale |
| :--- | :--- | :--- | :--- |
| **Chapter Start** | Verse 1 | `+ 0.1s` | Clips tightly to the first spoken word, skipping leading silence. |
| **Middle Start** | Verse > 1 | `- 1.0s` | Provides a "breath" or lead-in, ensuring the start isn't abrupt. |
| **Verse End** | Range End | `+ 0.1s` | Adds a micro-buffer to prevent the final syllable from being truncated. |

#### **Implementation Snippet**
The following logic is handled within the `get_refined_times` function to calculate the `start_ts` and `end_ts` used by FFmpeg for extraction:

```python
# Refinement logic for natural-sounding clips
if v_start in v_list and start_ts is None:
    raw_s = float(s)
    # Verse 1 starts tight; subsequent verses get 1 second of lead-in
    start_ts = raw_s + 0.1 if v_list[0] == 1 else max(0, raw_s - 1.0)

if v_end in v_list:
    # Small buffer added to the end timestamp to avoid clipping
    end_ts = float(e) + 0.1
