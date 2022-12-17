from flask import *
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from firebase_admin import db
from firebase_admin import firestore
import requests
from bs4 import BeautifulSoup
import urllib.request
import product_info
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import difflib


cred = credentials.Certificate('e-commerce-price-tracker-firebase-adminsdk-c36t9-729193703a.json')

app = firebase_admin.initialize_app(cred,{
'databaseURL': 'https://e-commerce-price-tracker-default-rtdb.firebaseio.com'})

header={
    "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 FKUA/website/42/website/Desktop"
}
db2=firestore.client()
current_user=""
predict_disc={'clothing': 52.0,
 'furniture': 35.0,
 'footwear': 41.0,
 'pet': 34.0,
 'pens': 38.0,
 'home': 28.0,
 'baby': 40.5,
 'watches': 7.0,
 'sports': 24.0,
 'jewellery': 43.0,
 'bags,': 57.0,
 'mobiles': 54.0,
 'beauty': 14.0,
 'toys': 29.0,
 'kitchen': 54.0,
 'computers': 45.0,
 'automotive': 68.0,
 'tools': 15.0,
 'cameras': 30.0,
 'health': 26.5}

app = Flask(__name__)

def flipkart_image(url):
    ur=requests.get(url,headers=header)
    page = BeautifulSoup(ur.content,'html.parser')
    img=page.find_all("div",{"class":"CXW8mj _3nMexc"})

    image=str(img[0]).split("src=")[1].split(" ")[0]
    return image.replace('"','')

def amazon_image(url):
    ur=requests.get(url,headers=header)
    page = BeautifulSoup(ur.content,'html.parser')
    img=page.find_all("div",{"class":"imgTagWrapper"})
    image =str(img[0]).split("data-a-dynamic-image='{")[1].split(":[")[0]
    return image

    
def verify(email,password):
    global current_user
    uid=auth.get_user_by_email(email).uid
    ref = db.reference('')
    correct_pass=ref.get()['users'][str(uid)]['password']
    current_user=uid
    print("current user is :",current_user)
    return correct_pass==password

@app.route('/about.html', methods=['GET', 'POST'])
def about():
    return render_template('about.html')

@app.route('/Login', methods=['GET', 'POST'])
def Login():  
    email=request.form.get('UserName')
    password=request.form.get('password')
    if email!=None:
        try:
            if verify(email,password):
                print("Done")
                return addProduct();
        except:
            print('error')
            return render_template('notmatch.html');

    return render_template('Login.html'); 

@app.route('/signup.html', methods=['GET', 'POST'])
def signup():
    email=request.form.get('UserName')
    password=request.form.get('password')
    if email!=None:
        try:
            user=auth.create_user(email=email,password=password)
            ref = db.reference('')
            users_ref = ref.child('users')
            users_ref.update({
                str(user.uid):{
                'password':password
            }})

        except:
            print('Email already exist')
            

    return render_template('signup.html'); 

@app.route('/plot.png')
def plot_png(x,y):
    fig = create_figure(x,y)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

def create_figure(x,y):
    fig = Figure(figsize=[10,10])
    axis = fig.add_subplot(1, 1, 1)
    axis.plot(x,y)
    return fig

@app.route('/showgraph', methods=['GET', 'POST'])
def showgraph(graph):
    print(graph)
    doc_ref = db2.collection(u'products').document(graph).collection('daily price')
    date=[]
    price=[]
    for x in doc_ref.stream():
        date.append(x.id)
        d=doc_ref.document(x.id)
        dict=d.get().to_dict()
        p=dict["price"]
        price.append(p)
    print(date)
    print(price)
    return plot_png(date,price)

@app.route('/productList', methods=['GET', 'POST'])
def productList():
    
    doc_ref = db2.collection(u'products')
    doc_ref2 = db2.collection(u'users').document(current_user).collection('products')
    
    graph=request.form.get('graphbtn')
    # if graph in doc_ref.stream():
    for x in doc_ref.stream():
        if graph==x.id:
            print("GRAPH    :   ",graph)
            return showgraph(graph)
    info=[]
    # print("current user is :",current_user)
    for doc in doc_ref2.stream():
        d=doc_ref.document(doc.id)
        print(doc.id)
        dict=d.get().to_dict()

        discount=0
        for p in predict_disc:
            if difflib.SequenceMatcher(None, str(dict['category']).lower(),p).ratio() >= 0.5:
                discount=predict_disc[p]
                break
            else:
                discount=36.75
        predicted_price=(dict['M.R.P.']*discount)/100
        dict['predicted_price']=round(predicted_price)
        info.append(dict)
    return render_template('listproduct.html',info=info,discount=discount)
    
def addToDatabase(url,desired_price):
    product_info.add_to_firestore(url,current_user,desired_price,db2)

@app.route('/addProduct', methods=['GET', 'POST'])
def addProduct():
    url=request.form.get('productUrl')
    add=request.form.get('addUrl')
    desired_price=request.form.get('desired_price')

    imageUrl=""
    if url!=None:
        try:
            if "www.flipkart" in url:
                imageUrl=flipkart_image(url)
            else:
                imageUrl=amazon_image(url)
            print(imageUrl)
            if add=='add' and desired_price:
                print('added')
                addToDatabase(url,desired_price)
                imageUrl=""
        except Exception as e: 
            print(e)
            print('image error')

    return render_template('home.html',imageUrl=imageUrl)

@app.route('/')
def home():
    return Login()

if __name__ =="__main__":  
    app.static_folder='static'
    app.run(debug=True)  
