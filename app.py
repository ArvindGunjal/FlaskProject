from flask import Flask, request, g, flash, url_for, redirect, render_template,session, make_response
from flask_sqlalchemy import SQLAlchemy
import datetime
import sqlite3
import os
import os.path as op
import flask_admin as admin
from flask_admin.contrib import fileadmin
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from flask_mail import Mail, Message

app = Flask(__name__, template_folder='templates',static_folder='files')
app = Flask(__name__, static_url_path='/static')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myblogweb.sqlite3'
app.config['SECRET_KEY'] = "random string"
#mail configuration
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'amigodesktoppartner@gmail.com'
app.config['MAIL_PASSWORD'] = 'amigodesktop'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


currentDT = str(datetime.datetime.now())

mail=Mail(app)

db = SQLAlchemy(app)

class blogger(db.Model):
   id = db.Column('blog_id', db.Integer, primary_key = True)
   name = db.Column(db.String(100))
   city = db.Column(db.String(50))
   title = db.Column(db.String(200)) 
   email = db.Column(db.String(10))
   message=db.Column(db.String(1000))
   datetime=db.Column(db.String(50))
   imgdata = db.Column(db.LargeBinary)
   def __init__(self,name,city,title,email,message,datetime,imgdata):
      self.name = name
      self.city = city
      self.title = title
      self.email = email
      self.message=message
      self.datetime=datetime
      self.imgdata=imgdata

class registration(db.Model):
   id = db.Column('blog_id', db.Integer, primary_key = True)
   name = db.Column(db.String(100))
   city = db.Column(db.String(50)) 
   email = db.Column(db.String(100))
   passw=db.Column(db.String(100))
   
   def __init__(self,name,city,email,passw):
      self.name = name
      self.city = city
      self.email = email
      self.passw = passw

class report(db.Model):
   id = db.Column('blog_id', db.Integer, primary_key = True)
   title = db.Column(db.String(100))
   cate = db.Column(db.String(100))
   issue = db.Column(db.String(10000))
   reportertitle = db.Column(db.String(100))
   datetimecol=db.Column(db.String(50))

   def __init__(self,title,cate,issue,reportertitle,datetimecol):
      self.title = title
      self.cate=cate
      self.issue = issue
      self.reportertitle=reportertitle
      self.datetimecol=datetimecol
@app.route('/show_all')
def show_all():
   result = db.engine.execute("SELECT * FROM blogger ORDER BY datetime DESC")
   
   return render_template('show_all.html', result = result )
   
@app.route('/searchmethod', methods=['GET','POST'])
def searchmethod():
   if request.form['searchtext']!="":
      try: 
         result = db.engine.execute("SELECT * FROM blogger where title=?",request.form['searchtext'])
         return render_template('show_all.html', result = result)      
      except ValueError:
         flash("Blog Not Found")
         return render_template('datanotfound.html')
   else:
      return render_template('datanotfound.html')
      

@app.route('/')
def login():
   return render_template('login.html')

@app.route('/new', methods = ['GET', 'POST'])
def new():
   if request.method == 'POST':
      if not request.form['name'] or not request.form['city'] or not request.form['title'] or not request.form['email'] or not request.form['message']:
         flash('Please enter all the fields', 'error')
      else:
         file=request.files["imgfile"]
         blogs = blogger(request.form['name'], request.form['city'],
            request.form['title'], request.form['email'],request.form['message'],currentDT,file.read())
         
         db.session.add(blogs)
         db.session.commit()
         
         return redirect(url_for('show_all'))
   return render_template('formpage.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/registered', methods = ['GET', 'POST'])   
def registered():
   if request.method == 'POST':
      if not request.form['user'] or not request.form['email'] or not request.form['passw']:
         flash('Record was not added')
      else:
         exists = db.session.query(db.exists().where(registration.email == request.form['email'] and registration.user == request.form['user'])).scalar()
         if exists:
            return render_template("userrepeat.html")
         else:
            log = registration(request.form['user'],request.form['city'],request.form['email'],request.form['passw'])
            db.session.add(log)
            db.session.commit()
            #send mail
            msg = Message('Successful Registration', sender = 'amigodesktoppartner@gmail.com', recipients = [request.form['email']])
            msg.body = "You Have Successfully Registered To Bloggers Site "
            mail.send(msg)
            message="Your Account Created Successully "
            return render_template('login.html',message=message)
   else:
      pass
         
      
@app.route("/validate",methods=['GET','POST'])
def validate():
   emailID=request.form['email']
   passw=request.form['passw']
   
   exists = db.session.query(db.exists().where(registration.email == emailID)).scalar()
   if exists:
      session['username']=emailID
      return redirect(url_for('show_all'))
   else:
      
      return render_template("datanotfound.html")      
      
  
@app.route("/adminvalidate", methods=['GET','POST'])
def adminvalidate():
   if request.method == 'POST':
      if request.form['email']=="arvindgunjal8@gmail.com" and request.form['passw']=="arvind123":
         return render_template("adminpage.html")            
      else:
         return render_template("datanotfound.html")
   else:
      return redirect(url_for("show_all"))

@app.route("/redirectblockdelete", methods=['GET','POST'])
def redirectblockdelete():
   return render_template("blogdelete.html")

@app.route("/blogdelete", methods=['GET','POST'])
def blogdelete():
   title=request.form['title']
   bdel = blogger.query.filter_by(title=title).delete()  
   db.session.commit()
   message="Blog"
   return render_template('deletemessage.html',message=message)
      


@app.route("/redirectuserdelete")
def redirectuserdelete():
   return render_template("userdelete.html")      

@app.route("/userdelete", methods=['GET','POST'])
def userdelete():
   user=request.form['user']
   book = registration.query.filter_by(name=user).delete()  
   db.session.commit()
   message="User"
   return render_template("deletemessage.html",message=message)
      

def connect_db():
    return sqlite3.connect('myblogweb.db')


@app.route('/idfetch/<int:id>')
def idfetch(id):
   con = sqlite3.connect("myblogweb.sqlite3")
   con.row_factory = sqlite3.Row
   
   cur = con.cursor()
   cur.execute('SELECT * FROM blogger where blog_id=?;',[id])
   rows = cur.fetchall();
   
   cur.close();
   return render_template('blogshow.html', rows=rows, id=id)

#image display
@app.route('/imagedis/<int:id>')
def imagedis(id):
   con = sqlite3.connect("myblogweb.sqlite3")
   con.row_factory = sqlite3.Row
   
   cur = con.cursor()
   cur.execute('SELECT * FROM blogger where blog_id=?;',[id])
   
   rows = cur.fetchone();
   imgBlob = rows[7]
   response = make_response(imgBlob)
   response.headers["Content-type"] = "image/jpg"
   cur.close();
   return response

     
  


@app.route('/reportblog')
def reportblog():
   return render_template('reportpage.html')


@app.route('/reportpage', methods=['GET','POST'])
def reportpage():
      log = report(request.form['title'],request.form['cate'],request.form['message'],request.form['reportertitle'],currentDT)
      db.session.add(log)
      db.session.commit()
      return redirect(url_for("show_all"))


@app.route('/adminissue', methods=['GET','POST'])
def adminissue():
   result = db.engine.execute("SELECT * FROM report")
   return render_template('issue_show_all.html', result = result )

@app.route('/deleteissue/<string:title>')
def deleteissue(title):
   bdel =report.query.filter_by(title=title).delete()  
   db.session.commit()
   message="1 Blog Deleted"
   return render_template('show_all.html', message = message )


@app.route('/logout')
def logout():
   message="Thank You!!"
   session.pop('username', None)
   return render_template('logout.html',message=message)
   


      


         
 
@app.route('/adminpg')
def adminpg():
   return render_template("adminlogin.html")

   
if __name__ == '__main__':
  
    # Start app
   app.run(debug = True)
