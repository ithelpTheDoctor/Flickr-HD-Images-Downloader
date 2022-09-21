import requests
import os
import json
import shutil
import re
import sys
from urllib.parse import urlparse,urljoin
import threading
import time

album_link = input('Album link \'username/albums/XXXXXXX\' : ')
album_id = re.search('photos/.*?/albums/(\d+)',album_link)
if not album_id:
    print('Not an album_link.')
    sys.exit(1)
album_id = album_id.groups()[0]

headers_html = {
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36 Edg/104.0.1293.54",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9",
    'referer':'https://www.google.com/'
}

r = requests.get(album_link,headers=headers_html)
if not r.status_code==200:
    print('Error 1, retry!')
    sys.exit(1)

source_text = r.text
api_key = re.search("flickr\.api\.site_key = \"(.*?)\"",r.text)
req_id = re.search("root\.reqId = \"(.*?)\"",r.text)
try:
    api_key = api_key.groups()[0]
    req_id = req_id.groups()[0]
except Exception as e:
    print(e)
    print('Error 2, retry!')
    sys.exit(1)
    
album_photos = {}

r = requests.get(f"https://api.flickr.com/services/rest?extras=can_addmeta%2Ccan_comment%2Ccan_download%2Ccan_print%2Ccan_share%2Ccontact%2Ccontent_type%2Ccount_comments%2Ccount_faves%2Ccount_views%2Cdate_taken%2Cdate_upload%2Cdescription%2Cicon_urls_deep%2Cisfavorite%2Cispro%2Clicense%2Cmedia%2Cneeds_interstitial%2Cowner_name%2Cowner_datecreate%2Cpath_alias%2Cperm_print%2Crealname%2Crotation%2Csafety_level%2Csecret_k%2Csecret_h%2Curl_sq%2Curl_q%2Curl_t%2Curl_s%2Curl_n%2Curl_w%2Curl_m%2Curl_z%2Curl_c%2Curl_l%2Curl_h%2Curl_k%2Curl_3k%2Curl_4k%2Curl_f%2Curl_5k%2Curl_6k%2Curl_o%2Cvisibility%2Cvisibility_source%2Co_dims%2Cpubliceditability%2Csystem_moderation&per_page=25&page=1&get_user_info=1&primary_photo_extras=url_c%2C%20url_h%2C%20url_k%2C%20url_l%2C%20url_m%2C%20url_n%2C%20url_o%2C%20url_q%2C%20url_s%2C%20url_sq%2C%20url_t%2C%20url_z%2C%20needs_interstitial%2C%20can_share&jump_to=&photoset_id={album_id}&viewerNSID=&method=flickr.photosets.getPhotos&csrf=&api_key={api_key}&format=json&hermes=1&hermesClient=1&reqId={req_id}&nojsoncallback=1")

 
json_data = r.json()['photoset']
total_pages = json_data['pages']
album_name = json_data['title']

for i in range(1,total_pages+1):
    r = requests.get(f"https://api.flickr.com/services/rest?extras=can_addmeta%2Ccan_comment%2Ccan_download%2Ccan_print%2Ccan_share%2Ccontact%2Ccontent_type%2Ccount_comments%2Ccount_faves%2Ccount_views%2Cdate_taken%2Cdate_upload%2Cdescription%2Cicon_urls_deep%2Cisfavorite%2Cispro%2Clicense%2Cmedia%2Cneeds_interstitial%2Cowner_name%2Cowner_datecreate%2Cpath_alias%2Cperm_print%2Crealname%2Crotation%2Csafety_level%2Csecret_k%2Csecret_h%2Curl_sq%2Curl_q%2Curl_t%2Curl_s%2Curl_n%2Curl_w%2Curl_m%2Curl_z%2Curl_c%2Curl_l%2Curl_h%2Curl_k%2Curl_3k%2Curl_4k%2Curl_f%2Curl_5k%2Curl_6k%2Curl_o%2Cvisibility%2Cvisibility_source%2Co_dims%2Cpubliceditability%2Csystem_moderation&per_page=25&page={i}&get_user_info=1&primary_photo_extras=url_c%2C%20url_h%2C%20url_k%2C%20url_l%2C%20url_m%2C%20url_n%2C%20url_o%2C%20url_q%2C%20url_s%2C%20url_sq%2C%20url_t%2C%20url_z%2C%20needs_interstitial%2C%20can_share&jump_to=&photoset_id={album_id}&viewerNSID=&method=flickr.photosets.getPhotos&csrf=&api_key={api_key}&format=json&hermes=1&hermesClient=1&reqId={req_id}&nojsoncallback=1")
    
    
    json_data = r.json()['photoset']
    
    quality_order = ['4k','3k','k','h','l', 'c', 'z', 'm', 'w', 'n', 's', 't', 'q', 'sq']
    
        
    for photo in json_data['photo']:
        best_image = None
        for quality in quality_order:
            try:
                best_image = photo[f"url_{quality}"]
                break
            except:
                pass
        "test" in best_image    
        album_photos[photo['id']] = {
            "photoid":photo['id'],
            "title":photo['title'],
            "image":best_image
        }
        
if not len(album_photos):
    print('No album photos found!')
    print('Please retry.')
    sys.exit(1)


dup_paths = {}
download_images = {}
for photo_id, photo_data in album_photos.copy().items():
    photo_name = re.sub('[\\/:*?"<>|]', '', photo_data['title']).strip()
    ext = os.path.basename(urlparse(photo_data['image'].lstrip('/')).path)
    ext = os.path.splitext(ext)[-1]
    if not ext:
        ext = ".jpg"
    fullpath = os.path.join("Flickr Albums",album_name,photo_name+ext)
    save_dir = os.path.dirname(fullpath)
    
    if not dup_paths.get(fullpath.lower()):          
        dup_paths[fullpath.lower()] = 1
        download_images[fullpath] = photo_data['image']
    else:
        cc = 1
        while True:
            fullpath = os.path.join(save_dir,photo_name+f"-{cc}"+ext)
            if not dup_paths.get(fullpath.lower()):          
                dup_paths[fullpath.lower()] = 1
                download_images[fullpath] = photo_data['image']
                break
            cc+=1
            
            
thread_limit = 0
def thread_download(url,savepath):
    global thread_limit
    
    try:
        r = requests.get(url,headers=headers_html)
        if r.status_code==200:
            if 'image' in r.headers.get('content-type',''):
                with open(savepath,'wb') as f:
                    f.write(r.content)
                print("Downloaded : ",url)
                
    except Exception as e:
        try:
            os.remove(savepath)
        except:       
            pass
            
    thread_limit-=1

print(f'Downloading found {len(download_images)} images.')
c = 0
for fullpath,link in download_images.items():
    save_dir = os.path.dirname(fullpath)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    if os.path.exists(fullpath):
        if os.path.getsize(fullpath):
            print("Exists : ",os.path.basename(fullpath))
            continue
        else:
            os.remove(fullpath)
                      
    threading.Thread(target=thread_download,kwargs={'url':link,'savepath':fullpath}).start()
    thread_limit+=1
    
    while thread_limit>6:
        time.sleep(.3)
    
while thread_limit>0:
    time.sleep(1)