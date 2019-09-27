from flask import Flask, render_template, url_for, request, session, redirect,flash, message_flashed,Response
from flask_pymongo import PyMongo
from camera import VideoCamera
import csv
import time

app = Flask(__name__)
start_time = 0
end_time = 0

# Here i am writing all code to connect my application with mongoDb and user authentications.

app.config["MONGO_URI"] = "mongodb://localhost:27017/True_Face"
app.config['SECRET_KEY'] = "You_r_secret"
# mongo =  PyMongo(app,config_prefix ="MONGO")
mongo = PyMongo(app)
@app.route('/')
def home():
  # if 'username' in session:
  #       return 'You are logged in as ' + session['username']
  return  render_template('page_home3.html')


@app.route('/about')
def about():
    return render_template('page_about3.html')


@app.route('/contact')
def contact():
    return render_template('page_contact.html')


@app.route('/login',methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        users = mongo.db.users
        login_user = users.find_one ({'name': request.form['username']})
        if login_user:
            if  (request.form['pass'] == login_user['password']):
                # if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password'].encode('utf-8')) == login_user['password'].encode('utf-8'):
                    session['username'] = request.form['username']
                    return redirect(url_for('profile_main'))
            # return 'Invalid username/password combination'
        if (not login_user) or ((request.form['pass'] != login_user['password'])):
            flash("Invalid Username/Password")
    return render_template('page_login.html')


@app.route('/registration', methods=['POST', 'GET'])
def registration():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name': request.form['username']})
        if existing_user is None:
            # hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            password = request.form['pass']
            Email = request.form['Email']
            if request.form['username']=="" or  request.form['pass'] =="" or request.form['Email'] =="":
                flash("Please fill all entries")
            else:
                users.insert({'name': request.form['username'], 'password': password, 'email':Email})
                session['username'] = request.form['username']
                return redirect(url_for('profile_main'))
        # return 'That username already exists!'
    return render_template('page_registration.html')


@app.route('/profile')
def profile_main():
    user = session["username"]
    return render_template('page_profile.html',user=user)


def gen(cam):
    global start_time
    start_time = time.time()
    while True:
        frame = cam.get_frame()
        if frame != None:
            for pic in frame:
                yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + pic() + b'\r\n\r\n')
        else:
            break
            # for frame in cam.get_frame():
        #     yield (b'--frame\r\n'
        #            b'Content-Type: image/jpeg\r\n\r\n' + frame() + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/my_projects', methods=['GET','POST'])
def my_projects():
    user = session["username"]
    if request.method=='POST':
        title=request.form['title']
        disp = request.form['desc']
        project = mongo.db.projects
        project.remove({"Project_title": title}, {"Description": disp})
        # return render_template('page_profile_projects.html')
    projects = mongo.db.projects.find({'user': user})
    return render_template('page_profile_projects.html',user=user, projects = projects)


@app.route('/my_history')
def my_history():
    user = session["username"]
    history = mongo.db.history.find({'user': user})
    return render_template('page_profile_history.html',user =user,history=history)


@app.route('/my_historyy')
def clear_history():
    mongo.db.history.drop()
    user = session["username"]
    history = mongo.db.history.find({'user': user})
    return render_template('page_profile_history.html',user =user,history=history)


@app.route('/my_profile')
def my_profile():
    user = session["username"]
    return render_template('page_profile_me.html',user = user)


@app.route('/User_Guide')
def User_Guide():
    user = session["username"]
    return render_template('User_guide.html',user = user)


@app.route('/New_Project' , methods=['POST', 'GET'])
def New_Project():
    user = session["username"]
    if (request.method == 'POST'):
        projects = mongo.db.projects
        history = mongo.db.history
        Project_title =request.form['Project_title']
        Date = request.form ['Date']
        Description = request.form['Description']
        if request.form['Project_title']=="" or  request.form ['Date']=="":
            flash("Please fill all mandatory enteries")
        else:
            projects.insert({"Project_title":Project_title, "Date":Date ,"Description":Description,"user":user})
            history.insert({"Project_title": Project_title, "Date": Date, "Description": Description, "user": user})

            return render_template("page_project_started.html",user = user)
    return render_template('New_Project.html',user =user)


@app.route('/want_graph')
def graphing():
    p = VideoCamera()
    user = session["username"]
    global end_time
    end_time = time.time()

    p.destroy()
    print("Instance Successfully Destroyed. . .")
    return render_template('page_profile_graphing.html',user = user)


@app.route('/graph')
def graph():
    file = open("Expressions.csv", "r")
    # reading = file.read()
    mylist = []
    with open("Expressions.csv") as file:
        reading1 = csv.reader(file, delimiter=',')
        for i in reading1:
            for k in i:
                mylist.append(k)
    data = mylist
    user = session["username"]
    return render_template('graph.html', user= user, data = data)


if __name__ ==('__main__'):
    app.run(debug=True, threaded=True)