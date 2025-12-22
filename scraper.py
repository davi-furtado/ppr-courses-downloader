from scraperclass import CourseScraper
from os import path
from sys import argv

def main():
    if not ((len(argv) == 2 and argv[1] == '--allcourses')
            or (len(argv) == 3 and argv[1] == '--course')):
        print('''-> Please use one of the following commands:\n>>> main.py --allcourses\n>>> main.py --course [course link]''')
        return
        
    elif argv[1] == '--allcourses':
        download_link = 'https://padrepauloricardo.org/cursos'
    elif argv[1] == '--course':
        download_link = argv[2]

    if not path.exists('credentials.json'):
        print('-> Credentials file was not found! Please create one as explained in the README file')
        return
        
    scraper = CourseScraper()
    scraper.login("https://padrepauloricardo.org/entrar")

    if argv[1] == '--allcourses':
        scraper.download_all_courses(download_link)
    elif argv[1] == '--course':
        scraper.download_course(download_link)

if __name__ == "__main__":
    main()