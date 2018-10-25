from flask import Flask, request, session, redirect, url_for, abort, render_template, flash
from bs4 import BeautifulSoup
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
import smtplib

app= Flask(__name__)


app.config['DEBUG'] = True
app.config['SECRET_KEY'] ='super-secret-key'
app.config['USERNAME'] = 'admin'
app.config['PASSWORD'] = '12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///practicum.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
smtpObj = smtplib.SMTP('smtp.sendgrid.net',587)
smtpObj.login("apikey", "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")

db=SQLAlchemy(app)

class Login(db.Model):
    __tablename__ = 'users'
    email = db.Column(db.String(100), primary_key=True)
    username = db.Column(db.String(100),unique=True)
    password = db.Column(db.String(24))
    subscription = db.Column(db.String(100))

    def __init__(self, email,username, password, subscription):
        self.email = email
        self.username = username
        self.password = password
        self.subscription= subscription

    def __repr__(self):
        return '<Entry %r %r %r %r>' % (self.email,self.username, self.password, self.subscription)

class Tenders(db.Model):
    __tablename__ = 'tenders'
    S_No = db.Column(db.Integer, primary_key=True,unique=False)
    ePub = db.Column(db.DateTime())
    BidSub = db.Column(db.DateTime())
    TenderOpDate = db.Column(db.DateTime())
    Title = db.Column(db.String(100))
    Org = db.Column(db.String(100))

    def __init__(self, S_No,ePub, BidSub, TenderOpDate, Title, Org):
        self.S_No = S_No
        self.ePub = ePub
        self.BidSub = BidSub
        self.TenderOpDate= TenderOpDate
        self.Title= Title
        self.Org= Org

    def __repr__(self):
        return '<Entry %r %r %r %r %r %r>' % (self.S_No,self.ePub, self.BidSub, self.TenderOpDate, self.Title, self.Org)

db.create_all()


def authenticate(e, p):
    details= Login.query.filter_by(email=e).filter_by(password=p).all()
    if(len(details)>0):
        return True
    else:
        return False
# X=[]
# def fun(i):
#     f2=open("out/"+i+".html")
#     soup=BeautifulSoup(f2.read(),'lxml')
#     f2.close()
#     tb = soup.find_all("table",{"class":"list_table","id":"table"})
#     tl = tb[0].find_all("tr")

#     for x in range(1,len(tl)):
#         L={}
#         f = tl[x].find_all("td")
#         L['id']= f[0].text
#         L['ePublishedDate']= datetime.strptime(f[1].text, '%d-%b-%Y %I:%M %p')
#         L['BidSubmissionDate']= datetime.strptime(f[2].text, '%d-%b-%Y %I:%M %p')
#         L['TenderOpeningDate']= datetime.strptime(f[3].text, '%d-%b-%Y %I:%M %p')
#         L['Title']= f[4].text
#         L['Organisation']= f[5].text
#         print("The length of dictionary is "+str(len(X)))
#         # print("https://eprocure.gov.in"+f[4].find("a")['href'])
#         new_tender=Tenders(f[0].text,datetime.strptime(f[1].text, '%d-%b-%Y %I:%M %p'),datetime.strptime(f[2].text, '%d-%b-%Y %I:%M %p'),datetime.strptime(f[3].text, '%d-%b-%Y %I:%M %p'),f[4].text,f[5].text)
#         # print(new_tender)
#         db.session.add(new_tender)
#         db.session.commit()
#         X.append(L)
        
# for i in range(1,21):
#     fun(str(i))

def expired_tenders():
	t=[]
	time_now= datetime.now()
	k= Tenders.query.all()
	for a in k:
		if a.BidSub < time_now: 
			session.delete(a)

Orgz=[]
def org():
    Q=[]
    k= Tenders.query.order_by(Tenders.Org).all()
    for a in k:
        Q.append(a.Org)
    for b in Q:
        if b not in Orgz:
            Orgz.append(b)
    return Orgz

def tenders():
	return Tenders.query.all()

def user_emails():
	emails=[]
	users=  Login.query.all()
	for u in users:
		emails.append(u)
	return emails

def mail_body(a):
    t = Tenders.query.filter_by(Org=a).order_by(Tenders.BidSub.desc()).all()
    html_mailer="""
        MIME-Version: 1.0
        Content-type: text/html
        Subject: SMTP HTML e-mail test
        <table>\
          <thead>\
            <tr>\
              <th>S.No</th>\
              <th>e-Published Date</th>\
              <th>Bid Submission Closing Date</th>\
              <th>Tender Opening Date</th>\
              <th>Title and Ref.No./Tender Id</th>\
              <th>Organisation Name</th>\
            </tr>\
          </thead>\
          <tbody>"""
    print(t)
    for a in t:
        html_mailer+="<tr>"
        html_mailer+="<td>"+str(a.S_No)+"</td>"+"<td>"+str(a.ePub)+"</td>"+"<td>"+str(a.BidSub)+"</td>"+"<td>"+str(a.TenderOpDate)+"</td>"+"<td>"+str(a.Title)+"</td>"+"<td>"+str(a.Org)+"</td>"
    html_mailer+="</tr></tbody></table>"
    return html_mailer
@app.route('/test')
def test():
	return mail_body('Bharat Petroleum Corporation Limited')

def send_all_mails():
    A=Login.query.order_by(Login.email).all()
    if len(A)>0:
        for i in range(len(A)):
            user_email=A[i].email
            user_subscription=str(mail_body(A[0].subscription))
            smtpObj.sendmail("joelvinaykumar@gmail.com", str(user_email), user_subscription)
            print("Mail sent to "+user_email)
    else:
        print("Sorry. No users found")

@app.route('/send')
def send():
    send_all_mails()
    msg= "All mails are sent to users successfully!"
    return redirect('/')

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/tenders')
def tenders():
	all = Tenders.query.all()
	return render_template('tenders.html',all= all)

@app.route('/sign_up',methods=['GET','POST'])
def sign_up():
    error = None
    if request.method== 'GET':
        return render_template('sign_up.html', orgs=org())
    else:
        uname = request.form.get('username')
        email = request.form.get('email')
        pwd = request.form.get('pwd')
        rpwd = request.form.get('rpwd')
        sub = request.form.get('sel')

        if pwd==rpwd:
        	if email in user_emails():
        		success = "Email already in our records."
        		return render_template('sign_up.html',success=success)
        	else:
	            new_user = Login(email,uname,pwd,sub)
	            db.session.add(new_user)
	            db.session.commit()

	            success= "New account created for "+request.form.get('username')+"\nCheck your inbox."
	            # msg = Message('Message from Pheasant', sender = 'joelvinaykumar@riseup.net', recipients = [email])
	            # msg.body = "Hello,"+str(uname)+".\nWe've created an account for you.\nThank you for subscribing to"+str(sub)+".\nWe will keep you posted daily."
	            # mail.send(msg)
	            return render_template('sign_up.html',success=success)
        else:
            error= "Sorry, passwords don't match."
            return render_template('sign_up.html',error=error)

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if authenticate(request.form['email'], request.form['pwd']):
            session['logged_in'] = True
            a= request.form['email']
            session['log_user'] = Login.query.filter_by(email=a).one().username
            return redirect('/')
        else:
            error='Invalid credentials'
            return render_template('login.html',error=error)
    if request.method == 'GET':
   		return render_template('login.html')

@app.route('/logout')
def logout():
    if session['logged_in'] == True:
        session['logged_in'] = False
        return redirect('/')
    else:
        return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)