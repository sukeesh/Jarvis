from selenium import webdriver
from bs4 import BeautifulSoup


def find_hackathon(self):
    print('--- Fetching hackathons--- \n')
    driver = webdriver.PhantomJS()
    driver.get('https://www.hackerearth.com/challenges/')
    res = driver.page_source
    soup = BeautifulSoup(res, 'lxml')
    upcoming = soup.find('div', {'class': 'upcoming challenge-list'})

    if upcoming is not None:

        all_hackathons = upcoming.find_all('div', {'class': 'challenge-content'})

        for i, hackathon in enumerate(all_hackathons, 1):
            challenge_type = hackathon.find('div', {'class': 'challenge-type'}).text.replace("\n", " ").strip()
            challenge_name = hackathon.find('div', {'class': 'challenge-name'}).text.replace("\n", " ").strip()
            date_time = hackathon.find('div', {'class': 'challenge-list-meta challenge-card-wrapper'}).text.replace("\n", " ").strip()
            print("[{}] {}\n{}\n{}\n\n".format(str(i), challenge_name, challenge_type, date_time))
    else:
        print("No hackathon data found.")
