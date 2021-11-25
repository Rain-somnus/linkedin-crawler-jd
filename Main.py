from Browser import Browser
from Website import Website
import pandas as pd

def main(start_page,end_page,topic):
    a = open('config.txt')
    username = a.readline()
    password = a.readline().strip()
    web_site = Website("Linkedin", 'https://linkedin.com',
                       'https://www.linkedin.com/jobs/search/?geoId=103291313&keywords=',
                       'https://www.linkedin.com/uas/login')
    browser = Browser(web_site)
    browser.log_in(username, password)
    topics = [topic]
    browser.generate_search_url(topics)
    for j in range(start_page,end_page):
        print("page",j+1)
        browser.get_jobs_details(browser.search_urls[j])
    browser.outputcsv('data_page%d_%d'%(start_page+1,end_page))

if __name__ == "__main__":
    topic = input('input the topic: ').split()
    topic = '%20'.join(topic)
    main(0,10,topic)
    main(10,20,topic)
    main(20,30,topic)
    main(30,40,topic)
    