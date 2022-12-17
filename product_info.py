import requests
from bs4 import BeautifulSoup
from datetime import datetime

class Flipkart:
    def get_price(self,page):
        current = page.findAll("div",{"class" : "_30jeq3 _16Jk6d"})
        mrp = page.findAll("div",{"class" : "_3I9_wc _2p6lqe"})
        if len(mrp)==0:
            mrp=current
        price1=str(current[0].text).replace("₹","").replace(",","")
        price2=str(mrp[0].text).replace("₹","").replace(",","")
        return [int(price1),int(price2)] 


    def get_productTitle(self,page):
        productTitle = page.findAll("span",{"class" : "B_NuCI"})
        title = str(productTitle).split(">")
        return (title[1].replace("/",""))

    def get_category(self,page):
        productCategory = page.findAll("a",{"class" : "_2whKao"})
        category = str(productCategory[2]).split(">")[1].split("<")[0]
        return category

    def get_image(self,page):
        img=page.find_all("div",{"class":"CXW8mj _3nMexc"})
        image=str(img[0]).split("src=")[1].split(" ")[0]
        return image

class Amazon:
    def get_price(self,page):
        price_col=page.findAll("div",{"id":"apex_desktop"})
        price = price_col[0].findAll("span",{"class" : "a-offscreen"})
        current = str(price[0]).split("<")[1].split("₹")[1]
        if(len(price)>1):
            mrp = str(price[1]).split("<")[1].split("₹")[1]
        else:
            mrp=current
        convert_to_int=current.split(',')
        mrp_convert=mrp.split(",")
        price_int=""
        mrp_int=""
        for i in convert_to_int:
            price_int+=i
        for j in mrp_convert:
            mrp_int+=j
        return [int(float(price_int)),int(float(mrp_int))]

    def get_productTitle(self,page):
        productTitle = page.findAll("span",{"id" : "productTitle"})
        title = str(productTitle[0]).split(">")[1].split("<")
        return (title[0].replace(" ",''))

    def get_category(self,page):
        productCategory = page.findAll("a",{"class" : "a-link-normal a-color-tertiary"})
        category=str(productCategory[0]).split('>')[1].split('<')
        return (category[0].replace("\n","").strip())

    def get_image(self,page):
        img=page.find_all("div",{"class":"imgTagWrapper"})
        image =str(img[0]).split("data-a-dynamic-image='{")[1].split(":[")[0]
        return image

def add_to_firestore(url,user,desired_price,db):
    if "www.flipkart" in url:
        site=Flipkart()
        header={
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 FKUA/website/42/website/Desktop"
        }
    else:
        site=Amazon()
        header={
            'User-Agent':"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
        }

    ur = requests.get(url,headers=header)
    page = BeautifulSoup(ur.content,'html.parser')
    
    title = site.get_productTitle(page)
    price=site.get_price(page)
    category=site.get_category(page)
    image=site.get_image(page)
    image=image.replace('"','')

    doc_ref = db.collection(u'products').document(title.replace(" ","")[:50])
    doc_ref.set({
        'title':title,
        u'url': url,
        u'current_price': price[0],
        'M.R.P.':  price[1],
        'category': category,
        'image':image
    })

    doc_ref2 = doc_ref.collection('daily price').document(datetime.now().strftime("%d-%m-%y"))
    doc_ref2.set({
        'price': price[0]
    })

    doc_ref = db.collection(u'users').document(user).collection('products').document(title.replace(" ","")[:50])
    doc_ref.set({
        u'url': url,
        u'price_wanted': int(desired_price)
    })
