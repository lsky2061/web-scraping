def astrid_shot_scrape():

#https://www.scrapingbee.com/blog/selenium-python/
    #https://towardsdatascience.com/data-science-skills-web-scraping-javascript-using-python-97a29738353f
    
    # import libraries
    import urllib.request
    from bs4 import BeautifulSoup
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver import ActionChains
    import time
    import pandas as pd
    import calendar
    import dateutil.parser as dp
    #import wget
    
    #Since the webpage seems limited in the number of results, I need to break the search up into time chunks.
    
    basetime = calendar.timegm([2019,11,1,0,0,0])
    timestep = 30*24*3600
    finaltime = calendar.timegm([2020,7,3,0,0,0])
    
    
    #urlpage = 'http://redditsearch.io/?term=astrid%20shot%20of%20the%20day&dataviz=false&aggs=false&subreddits=httyd&searchtype=posts&search=true&start=1572588000&end=1577775600&size=300'

    
    
    DRIVER_PATH = './browserdrivers/geckodriver'
    driver = webdriver.Firefox(executable_path=DRIVER_PATH)
    
    # create empty array to store data
    shot_label = []
    file_name = []
    data = []
    
    for t in range(basetime,finaltime,timestep):
        start = t
        end_t = start + timestep
        if(end_t > finaltime): end_t = finaltime
        
        #driver.get("http://redditsearch.io/")
        #http://redditsearch.io/?term=astrid%20shot%20of%20the&dataviz=false&aggs=false&subreddits=httyd&searchtype=posts&search=true&start=1574319600&end=1574578800&size=100
        
        #urlpage = 'http://redditsearch.io/?term=astrid%20shot%20of%20the%20day&dataviz=false&aggs=false&subreddits=httyd&searchtype=posts&search=true&start='+str(start)+'&end='+str(end_t)+'&size=300'
        urlpage = 'http://redditsearch.io/?term=astrid%20shot%20of%20the&dataviz=false&aggs=false&subreddits=httyd&searchtype=posts&search=true&start='+str(start)+'&end='+str(end_t)+'&size=300'
        print('Pincer 1.0  ',urlpage,'\n')
        driver.get(urlpage)
        print('Pincer 2.0 \n')
        time.sleep(10)
        
        
        #https://www.youtube.com/watch?v=QTLDEjvdoOs
        #Search term is: id="sterm"
        #Subreddit is: id="ssubreddits"
        #//
        
        #driver.find_element_by_id("sterm").send_keys("Astrid shot of the day")
        #driver.find_element_by_id("ssubreddits").send_keys("httyd")
        
        
        #time.sleep(5)
        
        #driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        
        #We can inspect the element of interest and within the toolbar, right-click on the highlighted element and Copy > Copy xpath (or Copy Selector). This is another interesting way to understand the structure of the html. In this case we will be using the xpath to find the elements, and we can then print the number of results that match:
        
        #results = driver.find_elements_by_xpath("//*[@class=' co-product-list__main-cntr']//*[@class=' co-item ']//*[@class='co-product']//*[@class='co-item__title-container']//*[@class='co-product__title']")
        

        results = driver.find_elements_by_xpath("//*[@id='results-container']//*[@id='posts']//*[@class='submission']//*[@class='content']")
        #("//*[@class='title']")
        print('Number of results', len(results))

        #ADD FUNCTIONALITY TO GET MORE EXACT TIME OF POSTING

        # loop over results
        for result in results:
            title = result.find_element_by_xpath(".//*[@class='title']")
            post_info = title.text
            
            datestamp = result.find_element_by_xpath(".//*[@class='description']//*[@class='date']")
            datetext = datestamp.get_attribute("title")
            #https://stackoverflow.com/questions/27245488/converting-iso-8601-date-time-to-seconds-in-python
            parsed_date = dp.parse(datetext)
            parsed_epoch = int(parsed_date.strftime('%s'))
            

            print(title.text,' ',datetext)
            
            if(('Astrid shot of the day #' in post_info) or
               ('Astrid shot of the #' in post_info)):
                f = title.get_attribute("data-url")
                shot_label.append(post_info)
                tmp = post_info.split('#')
                shot_num = tmp[1]
                file_name.append(f)
                print(f)
                data.append({"post title" : post_info, "number" : shot_num, "file_location" : f, "Time (ISO)" : datetext, "Time (Linux epoch)" : parsed_epoch})
                
                #link = result.find_element_by_tag_name('div')
                #post_line = link.get_attribute('data-url')
                #print(post_line,'\n \n')
                #product_name = result.text
                #link = result.find_element_by_tag_name('a')
                #product_link = link.get_attribute("href")
                # append dict to array
                #data.append({"product" : product_name, "link" : product_link})
                
                # sleep for 2s
                #time.sleep(2)
            print('pincer 4.0')
            #driver.quit()
                
    driver.quit()
    df = pd.DataFrame(data)
    print(df)
    # write to csv
    df.to_csv('ASOD_archive.csv')
                

        
        #Make sure we capture all of the relevant results
        
        
        #Get image from website
        #https://stackabuse.com/download-files-with-python/
        
#Save with appropriate name
#for s in range(0,len(shot_label)-1):
#    print(shot_label[s],'  ',file_name[s],'\n')
#    if('#' in shot_label[s]):
#        tmp = shot_label[s].split('#')
#        shot_num = tmp[1]
#        print(shot_num,'\n');
#        pad_num = shot_num.zfill(3)
#        out_name = 'ASOD_'+pad_num
#        print(out_name,'\n')
#        urllib.request.urlretrieve(file_name[s],'./ASOD_archive/'+out_name+'.jpg')
#    else:
#        print('PROBLEM:  ',shot_label[s],'  ',file_name[s],'\n')


def clean_download():
    import pandas as pd
    import requests
    import wget
    
    print('starting...')
    #import csv file and load into data frame
    ASOD_data = pd.read_csv('./ASOD_archive.csv')
    #sort by shot number
    ds = pd.DataFrame.sort_values(ASOD_data,'number')
    print(ds)
    #remove files that generate errors or don't exist
    dimension = ds.shape
    rows = dimension[0]
    ## loop through all rows in data frame
################
    zz = 1
    if(zz):
        for i in range(0,rows-1):
            url = ds.at[i,"file_location"]
            shot_num = ds.at[i,"number"]
            r = requests.head(url)
            ## if the wget results in an error, remove that row
            if(not r.ok):
                ds = ds.drop(i)
                print("Removed index ",i, "(shot number ",shot_num,") because file ",url," is not OK\n")
                
#########
    print(ds.shape)
    dimension = ds.shape
    rows = dimension[0]

    #identify missing numbers
    max_shot_num = ds["number"].max()
    missing = []
    
    
    for j in range(1,max_shot_num+1):
        if(not(j in ds["number"].values)):
            print("Missing number: ",j)
            missing.append(j)
            
    
    #identify duplicates
    vc = ds["number"].value_counts()
    duplicate_list = vc[vc>1]
    #print(duplicate_list)
    
    #for special cases, change the number
    #Loop through all missing numbers; if duplicate is adjacent to a missing number, change one of the duplicates to one of the missing numbers, but which one to change? We will need time information for that. Change so that the new numerical order matches the time order.
    for m in missing:
        dmm = -1 #duplicate matching missing
        if (m+1 in duplicate_list) or  (m-1 in duplicate_list):
            if m+1 in duplicate_list:
                dmm = m+1
                print('Missing number is one greater than the duplicate')
            if m-1 in duplicate_list:
                dmm = m-1
                print('Missing number is one less than the duplicate')

            print(m,' is missing, but ',dmm,' is duplicated, implying that one of the instances of ',dmm,' should be changed to ',m)
            dd = ds[ds["number"] == dmm]
            dds = pd.DataFrame.sort_values(dd,'Time (Linux epoch)') #sort the list of duplicates
            dimension = dds.shape
            rows = dimension[0]
            change_time = dds.iloc[rows-1,5] #this is true if dmm = m+1 (our missing number is one more than the duplicate
            if(dmm == m-1): change_time = dds.iloc[0,5]

            #Now, change the actual shot number in the sorted and cleaned data set
            ds.loc[ds["Time (Linux epoch)"] == change_time, "number"] = m
            missing.pop(missing.index(m))#Remove this item from the missing list

    print('Missing ASOD: ',missing)

    #write cleaned and sorted data frame to a new csv file
    ds.to_csv("ASOD_archive_clean.csv")

    #Download all files with convetion ASOD_NNN.jpg
    dimension = ds.shape
    rows = dimension[0]
    for i in range(rows):
        num = ds.iloc[i,2]
        url = ds.iloc[i,3]
        wget.download(url,'./ASOD_output/ASOD_'+str(num).zfill(3)+'.jpg')
        
        
