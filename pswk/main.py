from flask import Flask,render_template,request,session,redirect,url_for,flash,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,logout_user,login_manager,LoginManager
from flask_login import login_required,current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import os
local_server= True
app = Flask(__name__)
app.secret_key="some"

login_manager=LoginManager(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.config['SQLALCHEMY_DATABASE_URI']='mysql://sql9581468:LEBSMMetGR@sql9.freesqldatabase.com:3306/sql9581468'
db=SQLAlchemy(app)

class Test(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100))
    email=db.Column(db.String(100))

class Remainders(db.Model):
    aid=db.Column(db.Integer,primary_key=True)
    rollno=db.Column(db.String(100))
    remainder_text=db.Column(db.String(100))
    date=db.Column(db.Date())
    user_id=db.Column(db.Integer)

class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50))
    email=db.Column(db.String(50),unique=True)
    password=db.Column(db.String(1000))
    standard=db.Column(db.Integer)
    admin=db.Column(db.Boolean())
    rollno=db.Column(db.String(50))

class Student(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    rollno=db.Column(db.String(50))
    sname=db.Column(db.String(50))
    standard=db.Column(db.Integer)
    gender=db.Column(db.String(50))
    branch=db.Column(db.String(50))
    email=db.Column(db.String(50))
    number=db.Column(db.String(12))
    address=db.Column(db.String(100))
    

@app.route('/')
@login_required
def index(): 
    homeFlag=True
    student=db.engine.execute(f"SELECT * FROM `user`") 
    events=db.engine.execute(f"SELECT * FROM `to_do_list` where user_id='{current_user.id}' and date > DATE(NOW()) group by date asc LIMIT 2") 
    images=db.engine.execute(f"SELECT * FROM `media` where user_id='{current_user.id}'") 
    length=len(list(student.fetchall()))
    return render_template('index.html',homeFlag=homeFlag,student=student,length=length,images=images,events=events)

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/contactus')
def contact_us():
    return render_template('contact_us.html')

@app.route('/aboutus')
def about_us():
    return render_template('about_us.html')

@app.route('/studentdetails')
@login_required
def studentdetails():
    query=db.engine.execute(f"SELECT * FROM `user`") 
    return render_template('studentdetails.html',query=query)

@app.route('/details')
@login_required
def details():
    query=db.engine.execute(f"SELECT * FROM `user` where id='{current_user.id}'") 
    return render_template('details.html',query=query)

@app.route('/to_do_list',methods=['POST','GET'])
@login_required
def to_do_list():
    query=db.engine.execute(f"SELECT * FROM `to_do_list` where user_id='{current_user.id}'") 
    if request.method=="POST":
        date=request.form.get('date')
        message=request.form.get('task')
        time=request.form.get('time')
        db.engine.execute(f"INSERT INTO `to_do_list` (`date`,`task`,`time`,`user_id`) VALUES ('{date}','{message}','{time}','{current_user.id}')")
        flash("to_do_list Addes","success")
        query=db.engine.execute(f"SELECT * FROM `to_do_list` where user_id='{current_user.id}'") 
        return render_template('to_do_list.html',query=query)
    return render_template('to_do_list.html',query=query)


@app.route('/activities',methods=['POST','GET'])
@login_required
def activities():
    query=db.engine.execute(f"SELECT * FROM `activities` where user_id='{current_user.id}' and activity_class='{current_user.standard}'") 
    if request.method=="POST":
        activity_type=request.form.get('activity_type')
        activity_name=request.form.get('activity_name')
        activity_class=request.form.get('activity_class')
        activity_date=request.form.get('activity_date')
        db.engine.execute(f"INSERT INTO `activities` (`activity_type`,`activity_name`,`user_id`,`activity_class`,`activity_date`) VALUES ('{activity_type}','{activity_name}','{current_user.id}','{activity_class}','{activity_date}')")
        flash("activities Added","success")
        query=db.engine.execute(f"SELECT * FROM `activities` where user_id='{current_user.id}' and activity_class='{current_user.standard}'") 
        return render_template('activities.html',query=query)
    return render_template('activities.html',query=query)

@app.route('/save_activities/<string:id>',methods=['POST','GET'])
@login_required
def save_activities(id):
    query=db.engine.execute(f"SELECT * FROM `activities` where activity_id ='{id}'")
    if request.method=="POST":
        activity_type=request.form.get('activity_type')
        activity_name=request.form.get('activity_name')
        activity_class=request.form.get('activity_class')
        activity_date=request.form.get('activity_date')
        db.engine.execute(f"update `activities` set `activity_type`='{activity_type}',`activity_name`='{activity_name}',`activity_class`='{activity_class}',`activity_date`='{activity_date}' where activity_id='{id}'")
        flash("activities Updated","success")
        return redirect('/activities')
    return render_template('activity_edit.html',query=query)



@app.route('/images',methods=['POST','GET'])
@login_required
def images():
    query=db.engine.execute(f"SELECT * FROM `media` where user_id='{current_user.id}' and space='images'") 
    return render_template('images.html',query=query)

@app.route('/student_documents',methods=['POST','GET'])
@login_required
def student_documents():
    query=db.engine.execute(f"SELECT * FROM `media` where user_id='{current_user.id}' and space='student_documents'") 
    return render_template('student_documents.html',query=query)

@app.route('/acheivements_media',methods=['POST','GET'])
@login_required
def acheivements():
    query=db.engine.execute(f"SELECT * FROM `media` where user_id='{current_user.id}' and space='acheivements'") 
    return render_template('acheivements.html',query=query)


@app.route('/media',methods=['POST','GET'])
@login_required
def media():
    query=db.engine.execute(f"SELECT * FROM `media` where user_id='{current_user.id}'") 
    if request.method=="POST":
        f = request.files['file']
        media_type=request.form.get('media_type')
        space=request.form.get('space')
        time=datetime.now(tz=None)
        file_name=f.filename
        name=current_user.username.replace(" ","")
        url="/images/"+name+"/"+media_type+"/"+f.filename
        db.engine.execute(f"INSERT INTO `media` (`media_type`,`file_name`,`c_time`,`user_id`,`media_url`,`space`) VALUES ('{media_type}','{file_name}','{time}','{current_user.id}','{url}','{space}')")
        flash("media Added","success")
        query=db.engine.execute(f"SELECT * FROM `media` where user_id='{current_user.id}'")         
        isExist = os.path.exists("./static/images/"+name)
        if(isExist):
            if(os.path.exists("./static/images/"+name+"/"+media_type+"/")):
                UPLOAD_FOLDER="./static/images/"+name+"/"+media_type+"/"
                f.save(os.path.join(UPLOAD_FOLDER, f.filename))
            else:
                os.mkdir("./static/images/"+name+"/"+media_type+"/")        
                UPLOAD_FOLDER="./static/images/"+name+"/"+media_type+"/"
                f.save(os.path.join(UPLOAD_FOLDER, f.filename))           
        else:
            os.mkdir("./static/images/"+name)               
            os.mkdir("./static/images/"+name+"/"+media_type+"/")               
            UPLOAD_FOLDER="./static/images/"+name+"/"+media_type+"/"
            f.save(os.path.join(UPLOAD_FOLDER, f.filename))
        return render_template('media.html',query=query)
    return render_template('media.html',query=query)

@app.route('/ajaxfile',methods=['POST','GET'])
@login_required
def ajaxfile():
    if request.method=="POST":
        userid=request.form.get('userid')
        emp_list=db.engine.execute(f"SELECT * FROM `media` where user_id ='{current_user.id}' and media_id='{userid}'")
        return jsonify({'htmlresponse':render_template('image_modal.html',rec=emp_list)})

@app.route('/ajax_activity',methods=['POST','GET'])
@login_required
def ajax_activity():
    if request.method=="POST":
        activity_id=request.form.get('activity_id')
        act_list=db.engine.execute(f"SELECT * FROM `activities` where activity_id='{activity_id}'")
        return jsonify({'htmlresponse':render_template('activity_edit.html',rec=act_list)})

@app.route('/addremainders',methods=['POST','GET'])
@login_required
def addremainders():
    list=db.engine.execute(f"SELECT * FROM `remainders` where user_id ='{current_user.id}'") 
    if request.method=="POST":
        rollno=request.form.get('rollno')
        remainder_text=request.form.get('remainder_text')
        date=request.form.get('date')
        atte=Remainders(rollno=current_user.rollno,remainder_text=remainder_text,date=date,user_id=current_user.id)
        db.session.add(atte)
        db.session.commit()
        flash("remainders added","warning")
    return render_template('remainders.html',list=list)


@app.route("/delete_image/<string:id>",methods=['POST','GET'])
@login_required
def delete_image(id):
    db.engine.execute(f"DELETE FROM `media` WHERE media_id='{id}'")
    flash("Image Deleted Successful","danger")
    return redirect('/media')

@app.route("/delete/<string:id>",methods=['POST','GET'])
@login_required
def delete(id):
    db.engine.execute(f"DELETE FROM `user` WHERE id='{current_user.id}'")
    flash("Student Deleted Successful","danger")
    return redirect('/login')


@app.route("/delete_activity/<string:id>",methods=['POST','GET'])
@login_required
def delete_activity(id):
    db.engine.execute(f"DELETE FROM `activities` WHERE activity_id='{id}'")
    flash("Activity Deleted Successful","danger")
    return redirect('/activities')

@app.route("/edit/<string:id>",methods=['POST','GET'])
@login_required
def edit(id):
    query=db.engine.execute(f"SELECT * FROM `user` where id ='{id}'") 
    if request.method=="POST":
        rollno=request.form.get('rollno')
        sname=request.form.get('sname')
        standard=request.form.get('standard')
        gender=request.form.get('gender')
        email=request.form.get('email')
        user_id=request.form.get('user_id')
        is_admin=request.form.get('is_admin')
        mobile=request.form.get('mobile')
        query=db.engine.execute(f"UPDATE `user` SET `rollno`='{rollno}',`username`='{sname}',`standard`='{standard}',`gender`='{gender}',`email`='{email}',`mobile`='{mobile}',`admin`='{is_admin}' where id='{user_id}'")
        flash("Student Updated","success")
        return redirect('/details')
    return render_template('edit.html',query=query)


@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method == "POST":
        username=request.form.get('username')
        email=request.form.get('email')
        password=request.form.get('password')
        standard=request.form.get('standard')
        gender=request.form.get('gender')
        mobile=request.form.get('mobile')
        rollno=request.form.get('rollno')
        user=User.query.filter_by(email=email).first()
        if user:
            flash("Email Already Exist","warning")
            return render_template('/signup.html')
        encpassword=generate_password_hash(password)
        new_user=db.engine.execute(f"INSERT INTO `user` (`username`,`email`,`password`,`standard`,`gender`,`mobile`,`rollno`) VALUES ('{username}','{email}','{encpassword}','{standard}','{gender}','{mobile}','{rollno}')")
        flash("Signup Succes Please Login","success")
        return render_template('login.html')
    return render_template('signup.html')

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == "POST":
        email=request.form.get('email')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password,password):
            login_user(user)
            flash("Login Success","primary")
            return redirect(url_for('index'))
        else:
            flash("invalid credentials","danger")
            return render_template('login.html')    

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout SuccessFul","warning")
    return redirect(url_for('login'))

@app.route('/addstudent',methods=['POST','GET'])
@login_required
def addstudent():
    if request.method=="POST":
        rollno=request.form.get('rollno')
        sname=request.form.get('sname')
        standard=request.form.get('standard')
        gender=request.form.get('gender')
        admin=request.form.get('isadmin')
        email=request.form.get('email')
        num=request.form.get('mobile')
        password=request.form.get('password')        
        encpassword=generate_password_hash(password)
        query=db.engine.execute(f"INSERT INTO `user` (`rollno`,`username`,`standard`,`gender`,`admin`,`email`,`mobile`,`password`) VALUES ('{rollno}','{sname}','{standard}','{gender}','{admin}','{email}','{num}','{encpassword}')")
        flash("Student Added","info")
        return redirect('/studentdetails')
app.run(debug=True)    