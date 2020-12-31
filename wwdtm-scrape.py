#This is what I really want : all the wait wait episode podcast mp3 files (ideally between specified dates) downloaded!  I do it by hand and it's tedious.
#https://www.npr.org/podcasts/344098539/wait-wait-don-t-tell-me


# import libraries
import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import time
import pandas as pd
import calendar
import wget

#the XML paths for the various elements we want on the page
path_start = '//*[@id="podcast"]//*[@aria-label="main content"]//*[@id="wrapper"]//*[@id="main-section"]'
path_diff_main = '//*[@class="podcast-section episode-list"]'
path_diff_more = '//*[@class="podcast-section episode-list episode-list-infinite"]//*[@id="infinitescroll"]'
path_same_2 = '//*[@class="item podcast-episode"]//*[@class="item-info"]'
path_download = '//*[@class="bucketwrap resaudio"]//*[@class="audio-module"]//*[@class="audio-module-tools"]//*[@class="audio-module-more-tools"]//*[@class="audio-tool audio-tool-download"]'
path_date = '//*[@class="episode-date"]'

#Get dates from user
#Note that as of the writing of this program, the website archive only goes back to Aug. 28, 2014

dateon = 1
if(dateon):
    old_year = input("Enter start year:")
    old_month = input("Enter start month:")
    old_day = input("Enter start day:")

    new_year = input("Enter end year:")
    new_month = input("Enter end month:")
    new_day = input("Enter end day:")
    #basetime = calendar.timegm([2019,11,1,0,0,0])
        
    tmp = (int(old_year),int(old_month),int(old_day),0,0,0)
    start_date = calendar.timegm(tmp)
    
    tmp = (int(new_year),int(new_month),int(new_day),23,59,59)
    end_date = calendar.timegm(tmp)

today_date = calendar.timegm(time.localtime())
oldest_date = today_date
    

#Get podcast webpage
DRIVER_PATH = './browserdrivers/geckodriver'
browser = webdriver.Firefox(executable_path=DRIVER_PATH)

browser.get('https://www.npr.org/podcasts/344098539/wait-wait-don-t-tell-me')
time.sleep(5)

####click the more button on bottom of page until desired date range is reached
clicks = 0
date_list = []
ep_list = []
ep_array = []
more_button = browser.find_elements_by_xpath('//*[@id="podcast"]//*[@aria-label="main content"]//*[@id="wrapper"]//*[@id="main-section"]//*[@class="podcast-section episode-list episode-list-infinite"]//*[@id="infinitescrollwrap"]//*[@class="options has-more-results"]//*[@class="options__load-more"]')

scroll_to_bottom = "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;"


while(oldest_date > start_date):
    if(clicks == 0):
        #First, get list of dates on the main page
        date_list = browser.find_elements_by_xpath(path_start + path_diff_main + path_same_2 + path_date)
        clicks += 1
    else: #If the last date on the page is not far enough in the past, click the button
        #scroll to bottom of page 
        browser.execute_script(scroll_to_bottom)
        #click to get more
        action = ActionChains(browser)
        action.move_to_element(more_button[0])
        action.click()
        action.perform()
        #append to episode list (without addiding duplicates)! 
        time.sleep(2)
        date_list = [] #Blank the date list so that we will not have duplicates
        date_list = browser.find_elements_by_xpath(path_start + path_diff_main + path_same_2 + path_date) + browser.find_elements_by_xpath(path_start + path_diff_more + path_same_2 + path_date)
        clicks += 1
    #Go to end of episode list to find oldest date
    print(len(date_list))
    bottom=date_list[len(date_list)-1]
    datestring = bottom.find_element_by_tag_name('time').get_attribute('datetime')
    print(datestring)
    #convert string to time stamp
    dateparts = datestring.split('-')
    oldest_date = calendar.timegm([int(dateparts[0]),
                                   int(dateparts[1]),
                                   int(dateparts[2])
                                   ,0,0,0])
#Get list of episods (up to HTML common for both date and url)
ep_list = browser.find_elements_by_xpath(path_start + path_diff_main + path_same_2) +  browser.find_elements_by_xpath(path_start + path_diff_more + path_same_2)

#Extract the URL and date for each episode on the page
for i in ep_list:
    #https://stackoverflow.com/questions/14049983/selenium-webdriver-finding-an-element-in-a-sub-element
    x = i.find_element_by_xpath('.'+path_download)
    link = x.find_element_by_tag_name('a')
    url1 = link.get_attribute('href')
    datestring = i.find_element_by_xpath('.'+path_date).find_element_by_tag_name('time').get_attribute('datetime')
    ep_array.append([datestring,url1]) #Load the date and URL strings into an array
   
ep_num = len(ep_array)
print('Number of episodes on current page', ep_num)
print('Checking in range: ',start_date,' - ',end_date,'\n')

#Now that we have episodes loaded in array, we can check the dates and download the .mp3 files in our desired range
j = 0 #add a counter since some episodes have the same (innacurate) date
for episode in ep_array:
    #Get episode date
    ep_date = episode[0]
    #check if it is within desired range. If so, download
    
    dateparts = ep_date.split('-')
    ep_time = calendar.timegm([int(dateparts[0]),
                               int(dateparts[1]),
                               int(dateparts[2])
                               ,0,0,0])
    print('Checking episode date: ',ep_date,' (',ep_time,')')
    if((ep_time >= start_date) and (ep_time <= end_date)):
        print('Episode is withing range!')
        durl = episode[1]
        pos = durl.find(".mp3") + 4
        mp3_location = durl[0:pos]
        #Download file with date first (padded) to keep the order correct.
        wget.download(mp3_location,'./WWDTM/'+dateparts[0]
                      +dateparts[1].zfill(2)
                      +dateparts[2].zfill(2)+
                      '_WWDTM_'+str(j).zfill(3)+'.mp3')
        print('\n')
        j+=1
        #shot_num.zfill(3)

browser.close()

