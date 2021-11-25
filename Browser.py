import  time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import re
from bs4 import BeautifulSoup
from Job import Job
import pandas as pd
import random

options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])

class Browser:
    def __init__(self, website):
        self.browser = webdriver.Chrome('F:\gitlab\code\chromedriver.exe',options=options)  # Path to chrome driver
        self.search_urls = []
        self.website = website
        self.output = pd.DataFrame(columns=['title','company','detail'])
        self.count_link = 0

    def log_in(self, username, password):
        print(self.website.login_url)
        self.browser.get(self.website.login_url)
        elementId = self.browser.find_element_by_id('username')
        elementId.send_keys(username)
        elementId = self.browser.find_element_by_id('password')
        elementId.send_keys(password)
        elementId.submit()

    def generate_search_url(self, topics):
        for topic in topics:
            prefix_search_url = self.website.search_url
            for i in range(40):
                search_url = prefix_search_url + topic + "&location={}".format('Hong%20Kong%20SAR') + "&start=%d"%(int(25*i))
                if search_url not in self.search_urls:
                    self.search_urls.append(search_url)


    def make_page_complete(self, jobs_search_url):
        actions = ActionChains(self.browser)
        self.browser.get(jobs_search_url)
        time.sleep(random.uniform(0.5,2.5))
        current_in_view = 3
        base_css_selector = 'div.jobs-search-two-pane__job-card-container--viewport-tracking-'
        css_selector = base_css_selector + str(current_in_view)
        success = False
        while not success:
            try:
                element = self.browser.find_element_by_css_selector(css_selector)
                self.browser.execute_script("arguments[0].scrollIntoView();", element)
                success = True
                time.sleep(random.uniform(0.5,2.5))
            except:
                self.browser.get(jobs_search_url)
        while (current_in_view < 22):
            current_in_view += 3
            css_selector = base_css_selector + str(current_in_view)
            try:
                element = self.browser.find_element_by_css_selector(css_selector)
                self.browser.execute_script("arguments[0].scrollIntoView();", element)
                time.sleep(random.uniform(0.5,2.5))
            except:
                print("Cant find the element, something is wrong with the site")
                continue
        element = self.browser.find_element_by_css_selector('section.jobs-search-two-pane__pagination')
        actions.move_to_element(element)
        actions.perform()

    def get_jobs_details(self, jobs_search_url):
        self.make_page_complete(jobs_search_url)
        src = self.browser.page_source
        soup = BeautifulSoup(src, 'html.parser')
        links = soup.select("a.job-card-container__link ")
        while len(links)<2:
            time.sleep(random.uniform(0.5,2.5))
            self.make_page_complete(jobs_search_url) 
            src = self.browser.page_source
            soup = BeautifulSoup(src, 'html.parser')
            links = soup.select("a.job-card-container__link ")
        visited = []
        company_patterns = '/company/*'
        regex = re.compile(company_patterns)
        for li in links:
            url = li.attrs['href']
            if not regex.match(url) and url not in visited:
                visited.append(url)
                abs_link = "https://www.linkedin.com/" + url
                self.browser.get(abs_link)
                src = self.browser.page_source
                bs = BeautifulSoup(src, 'html.parser')
                times = 0
                success = False
                while times <= 15 and not success:
                    try:
                        title = bs.find('h1').get_text().strip()
                        rr = bs.find('div', {'class': 'mt2'})
                        try:
                            company = rr.find('a').get_text().strip()
                        except:
                            company = rr.find('span',class_='jobs-unified-top-card__subtitle-primary-grouping mr2 t-black').get_text().strip()
                        dt = bs.find('div', {'class': 'jobs-box__html-content jobs-description-content__text t-14 t-normal'}).get_text().strip()
                        success = True
                    except:
                        times += 1
                        time.sleep(random.uniform(0.5,2.5))
                        self.browser.get(abs_link)
                        src = self.browser.page_source
                        bs = BeautifulSoup(src, 'html.parser')
                if not success:
                    continue
                job = Job(title, company,dt)
                self.count_link += 1
                print("Job {}".format(self.count_link), end=': ')
                job.myprint()
                self.output = self.output.append({'title':job.title,'company':job.company,'detail':job.dt},ignore_index=True)
                time.sleep(random.uniform(0.5,2.5))

    def outputcsv(self,name):
        self.output.to_csv('%s.csv'%name,encoding="utf_8_sig")