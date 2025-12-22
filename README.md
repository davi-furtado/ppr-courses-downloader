# Padre Paulo Ricardo Courses Downloader & Manager

This project is a complete toolset to **download, organize, and search** course materials from [padrepauloricardo.org](https://padrepauloricardo.org) with a Web Scraper and a Database Manager.

It consists of two main components:
1. **Scraper (`scraper.py`):** Automates the download of audio and text summaries using Selenium.
2. **Database Manager (`dbmanager.py`):** Indexes downloaded content into a SQLite database allowing full-text search across all lessons.

## Features
- ✔ Automatic login using saved cookies  
- ✔ Download content:
    - *Single course*
    - *All platform courses*
- ✔ Extract and format lesson text into `.txt` files  
- ✔ Download class audio files  
- ✔ Local SQLite Database creation
- ✔ Full-text search through all transcripts
- ✔ Rank courses by keyword frequency

## Requirements
### Python libraries
- selenium
- beautifulsoup4

Install with:

```bash
pip install selenium beautifulsoup4
```

*Note: `dbmanager.py` uses only standard Python libraries (sqlite3, argparse, pathlib).*

## Credentials Setup
Fill the `credentials.json` with your credentials:
```json
{
    "email": "your_email_here@gmail.com",
    "password": "your_password_here"
}
```
On first run, cookies will be generated and reused automatically.

## Usage: 1. Downloading Content
Use `scraper.py` to download the courses to your local drive (default folder is `downloads/`).

### Download ALL courses
```bash
python scraper.py --allcourses
```

### Download a SINGLE course
```bash
python scraper.py --course https://padrepauloricardo.org/cursos/course-link-here
```

---

## Usage: 2. Database & Search
Once you have downloaded the courses, use `dbmanager.py` to index the content and perform searches.

### Step 1: Import downloaded courses
Scan the download directory and index all text and audio metadata into `courses.db`.
```bash
# Assuming 'downloads' is your output folder
python dbmanager.py import downloads
```

### Step 2: Search for keywords
Search for a specific word or phrase across **all** downloaded lessons.
```bash
python dbmanager.py search "virtude"
```
*Output will show the lesson title, course, and match context.*

### Search and rank courses
Find which courses discuss a topic the most (ranked by frequency).
```bash
python dbmanager.py search "tomismo" --courses
```

### List all indexed courses
```bash
python dbmanager.py list
```

### View Database Statistics
See total words, lessons, and top courses.
```bash
python dbmanager.py stats
```

---

## Logging
All download operations, timestamps, warnings, and errors are stored in: `downloads/log.txt`. The script prints logs to console when DEBUG_MODE is enabled.

## How It Works
1. **Scraper (`scraper.py`)**:
    - Logs in and retrieves course URLs.
    - Iterates through lessons, downloading `.mp3` and extracting text to `.txt` files.
    - Saves files in structured folders (e.g., `downloads/Course Name/01. Lesson.txt`).

2. **Manager (`manager.py`)**:
    - **Import**: Recursively reads the folder structure.
    - **Indexing**: Reads `.txt` files and stores content in a SQLite Virtual Table (FTS5) for fast searching.
    - **Querying**: Allows you to find exactly which lessons a specific topic was mentioned (based on the text summary).

## ⚠ Disclaimer
This tool is for **personal use only**.
Only download content you already have rights to access.
Respect platform Terms of Service and copyright.
