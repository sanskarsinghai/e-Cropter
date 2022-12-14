from flask import Flask, render_template, request, redirect,flash,session
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import json
import requests
import time
import math
from datetime import datetime
import hashlib
import requests
import pandas as pd
import itertools
from sklearn.preprocessing import OrdinalEncoder
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
import csv

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super secret key'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///feedback.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)

# em=""
# pa=""

class ContactUs(db.Model):
    sno=db.Column(db.Integer, primary_key=True)
    fname=db.Column(db.String(20), nullable=False)
    lname=db.Column(db.String(20), nullable=False)
    gender=db.Column(db.String(7), nullable=False)
    phone=db.Column(db.Integer, nullable=False)
    email=db.Column(db.String(20), nullable=False)
    msg=db.Column(db.String(500), nullable=False)
    response=db.Column(db.String(500), nullable=True)

class registration(db.Model):
    sno=db.Column(db.Integer, primary_key=True)
    fname=db.Column(db.String(20), nullable=False)
    lname=db.Column(db.String(20), nullable=False)
    gender=db.Column(db.String(7), nullable=False)
    phone=db.Column(db.Integer, nullable=False)
    email=db.Column(db.String(50), nullable=False)
    role=db.Column(db.String(10),nullable=False)
    status=db.Column(db.String(10),nullable=False)
    password=db.Column(db.String(20), nullable=False)
    
class weather(db.Model):
    sno=db.Column(db.Integer, primary_key=True) 
    Email=db.Column(db.String(50), nullable=False)
    City=db.Column(db.String(20), nullable=False)
    Longitude=db.Column(db.String(20), nullable=False)
    Latitude=db.Column(db.String(20), nullable=False)
    Weather=db.Column(db.String(20), nullable=False)
    Temperature=db.Column(db.String(20), nullable=False)
    Feels_Like=db.Column(db.String(20), nullable=False)
    Pressure=db.Column(db.String(20), nullable=False)
    Humidity=db.Column(db.String(20), nullable=False)
    Wind=db.Column(db.String(20), nullable=False)
    Time=db.Column(db.String(20), nullable=False)

class feedback(db.Model):
    sno=db.Column(db.Integer, primary_key=True) 
    Email=db.Column(db.String(20), nullable=False)
    Feedb=db.Column(db.String(50), nullable=False)
    Time=db.Column(db.String(20), nullable=False)

class cropdetails(db.Model):
    Sno=db.Column(db.Integer, primary_key=True)
    Crop=db.Column(db.String(20), nullable=False)
    Details=db.Column(db.String(500), nullable=False)
    ImgName=db.Column(db.String(30), nullable=False)
         
class graphd(db.Model):
    Sno=db.Column(db.Integer, primary_key=True)
    Crop=db.Column(db.String(20), nullable=False)
    p2006_7=db.Column(db.String(10), nullable=False)
    p2007_8=db.Column(db.String(10), nullable=False)
    p2008_9=db.Column(db.String(10), nullable=False)
    p2009_10=db.Column(db.String(10), nullable=False)
    p2010_11=db.Column(db.String(10), nullable=False)
    y2006_7=db.Column(db.String(10), nullable=False)
    y2007_8=db.Column(db.String(10), nullable=False)
    y2008_9=db.Column(db.String(10), nullable=False)
    y2009_10=db.Column(db.String(10), nullable=False)
    y2010_11=db.Column(db.String(10), nullable=False)

@app.route("/admin/",methods=["GET","POST"])
def adminlogin():
    # global em,pa
    if 'un' in session:
        flash("You are already login","success")
        return render_template('admin/home.html')

    if request.method=="POST":
        username=request.form['email']
        password=request.form['password']
        
        if username=="" or password=="":
            flash("Please Enter Email or Password","warning")
            return redirect("/admin/")
        
        if username=='Admin' and password=='Admin':
            session['un']='Admin'
            return redirect("/admin/home")
        else:
            return redirect("/admin/")

    return render_template("admin/login.html")


@app.route("/admin/home")
def adminhome():
    if 'un' in session:
        return render_template("/admin/home.html")
    else:
        return redirect("/admin/")

@app.route("/admin/users")
def users():
    if 'un' in session:
        allfeed=registration.query.filter_by(role='User').all()
        return render_template("admin/Users.html",allfeed=allfeed)
    else:
        return redirect("/admin/")

@app.route("/admin/status/<string:email>")
def status(email):
    if 'un' in session:
        s=registration.query.filter_by(email=email).first()
        if s.status=="Unblocked":
            s.status="Blocked"
        else:
            s.status="Unblocked"
        a=s.status
        db.session.add(s)
        db.session.commit()
        flash(email+" is "+a+" successfully","success")
        return redirect("/admin/users")

@app.route("/admin/profile/<string:email>")
def pro(email):
    if 'un' in session:
        r=registration.query.filter_by(email=email).first()
        f=feedback.query.filter_by(Email=email).all()
        c=ContactUs.query.filter_by(email=email).all()
        w=weather.query.filter_by(Email=email).all()
        return render_template("admin/UserProfile.html",r=r,f=f,c=c,w=w)

@app.route("/admin/Feedbacks")
def feed():
    if 'un' in session:
        f=feedback.query.all()
        return render_template("/admin/feedbacks.html",f=f)
    else:
        return redirect("/admin")

@app.route("/admin/Queries")
def quer():
    if 'un' in session:
        c=ContactUs.query.all()
        return render_template("admin/queries.html",c=c)
    else:
        return redirect("/admin")

@app.route("/admin/delete/<string:email>/<int:sno>")
def delete(email,sno):
    # if em !="" and pa !="":   
    if 'un' in session:
        f=feedback.query.filter_by(Email=email,sno=sno).first()
        db.session.delete(f)
        db.session.commit()
        flash(email+" feedback is successfully deleted","success")
        return redirect('/admin/users')
    else:
        return redirect("/admin")

@app.route("/admin/response/<string:email>/<int:sno>",methods=['GET','POST'])
def resp(email,sno):
    # if em !="" and pa !="":   
    if 'un' in session:
        if request.method=='POST':
            r=request.form['response']
            c=ContactUs.query.filter_by(email=email,sno=sno).first()
            c.response=r
            db.session.add(c)
            db.session.commit()
            flash(email+" response send is successfully","success")
        return redirect('/admin/users')
    else:
        return redirect("/admin")


@app.route("/",methods=["GET","POST"])
def login():
    # global em,pa
    if 'email' in session:
        flash("You are already login","success")
        return render_template('home.html')

    if request.method=="POST":
        email=request.form['email']
        password=request.form['password']
        
        if email=="" or password=="":
            flash("Please Enter Email or Password","warning")
            return redirect("/")
        
        p = hashlib.md5(password.encode())

        lo=registration.query.filter_by(email=email).first()

        if lo is None:
            flash("You may have not signed up!!")
            return redirect("/")
        elif lo.status=="Blocked":
                flash(lo.email+" is blocked by our admin!!")
                return redirect("/")
        elif lo.password!=p.hexdigest():
            flash("Invalid Password entered")
            return redirect("/")
        else:
            session['email']=lo.email
            session['role']=lo.role
            return redirect("/home")
            
    return render_template("login.html")

@app.route("/signup",methods=["GET","POST"])
def signup():

    if 'email' in session:
        flash("You are already login","success")
        return render_template('home.html')


    if request.method=="POST":
        fname=request.form['fname']
        lname=request.form['lname']
        gender=request.form['gender']
        phone=request.form['phone']
        email=request.form['email']
        password=request.form['password']
        conpassword=request.form['conpassword']

        c=registration.query.filter_by(email=email).first()
        if c is not None:
            flash("Email already register")
            return redirect("/signup")
        
        elif password!=conpassword:
            flash("New and Confirm password are not matched")
            return redirect("/signup")
        elif len(phone)!=10:
            flash("Invalid phone number")
            return redirect("/signup")
        else:
            p = hashlib.md5(password.encode())
            log=registration(fname=fname,lname=lname,gender=gender,phone=phone,email=email,password=p.hexdigest(),role="User",status="Unblocked")
            db.session.add(log)
            db.session.commit()
            flash("Successfully Sign Up","success")
            return redirect("/")
        
    return render_template("register.html")

@app.route("/logout")
def logout():
    if 'email' in session:
      session.pop('email')
      return redirect("/")
    elif 'un' in session:
        session.pop('un')
        return redirect("/admin")

@app.route("/profile")
def profile():
    if 'email' in session:
        lo=registration.query.filter_by(email=session['email']).first()
        return render_template("profile.html",lo=lo)
    else:
        return redirect("/")

@app.route("/profileupdate",methods=["GET","POST"])
def profileupdate():
    if 'email' in session:
        if request.method=='POST':
            fname=request.form['fname']
            lname=request.form['lname']
            gender=request.form['gender']
            phone=request.form['phone']
            cpass=request.form['cpassword']
            npass=request.form['npassword']
            copass=request.form['copassword']

            re=registration.query.filter_by(email=session['email']).first()
            
            if cpass!="":
                c=hashlib.md5(cpass.encode())
                if c.hexdigest()!=re.password:
                    flash("Invalid Current Password","warning")
                    return redirect("/profile")
                else:
                    if npass=="":
                        flash("New password is empty string","warning")
                        return redirect("/profile")
                    
                    elif npass!=copass:
                        flash("New and Confirm password does not matched","warning")
                        return redirect("/profile")
                    n=hashlib.md5(npass.encode())
                    re.password=n.hexdigest()            
            re.fname=fname
            re.lname=lname
            re.gender=gender
            re.phone=phone

            db.session.add(re)
            db.session.commit()
            flash("Your profile is successfully updated","success")

            return redirect('/profile')

    else:
        redirect("/")

@app.route("/home")
def home():
    # if em !="" and pa !="":
    if 'email' in session:
        return render_template("home.html")
    else:
        return redirect("/")

@app.route("/currentwea",methods=['GET','POST'])
def currentwea():
    # if em !="" and pa !="":
    if 'email' in session:
        im=""
        co=""
        if request.method=='POST':
            c=request.form['city']
            url="https://api.openweathermap.org/data/2.5/weather?appid=850789bc308ec795c19f9f4df7ed367d&q="+c
               
            d=requests.get(url).json()
            l=dict(d)
            if l['cod']!='404':
                t=time.strftime('%H:%M:%S', time.gmtime(l['dt']-l['timezone']))
                l['dth']=t
                l['main']['temp']=round(l['main']['temp']-273.15,2)

                we=weather(Email=session['email'],City=l['name'],Longitude=l['coord']['lon'],Latitude=l['coord']['lon'],Weather=l['weather'][0]['main'],Temperature=(l['main']['temp']-273.15),Feels_Like=(l['main']['feels_like']-273.15),Pressure=l['main']['pressure'],Humidity=l['main']['humidity'],Wind=l['wind']['speed'],Time=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                db.session.add(we)
                db.session.commit()
                    
                if l['weather'][0]['main']=="Clear":
                    im="Clear Sky.jpeg"
                    co="black"
                elif l['weather'][0]['main']=="Snow" or l['weather'][0]['main']=="Winter":
                    im="Winter.jpeg"
                    co="black"
                elif l['weather'][0]['main']=="Sunny":
                    im="Sunny.jpeg"
                    co="black"
                elif l['weather'][0]['main']=="Cloudy" or l['weather'][0]['main']=="Smoke" or l['weather'][0]['main']=="Clouds":
                    im="Cloudy.jpeg"
                    co="white"
                elif l['weather'][0]['main']=="Rainy":
                    im="Rainy.jpeg"
                    co="white"
                else:
                    im="General.jpeg"
                    co="white"

            return render_template("currentwea.html",l=l,im=im,co=co)

        return render_template("currentwea.html",l={'0':0},c='black')
    else:
        return redirect("/")

@app.route("/history")
def history():
    if 'email' in session:
        c = weather.query.filter_by(Email=session['email']).all()
        last = math.ceil(len(c)/3)
        print(last)
        page = request.args.get('page')
        if (not str(page).isnumeric()):
            page = 1
        page = int(page)
        c = c[(page-1)*3:(page-1)*3+ 3]
        
        if last==1:
            prev = "#"
            next = "#"
        elif page==1:
            prev = "#"
            next = "/history?page="+ str(page+1)
            flash("Your are on latest history search","info")
            
        elif page==last:
            prev = "/history?page="+ str(page-1)
            next = "#"
            flash("Your are on oldest history search","info")
        else:
            prev = "/history?page="+ str(page-1)
            next = "/history?page="+ str(page+1)
        
        return render_template('history.html',allfeed=c, prev=prev, next=next)
    else:
        return redirect("/")
    

@app.route("/deletehistory/<int:sno>")
def deletehistory(sno):
    # if em !="" and pa !="":   
    if 'email' in session:
        feed=weather.query.filter_by(Email=session['email'],sno=sno).first()
        db.session.delete(feed)
        db.session.commit()
        flash("History is successfully deleted","success")
        return redirect('/history')
    else:
        return redirect("/")

@app.route("/forecast",methods=['GET','POST'])
def forecast():
    # if em !="" and pa !="":
    if 'email' in session:
    
        if request.method=='POST':
            c=request.form['city']
            
            url="https://api.weatherbit.io/v2.0/forecast/daily?city="+c+"&key=a6a52896bb4b4e5db0316789bb323bd2"
            data=requests.get(url).json()

            d=list()

            for i in range(0,len(data['data'])):
                    t=list()
                    t.append(data['data'][i]['temp'])
                    t.append(data['data'][i]['pres'])
                    t.append(data['data'][i]['rh'])
                    t.append(data['data'][i]['wind_spd'])
                    t.append(data['data'][i]['valid_date'])
                    d.append(t)
                    
                
            return render_template("forecast.html",l=data,d=d)
        return render_template("forecast.html",l={'0':0},c='black')
    else:
        return redirect("/")

@app.route("/crop",methods=['GET','POST'])
def crop():
    if 'email' in session:
        return render_template("crop.html",l={'cod':0},c='black')
    else:
        return redirect("/")

@app.route("/cropprediction",methods=['GET','POST'])
def cropprediction():
    # if em !="" and pa !="":
    if 'email' in session:
        im=""
        co=""
        if request.method=='POST':
            c=request.form['city']
            n=request.form['Nitrogen']
            p=request.form['Phosphorus']
            k=request.form['Potassium']
            ph=request.form['PH Level']
            
            a=dict()
            a['cod']=0
            
            if 0>float(n) or float(n)>150:
                flash("Value of Nitrogen must be in between 0 to 150 !!","warning")
                return render_template("crop.html",l=a)
            elif 5>float(p) or float(p)>250:
                flash("Value of Phosphorus must be in between 5 to 250 !!","warning")
                return render_template("crop.html",l=a)
            elif 5>float(k) or float(k)>220:
                flash("Value of Potassium must be in between 5 to 220 !!","warning")
                return render_template("crop.html",l=a)
            elif 0>float(ph) or float(ph)>14:
                flash("Value of PH must be in between 0 to 14 !!","warning")
                return render_template("crop.html",l=a)

            #url = "https://api.openweathermap.org/data/2.5/forecast?q="+c+"&exclude=minutely,hourly&appid=850789bc308ec795c19f9f4df7ed367d"
            url="https://api.weatherbit.io/v2.0/forecast/hourly?city="+c+"&key=a6a52896bb4b4e5db0316789bb323bd2&hours=240"    

            d=requests.get(url).json()
            myjson=dict(d)
                
            # if d['cod']=='404':
            #     return render_template("crop.html",se=session['logo'],l=d)
               

            temperature = []
            humidity = []
            rainfall = [] 

            # for i in range(0,len(myjson['list'])):
            #     temperature.append(round(myjson['list'][i]['main']['temp']-273.2))
            #     humidity.append(myjson['list'][i]['main']['humidity'])
            #     if "rain" not in myjson['list'][i]:
            #         rainfall.append(0)
            #     else:
            #         rainfall.append(round(myjson['list'][i]['rain']['3h']))    


            for i in range(0,len(myjson['data'])):
                temperature.append(round(myjson['data'][i]['temp']))
                humidity.append(myjson['data'][i]['rh'])
                if "precip" not in myjson['data'][i]:
                    rainfall.append(0)
                else:
                    rainfall.append(round(myjson['data'][i]['precip'])) 

            temp = sum(temperature)/len(temperature) 
            humi = sum(humidity)/len(humidity)
            rainf = sum(rainfall)/len(rainfall)
            data = pd.read_csv("Crop_recommendation.csv")
            ord_enc = OrdinalEncoder()
            data["label_code"] = ord_enc.fit_transform(data[["label"]])
            label = data['label_code']
            data.drop(data.columns[7],axis=1,inplace = True)
            data1 = data.values

            X,y = data1[:, :-1], label
            X_train, X_test, y_train, y_test = train_test_split(X, y,test_size=0.33,random_state=1)
            # print(X_train.shape, X_train.shape, y_train.shape, y_test.shape)
            model  = KNeighborsClassifier()

            model.fit(X_train, y_train)

            preds = model.predict([[n,p,k,temp,humi,ph,rainf]])

            print(*preds)
            rev = ord_enc.inverse_transform([preds])
            print(*rev)

            res = list(itertools.chain(*rev))
            a = " ".join(map(str, res))


            cro=cropdetails.query.filter_by(Crop=a).first()
            cro.Crop=cro.Crop[:1].upper()+cro.Crop[1:]
            
            ye=list()
            py=list()
            yy=list()
            
            gr=graphd.query.filter_by(Crop=a).first()
            if gr is None:
               gr=graphd.query.filter_by(Crop='Other Pulses').first()
            
            for i in range(6,11):
                if i<9:
                  s='200'+str(i)+'-0'+str((i+1))
                elif i==9:
                  s='200'+str(i)+'-'+str((i+1))
                else:
                  s='20'+str(i)+'-'+str((i+1))
                ye.append(s)

            py.append(gr.p2006_7)
            py.append(gr.p2007_8)
            py.append(gr.p2008_9)
            py.append(gr.p2009_10)
            py.append(gr.p2010_11)

            yy.append(gr.y2006_7)
            yy.append(gr.y2007_8)
            yy.append(gr.y2008_9)
            yy.append(gr.y2009_10)
            yy.append(gr.y2010_11)

            ye=json.dumps(ye)
            py=json.dumps(py)
            yy=json.dumps(yy)

            return render_template("cropprediction.html",cro=cro,py=py,yy=yy,ye=ye)

        return render_template("crop.html",l={'0':0})
    else:
        return redirect("/")


@app.route("/AboutUs",methods=['GET','POST'])
def about():
    # if em !="" and pa !="":
    if 'email' in session:
        if request.method=='POST':
            f=request.form['feedback']
            
            feedb=feedback(Email=session['email'],Feedb=f,Time=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            db.session.add(feedb)
            db.session.commit()
            flash("Your feedback is successfully send ","success")
            return redirect("/AboutUs")

        return render_template("about.html")
    else:
        return redirect("/")

@app.route("/feedback")
def feedb():
    feed = feedback.query.filter_by().all()
    last = math.ceil(len(feed)/2)
    print(last)
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    feed = feed[(page-1)*2:(page-1)*2+ 2]
    
    if last==1:
        prev = "#"
        next = "#"
    elif page==1:
        prev = "#"
        next = "/feedback?page="+ str(page+1)
        flash("Your are on latest feedback","info")
    elif page==last:
        prev = "/feedback?page="+ str(page-1)
        next = "#"
        flash("Your are on oldest feedback","info")
    else:
        prev = "/feedback?page="+ str(page-1)
        next = "/feedback?page="+ str(page+1)
    
    return render_template('feedback.html',feed=feed, prev=prev, next=next)


@app.route("/queries")
def queries():
    c = ContactUs.query.filter_by().all()
    last = math.ceil(len(c)/2)
    
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    c = c[(page-1)*2:(page-1)*2+ 2]
    
    if last==1:
        prev = "#"
        next = "#"
    elif page==1:
        prev = "#"
        next = "/queries?page="+ str(page+1)
        flash("Your are on latest queries","info")
        
    elif page==last:
        prev = "/queries?page="+ str(page-1)
        next = "#"
        flash("Your are on oldest queries","info")
    else:
        prev = "/queries?page="+ str(page-1)
        next = "/queries?page="+ str(page+1)
    
    return render_template('queries.html',queries=c, prev=prev, next=next)

@app.route("/ContactUs",methods=["GET","POST"])
def contact():
    # if em !="" and pa !=""4
    if 'email' in session:
        if request.method=="POST":
            fname=request.form['fname']
            lname=request.form['lname']
            gender=request.form['gender']
            phone=request.form['phone']
            email=request.form['email']
            msg=request.form['feedb']
            
            con=ContactUs(fname=fname,lname=lname,gender=gender,phone=phone,email=email,msg=msg,response='Null')
            db.session.add(con)
            db.session.commit()
            flash("Your Message is send successfully","success")
            return redirect("/ContactUs")
        
        lo=registration.query.filter_by(email=session['email']).first()
        return render_template("contact.html",lo=lo)
 
    else:
        return redirect("/")



# contactus curd operations

    
# @app.route("/update/<int:sno>",methods=['GET','POST'])
# def update(sno):
#     # if em !="" and pa !="":    
#     if 'email' in session:
#         if request.method=='POST':
#             fname=request.form['fname']
#             lname=request.form['lname']
#             gender=request.form['gender']
#             phone=request.form['phone']
#             email=request.form['email']
#             feedb=request.form['feedb']
#             if fname=="" or lname=="" or len(phone)!=10 or email=="" or feedb=="":
#                 flash("Please fill all the feilds and phone number should be of 10 digits","warning")
#                 redirect("/update/sno")
#             else:
#                 con=ContactUs.query.filter_by(sno=sno).first()
#                 con.fname=fname
#                 con.lname=lname
#                 con.gender=gender
#                 con.phone=phone
#                 con.email=email
#                 con.feedb=feedb

#                 db.session.add(con)
#                 db.session.commit()
#                 flash("Your feedback is successfully updated","success")

#                 return redirect('/history')

#         con=ContactUs.query.filter_by(sno=sno).first()
#         return render_template('update.html',feed=con,se=session['logo'])
#     else:
#         return redirect("/")

if __name__=="__main__":
    app.run(debug=True,port=8000)