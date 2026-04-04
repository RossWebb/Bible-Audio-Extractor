# Bible Audio Segment Extractor

A Flask-based web tool designed to synchronize Bible text (SFM) with audio files using **aeneas**, allowing users to extract specific verse ranges into a single sequence with customizable gaps and fades.
It takes a list of Bible references/ranges from available in a project on Paratext installation and extracts available audio downloaded from Bible.is for the language in question.

## Features
- **Bulk Extraction**: Paste multiple references (e.g., `John 3:16`, `Exodus 1:1-5`) to build a single MP3.
- **Audacity Integration**: Generates a Label Track for instant navigation in Audacity.
- **Auto-Sync**: Uses the `aeneas` engine to find exact verse timings.
- **Persistent Settings**: Remembers your folder paths, gap preferences, and fade settings.

## Installation

### Prerequisites
1. **Python 3.x** installed.
2. **FFmpeg** installed and added to your System PATH.
3. **Scripture App Builder (SAB)**: This tool is designed to use the `aeneas` engine bundled with SAB.

### Setup
1. Clone this repository or download the ZIP.
2. Open a terminal in the folder and install dependencies:
   ```bash
   pip install flask
