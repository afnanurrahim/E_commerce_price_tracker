import smtplib
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import auth

cred = credentials.Certificate('e-commerce-price-tracker-firebase-adminsdk-c36t9-729193703a.json')
app = firebase_admin.initialize_app(cred)

users=auth.list_users()
db= firestore.client()
for u in users.users:
    # print(u.uid)
    doc_user = db.collection(u'users').document(str(u.uid)).collection('products')
    doc_prod = db.collection(u'products')
    for d in doc_user.stream():
        info=doc_prod.document(d.id).get().to_dict()
        user_product=doc_user.document(d.id).get().to_dict()
        if(info['current_price']<=user_product['price_wanted']):
            print('send email')
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls()
            s.login("pricetracker46@gmail.com", "lboaupozwbxoylqn")
            message = f"Greetings from price tracker \n\n We are here to inform you that your product {info['title']} has reached your desired price of {user_product['price_wanted']} \n\n\n Click on the url given below to purchase the product\n {info['url']}"
            s.sendmail("pricetracker46@gmail.com", u.email, message)
            s.quit()
