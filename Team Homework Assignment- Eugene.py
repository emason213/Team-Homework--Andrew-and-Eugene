#!/usr/bin/env python
# coding: utf-8

# In[130]:


# Dependencies
from bs4 import BeautifulSoup
import requests
import pymongo
import pandas as pd


# In[131]:


# Initialize PyMongo to work with MongoDBs
conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)


# In[132]:


# Define database and collection
db = client.craigslist_houses_db
collection = db.items


# In[133]:


# URL of page to be scraped
# craigslist homes for sale in McLean
url = 'https://washingtondc.craigslist.org/search/rea?query=mclean&availabilityMode=0&sale_date=all+dates'


# In[134]:


# Retrieve page with the requests module
response = requests.get(url)


# In[135]:


# Create BeautifulSoup object; parse with 'html.parser'
#soup = BeautifulSoup(response.text, 'html.parser')
#or
# Create BeautifulSoup object; parse with 'lxml'
soup = BeautifulSoup(response.text, 'lxml')


# In[136]:


# Examine the results, then determine element that contains sought info
print(soup.prettify())


# In[137]:


# results are returned as an iterable list
results = soup.find_all('li', class_="result-row")


# In[138]:


def url_to_address(url):
    try:             
        response = requests.get(url)
        soup2 = BeautifulSoup(response.text, 'lxml')
        results2 = soup2.find('div', class_="mapaddress").text
      
    except: 
        results2 = "no address"
            
            

    return results2
    


# In[139]:


for result in results:
    # Error handling
    try:
        # Identify and return title of listing
        title = result.find('a', class_="result-title").text
        # Identify and return price of listing
        price = result.a.span.text
        # Identify and return link to listing
        link = result.a['href']
        # identify the address
        address = url_to_address(link)
        
        # Print results only if title, price, and link are available
        if (title and price and link):
            print('-------------')
            print(title)
            print(price)
            print(link)
            print(address)
            
        #go to link, use request library to grab, make a new soup2, extract address from new page
        
        address = url_to_address(link)
        
             
          # Dictionary to be inserted as a MongoDB document
        post = {
                'title': title,
                'price': price,
                'url': link,
                'address': address
                   }

        collection.insert_one(post)
            
    except AttributeError as e:
        print(e)


# In[140]:


#url = 'https://washingtondc.craigslist.org/nva/reo/d/mc-lean-great-colonial-house-in-mclean/6825971559.html'
#response = requests.get(url)
#soup2 = BeautifulSoup(response.text, 'lxml')
#results2 = soup2.find('div', class_="mapaddress").text
#print(soup2.prettify())
#results2


# In[141]:


#url = 'https://washingtondc.craigslist.org/nva/reo/d/mc-lean-great-colonial-house-in-mclean/6825971559.html'
#url_to_address(url)


# In[172]:


#!pip install python-zillow
collection.count()


# In[143]:


import zillow

#with open("./bin/config/zillow_key.conf", 'r') as f:
 #   key = f.readline().replace("\n", "")



api = zillow.ValuationApi()


# In[144]:


import pprint


# In[145]:


#address = "6533 Sunny Hill Court"


# In[146]:


#data = api.GetSearchResults(key, address, postal_code)


# In[ ]:


#data.zestimate.amount


# In[147]:


db = client.zillow_market_db
collection2 = db.items

#collection.count()


# In[150]:


postal_code = "22102"
key = "X1-ZWz1gx8me6fbbf_a57uf"

for record in collection.find():
    try:
        
        #print(record["address"])
        list_address = record["address"]
        data = api.GetSearchResults(key, list_address, postal_code)

               # Dictionary to be inserted as a MongoDB document
        marketvalue = {
                    'address': list_address,
                    'zillow_price': data.zestimate.amount,
                          }

        collection2.insert_one(marketvalue)
            
    except:
        marketvalue = {
                'address': list_address,
                'zillow_price': -1,
                          }

        collection2.insert_one(marketvalue)
    
    


# In[ ]:





# In[153]:


for record in collection2.find():
    print(record)


# In[154]:


cursor = collection2.find()
# Expand the cursor and construct the DataFrame
df =  pd.DataFrame(list(cursor))
df


# In[155]:


#collection.delete_many({})


# In[156]:


#collection.count()


# In[158]:


df.head()


# In[171]:


df1 = df.groupby("address")["zillow_price"].mean()
df1 = pd.DataFrame(df1)
df1 = df1.reset_index()
df1.sort_values(by = "zillow_price", ascending=False)


# In[ ]:





# In[185]:


cursor = collection.find()
# Expand the cursor and construct the DataFrame
df_cl =  pd.DataFrame(list(cursor))
df_cl.head()
df_cl = df_cl.groupby("address").first()
df_cl


# In[202]:


df_merge = pd.merge(df1, df_cl, how="left", on="address")
df_merge.sort_values("zillow_price", ascending=False)
#make sure price is not an integar
df_merge["price"] = df_merge["price"].apply(lambda x: int(x.replace("$","")))
df_merge.head()
df_merge["price difference"] = df_merge["zillow_price"] - df_merge["price"]
df_merge.sort_values("price difference", ascending=False)


# In[ ]:





# In[ ]:




