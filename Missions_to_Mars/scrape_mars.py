from splinter import Browser
from bs4 import BeautifulSoup as bs
import time
import pandas as pd


def init_browser():
    executable_path = {"executable_path": "/Users/ebk/Downloads/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)


def scrape():
    browser = init_browser()

    # --- Visit Mars News site ---
    browser.visit('https://mars.nasa.gov/news/')

    time.sleep(1)

    # Scrape page into Soup
    html = browser.html
    soup = bs(html, "html.parser")

    # Get the first news title
    title_results = soup.find_all('div', class_='content_title')
    news_title = title_results[0].text

    # Get the corresponding paragraph text
    p_results = soup.find_all('div', class_='article_teaser_body')
    news_p = p_results[0].text


    
    # --- Visit JPL site for featured Mars image ---
    browser.visit('https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars')

    time.sleep(1)

    # Click through to full image
    browser.click_link_by_partial_text('FULL IMAGE')
    time.sleep(2)
    browser.click_link_by_partial_text('more info')

    # Scrape page into Soup
    html = browser.html
    soup = bs(html, 'html.parser')

    # Search for image source
    results = soup.find_all('figure', class_='lede')
    relative_img_path = results[0].a['href']
    featured_img = 'https://www.jpl.nasa.gov' + relative_img_path



    # --- Visit Mars Weather Twitter Account ---
    browser.visit('https://twitter.com/marswxreport?lang=en')
    
    time.sleep(1)
    
    # Scrape page into Soup
    html = browser.html
    soup = bs(html, 'html.parser')

    # Search for tweets
    results = soup.find_all('p', class_="TweetTextSize")

    # Grab text of first tweet
    mars_weather = results[0].text
    

    # --- Use Pandas to scrape Mars Space Facts ---
    tables = pd.read_html('https://space-facts.com/mars/')

    # Take second table for Mars facts
    df = tables[1]

    # Rename columns and set index
    df.columns=['description', 'value']
    
    # Convert table to html
    mars_facts_table = df.to_html(classes='data table', index=False, header=False, border=0)



    # --- Visit USGS Astrogeology Site ---
    browser.visit('https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars')
    
    time.sleep(1)
    
    # Scrape page into Soup
    html = browser.html
    soup = bs(html, 'html.parser')

    hemi_names = []

    # Search for the names of all four hemispheres
    results = soup.find_all('div', class_="collapsible results")
    hemispheres = results[0].find_all('h3')

    # Get text and store in list
    for name in hemispheres:
        hemi_names.append(name.text)

    # Search for thumbnail links
    thumbnail_results = results[0].find_all('a')
    thumbnail_links = []

    # Iterate through thumbnail links for full-size image
    for thumbnail in thumbnail_results:
        
        # If the thumbnail element has an image...
        if (thumbnail.img):
            
            # then grab the attached link
            thumbnail_url = 'https://astrogeology.usgs.gov/' + thumbnail['href']
            
            # Append list with links
            thumbnail_links.append(thumbnail_url)
    
    full_imgs = []

    for url in thumbnail_links:
        
        # Click through each thumbanil link
        browser.visit(url)
        
        html = browser.html
        soup = bs(html, 'html.parser')
        
        # Scrape each page for the relative image path
        results = soup.find_all('img', class_='wide-image')
        relative_img_path = results[0]['src']
        
        # Combine the reltaive image path to get the full url
        img_link = 'https://astrogeology.usgs.gov/' + relative_img_path
        
        # Add full image links to a list
        full_imgs.append(img_link)

    # Zip together the list of hemisphere names and hemisphere image links
    mars_hemi_zip = zip(hemi_names, full_imgs)

    hemisphere_image_urls = []

    # Iterate through the zipped object
    for title, img in mars_hemi_zip:
        
        mars_hemi_dict = {}
        
        # Add hemisphere title to dictionary
        mars_hemi_dict['title'] = title
        
        # Add image url to dictionary
        mars_hemi_dict['img_url'] = img
        
        # Append the list with dictionaries
        hemisphere_image_urls.append(mars_hemi_dict)
    

    # Store data in a dictionary
    mars_data = {
        "news_title": news_title,
        "news_paragraph": news_p,
        "featured_image": featured_img,
        "weather": mars_weather,
        "mars_facts": mars_facts_table,
        "hemispheres": hemisphere_image_urls
    }

    # Close the browser after scraping
    browser.quit()

    # Return results
    return mars_data