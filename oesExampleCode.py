#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template, request, redirect, url_for, \
    flash, send_from_directory
from datetime import datetime
from sqlalchemy.orm import scoped_session
from flask import Flask, render_template, request, redirect, jsonify, \
    url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from flask import session as login_session
import sqlalchemy
import random
import string
import oauth2client
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from werkzeug.utils import secure_filename
import codecs

# from flask.ext.sqlalchemy import SQLAlchemy

from flask_sqlalchemy import SQLAlchemy

from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import desc
from flask_login import LoginManager
from flask_login import current_user, login_user
from flask_login import logout_user
from flask_login import login_required

reader = codecs.getreader('utf-8')

UPLOAD_FOLDER = os.path.dirname('static/im/usrs/')
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png'])
ALLOWED_EXTENSIONS_VIDEOS = set(['mpg', 'mpeg', 'mp4', 'mov'])

app = Flask(__name__)
app.secret_key = 'ev17345330665270'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

login = LoginManager(app)
login.login_view = 'signIn'

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from create_db import Base, User, Executive, Executive2, Page_Private, \
    Page_Private_Post, Public_Post, Photos, Videos, PDMessages, \
    Houdini, PDVideos, UserMixin

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web'
        ]['client_id']
APPLICATION_NAME = 'One Last Thing'

# create db engine and session

engine = create_engine('sqlite:///1lastthingdatabase.db')
Base.metadata.bind = engine

# DBSession = sessionmaker(bind = engine)
# session = DBSession()

session = scoped_session(sessionmaker(bind=engine))

# app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 465
# app.config['MAIL_USE_SSL'] = True
# app.config['MAIN_USERNAME'] = 'paynedanielfranklin@gmail.com'
# app.config['MAIL_PASSWORD'] = 'Bright661ev137453'

app.config.update(  # EMAIL SETTINGS
    DEBUG=True,
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='paynedanielfranklin@gmail.com',
    MAIL_PASSWORD='Bright661ev173453',
    )

mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)

# login_manager.login_view = "http://ourEternalSpace.com"

login_manager.login_view = 'showLogin'


# Create anti-forgery state token
# @app.route('/login')
# def showLogin():
#     state = ''.join(random.choice(string.ascii_uppercase + string.digits)
#                     for x in xrange(32))
#     login_session['state'] = state
#     # return "The current session state is %s" % login_session['state']
#     return render_template('login.html', STATE=state)

# see if user exists, if it doesnt make a new account

@login_manager.user_loader
def load_user(id):
    user = session.query(User).filter_by(id=id).one()
    return user


@app.teardown_request
def remove_session(ex=None):
    session.remove()


@app.route('/logout')
def logout():
    print 'logged out'
    logout_user()

    return redirect(url_for('showLogin'))


def checkOutGoing():
    iterate = session.query(PDMessages).all()
    today = datetime.now().date()
    print 'checking for outgoing'
    for i in iterate:

        # print('owner_id ' + str(i.owner_id))
        # print('target date is ' + i.date_target.strftime("%Y-%m-%d"))
        # print('todays date is ' + datetime.now().date().strftime("%Y-%m-%d"))
        # print('title is ' + i.title)
        # print ('body is ' + i.body)
        # print('target_email is ' + i.email_target)

        if today == i.date_target.date() and i.user.unlocked == 'yes':

            # print('target is unlocked? ' + i.user.unlocked)

            if i.sent == 'no':
                print 'EMAIL will BE SENT'

                msg1 = 'Hello ' + i.page_private.name_first + ' ' \
                    + i.page_private.name_last
                msg = Message('There is a new message for you from '
                              + i.user.name_first
                              + ' on Our Eternal Space',
                              sender='paynedanielfranklin@gmail.com',
                              recipients=[i.email_target])
                msg.html = ' <p> ' + msg1 \
                    + '<br>There is a new post dated message available for you now from <strong>' \
                    + i.user.name_first + ' ' + i.user.name_last \
                    + "</strong>. To view this message log into <a href='OurEternalSpace.com'>Our Eternal Space</a></p>"

                # msg.body = msg1 + ' You have been chosen by your loved one ' + userinfo.name + ' ' + userinfo.name + ' to be their executive on Our Eternal Space.' + userinfo.name + ' Needs your help in activating their website once they pass away.'

                mail.send(msg)
                i.sent = 'yes'
                session.add(i)
                session.commit()
                print 'was the message sent? ' + i.sent


@app.route('/home')
@app.route('/', methods=['POST', 'GET'])
def showLogin():
    checkOutGoing()
    all_users = session.query(User).all()
    if request.method == 'POST':
        for a in all_users:

            if a.email == request.form['email'].lower() and a.p \
                == request.form['p']:
                login_user(a, remember=True)
                return redirect(url_for('User_Main'))
        return render_template('indexBL.html')
    return render_template('index.html')


    # return render_template('direct.html')

# creating new users

@app.route('/createUser/', methods=['GET', 'POST'])
def createUser():
    all_users = session.query(User).all()

    if request.method == 'POST':
        for a in all_users:
            if a.email == request.form['email'].lower():
                return render_template('indexBS.html')

        random_key = random.randint(1, 100000000)
        random_key_string = str(random_key)
        newUser = User(
            name_first=request.form['name_first'].lower(),
            name_last=request.form['name_last'].lower(),
            email=request.form['email'].lower(),
            p=request.form['p'],
            unlocked='no',
            initial_key=random_key,
            )
        session.add(newUser)
        session.commit()
        print newUser.profile_picture
        login_user(newUser, remember=True)
        os.makedirs('static/im/usrs/' + str(newUser.id))

        user = \
            session.query(User).filter_by(email=newUser.email.lower()).one()
        msg1 = 'Hello ' + user.name_first \
            + '. Welcome to Our Eternal Space.'
        msg = Message('Welcome to Our Eternal Space',
                      sender='paynedanielfranklin@gmail.com',
                      recipients=[user.email])
        msg.html = ' <p> ' + msg1 + '<br><br> Your key is  ' \
            + '<strong>' + random_key_string + '</strong>' + '<br><br>' \
            + "Please visit <a href = 'http://www.OurEternalSpace.com/validate/'>ourEternalSpace.com</a>" \
            + ' to validate your account.'
        mail.send(msg)
        return redirect(url_for('validate'))

    # ----------------send welcome email------------

    return redirect(url_for('showLogin'))


@app.route('/validate/', methods=['GET', 'POST'])
@login_required
def validate():
    userinfo = session.query(User).filter_by(id=current_user.id).one()
    if request.method == 'POST':
        correct_Code = str(userinfo.initial_key)
        print 'given key is ' + str(request.form['key']) \
            + '. assigned key is ' + str(userinfo.initial_key)
        if request.form['key'] == correct_Code:
            userinfo.is_validated = 'yes'
            session.add(userinfo)
            session.commit()
            return redirect(url_for('User_Main'))

    return render_template('ValidateUser.html')


@app.route('/main')
@login_required
def User_Main():
    userinfo = session.query(User).filter_by(id=current_user.id).one()
    page_private = \
        session.query(Page_Private).filter_by(user_id=current_user.id).all()
    executive1 = \
        session.query(Executive).filter_by(user_id=current_user.id).all()

    pagesAttachedToThisUser = \
        session.query(Page_Private).filter_by(email=userinfo.email).all()
    allUsers = session.query(User).all()
    allExecutives1 = session.query(Executive).all()
    allExecutives2 = session.query(Executive2).all()

    if userinfo.is_validated == 'no':
        return redirect(url_for('validate'))

    checkingPrivate = \
        session.query(Page_Private).filter_by(user_id=current_user.id).all()

    if not checkingPrivate and not executive1:
        folderString = str(userinfo.id)
        print 'first'
        print 'current user id is ' + folderString
        return render_template(
            'profile.html',
            user=userinfo,
            user_id=userinfo.id,
            page_private=page_private,
            profile_picture=userinfo.profile_picture,
            folder=folderString,
            hasExecutives='no',
            hasPrivate='no',
            executive1=userinfo,
            executive2=userinfo,
            pagesAttachedToThisUser=pagesAttachedToThisUser,
            allUsers=allUsers,
            allExecutives1=allExecutives1,
            allExecutives2=allExecutives2,
            )
    if not checkingPrivate and executive1:
        print 'second'
        executive1 = \
            session.query(Executive).filter_by(user_id=current_user.id).one()
        executive2 = \
            session.query(Executive2).filter_by(user_id=current_user.id).one()
        return render_template(
            'profile.html',
            user=userinfo,
            user_id=userinfo.id,
            page_private=page_private,
            profile_picture=userinfo.profile_picture,
            executive1=executive1,
            executive2=executive2,
            folder=str(userinfo.id),
            hasExecutives='yes',
            hasPrivate='no',
            pagesAttachedToThisUser=pagesAttachedToThisUser,
            allUsers=allUsers,
            allExecutives1=allExecutives1,
            allExecutives2=allExecutives2,
            )
    if not executive1:
        print 'third'
        userinfo = \
            session.query(User).filter_by(id=current_user.id).one()
        page_private = \
            session.query(Page_Private).filter_by(user_id=current_user.id).all()
        return render_template(
            'profile.html',
            user=userinfo,
            user_id=userinfo.id,
            page_private=page_private,
            profile_picture=userinfo.profile_picture,
            privatePages=checkingPrivate,
            folder=str(current_user.id),
            hasExecutives='no',
            hasPrivate='yes',
            executive1=userinfo,
            executive2=userinfo,
            pagesAttachedToThisUser=pagesAttachedToThisUser,
            allUsers=allUsers,
            allExecutives1=allExecutives1,
            allExecutives2=allExecutives2,
            )
    else:

        print 'fourth'
        userinfo = \
            session.query(User).filter_by(id=current_user.id).one()
        page_private = \
            session.query(Page_Private).filter_by(user_id=current_user.id).all()

        # public_posts = session.query(Public_Post).filter_by(user_id = userinfo.id).order_by('id desc').all()

        executive1 = \
            session.query(Executive).filter_by(user_id=current_user.id).one()
        executive2 = \
            session.query(Executive2).filter_by(user_id=current_user.id).one()

        # return render_template('user_main.html', user_id = userinfo.id,  page_private = page_private, posts = public_posts, profile_picture = userinfo.profile_picture,folder = str(userinfo.id))

        return render_template(
            'profile.html',
            user=userinfo,
            user_id=userinfo.id,
            page_private=page_private,
            profile_picture=userinfo.profile_picture,
            executive1=executive1,
            executive2=executive2,
            privatePages=checkingPrivate,
            folder=str(current_user.id),
            hasExecutives='yes',
            hasPrivate='yes',
            pagesAttachedToThisUser=pagesAttachedToThisUser,
            allUsers=allUsers,
            allExecutives1=allExecutives1,
            allExecutives2=allExecutives2,
            )


@app.route('/main/edit/executive1/', methods=['GET', 'POST'])
@login_required
def editExecutive1():
    userinfo = session.query(User).filter_by(id=current_user.id).one()
    executive1 = \
        session.query(Executive).filter_by(user_id=userinfo.id).one()
    executive2 = \
        session.query(Executive2).filter_by(user_id=userinfo.id).one()

    if userinfo.is_validated == 'no':
        return redirect(url_for('validate'))

    if request.method == 'POST':
        executive1.name_first = request.form['e1_name_first']
        executive1.name_last = request.form['e1_name_last']
        executive1.email = request.form['e1_email'].lower()
        session.add(executive1)
        session.commit()
        executive2.name_first = request.form['e2_name_first']
        executive2.name_last = request.form['e2_name_last']
        executive2.email = request.form['e2_email'].lower()
        session.add(executive2)
        session.commit()

         # ---------------------send email to executive1--------------
            # user= session.query(User).filter_by(name = login_session['username']).one()

        msg1 = '<strong>' + executive1.name_first + ' ' \
            + executive1.name_last + '</strong>'
        msg = Message(userinfo.name_first + ' ' + userinfo.name_last
                      + ' has chosen you to be their Executive',
                      sender='paynedanielfranklin@gmail.com',
                      recipients=[executive1.email])
        msg.html = ' <p> ' + msg1 \
            + '<br>You have been chosen by your loved one <strong>' \
            + userinfo.name_first + ' ' + userinfo.name_last \
            + " </strong>to be their Executive on <a href='OurEternalSpace.com'>ourEternalSpace.com</a></p> Our Eternal Space is a web app that allows users to easily create private pages for loved ones. These pages will remain locked until the creator has passed away, and will only ever be visible to the person it was created for. <br>As the Executive it is your job to unlock their page <strong>only</strong> when the time is appropriate.<br><br><br><strong>It is very important that you do not unlock these pages until after the creator has passed away.</strong><br>For more information please visit ourEternalSpace.com."

        # msg.body = msg1 + ' You have been chosen by your loved one ' + userinfo.name_first + ' ' + userinfo.name_last + ' to be their executive on Our Eternal Space.' + userinfo.name_first + ' Needs your help in activating their website once they pass away.'

        mail.send(msg)

        msg1 = '<strong>' + executive2.name_first + ' ' \
            + executive2.name_last + '</strong>'
        msg = Message(userinfo.name_first + ' ' + userinfo.name_last
                      + ' has chosen you to be their Executive',
                      sender='paynedanielfranklin@gmail.com',
                      recipients=[executive2.email])
        msg.html = ' <p> ' + msg1 \
            + '<br>You have been chosen by your loved one <strong>' \
            + userinfo.name_first + ' ' + userinfo.name_last \
            + " </strong>to be their Executive on <a href='OurEternalSpace.com'>ourEternalSpace.com</a></p> Our Eternal Space is a web app that allows users to easily create private pages for loved ones. These pages will remain locked until the creator has passed away, and will only ever be visible to the person it was created for. <br>As the Executive it is your job to unlock their page <strong>only</strong> when the time is appropriate.<br><br><br><strong>It is very important that you do not unlock these pages until after the creator has passed away.</strong><br>For more information please visit ourEternalSpace.com."

        # msg.body = msg1 + ' You have been chosen by your loved one ' + userinfo.name_first + ' ' + userinfo.name_last + ' to be their executive on Our Eternal Space.' + userinfo.name_first + ' Needs your help in activating their website once they pass away.'

        mail.send(msg)
        return redirect(url_for('User_Main'))


@app.route('/check')
def direction():
    if 'username' not in login_session:
        print 'username is not in login session in  check'

    # if 'username' not in login_session or creator.id != login_session['user_id']:

        return render_template('index.html')
    else:
        print 'user ' + login_session['username'] \
            + ' has just logged in'
        userinfo = \
            session.query(User).filter_by(email=current_user.email).one()
        page_private = \
            session.query(Page_Private).filter_by(user_id=userinfo.id).all()

        # public_posts = session.query(Public_Post).filter_by(user_id = userinfo.id).order_by('id desc').all()

        creator = getUserInfo(userinfo.id)
        executives = \
            session.query(Executive).filter_by(user_id=userinfo.id).one()
        if executives.name_first == 'none':
            return redirect(url_for('New_User_Page',
                            user_id=userinfo.id))
        else:

            # return redirect(url_for('New_User_Page1',user_id = userinfo.id))

            return redirect(url_for('User_Main', user_id=userinfo.id))


            # return render_template('user_main.html', user_id = userinfo.id,  page_private = page_private, posts = public_posts, profile_picture = userinfo.profile_picture)

@app.route('/setup/one/direct/')
@login_required
def New_User_Page():
    userinfo = session.query(User).filter_by(id=current_user.id).one()
    page_private = \
        session.query(Page_Private).filter_by(user_id=current_user.id).all()

    return render_template('setupUser.html')


@app.route('/setup/one/<int:user_id>/')
def New_User_Page1(user_id):
    userinfo = session.query(User).filter_by(id=user_id).one()
    page_private = \
        session.query(Page_Private).filter_by(user_id=userinfo.id).all()

    # public_posts = session.query(Public_Post).filter_by(user_id = userinfo.id).order_by('id desc').all()

    creator = getUserInfo(userinfo.id)

    if 'username' not in login_session or creator.id \
        != login_session['user_id']:

        return redirect(url_for('showLogin'))
    else:
        return render_template('newUserPage1.html', user_id=userinfo.id)


@app.route('/setup/one/commit/', methods=['POST', 'GET'])
@login_required
def add_Executive1():
    userinfo = session.query(User).filter_by(id=current_user.id).one()
    creator = getUserInfo(userinfo.id)

    if userinfo.is_validated == 'no':
        return redirect(url_for('validate'))

    if request.method == 'POST':
        newExecutive1 = \
            Executive(name_first=request.form['e1_name_first'],
                      name_last=request.form['e1_name_last'],
                      email=request.form['e1_email'].lower(),
                      user_id=userinfo.id)
        newExecutive2 = \
            Executive2(name_first=request.form['e2_name_first'],
                       name_last=request.form['e2_name_last'],
                       email=request.form['e2_email'].lower(),
                       user_id=userinfo.id)

        session.add(newExecutive1)
        session.commit()
        session.add(newExecutive2)
        session.commit()
        msg1 = '<strong>' + newExecutive1.name_first + ' ' \
            + newExecutive1.name_last + '</strong>'
        msg = Message(userinfo.name_first + ' ' + userinfo.name_last
                      + ' has chosen you to be their Executive',
                      sender='paynedanielfranklin@gmail.com',
                      recipients=[newExecutive1.email])
        msg.html = ' <p> ' + msg1 \
            + '<br>You have been chosen by your loved one <strong>' \
            + userinfo.name_first + ' ' + userinfo.name_last \
            + " </strong>to be their Executive on <a href='OurEternalSpace.com'>ourEternalSpace.com</a></p> Our Eternal Space is a web app that allows users to easily create private pages for loved ones. These pages will remain locked until the creator has passed away, and will only ever be visible to the person it was created for. <br>As the Executive it is your job to unlock their page <strong>only</strong> when the time is appropriate.<br><br><br><strong>It is very important that you do not unlock these pages until after the creator has passed away.</strong><br>For more information please visit ourEternalSpace.com."

        # msg.body = msg1 + ' You have been chosen by your loved one ' + userinfo.name_first + ' ' + userinfo.name_last + ' to be their executive on Our Eternal Space.' + userinfo.name_first + ' Needs your help in activating their website once they pass away.'

        mail.send(msg)

        msg1 = '<strong>' + newExecutive2.name_first + ' ' \
            + newExecutive2.name_last + '</strong>'
        msg = Message(userinfo.name_first + ' ' + userinfo.name_last
                      + ' has chosen you to be their Executive',
                      sender='paynedanielfranklin@gmail.com',
                      recipients=[newExecutive2.email])
        msg.html = ' <p> ' + msg1 \
            + '<br>You have been chosen by your loved one <strong>' \
            + userinfo.name_first + ' ' + userinfo.name_last \
            + " </strong>to be their Executive on <a href='OurEternalSpace.com'>ourEternalSpace.com</a></p> Our Eternal Space is a web app that allows users to easily create private pages for loved ones. These pages will remain locked until the creator has passed away, and will only ever be visible to the person it was created for. <br>As the Executive it is your job to unlock their page <strong>only</strong> when the time is appropriate.<br><br><br><strong>It is very important that you do not unlock these pages until after the creator has passed away.</strong><br>For more information please visit ourEternalSpace.com."

        # msg.body = msg1 + ' You have been chosen by your loved one ' + userinfo.name_first + ' ' + userinfo.name_last + ' to be their executive on Our Eternal Space.' + userinfo.name_first + ' Needs your help in activating their website once they pass away.'

        mail.send(msg)

        return redirect(url_for('User_Main'))


@app.route('/setup/two/<int:user_id>/')
@login_required
def New_User_Page2(user_id):
    userinfo = session.query(User).filter_by(id=user_id).one()
    page_private = \
        session.query(Page_Private).filter_by(user_id=userinfo.id).all()

    # public_posts = session.query(Public_Post).filter_by(user_id = userinfo.id).order_by('id desc').all()

    creator = getUserInfo(userinfo.id)

    if 'username' not in login_session or creator.id \
        != login_session['user_id']:

        return redirect(url_for('showLogin'))

    executive1Check = \
        session.query(Executive).filter_by(user_id=userinfo.id).one()
    if executive1Check.name_first == 'none':
        return redirect(url_for('New_User_Page1', user_id=userinfo.id))
    else:
        return render_template('newUserPage2.html', user_id=userinfo.id)


@app.route('/setup/two/commit/<int:user_id>/', methods=['POST', 'GET'])
@login_required
def add_Executive2(user_id):
    userinfo = session.query(User).filter_by(id=user_id).one()
    creator = getUserInfo(userinfo.id)
    if 'username' not in login_session or creator.id \
        != login_session['user_id']:

        return redirect(url_for('showLogin'))
    else:

        if request.method == 'POST':
            newExecutive = \
                session.query(Executive2).filter_by(user_id=userinfo.id).one()
            newExecutive.name_first = request.form['name_first']
            newExecutive.name_last = request.form['name_last']
            newExecutive.email = request.form['email'].lower()
            newExecutive.user_id = userinfo.id
            session.add(newExecutive)
            session.commit()
            msg1 = 'Hello ' + newExecutive.name_first + ' ' \
                + newExecutive.name_last + '.' \
                + '. Welcome to Our Eternal Space.'
            msg = Message('Welcome to Our Eternal Space',
                          sender='paynedanielfranklin@gmail.com',
                          recipients=[newExecutive.email])
            msg.html = ' <p> ' + msg1 \
                + ' You have been chosen by your loved one ' \
                + userinfo.name \
                + " to be their Executive on<a href ='OurEternalSpace.com'> Our Eternal Space.</a><br> Our Eternal Space is an after life web page where you can create websites for those you love to be viewed only after you pass away.<br>These web pages will always be locked to the public and only viewable to the people they are created for. <br>Your responsibility, as an Executive, is to unlock the page once the creator has passed away. You can do so by visiting our website, logging in with this email address and click on open pages.<br> Please be sure not to unlock the page until the time is appropriate. When you do, an email will be sent out to everyone that has a page made for them! </p>"

            # msg.body = msg1 + ' You have been chosen by your loved one ' + userinfo.name + ' ' + userinfo.name + ' to be their executive on Our Eternal Space.' + userinfo.name + ' Needs your help in activating their website once they pass away.'

            mail.send(msg)
            return redirect(url_for('User_Main', user_id=userinfo.id))


@app.route('/setup/three/<int:user_id>/')
@login_required
def New_User_Page3(user_id):
    userinfo = session.query(User).filter_by(id=user_id).one()
    page_private = \
        session.query(Page_Private).filter_by(user_id=userinfo.id).all()

    # public_posts = session.query(Public_Post).filter_by(user_id = userinfo.id).order_by('id desc').all()

    creator = getUserInfo(userinfo.id)

    if 'username' not in login_session or creator.id \
        != login_session['user_id']:

        return redirect(url_for('showLogin'))

    executive1Check = \
        session.query(Executive).filter_by(user_id=userinfo.id).one()

    if executive1Check.name_first == 'none':

        return redirect(url_for('New_User_Page1', user_id=userinfo.id))
    else:

        return render_template('newUserPage3.html', user_id=userinfo.id)


@app.route('/add/<int:user_id>/', methods=['GET', 'POST'])
@login_required
def Add_Public_Post(user_id):
    userinfo = session.query(User).filter_by(id=user_id).one()

    # executive1 = session.query(Executive).filter_by(user_id = userinfo.id).one()
    # executive2 = session.query(Executive2).filter_by(user_id = userinfo.id).one()

    page_private = \
        session.query(Page_Private).filter_by(user_id=userinfo.id).all()
    if request.method == 'POST':
        user = session.query(User).filter_by(id=user_id).one()
        thisPost = Public_Post(content=request.form['content'],
                               user_id=user.id)
        session.add(thisPost)
        session.commit()
        return redirect(url_for('User_Main', user_id=userinfo.id))


@app.route('/private/page/<int:user_id>/', methods=['GET', 'POST'])
@login_required
def Add_Private_Page(user_id):
    userinfo = session.query(User).filter_by(id=user_id).one()
    if request.method == 'POST':
        newPrivatePage = \
            Page_Private(name_first=request.form['name_first'],
                         name_last=request.form['name_last'],
                         email=request.form['email'].lower(),
                         user_id=userinfo.id)

        session.add(newPrivatePage)
        session.commit()
        privatePageId = \
            session.query(Page_Private).filter_by(user_id=user_id).one()
        return redirect(url_for('User_Main', user_id=userinfo.id))


        # return redirect(url_for('Private_Page', user_id = userinfo.id, page_id = privatePageId.id))

    # -------------------create private page--------------------

@app.route('/private/create', methods=['POST', 'GET'])
@login_required
def createPrivatePage():
    userinfo = session.query(User).filter_by(id=current_user.id).one()
    all_pages = \
        session.query(Page_Private).filter_by(user_id=current_user.id).all()
    print 'inside create private page'

    if request.method == 'POST':
        print 'inside request method'
        if len(all_pages) != False:
            print type(all_pages)
            for a in all_pages:
                print 'a is equal to ' + str(a)
                print 'inside a for all pages'
                if request.form['email'].lower() != a.email:
                    newPrivatePage = Page_Private(
                        nickname=request.form['nickname'],
                        name_first=request.form['name_first'],
                        name_last=request.form['name_last'],
                        email=request.form['email'].lower(),
                        user_id=userinfo.id,
                        owner_name=userinfo.name_first,
                        )
                    print 'does not equal email'
                    session.add(newPrivatePage)
                    session.commit()
                    return redirect(url_for('editPrivatePage',
                                    page_id=newPrivatePage.id))
            return redirect(url_for('User_Main'))
        newPrivatePage = Page_Private(
            nickname=request.form['nickname'],
            name_first=request.form['name_first'],
            name_last=request.form['name_last'],
            email=request.form['email'].lower(),
            user_id=userinfo.id,
            owner_name=userinfo.name_first,
            )

        session.add(newPrivatePage)
        session.commit()
        return redirect(url_for('editPrivatePage',
                        page_id=newPrivatePage.id))

    return redirect(url_for('User_Main'))


@app.route('/private/<int:page_id>/edit', methods=['GET', 'POST'])
@login_required
def editPrivatePage(page_id):
    userinfo = session.query(User).filter_by(id=current_user.id).one()
    owner = session.query(Page_Private).filter_by(id=page_id).one()
    photos = session.query(Photos).filter_by(user_owner=userinfo.id,
            page_id=page_id).all()
    videos = session.query(Videos).filter_by(user_owner=userinfo.id,
            page_id=page_id).all()
    pdmsg = session.query(PDMessages).filter_by(owner_id=userinfo.id,
            page_private_id=page_id).all()

    if userinfo.id != owner.user_id:
        return redirect(url_for('User_Main'))
    else:

        return render_template(
            'privatePage.html',
            user_id=userinfo.id,
            private=owner,
            private_id=owner.id,
            profile_picture=userinfo.profile_picture,
            folder=str(userinfo.id),
            photos=photos,
            videos=videos,
            pdmsg=pdmsg,
            )


@app.route('/private/<int:page_id>/edit/')
@login_required
def removePrivatePage(page_id):
    userinfo = session.query(User).filter_by(id=current_user.id).one()
    owner = session.query(Page_Private).filter_by(id=page_id).one()

    if userinfo.id != owner.user_id:
        return redirect(url_for('User_Main'))
    else:
        session.delete(owner)
        session.commit()
        return redirect(url_for('User_Main'))


@app.route('/private/<int:user_id>/<int:page_id>/')
@login_required
def Private_Page(user_id, page_id):
    return 'Working'


@app.route('/private/<int:user_id>/<int:page_id>/intro/edit/',
           methods=['GET', 'POST'])
@login_required
def editIntro(user_id, page_id):
    userinfo = session.query(User).filter_by(id=current_user.id).one()
    owner = session.query(Page_Private).filter_by(id=page_id).one()

    if current_user.id != owner.user_id:
        return redirect(url_for('User_Main'))

    if request.method == 'POST':
        intro = session.query(Page_Private).filter_by(id=page_id).one()
        intro.intro_text = request.form['intro']
        session.add(intro)
        session.commit()
        return redirect(url_for('editPrivatePage', page_id=page_id))


@app.route('/private/<int:user_id>/<int:page_id>/memory/edit/',
           methods=['GET', 'POST'])
@login_required
def editMemory(user_id, page_id):
    userinfo = session.query(User).filter_by(id=current_user.id).one()

    owner = session.query(Page_Private).filter_by(id=page_id).one()

    if userinfo.id != owner.user_id:
        return redirect(url_for('User_Main', user_id=userinfo.id))

    if request.method == 'POST':
        intro = session.query(Page_Private).filter_by(id=page_id).one()
        intro.memory = request.form['memory']
        session.add(intro)
        session.commit()
        return redirect(url_for('editPrivatePage', page_id=page_id))


@app.route('/private/<int:user_id>/<int:page_id>/know/edit/',
           methods=['GET', 'POST'])
@login_required
def editKnow(user_id, page_id):
    userinfo = session.query(User).filter_by(id=current_user.id).one()
    owner = session.query(Page_Private).filter_by(id=page_id).one()

    if userinfo.id != owner.user_id:
        return redirect(url_for('User_Main', user_id=userinfo.id))

    if request.method == 'POST':
        intro = session.query(Page_Private).filter_by(id=page_id).one()
        intro.you_should_know = request.form['know']
        session.add(intro)
        session.commit()
        return redirect(url_for('editPrivatePage', page_id=page_id))


# -----------------------------------PRIVATE PAGE MAIN ----------------------------------

@app.route('/private/page/preview/<int:page_id>/')
@login_required
def privatePagePreview(page_id):
    print 'inside privatePagePreview function top'
    userinfo = session.query(User).filter_by(id=current_user.id).one()
    owner = session.query(Page_Private).filter_by(id=page_id).one()
    photos = \
        session.query(Photos).filter_by(user_owner=userinfo.id).all()
    videos = \
        session.query(Videos).filter_by(user_owner=userinfo.id).all()
    pdmsg = session.query(PDMessages).filter_by(owner_id=userinfo.id,
            page_private_id=page_id).all()
    print 'inside privatePagePreview function'
    for p in pdmsg:
        print p.title
        print p.body

    if userinfo.id != owner.user_id:
        print 'userinfo.id is not equal to owner.user_id inside privatePageMain'
        return redirect(url_for('User_Main'))

    return render_template(
        'privatePagePreview.html',
        user_id=userinfo.id,
        private=owner,
        private_id=owner.id,
        profile_picture=userinfo.profile_picture,
        folder=str(userinfo.id),
        photos=photos,
        videos=videos,
        pdmsg=pdmsg,
        )


@app.route('/private/page/main/<int:user_id>/<int:page_id>')
@login_required
def privatePageMain(user_id, page_id):
    userinfo = session.query(User).filter_by(id=current_user.id).one()
    owner = session.query(Page_Private).filter_by(id=page_id).one()
    photos = \
        session.query(Photos).filter_by(user_owner=userinfo.id).all()
    videos = \
        session.query(Videos).filter_by(user_owner=userinfo.id).all()
    pdmsg = session.query(PDMessages).filter_by(owner_id=userinfo.id,
            page_private_id=page_id).all()

    if userinfo.id != owner.user_id:
        print 'userinfo.id is not equal to owner.user_id inside privatePageMain'
        return redirect(url_for('User_Main', user_id=userinfo.id))

    if userinfo.email != owner.email:
        return redirect(url_for('showLogin'))
    else:

        return render_template(
            'privatePagePreview.html',
            user_id=userinfo.id,
            private=owner,
            private_id=owner.id,
            profile_picture=userinfo.profile_picture,
            folder=str(userinfo.id),
            photos=photos,
            videos=videos,
            pdmsg=pdmsg,
            )


# --------------------------photo album------------------

@app.route('/upload/<int:user_id>/<int:page_id>/', methods=['GET',
           'POST'])
@login_required
def upload_photo(user_id, page_id):
    userinfo = session.query(User).filter_by(id=current_user.id).one()

    page_private = \
        session.query(Page_Private).filter_by(user_id=userinfo.id).all()
    all_photos = \
        session.query(Photos).filter_by(user_owner=current_user.id).all()

    # public_posts = session.query(Public_Post).filter_by(user_id = userinfo.id).order_by('id desc').all()

    if request.method == 'POST':
        print 'inside request method is equal to post inside upload profile picture'

        # check if the post request has the file part

        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        # if user does not select file, browser also
        # submit a empty part without filename

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):

            filename = secure_filename(file.filename)

            path = 'static/im/usrs/' + str(userinfo.id)
            print path
            UPLOAD_FOLDER = os.path.dirname('static/im/usrs/'
                    + str(userinfo.id) + '/')
            app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

            for a in all_photos:
                if a.name == filename:
                    filename = filename + str('1')

            file.save(os.path.join(app.config['UPLOAD_FOLDER'],
                      filename))

            # thisUser = session.query(User).filter_by(id = user_id).one()
            # thisUser.profile_picture = filename

            newPhoto = Photos(name=filename, user_owner=userinfo.id,
                              page_id=page_id)
            session.add(newPhoto)
            session.commit()

            return redirect(url_for('editPrivatePage', page_id=page_id))

    return redirect(url_for('editPrivatePage', page_id=page_id))


@app.route('/private/page/edit/delete/photo/<int:user_id>/<int:page_id>/<name>/'
           )
@login_required
def deletePhoto(user_id, page_id, name):
    userinfo = session.query(User).filter_by(id=current_user.id).one()
    owner = session.query(Page_Private).filter_by(id=page_id).one()

    if userinfo.id != owner.user_id:
        return redirect(url_for('User_Main'))

    thisPhoto = session.query(Photos).filter_by(user_owner=user_id,
            name=name).one()
    session.delete(thisPhoto)
    session.commit()
    return redirect(url_for('editPrivatePage', page_id=page_id))


@app.route('/upload/<int:user_id>/<int:page_id>/video/', methods=['GET'
           , 'POST'])
@login_required
def upload_video(user_id, page_id):
    all_videos = \
        session.query(Videos).filter_by(user_owner=current_user.id).all()
    userinfo = session.query(User).filter_by(id=current_user.id).one()
    page_private = \
        session.query(Page_Private).filter_by(user_id=userinfo.id).all()

    # public_posts = session.query(Public_Post).filter_by(user_id = userinfo.id).order_by('id desc').all()

    if request.method == 'POST':
        print 'inside request method is equal to post inside upload profile picture'

        # check if the post request has the file part

        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        # if user does not select file, browser also
        # submit a empty part without filename

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_fileVideo(file.filename):

            filename = secure_filename(file.filename)

            path = 'static/im/usrs/' + str(userinfo.id)
            print path
            UPLOAD_FOLDER = os.path.dirname('static/im/usrs/'
                    + str(userinfo.id) + '/')
            app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
            for a in all_videos:
                if a.name == filename:
                    filename = filename + str('1')
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],
                      filename))

            # thisUser = session.query(User).filter_by(id = user_id).one()
            # thisUser.profile_picture = filename

            newVideo = Videos(name=filename, user_owner=userinfo.id,
                              page_id=page_id)
            session.add(newVideo)
            session.commit()

            return redirect(url_for('editPrivatePage', page_id=page_id))

    return redirect(url_for('editPrivatePage', page_id=page_id))


@app.route('/private/page/edit/delete/video/<int:user_id>/<int:page_id>/<name>/'
           )
@login_required
def deleteVideo(user_id, page_id, name):
    userinfo = session.query(User).filter_by(id=current_user.id).one()
    owner = session.query(Page_Private).filter_by(id=page_id).one()

    if userinfo.id != owner.user_id:
        return redirect(url_for('User_Main', user_id=userinfo.id))

    thisVideo = session.query(Videos).filter_by(user_owner=user_id,
            name=name).one()
    session.delete(thisVideo)
    session.commit()
    return redirect(url_for('editPrivatePage', page_id=page_id))


# ---------------------------POST DATED MESSAGES --------------------------------------

@app.route('/private/user/create/pdmsg/<int:page_id>', methods=['GET',
           'POST'])
@login_required
def createPDMsg(page_id):
    userinfo = session.query(User).filter_by(id=current_user.id).one()
    creator = getUserInfo(userinfo.id)
    owner = session.query(Page_Private).filter_by(id=page_id).one()
    if creator.id != current_user.id:

        return redirect(url_for('showLogin'))

    if userinfo.id != owner.user_id:
        return redirect(url_for('User_Main'))

    if request.method == 'POST':
        datetime_object = datetime.strptime(request.form['date'],
                '%Y-%m-%d')

        # print (' date is ' + datetime_object)

        newMsg = PDMessages(
            owner_id=userinfo.id,
            title=request.form['title'],
            body=request.form['body'],
            date_target=datetime_object,
            email_target=owner.email,
            page_private_id=page_id,
            )
        session.add(newMsg)
        session.commit()
        print newMsg.title + ' ' + newMsg.body
        return redirect(url_for('editPrivatePage', page_id=page_id))


@app.route('/private/users/pdmsg/delete/<int:p_id>/<int:page_id>/')
@login_required
def deletePDMsg(p_id, page_id):
    userinfo = session.query(User).filter_by(id=current_user.id).one()
    pdMsg_to_delete = session.query(PDMessages).filter_by(id=p_id).one()
    owner = session.query(Page_Private).filter_by(id=page_id).one()

    if userinfo.id != owner.user_id:
        return redirect(url_for('User_Main'))

    if pdMsg_to_delete.owner_id == userinfo.id:
        session.delete(pdMsg_to_delete)
        session.commit()
        return redirect(url_for('editPrivatePage', page_id=page_id))


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# -------------------------openpage------------------------

@app.route('/user/page/private/<int:user_id>')
@login_required
def OpenPage(user_id):
    userinfo = session.query(User).filter_by(id=user_id).one()
    thisUser = getUserInfo(userinfo.id)

    if 'username' not in login_session or thisUser.id \
        != login_session['user_id']:

        return redirect(url_for('showLogin'))
    else:

        pagesAttachedToThisUser = \
            session.query(Page_Private).filter_by(email=userinfo.email).all()
        allUsers = session.query(User).all()
        allExecutives1 = session.query(Executive).all()
        allExecutives2 = session.query(Executive2).all()

        # for u in usersWhoMadePagesForThisUser:
        #     if usersWhoMadePagesForThisUser.unlocked == 'yes':

        return render_template(
            'openPages.html',
            user=thisUser,
            allExecutives1=allExecutives1,
            allExecutives2=allExecutives2,
            pagesAttachedToThisUser=pagesAttachedToThisUser,
            allUsers=allUsers,
            user_id=user_id,
            )


@app.route('/user/page/private/unlock/<int:user_unlock>/',
           methods=['GET', 'POST'])
@login_required
def unlockPage(user_unlock):
    userinfo = session.query(User).filter_by(id=current_user.id).one()
    checked = str(user_unlock)
    user_to_unlock = session.query(User).filter_by(id=user_unlock).one()
    user_to_unlock_e1 = \
        session.query(Executive).filter_by(user_id=user_to_unlock.id).one()
    user_to_unlock_e2 = \
        session.query(Executive2).filter_by(user_id=user_to_unlock.id).one()

    if userinfo.email.lower() != user_to_unlock_e1.email.lower() \
        and userinfo.email.lower() != user_to_unlock_e2.email.lower():
        return redirect(url_for('User_Main'))
    print 'user to be unlock has the id of ' + checked

    if userinfo.email.lower() == user_to_unlock_e1.email.lower() \
        or userinfo.email.lower() == user_to_unlock_e2.email.lower():

        if request.method == 'POST':

            user_to_unlock.unlocked = 'yes'
            session.add(user_to_unlock)
            session.commit()

                # ------------------SEND EMAILS TO USERS WHO HAVE PAGES CREATED FOR THEM-----------------

            allPrivatePages = \
                session.query(Page_Private).filter_by(user_id=user_to_unlock.id).all()
            for a in allPrivatePages:
                print a.email

                msg = Message(user_to_unlock.name_first + ' '
                              + user_to_unlock.name_last
                              + ' created a page for you on Our Eternal Space'
                              , sender='paynedanielfranklin@gmail.com',
                              recipients=[a.email])
                msg.html = \
                    ' <p> <br>A personal memorial page was created for you on ourEternalSpace.com by <strong>' \
                    + user_to_unlock.name_first + ' ' \
                    + user_to_unlock.name_last \
                    + ". </strong>To view this page you can visit <a href='OurEternalSpace.com'>ourEternalSpace.com</a> and create an account using this email address.</p>"
                mail.send(msg)
                print 'email would be sent now'

            return redirect(url_for('User_Main'))

        return render_template(
            'unlockPage.html',
            user_id=userinfo.id,
            user=userinfo,
            user_to_unlock=user_to_unlock,
            folder=str(userinfo.id),
            profile_picture=userinfo.profile_picture,
            )


@app.route('/user/page/private/<int:page_id>/<int:owner_id>')
@login_required
def OpenPageMAIN(page_id, owner_id):
    print 'page_id is ' + str(page_id)
    print 'owner_id is ' + str(owner_id)
    userinfo = session.query(User).filter_by(id=current_user.id).one()

    page = session.query(Page_Private).filter_by(email=userinfo.email,
            user_id=owner_id).one()
    pdmsg = session.query(PDMessages).filter_by(owner_id=owner_id,
            page_private_id=page_id).all()
    originalOwner = session.query(User).filter_by(id=page.user_id).one()
    originalOwnerString = str(originalOwner.id)
    print 'original owner is ' + str(originalOwner.id)

    photos = \
        session.query(Photos).filter_by(user_owner=originalOwner.id).all()
    videos = \
        session.query(Videos).filter_by(user_owner=originalOwner.id).all()

    if page.email == userinfo.email:

        return render_template(
            'PrivatePageMain.html',
            user_id=userinfo.id,
            folder=originalOwnerString,
            photos=photos,
            private=page,
            videos=videos,
            originalOwner=originalOwner,
            pdmsg=pdmsg,
            )


    # for file uploads

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() \
        in ALLOWED_EXTENSIONS


def allowed_fileVideo(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() \
        in ALLOWED_EXTENSIONS_VIDEOS


@app.route('/upload/<int:user_id>', methods=['GET', 'POST'])
@login_required
def upload_profile_picture(user_id):
    userinfo = session.query(User).filter_by(id=current_user.id).one()
    page_private = \
        session.query(Page_Private).filter_by(user_id=userinfo.id).all()
    if request.method == 'POST':
        print 'inside request method is equal to post inside upload profile picture'

        # check if the post request has the file part

        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        # if user does not select file, browser also
        # submit a empty part without filename

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):

            filename = secure_filename(file.filename)

            path = 'static/im/usrs/' + str(userinfo.id)
            print path
            UPLOAD_FOLDER = os.path.dirname('static/im/usrs/'
                    + str(userinfo.id) + '/')
            app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

            file.save(os.path.join(app.config['UPLOAD_FOLDER'],
                      filename))
            thisUser = session.query(User).filter_by(id=user_id).one()
            thisUser.profile_picture = filename
            session.add(thisUser)
            session.commit()

            return redirect(url_for('User_Main'))
    else:

            # return redirect(url_for('uploaded_file',
                                    # filename=filename, user_id = userinfo.id))

        return redirect(url_for('User_Main'))


# @app.route('/show/<filename>')
# def uploaded_file(filename):
#     filename = 'localhost:5000/static/im/' + filename
    # return render_template('user_main.html', user_id = user_id,  page_private = page_private, posts = public_posts, filename = filename, profile_picture = filename)

@app.route('/static/im/<filename>/')
def send_file(filename):
    return send_from_directory('UPLOAD_FOLDER', filename)


@app.route('/uploads/<filename>/<int:user_id>/')
def uploaded_file(filename, user_id):
    userinfo = session.query(User).filter_by(id=user_id).one()
    page_private = \
        session.query(Page_Private).filter_by(user_id=userinfo.id).all()

    # public_posts = session.query(Public_Post).filter_by(user_id = userinfo.id).order_by('id desc').all()

    return render_template('user_main.html', filename=filename,
                           user_id=user_id, page_private=page_private)


# ---------------------------------------------public page---------------------

@app.route('/public/<int:user_id>/')
def publicPage(user_id):
    userinfo = session.query(User).filter_by(id=user_id).one()

    # public_posts = session.query(Public_Post).filter_by(user_id = userinfo.id).order_by('id desc').all()

    creator = getUserInfo(userinfo.id)
    if 'username' not in login_session or creator.id \
        != login_session['user_id']:

        return redirect(url_for('showLogin'))
    else:
        return render_template('user_main.html', user_id=userinfo.id,
                               page_private=page_private,
                               profile_picture=userinfo.profile_picture)


        # return render_template('public.html', user_id = userinfo.id, posts = public_posts, profile_picture = userinfo.profile_picture)

@app.route('/back/admin/', methods=['GET', 'POST'])
def houdini():
    print 'TRYING TO ACCESS BACK/ADMIN'
    if request.method == 'POST':
        user = session.query(Houdini).filter_by(id=1).one()

        if request.form['username'] != user.name or request.form['p'] \
            != user.p:
            print 'TRYING TO ACCESS BACK/ADMIN | WRONG PASSWORD'
            return render_template('houdini.html')

        if request.form['username'] == user.name and request.form['p'] \
            == user.p:
            print 'GAINED ACCESS TO ADMIN PAGE'

            msg = Message('Daniel, Security Notice',
                          sender='paynedanielfranklin@gmail.com',
                          recipients=['paynedanielfranklin@gmail.com'])
            msg.body = 'SOMEONE HAS GAINED ACCESS TO ADMIN PAGE'
            mail.send(msg)
            return redirect(url_for('harryHoudini', user_id=user.p))

    return render_template('houdini.html')


@app.route('/harryHoudini/<user_id>', methods=['POST', 'GET'])
def harryHoudini(user_id):
    user = session.query(Houdini).filter_by(id=1).one()

    if user_id != user.p:
        return redirect(url_for('houdini'))

    users = session.query(User).all()
    return render_template('harryHoudini.html', users=users)

# @app.route('/Mallory')
# def lol():
#     return render_template('Mallory.html')

if __name__ == '__main__':
    app.debug = False
    app.run('0.0.0.0')

    # connect_args=={'check_same_thread': False}


			