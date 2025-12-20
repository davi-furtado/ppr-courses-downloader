# Padre Paulo Ricardo Courses Downloader

This project is a Web Scraper that automates the download of **course materials (audio + text summaries)** from the website [padrepauloricardo.org](https://padrepauloricardo.org) using Selenium and BeautifulSoup.

The downloader supports:  
- ✔ Automatic login using saved cookies  
- ✔ Downloading of:
    - *Single course*
    - *All platform courses*
- ✔ Extracting and formatting lesson text into `.txt` files  
- ✔ Downloading class audio files  
- ✔ Organized folder output per course  
- ✔ Detailed logging of all operations  

## Requirements
### Python libraries
- selenium
- beautifulsoup4

Install with:

```bash
pip install selenium beautifulsoup4
```

## Credentials Setup
Fill the `credentials.json` with your credentials:
```bash
{
    "email": "your_email_here@gmail.com",
    "password": "your_password_here"
}
```
On first run, cookies will be generated and reused automatically.

## Usage
### Download ALL courses
```bash
python main.py --allcourses
```

### Download a SINGLE course
```bash
python main.py --course https://padrepauloricardo.org/cursos/course-name-here
```

## Logging
All operations, timestamps, warnings, and errors are stored in: `downloads/log.txt`. The script prints logs to console when DEBUG_MODE is enabled.

## How It Works
- Initialize CourseScraper()
- Attempt login:
    - load cookies if valid
    - otherwise login using credentials
- Retrieve course URLs
- For each course:
    - create a directory
    - retrieve all class links
    - for each class:
        - download audio
        - extract text using BeautifulSoup
        - save content to .txt
- Continue until completion

## ⚠ Disclaimer
This tool is for **personal use only**.
Only download content you already have rights to access.
Respect platform Terms of Service and copyright.
