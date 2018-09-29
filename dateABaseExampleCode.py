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
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import desc
from werkzeug.security import generate_password_hash, \
    check_password_hash
from flask_login import LoginManager
from flask_login import current_user, login_user
from flask_login import logout_user
from flask_login import login_required

app = Flask(__name__)
app.secret_key = 'super_secret_key'

login = LoginManager(app)
login.login_view = 'signIn'

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dateabaseDBSetup import Base, User, User_Traits_Male, \
    User_Traits_Female, Photo, A, Messages, LastMessage

# create db engine and session

engine = create_engine('sqlite:///dateabase.db')
Base.metadata.bind = engine

UPLOAD_FOLDER = os.path.dirname('static/im/usrs/')
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

session = scoped_session(sessionmaker(bind=engine))


@app.teardown_request
def remove_session(ex=None):
    session.remove()


@login.user_loader
def load_user(id):

    user = session.query(User).filter_by(id=id).one()
    return user


@app.route('/')
def index():

    return render_template('index.html')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() \
        in ALLOWED_EXTENSIONS


def allowed_fileVideo(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() \
        in ALLOWED_EXTENSIONS_VIDEOS


@app.route('/login', methods=['GET', 'POST'])
def signIn():

    if current_user.is_authenticated:
        return redirect(url_for('profile', user_id=current_user.id))

    if request.method == 'POST':

        all_users = session.query(User).all()

        for a in all_users:

            if a.email.lower() == request.form['email'].lower():
                if check_password_hash(a.p, request.form['p']):
                    login_user(a, remember=True)
                    return redirect(url_for('profile', user_id=a.id))
                flash('incorrect password')
                return render_template('signIn.html')
        flash('user does not exist')
        return render_template('signIn.html')

    return render_template('signIn.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/createAccount', methods=['GET', 'POST'])
def newUser():
    print 'inside new user , current_user id is equal to ' \
        + str(current_user)

    if request.method == 'POST':
        all_users = session.query(User).all()
        for a in all_users:
            if a.email.lower() == request.form['email'].lower():
                flash('Email already Exists')
                return render_template('createAccount.html')

        p_hash = generate_password_hash(request.form['p'])
        new_User = User(
            name_first=request.form['name_first'].lower(),
            name_last=request.form['name_last'].lower(),
            p=p_hash,
            total_seen=1,
            liked_amount=1,
            email=request.form['email'].lower(),
            age=request.form['age'],
            sex=request.form['sex'].lower(),
            target_gender=request.form['target'].lower(),
            )
        session.add(new_User)
        session.commit()
        new_User.user_liked = '&' + str(new_User.id)
        new_User.user_disliked = '&' + str(new_User.id)
        new_User.matches = '0&'

        session.add(new_User)
        session.commit()
        if new_User.sex.lower() == 'female':
            new_user_traits = User_Traits_Female(user_id=new_User.id)
            new_user_messages = Messages(user1_id=new_User.id,
                    user2_id=new_User.id, message='')

        if new_User.sex.lower() == 'male':
            new_user_traits = User_Traits_Male(user_id=new_User.id)
            new_user_messages = Messages(user1_id=new_User.id,
                    user2_id=new_User.id, message='')

        if new_User.sex.lower() == 'lgbtqia':
            new_user_traits = User_Traits_LGBTQIA(user_id=new_User.id)
            new_user_messages = Messages(user1_id=new_User.id,
                    user2_id=new_User.id, message='')

        session.add(new_user_traits, new_user_messages)
        session.commit()

        os.makedirs('static/im/usrs/' + str(new_User.id))
        for i in xrange(5):
            photos = Photo(name='plus.png', owner_id=new_User.id, num=i
                           + 1)
            session.add(photos)
            session.commit()

        login_user(new_User, remember=True)
        print 'New User.id before profile redirect is  ' \
            + str(new_User.id)

        return redirect(url_for('profile', user_id=new_User.id))

    return render_template('createAccount.html')


@app.route('/profile/', methods=['GET', 'POST'])
@login_required
def profile():

    print 'inside new user , current_user id is equal to ' \
        + str(current_user.id)
    this_user = session.query(User).filter_by(id=current_user.id).one()
    user_photos = \
        session.query(Photo).filter_by(owner_id=current_user.id).all()
    all_users = session.query(User).all()
    all_photos = session.query(Photo).all()
    users_liked = this_user.user_liked
    users_disliked = this_user.user_disliked

    photo1 = None
    photo2 = None
    photo3 = None
    photo4 = None
    photo5 = None

    user_liked_list = []
    user_disliked_list = []

    user_stats_liked = []
    target_stats = []
    usersPossible = []
    canUse = True

    intNumberOfPhotos = 0

    for x in users_liked.split('&'):
        print 'for x in users liked directily after split is ' + x
        print str(users_liked)
        user_liked_list.append(x)
    for x in users_disliked.split('&'):
        print x
        user_disliked_list.append(x)
    if len(user_liked_list) > 25 and len(user_liked_list) < 100:

        # Get traits this user likes

        total_users_thisUser_seen = len(user_liked_list)

        # -----------------------------------------IF USER HAS LIKE BETWEEN 25 AND 100 PEOPLE MAKE PER 55% TARGET ------------------------

        if int(float(this_user.eyes) / int(total_users_thisUser_seen)
               * 100 > 25):
            user_stats_liked.append('a.eyes')
        if int(float(this_user.hairstyle)
               / int(total_users_thisUser_seen) * 100 > 25):
            user_stats_liked.append('a.hairstyle')
        if int(float(this_user.style) / int(total_users_thisUser_seen)
               * 100 > 25):
            user_stats_liked.append('a.style')
        if int(float(this_user.beard) / int(total_users_thisUser_seen)
               * 100 > 25):
            user_stats_liked.append('a.beard')
        if int(float(this_user.tattoos)
               / int(total_users_thisUser_seen) * 100 > 25):
            user_stats_liked.append('a.tattoos')
        if int(float(this_user.piercings)
               / int(total_users_thisUser_seen) * 100 > 25):
            user_stats_liked.append('a.piercings')
        if int(float(this_user.fit) / int(total_users_thisUser_seen)
               * 100 > 25):
            user_stats_liked.append('a.fit')
        if int(float(this_user.average)
               / int(total_users_thisUser_seen) * 100 > 25):
            user_stats_liked.append('a.average')
        if int(float(this_user.curvy) / int(total_users_thisUser_seen)
               * 100 > 25):
            user_stats_liked.append('a.curvy')
        if int(float(this_user.thin) / int(total_users_thisUser_seen)
               * 100 > 25):
            user_stats_liked.append('a.thin')
        if int(float(this_user.tall) / int(total_users_thisUser_seen)
               * 100 > 25):
            user_stats_liked.append('a.tall')
        if int(float(this_user.short) / int(total_users_thisUser_seen)
               * 100 > 25):
            user_stats_liked.append('a.short')
        if int(float(this_user.fair_complexion)
               / int(total_users_thisUser_seen) * 100 > 25):
            user_stats_liked.append('a.fair_complexion')
        if int(float(this_user.tan_complexion)
               / int(total_users_thisUser_seen) * 100 > 25):
            user_stats_liked.append('a.tan_complexion')
        if int(float(this_user.dark_complexion)
               / int(total_users_thisUser_seen) * 100 > 25):
            user_stats_liked.append('a.dark_complexion')
        if int(float(this_user.smile) / int(total_users_thisUser_seen)
               * 100 > 25):
            user_stats_liked.append('a.smile')
    if len(user_liked_list) >= 100:

        # Get traits this user likes

        total_users_thisUser_seen = len(user_liked_list)

        # -----------------------------------------IF USER HAS LIKE BETWEEN 25 AND 100 PEOPLE MAKE PER 55% TARGET ------------------------

        if int(float(this_user.eyes) / int(total_users_thisUser_seen)
               * 100 > 35):
            user_stats_liked.append('a.eyes')
        if int(float(this_user.hairstyle)
               / int(total_users_thisUser_seen) * 100 > 35):
            user_stats_liked.append('a.hairstyle')
        if int(float(this_user.style) / int(total_users_thisUser_seen)
               * 100 > 35):
            user_stats_liked.append('a.style')
        if int(float(this_user.beard) / int(total_users_thisUser_seen)
               * 100 > 35):
            user_stats_liked.append('a.beard')
        if int(float(this_user.tattoos)
               / int(total_users_thisUser_seen) * 100 > 35):
            user_stats_liked.append('a.tattoos')
        if int(float(this_user.piercings)
               / int(total_users_thisUser_seen) * 100 > 35):
            user_stats_liked.append('a.piercings')
        if int(float(this_user.fit) / int(total_users_thisUser_seen)
               * 100 > 35):
            user_stats_liked.append('a.fit')
        if int(float(this_user.average)
               / int(total_users_thisUser_seen) * 100 > 35):
            user_stats_liked.append('a.average')
        if int(float(this_user.curvy) / int(total_users_thisUser_seen)
               * 100 > 35):
            user_stats_liked.append('a.curvy')
        if int(float(this_user.thin) / int(total_users_thisUser_seen)
               * 100 > 35):
            user_stats_liked.append('a.thin')
        if int(float(this_user.tall) / int(total_users_thisUser_seen)
               * 100 > 35):
            user_stats_liked.append('a.tall')
        if int(float(this_user.short) / int(total_users_thisUser_seen)
               * 100 > 35):
            user_stats_liked.append('a.short')
        if int(float(this_user.fair_complexion)
               / int(total_users_thisUser_seen) * 100 > 35):
            user_stats_liked.append('a.fair_complexion')
        if int(float(this_user.tan_complexion)
               / int(total_users_thisUser_seen) * 100 > 35):
            user_stats_liked.append('a.tan_complexion')
        if int(float(this_user.dark_complexion)
               / int(total_users_thisUser_seen) * 100 > 35):
            user_stats_liked.append('a.dark_complexion')
        if int(float(this_user.smile) / int(total_users_thisUser_seen)
               * 100 > 35):
            user_stats_liked.append('a.smile')

    for a in all_users:
        canUse = True
        if len(user_liked_list) <= 25:
            if a.email != this_user.email:

                for x in user_liked_list:
                    print ' x in user_liked list is ' + str(x)
                    if str(a.id) == x and str(this_user.id) != x:
                        canUse = False

                for x in user_disliked_list:
                    if str(a.id) == x and str(this_user.id) != x:
                        canUse = False

                if a.sex != this_user.target_gender and a.target_gender \
                    != 'all':
                    canUse = False

                if canUse == True:

                    print a.name_first
                    print 'User Id of currently shown account is ' \
                        + str(a.id)
                    print 'USER ONLY HAS ' + str(len(user_liked_list)) \
                        + ' SWIPES. DATA UNABLE TO POPULATE'

                    numberOfPhotos = \
                        session.query(Photo).filter_by(owner_id=a.id).all()
                    for i in numberOfPhotos:
                        if i.name != 'plus.png':
                            intNumberOfPhotos = intNumberOfPhotos + 1

                    print 'Number of photos is ' \
                        + str(intNumberOfPhotos)

                    for i in range(1, len(numberOfPhotos) + 1):
                        print 'I is equal to ' + str(i)
                        if photo1 == None:
                            photo1 = \
                                session.query(Photo).filter_by(owner_id=a.id,
                                    num=i).one()
                            if i >= len(numberOfPhotos):
                                break
                            i = i + 1

                        if photo2 == None:
                            photo2 = \
                                session.query(Photo).filter_by(owner_id=a.id,
                                    num=i).one()
                            if i >= len(numberOfPhotos):
                                break
                            i = i + 1

                        if photo3 == None:
                            photo3 = \
                                session.query(Photo).filter_by(owner_id=a.id,
                                    num=i).one()
                            if i >= len(numberOfPhotos):
                                break
                            i = i + 1
                        if photo4 == None:
                            photo4 = \
                                session.query(Photo).filter_by(owner_id=a.id,
                                    num=i).one()
                            if i >= len(numberOfPhotos):
                                break
                            i = i + 1
                        if photo5 == None:
                            photo5 = \
                                session.query(Photo).filter_by(owner_id=a.id,
                                    num=i).one()
                            if i >= len(numberOfPhotos):
                                break
                            i = i + 1

                    if photo1 == None:
                        print 'inside photo1 is none'
                        return render_template(
                            'profile.html',
                            folder2=str(a.id),
                            first_match=a,
                            numberOfPhotos=intNumberOfPhotos,
                            all_photos=all_photos,
                            this_user=this_user,
                            photos=user_photos,
                            folder=str(current_user.id),
                            )

                    if photo2 == None:
                        print 'inside photo2 is none'
                        return render_template(
                            'profile.html',
                            folder2=str(a.id),
                            first_match=a,
                            numberOfPhotos=intNumberOfPhotos,
                            all_photos=all_photos,
                            this_user=this_user,
                            photos=user_photos,
                            folder=str(current_user.id),
                            photo1=photo1.name,
                            )
                    if photo3 == None:
                        print 'inside photo3 is none'
                        return render_template(
                            'profile.html',
                            folder2=str(a.id),
                            first_match=a,
                            numberOfPhotos=intNumberOfPhotos,
                            all_photos=all_photos,
                            this_user=this_user,
                            photos=user_photos,
                            folder=str(current_user.id),
                            photo1=photo1.name,
                            photo2=photo2.name,
                            )

                    if photo4 == None:
                        print 'inside photo4 is none'
                        return render_template(
                            'profile.html',
                            folder2=str(a.id),
                            first_match=a,
                            numberOfPhotos=intNumberOfPhotos,
                            all_photos=all_photos,
                            this_user=this_user,
                            photos=user_photos,
                            folder=str(current_user.id),
                            photo1=photo1.name,
                            photo2=photo2.name,
                            photo3=photo3.name,
                            )
                    if photo5 == None:
                        print 'inside photo5 is none'
                        return render_template(
                            'profile.html',
                            folder2=str(a.id),
                            first_match=a,
                            numberOfPhotos=intNumberOfPhotos,
                            all_photos=all_photos,
                            this_user=this_user,
                            photos=user_photos,
                            folder=str(current_user.id),
                            photo1=photo1.name,
                            photo2=photo2.name,
                            photo3=photo3.name,
                            photo4=photo4.name,
                            )
                    print 'outside all photos is none return full amount'
                    return render_template(
                        'profile.html',
                        folder2=str(a.id),
                        first_match=a,
                        numberOfPhotos=intNumberOfPhotos,
                        all_photos=all_photos,
                        this_user=this_user,
                        photos=user_photos,
                        folder=str(current_user.id),
                        photo1=photo1.name,
                        photo2=photo2.name,
                        photo3=photo3.name,
                        photo4=photo4.name,
                        photo5=photo5.name,
                        )

        if a.per <= this_user.per and a.per > this_user.per - 12 \
            or a.per >= this_user.per and a.per < this_user.per + 12:
            if a.email != this_user.email:

                for x in user_liked_list:
                    print ' x in user_liked list is ' + str(x)
                    if str(a.id) == x and str(this_user.id) != x:
                        canUse = False

                for x in user_disliked_list:
                    if str(a.id) == x and str(this_user.id) != x:
                        canUse = False

                if a.sex != this_user.target_gender and a.target_gender \
                    != 'all':
                    canUse = False

                if canUse == True:
                    usersPossible.append(a.id)
                    for u in usersPossible:
                        print 'users possible: ' + str(u)

    if len(user_liked_list) > 25:
        for x in usersPossible:
            user_stats_liked_len = len(user_stats_liked)
            a = session.query(User).filter_by(id=x).one()

            if int(float(eval(user_stats_liked[0])) / int(a.total_seen)
                   * 100) > 70 and int(float(eval(user_stats_liked[1]))
                    / int(a.total_seen) * 100) > 70 \
                and int(float(eval(user_stats_liked[2]))
                        / int(a.total_seen) * 100) > 70:
                print a.name_first
                print 'User Id of currently shown account is ' \
                    + str(a.id)
                print 'has 3 highest trait match'
                numberOfPhotos = \
                    session.query(Photo).filter_by(owner_id=a.id).all()
                for i in numberOfPhotos:
                    if i.name != 'plus.png':
                        intNumberOfPhotos = intNumberOfPhotos + 1
                intNumberOfPhotos = intNumberOfPhotos + 1

                print 'Number of photos is ' + str(intNumberOfPhotos)

                for i in range(1, len(numberOfPhotos) + 1):
                    print 'I is equal to ' + str(i)
                    if photo1 == None:
                        photo1 = \
                            session.query(Photo).filter_by(owner_id=a.id,
                                num=i).one()
                        if i >= len(numberOfPhotos):
                            break
                        i = i + 1

                    if photo2 == None:
                        photo2 = \
                            session.query(Photo).filter_by(owner_id=a.id,
                                num=i).one()
                        if i >= len(numberOfPhotos):
                            break
                        i = i + 1

                    if photo3 == None:
                        photo3 = \
                            session.query(Photo).filter_by(owner_id=a.id,
                                num=i).one()
                        if i >= len(numberOfPhotos):
                            break
                        i = i + 1
                    if photo4 == None:
                        photo4 = \
                            session.query(Photo).filter_by(owner_id=a.id,
                                num=i).one()
                        if i >= len(numberOfPhotos):
                            break
                        i = i + 1
                    if photo5 == None:
                        photo5 = \
                            session.query(Photo).filter_by(owner_id=a.id,
                                num=i).one()
                        if i >= len(numberOfPhotos):
                            break
                        i = i + 1

                if photo1 == None:
                    print 'inside photo1 is none'
                    return render_template(
                        'profile.html',
                        folder2=str(a.id),
                        first_match=x,
                        numberOfPhotos=intNumberOfPhotos,
                        all_photos=all_photos,
                        this_user=this_user,
                        photos=user_photos,
                        folder=str(current_user.id),
                        )
                    if photo2 == None:
                        print 'inside photo2 is none'
                        return render_template(
                            'profile.html',
                            folder2=str(a.id),
                            first_match=a,
                            numberOfPhotos=intNumberOfPhotos,
                            all_photos=all_photos,
                            this_user=this_user,
                            photos=user_photos,
                            folder=str(current_user.id),
                            photo1=photo1.name,
                            )
                    if photo3 == None:
                        print 'inside photo3 is none'
                        return render_template(
                            'profile.html',
                            folder2=str(a.id),
                            first_match=a,
                            numberOfPhotos=intNumberOfPhotos,
                            all_photos=all_photos,
                            this_user=this_user,
                            photos=user_photos,
                            folder=str(current_user.id),
                            photo1=photo1.name,
                            photo2=photo2.name,
                            )

                    if photo4 == None:
                        print 'inside photo4 is none'
                        return render_template(
                            'profile.html',
                            folder2=str(a.id),
                            first_match=a,
                            numberOfPhotos=intNumberOfPhotos,
                            all_photos=all_photos,
                            this_user=this_user,
                            photos=user_photos,
                            folder=str(current_user.id),
                            photo1=photo1.name,
                            photo2=photo2.name,
                            photo3=photo3.name,
                            )
                    if photo5 == None:
                        print 'inside photo5 is none'
                        return render_template(
                            'profile.html',
                            folder2=str(a.id),
                            first_match=a,
                            numberOfPhotos=intNumberOfPhotos,
                            all_photos=all_photos,
                            this_user=this_user,
                            photos=user_photos,
                            folder=str(current_user.id),
                            photo1=photo1.name,
                            photo2=photo2.name,
                            photo3=photo3.name,
                            photo4=photo4.name,
                            )
                    print 'outside all photos is none return full amount'
                    return render_template(
                        'profile.html',
                        folder2=str(a.id),
                        first_match=a,
                        numberOfPhotos=intNumberOfPhotos,
                        all_photos=all_photos,
                        this_user=this_user,
                        photos=user_photos,
                        folder=str(current_user.id),
                        photo1=photo1.name,
                        photo2=photo2.name,
                        photo3=photo3.name,
                        photo4=photo4.name,
                        photo5=photo5.name,
                        )

        for x in usersPossible:
            user_stats_liked_len = len(user_stats_liked)
            a = session.query(User).filter_by(id=x).one()

            print 'EVAL ' + str(user_stats_liked[0])
            print eval(user_stats_liked[0])

            if int(float(eval(user_stats_liked[0])) / int(a.total_seen)
                   * 100) > 60 and int(float(eval(user_stats_liked[1]))
                    / int(a.total_seen) * 100) > 60 \
                or int(float(eval(user_stats_liked[1]))
                       / int(a.total_seen) * 100) > 60 \
                and int(float(eval(user_stats_liked[2]))
                        / int(a.total_seen) * 100) > 60 \
                or int(float(eval(user_stats_liked[0]))
                       / int(a.total_seen) * 100) > 60 \
                and int(float(eval(user_stats_liked[2]))
                        / int(a.total_seen) * 100) > 60:
                print a.name_first
                print 'User Id of currently shown account is ' \
                    + str(a.id)
                print 'has 2 highest trait match'
                numberOfPhotos = \
                    session.query(Photo).filter_by(owner_id=a.id).all()
                for i in numberOfPhotos:
                    if i.name != 'plus.png':
                        intNumberOfPhotos = intNumberOfPhotos + 1
                intNumberOfPhotos = intNumberOfPhotos + 1

                print 'Number of photos is ' + str(intNumberOfPhotos)

                for i in range(1, len(numberOfPhotos) + 1):
                    print 'I is equal to ' + str(i)
                    if photo1 == None:
                        photo1 = \
                            session.query(Photo).filter_by(owner_id=a.id,
                                num=i).one()
                        if i >= len(numberOfPhotos):
                            break
                        i = i + 1

                    if photo2 == None:
                        photo2 = \
                            session.query(Photo).filter_by(owner_id=a.id,
                                num=i).one()
                        if i >= len(numberOfPhotos):
                            break
                        i = i + 1

                    if photo3 == None:
                        photo3 = \
                            session.query(Photo).filter_by(owner_id=a.id,
                                num=i).one()
                        if i >= len(numberOfPhotos):
                            break
                        i = i + 1
                    if photo4 == None:
                        photo4 = \
                            session.query(Photo).filter_by(owner_id=a.id,
                                num=i).one()
                        if i >= len(numberOfPhotos):
                            break
                        i = i + 1
                    if photo5 == None:
                        photo5 = \
                            session.query(Photo).filter_by(owner_id=a.id,
                                num=i).one()
                        if i >= len(numberOfPhotos):
                            break
                        i = i + 1

                    if photo1 == None:
                        print 'inside photo1 is none'
                        return render_template(
                            'profile.html',
                            folder2=str(a.id),
                            first_match=x,
                            numberOfPhotos=intNumberOfPhotos,
                            all_photos=all_photos,
                            this_user=this_user,
                            photos=user_photos,
                            folder=str(current_user.id),
                            )

                    if photo2 == None:
                        print 'inside photo2 is none'
                        return render_template(
                            'profile.html',
                            folder2=str(a.id),
                            first_match=a,
                            numberOfPhotos=intNumberOfPhotos,
                            all_photos=all_photos,
                            this_user=this_user,
                            photos=user_photos,
                            folder=str(current_user.id),
                            photo1=photo1.name,
                            )
                    if photo3 == None:
                        print 'inside photo3 is none'
                        return render_template(
                            'profile.html',
                            folder2=str(a.id),
                            first_match=a,
                            numberOfPhotos=intNumberOfPhotos,
                            all_photos=all_photos,
                            this_user=this_user,
                            photos=user_photos,
                            folder=str(current_user.id),
                            photo1=photo1.name,
                            photo2=photo2.name,
                            )

                    if photo4 == None:
                        print 'inside photo4 is none'
                        return render_template(
                            'profile.html',
                            folder2=str(a.id),
                            first_match=a,
                            numberOfPhotos=intNumberOfPhotos,
                            all_photos=all_photos,
                            this_user=this_user,
                            photos=user_photos,
                            folder=str(current_user.id),
                            photo1=photo1.name,
                            photo2=photo2.name,
                            photo3=photo3.name,
                            )
                    if photo5 == None:
                        print 'inside photo5 is none'
                        return render_template(
                            'profile.html',
                            folder2=str(a.id),
                            first_match=a,
                            numberOfPhotos=intNumberOfPhotos,
                            all_photos=all_photos,
                            this_user=this_user,
                            photos=user_photos,
                            folder=str(current_user.id),
                            photo1=photo1.name,
                            photo2=photo2.name,
                            photo3=photo3.name,
                            photo4=photo4.name,
                            )
                    print 'outside all photos is none return full amount'
                    return render_template(
                        'profile.html',
                        folder2=str(a.id),
                        first_match=a,
                        numberOfPhotos=intNumberOfPhotos,
                        all_photos=all_photos,
                        this_user=this_user,
                        photos=user_photos,
                        folder=str(current_user.id),
                        photo1=photo1.name,
                        photo2=photo2.name,
                        photo3=photo3.name,
                        photo4=photo4.name,
                        photo5=photo5.name,
                        )

        for x in usersPossible:
            user_stats_liked_len = len(user_stats_liked)
            a = session.query(User).filter_by(id=x).one()

            print 'EVAL ' + str(user_stats_liked[0])
            print eval(user_stats_liked[0])

            if int(float(eval(user_stats_liked[0])) / int(a.total_seen)
                   * 100) > 60 or int(float(eval(user_stats_liked[1]))
                    / int(a.total_seen) * 100) > 60 \
                or int(float(eval(user_stats_liked[2]))
                       / int(a.total_seen) * 100) > 60:
                print a.name_first
                print 'User Id of currently shown account is ' \
                    + str(a.id)
                print 'has 1 highest trait match'
                numberOfPhotos = \
                    session.query(Photo).filter_by(owner_id=a.id).all()
                for i in numberOfPhotos:
                    if i.name != 'plus.png':
                        intNumberOfPhotos = intNumberOfPhotos + 1
                intNumberOfPhotos = intNumberOfPhotos + 1

                print 'Number of photos is ' + str(intNumberOfPhotos)
                for i in range(1, len(numberOfPhotos) + 1):
                    print 'I is equal to ' + str(i)
                    if photo1 == None:
                        photo1 = \
                            session.query(Photo).filter_by(owner_id=a.id,
                                num=i).one()
                        if i >= len(numberOfPhotos):
                            break
                        i = i + 1

                    if photo2 == None:
                        photo2 = \
                            session.query(Photo).filter_by(owner_id=a.id,
                                num=i).one()
                        if i >= len(numberOfPhotos):
                            break
                        i = i + 1

                    if photo3 == None:
                        photo3 = \
                            session.query(Photo).filter_by(owner_id=a.id,
                                num=i).one()
                        if i >= len(numberOfPhotos):
                            break
                        i = i + 1
                    if photo4 == None:
                        photo4 = \
                            session.query(Photo).filter_by(owner_id=a.id,
                                num=i).one()
                        if i >= len(numberOfPhotos):
                            break
                        i = i + 1
                    if photo5 == None:
                        photo5 = \
                            session.query(Photo).filter_by(owner_id=a.id,
                                num=i).one()
                        if i >= len(numberOfPhotos):
                            break
                        i = i + 1

                    if photo1 == None:
                        print 'inside photo1 is none'
                        return render_template(
                            'profile.html',
                            folder2=str(a.id),
                            first_match=x,
                            numberOfPhotos=intNumberOfPhotos,
                            all_photos=all_photos,
                            this_user=this_user,
                            photos=user_photos,
                            folder=str(current_user.id),
                            )

                    if photo2 == None:
                        print 'inside photo2 is none'
                        return render_template(
                            'profile.html',
                            folder2=str(a.id),
                            first_match=a,
                            numberOfPhotos=intNumberOfPhotos,
                            all_photos=all_photos,
                            this_user=this_user,
                            photos=user_photos,
                            folder=str(current_user.id),
                            photo1=photo1.name,
                            )
                    if photo3 == None:
                        print 'inside photo3 is none'
                        return render_template(
                            'profile.html',
                            folder2=str(a.id),
                            first_match=a,
                            numberOfPhotos=intNumberOfPhotos,
                            all_photos=all_photos,
                            this_user=this_user,
                            photos=user_photos,
                            folder=str(current_user.id),
                            photo1=photo1.name,
                            photo2=photo2.name,
                            )

                    if photo4 == None:
                        print 'inside photo4 is none'
                        return render_template(
                            'profile.html',
                            folder2=str(a.id),
                            first_match=a,
                            numberOfPhotos=intNumberOfPhotos,
                            all_photos=all_photos,
                            this_user=this_user,
                            photos=user_photos,
                            folder=str(current_user.id),
                            photo1=photo1.name,
                            photo2=photo2.name,
                            photo3=photo3.name,
                            )
                    if photo5 == None:
                        print 'inside photo5 is none'
                        return render_template(
                            'profile.html',
                            folder2=str(a.id),
                            first_match=a,
                            numberOfPhotos=intNumberOfPhotos,
                            all_photos=all_photos,
                            this_user=this_user,
                            photos=user_photos,
                            folder=str(current_user.id),
                            photo1=photo1.name,
                            photo2=photo2.name,
                            photo3=photo3.name,
                            photo4=photo4.name,
                            )
                    print 'outside all photos is none return full amount'
                    return render_template(
                        'profile.html',
                        folder2=str(a.id),
                        first_match=a,
                        numberOfPhotos=intNumberOfPhotos,
                        all_photos=all_photos,
                        this_user=this_user,
                        photos=user_photos,
                        folder=str(current_user.id),
                        photo1=photo1.name,
                        photo2=photo2.name,
                        photo3=photo3.name,
                        photo4=photo4.name,
                        photo5=photo5.name,
                        )

        for x in usersPossible:
            user_stats_liked_len = len(user_stats_liked)
            a = session.query(User).filter_by(id=x).one()

            if int(float(eval(user_stats_liked[0])) / int(a.total_seen)
                   * 100) > 40 or int(float(eval(user_stats_liked[1]))
                    / int(a.total_seen) * 100) > 40 \
                or int(float(eval(user_stats_liked[2]))
                       / int(a.total_seen) * 100) > 40:
                print a.name_first
                print 'User Id of currently shown account is ' \
                    + str(a.id)
                print 'has 0 highest trait match'
                numberOfPhotos = \
                    session.query(Photo).filter_by(owner_id=a.id).all()
                for i in numberOfPhotos:
                    if i.name != 'plus.png':
                        intNumberOfPhotos = intNumberOfPhotos + 1
                intNumberOfPhotos = intNumberOfPhotos + 1

                print 'Number of photos is ' + str(intNumberOfPhotos)

                for i in range(1, len(numberOfPhotos) + 1):
                    print 'I is equal to ' + str(i)
                    if photo1 == None:
                        photo1 = \
                            session.query(Photo).filter_by(owner_id=a.id,
                                num=i).one()
                        if i >= len(numberOfPhotos):
                            break
                        i = i + 1

                    if photo2 == None:
                        photo2 = \
                            session.query(Photo).filter_by(owner_id=a.id,
                                num=i).one()
                        if i >= len(numberOfPhotos):
                            break
                        i = i + 1

                    if photo3 == None:
                        photo3 = \
                            session.query(Photo).filter_by(owner_id=a.id,
                                num=i).one()
                        if i >= len(numberOfPhotos):
                            break
                        i = i + 1
                    if photo4 == None:
                        photo4 = \
                            session.query(Photo).filter_by(owner_id=a.id,
                                num=i).one()
                        if i >= len(numberOfPhotos):
                            break
                        i = i + 1
                    if photo5 == None:
                        photo5 = \
                            session.query(Photo).filter_by(owner_id=a.id,
                                num=i).one()
                        if i >= len(numberOfPhotos):
                            break
                        i = i + 1

                    if photo1 == None:
                        print 'inside photo1 is none'
                        return render_template(
                            'profile.html',
                            folder2=str(a.id),
                            first_match=x,
                            numberOfPhotos=intNumberOfPhotos,
                            all_photos=all_photos,
                            this_user=this_user,
                            photos=user_photos,
                            folder=str(current_user.id),
                            )

                    if photo2 == None:
                        print 'inside photo2 is none'
                        return render_template(
                            'profile.html',
                            folder2=str(a.id),
                            first_match=a,
                            numberOfPhotos=intNumberOfPhotos,
                            all_photos=all_photos,
                            this_user=this_user,
                            photos=user_photos,
                            folder=str(current_user.id),
                            photo1=photo1.name,
                            )
                    if photo3 == None:
                        print 'inside photo3 is none'
                        return render_template(
                            'profile.html',
                            folder2=str(a.id),
                            first_match=a,
                            numberOfPhotos=intNumberOfPhotos,
                            all_photos=all_photos,
                            this_user=this_user,
                            photos=user_photos,
                            folder=str(current_user.id),
                            photo1=photo1.name,
                            photo2=photo2.name,
                            )

                    if photo4 == None:
                        print 'inside photo4 is none'
                        return render_template(
                            'profile.html',
                            folder2=str(a.id),
                            first_match=a,
                            numberOfPhotos=intNumberOfPhotos,
                            all_photos=all_photos,
                            this_user=this_user,
                            photos=user_photos,
                            folder=str(current_user.id),
                            photo1=photo1.name,
                            photo2=photo2.name,
                            photo3=photo3.name,
                            )
                    if photo5 == None:
                        print 'inside photo5 is none'
                        return render_template(
                            'profile.html',
                            folder2=str(a.id),
                            first_match=a,
                            numberOfPhotos=intNumberOfPhotos,
                            all_photos=all_photos,
                            this_user=this_user,
                            photos=user_photos,
                            folder=str(current_user.id),
                            photo1=photo1.name,
                            photo2=photo2.name,
                            photo3=photo3.name,
                            photo4=photo4.name,
                            )
                    print 'outside all photos is none return full amount'
                    return render_template(
                        'profile.html',
                        folder2=str(a.id),
                        first_match=a,
                        numberOfPhotos=intNumberOfPhotos,
                        all_photos=all_photos,
                        this_user=this_user,
                        photos=user_photos,
                        folder=str(current_user.id),
                        photo1=photo1.name,
                        photo2=photo2.name,
                        photo3=photo3.name,
                        photo4=photo4.name,
                        photo5=photo5.name,
                        )

    for x in usersPossible:
        user_stats_liked_len = len(user_stats_liked)
        a = session.query(User).filter_by(id=x).one()

        print a.name_first
        print 'User Id of currently shown account is ' + str(a.id)
        print 'lOGGED IN USER DOES NOT HAVE 25 SWIPES'
        numberOfPhotos = \
            session.query(Photo).filter_by(owner_id=a.id).all()
        for i in numberOfPhotos:
            if i.name != 'plus.png':
                intNumberOfPhotos = intNumberOfPhotos + 1
        intNumberOfPhotos = intNumberOfPhotos + 1

        print 'Number of photos is ' + str(intNumberOfPhotos)
        for i in range(1, len(numberOfPhotos) + 1):
            print 'I is equal to ' + str(i)
            if photo1 == None:
                photo1 = session.query(Photo).filter_by(owner_id=a.id,
                        num=i).one()
                if i >= len(numberOfPhotos):
                    break
                i = i + 1

            if photo2 == None:
                photo2 = session.query(Photo).filter_by(owner_id=a.id,
                        num=i).one()
                if i >= len(numberOfPhotos):
                    break
                i = i + 1

            if photo3 == None:
                photo3 = session.query(Photo).filter_by(owner_id=a.id,
                        num=i).one()
                if i >= len(numberOfPhotos):
                    break
                i = i + 1
            if photo4 == None:
                photo4 = session.query(Photo).filter_by(owner_id=a.id,
                        num=i).one()
                if i >= len(numberOfPhotos):
                    break
                i = i + 1
            if photo5 == None:
                photo5 = session.query(Photo).filter_by(owner_id=a.id,
                        num=i).one()
                if i >= len(numberOfPhotos):
                    break
                i = i + 1

            if photo1 == None:
                print 'inside photo1 is none'
                return render_template(
                    'profile.html',
                    folder2=str(a.id),
                    first_match=x,
                    numberOfPhotos=intNumberOfPhotos,
                    all_photos=all_photos,
                    this_user=this_user,
                    photos=user_photos,
                    folder=str(current_user.id),
                    )
                if photo2 == None:
                    print 'inside photo2 is none'
                    return render_template(
                        'profile.html',
                        folder2=str(a.id),
                        first_match=a,
                        numberOfPhotos=intNumberOfPhotos,
                        all_photos=all_photos,
                        this_user=this_user,
                        photos=user_photos,
                        folder=str(current_user.id),
                        photo1=photo1.name,
                        )
                if photo3 == None:
                    print 'inside photo3 is none'
                    return render_template(
                        'profile.html',
                        folder2=str(a.id),
                        first_match=a,
                        numberOfPhotos=intNumberOfPhotos,
                        all_photos=all_photos,
                        this_user=this_user,
                        photos=user_photos,
                        folder=str(current_user.id),
                        photo1=photo1.name,
                        photo2=photo2.name,
                        )

                if photo4 == None:
                    print 'inside photo4 is none'
                    return render_template(
                        'profile.html',
                        folder2=str(a.id),
                        first_match=a,
                        numberOfPhotos=intNumberOfPhotos,
                        all_photos=all_photos,
                        this_user=this_user,
                        photos=user_photos,
                        folder=str(current_user.id),
                        photo1=photo1.name,
                        photo2=photo2.name,
                        photo3=photo3.name,
                        )
                if photo5 == None:
                    print 'inside photo5 is none'
                    return render_template(
                        'profile.html',
                        folder2=str(a.id),
                        first_match=a,
                        numberOfPhotos=intNumberOfPhotos,
                        all_photos=all_photos,
                        this_user=this_user,
                        photos=user_photos,
                        folder=str(current_user.id),
                        photo1=photo1.name,
                        photo2=photo2.name,
                        photo3=photo3.name,
                        photo4=photo4.name,
                        )
                print 'outside all photos is none return full amount'
                return render_template(
                    'profile.html',
                    folder2=str(a.id),
                    first_match=a,
                    numberOfPhotos=intNumberOfPhotos,
                    all_photos=all_photos,
                    this_user=this_user,
                    photos=user_photos,
                    folder=str(current_user.id),
                    photo1=photo1.name,
                    photo2=photo2.name,
                    photo3=photo3.name,
                    photo4=photo4.name,
                    photo5=photo5.name,
                    )

    return render_template('noMatches.html')


# def populate(current_user):
# ....this_user = session.query(User).filter_by(id = current_user.id).one()

# ....all_users = session.query(User).all()

# ....users_liked = this_user.user_liked
# ....users_disliked = this_user.user_disliked....
# ....user_liked_list = []
# ....user_disliked_list = []
# ....user_stats_liked = []
# ....target_stats = []
# ....canUse = True

# ....for x in users_liked.split("&"):
# ........print("for x in users liked directily after split is " + x)
# ........print(str(users_liked))
# ........user_liked_list.append(x)....
# ....for x in users_disliked.split("&"):
# ........print(x)
# ........user_disliked_list.append(x)

# ....for a in all_users:
# ........canUse = True
# ........if a.per <= this_user.per and a.per > this_user.per - 12 or a.per >= this_user.per and a.per < this_user.per + 12:
# ............if a.email != this_user.email:

# ................for x in user_liked_list:
# ....................print (" x in user_liked list is " + str(x))
# ....................if str(a.id) == x and str(this_user.id) != x:
# ........................canUse = False

# ................for x in user_disliked_list:
# ....................if str(a.id) == x and str(this_user.id) != x:
# ........................canUse = False

# ................if a.target_gender != this_user.sex and a.target_gender != 'all':
# ....................canUse = False

# ................if canUse == True:

                    # //all matches inside my per

@app.route('/profile/liked/<int:target_liked>/', methods=['GET', 'POST'
           ])
@login_required
def liked(target_liked):
    this_user = session.query(User).filter_by(id=current_user.id).one()
    target_liked = session.query(User).filter_by(id=target_liked).one()
    print 'this user name is ' + this_user.name_first
    print 'target user name is ' + target_liked.name_first

    photo1 = session.query(Photo).filter_by(owner_id=target_liked.id,
            num=1).one()
    this_user_photo = \
        session.query(Photo).filter_by(owner_id=this_user.id,
            num=1).one()

    if target_liked.sex.lower() == 'female':
        print 'target user is female'
        target_features = \
            session.query(User_Traits_Female).filter_by(user_id=target_liked.id).one()
    if target_liked.sex.lower() == 'male':
        print 'target user is male'
        target_features = \
            session.query(User_Traits_Male).filter_by(user_id=target_liked.id).one()
    if target_liked.sex.lower() == 'lgbtqia':
        print 'target user is lgbtqia'
        target_features = \
            session.query(User_Traits_LGBTQIA).filter_by(user_id=target_liked.id).one()

    if request.method == 'POST':
        print 'this user liked list is ' + str(this_user.user_liked)
        this_user.user_liked = str(this_user.user_liked) + '&' \
            + str(target_liked.id)
        this_user.hairstyle = this_user.hairstyle \
            + int(request.form['hairstyle'])
        this_user.eyes = this_user.eyes + int(request.form['eyes'])
        this_user.style = this_user.style + int(request.form['style'])
        this_user.beard = this_user.beard + int(request.form['beard'])
        this_user.tattoos = this_user.tattoos \
            + int(request.form['tattoos'])
        this_user.piercings = this_user.piercings \
            + int(request.form['piercings'])
        this_user.fit = this_user.fit + int(request.form['fit'])
        this_user.average = this_user.average \
            + int(request.form['average'])
        this_user.curvy = this_user.curvy + int(request.form['curvy'])
        this_user.thin = this_user.thin + int(request.form['thin'])
        this_user.tall = this_user.tall + int(request.form['tall'])
        this_user.short = this_user.short + int(request.form['short'])
        this_user.fair_complexion = this_user.fair_complexion \
            + int(request.form['fair'])
        this_user.tan_complexion = this_user.tan_complexion \
            + int(request.form['tan'])
        this_user.dark_complexion = this_user.dark_complexion \
            + int(request.form['dark'])
        this_user.smile = this_user.smile + int(request.form['smile'])

        session.add(this_user)
        session.commit()

        target_features.hairstyle = target_features.hairstyle \
            + int(request.form['hairstyle'])
        target_features.eyes = target_features.eyes \
            + int(request.form['eyes'])
        target_features.style = target_features.style \
            + int(request.form['style'])
        target_features.beard = target_features.beard \
            + int(request.form['beard'])
        target_features.tattoos = target_features.tattoos \
            + int(request.form['tattoos'])
        target_features.piercings = target_features.piercings \
            + int(request.form['piercings'])
        target_features.fit = target_features.fit \
            + int(request.form['fit'])
        target_features.average = target_features.average \
            + int(request.form['average'])
        target_features.curvy = target_features.curvy \
            + int(request.form['curvy'])
        target_features.thin = target_features.thin \
            + int(request.form['thin'])
        target_features.tall = target_features.tall \
            + int(request.form['tall'])
        target_features.short = target_features.short \
            + int(request.form['short'])
        target_features.fair_complexion = \
            target_features.fair_complexion + int(request.form['fair'])
        target_features.tan_complexion = target_features.tan_complexion \
            + int(request.form['tan'])
        target_features.dark_complexion = \
            target_features.dark_complexion + int(request.form['dark'])
        target_features.smile = target_features.smile \
            + int(request.form['smile'])

        session.add(target_features)
        session.commit()

        print 'eyes are now ' + str(this_user.eyes)
        print 'hair are now ' + str(this_user.hairstyle)

        users_liked = this_user.user_liked
        users_liked_list = []

        target_users_liked = target_liked.user_liked
        target_users_liked_list = []

        for x in target_users_liked.split('&'):
            target_users_liked_list.append(x)
            print 'user ids in target user liked list is: ' + x

        for x in users_liked.split('&'):
            users_liked_list.append(x)

        for x in users_liked_list:
            for y in target_users_liked_list:

                if y:

                    if x == y and unichr(target_liked.id) \
                        != unichr(int(float(y))):
                        print 'target_liked.id type is ' \
                            + str(type(unichr(target_liked.id)))
                        print 'y type is ' + str(type(y))
                        print 'target liked id is ' \
                            + str(target_liked.id) \
                            + '  while y is equal to ' + str(y)
                        print str(x) + ' string y is: ' + str(y)
                        this_user.matches = str(this_user.matches) \
                            + str(target_liked.id) + '&'
                        target_liked.matches = \
                            str(target_liked.matches) \
                            + str(this_user.id) + '&'
                        session.add(this_user, target_liked)
                        session.commit()
                        folder = str(this_user.id)

                        return render_template(
                            'newMatch.html',
                            this_user=this_user,
                            target=target_liked,
                            photo1=photo1.name,
                            folder2=str(target_liked.id),
                            this_user_photo=this_user_photo,
                            folder=folder,
                            )

        # if target user is a male use user traits male

        return redirect(url_for('profile'))

    return render_template('swipeRight.html', photo1=photo1.name,
                           folder2=str(target_liked.id),
                           target_liked=target_liked)


@app.route('/profile/nliked/<int:target_nliked>/', methods=['GET',
           'POST'])
@login_required
def nliked(target_nliked):
    this_user = session.query(User).filter_by(id=current_user.id).one()
    target_disliked = \
        session.query(User).filter_by(id=target_nliked).one()
    print 'this user disliked list is ' + str(this_user.user_disliked)
    this_user.user_disliked = str(this_user.user_disliked) + '&' \
        + str(target_disliked.id)
    session.add(this_user)
    session.commit()
    return redirect(url_for('profile'))


@app.route('/profile/options/', methods=['GET', 'POST'])
@login_required
def profileOptions():

    this_user = session.query(User).filter_by(id=current_user.id).one()
    print 'current_user.id is equal to ' + str(current_user.id) \
        + ' this_user from session query is equal to ' \
        + str(this_user.id)
    user_photos = \
        session.query(Photo).filter_by(owner_id=current_user.id).all()
    photo1 = session.query(Photo).filter_by(owner_id=current_user.id,
            num=1).one()
    photo2 = session.query(Photo).filter_by(owner_id=current_user.id,
            num=2).one()
    photo3 = session.query(Photo).filter_by(owner_id=current_user.id,
            num=3).one()
    photo4 = session.query(Photo).filter_by(owner_id=current_user.id,
            num=4).one()
    photo5 = session.query(Photo).filter_by(owner_id=current_user.id,
            num=5).one()
    return render_template(
        'profileOptions.html',
        this_user=this_user,
        photos=user_photos,
        folder=str(current_user.id),
        photo1=photo1,
        photo2=photo2,
        photo3=photo3,
        photo4=photo4,
        photo5=photo5,
        )


@app.route('/profile/edit/', methods=['GET', 'POST'])
@login_required
def editProfile():

    this_user = session.query(User).filter_by(id=current_user.id).one()
    print 'current_user is ' + str(this_user.id)
    user_photos = \
        session.query(Photo).filter_by(owner_id=current_user.id).all()
    photo1 = session.query(Photo).filter_by(owner_id=this_user.id,
            num=1).one()
    photo2 = session.query(Photo).filter_by(owner_id=this_user.id,
            num=2).one()
    photo3 = session.query(Photo).filter_by(owner_id=this_user.id,
            num=3).one()
    photo4 = session.query(Photo).filter_by(owner_id=this_user.id,
            num=4).one()
    photo5 = session.query(Photo).filter_by(owner_id=this_user.id,
            num=5).one()
    return render_template(
        'profileEdit.html',
        this_user=this_user,
        photos=user_photos,
        folder=str(current_user.id),
        photo1=photo1,
        photo2=photo2,
        photo3=photo3,
        photo4=photo4,
        photo5=photo5,
        )


@app.route('/profile/messages/', methods=['GET', 'POST'])
@login_required
def messages():

    this_user = session.query(User).filter_by(id=current_user.id).one()
    user_photos = session.query(Photo).all()
    all_users = session.query(User).all()
    all_messages = session.query(Messages).all()
    last_message_all = session.query(LastMessage).all()
    conversation_id_here = None
    current_conversation = None
    current_conversation_count = None

    matches_list = []
    matches_list_int = []
    folder_list = []
    matches_list_str = []

    if this_user.matches:

        for x in this_user.matches.split('&'):

            matches_list.append(x)
        for x in matches_list:
            if x and x is not chr(0):
                print str(type(x))
                print 'Matches are ' + str(x)
                matches_list_int.append(int(float(x)))

                matches_list_str.append(str(x))
                for i in range(0, 200):
                    folder_list.append(str(i))
                    print 'folders are ' + str(i)
                print str(type(matches_list_int[0]))

        # for a in all_messages:
        # ....print("this user id is " + str(this_user.id))
        # ....print("target user id is " + str(target_user.id))
        # ....print("a.user1 id is " + str(a.user1_id) + " and a.user2.id is " + str(a.user2_id))
        # ....if a.user1_id == this_user.id and a.user2_id == target_user.id or a.user1_id == target_user.id and a.user2_id == this_user.id:
        # ........print("should have found id inside if users match up with id inside messages")
        # ........conversation_id_here = a.conversation_id
        # ........current_conversation_count = a.conversation_count
        # ........print("conversation id is inside if statement is equal to " + str(conversation_id_here))

        # if conversation_id_here != None:............
        # ....current_conversation = session.query(Messages).filter_by(conversation_id = conversation_id_here).all()
        # ....conversation_count = len(current_conversation)
        # ....last_message = session.query(Messages).filter_by(conversation_id = conversation_id_here, conversation_count = conversation_count).one()
        # ....return render_template('matches.html', matches = matches_list_int, this_user = this_user, photos = user_photos, matches_str = matches_list_str, last_message = last_message, folder = folder_list, all_users = all_users, current_conversation = current_conversation, conversation_count = conversation_count)................

        return render_template(
            'matches.html',
            last_messages=last_message_all,
            matches=matches_list_int,
            this_user=this_user,
            photos=user_photos,
            matches_str=matches_list_str,
            folder=folder_list,
            all_users=all_users,
            messages=all_messages,
            )
    return render_template('matches.html', this_user=this_user,
                           photos=user_photos,
                           folder=str(current_user.id),
                           all_users=all_users)


@app.route('/profile/messages/<int:target>/', methods=['GET', 'POST'])
@login_required
def conversation(target):
    this_user = session.query(User).filter_by(id=current_user.id).one()
    target_user = session.query(User).filter_by(id=target).one()
    all_messages = session.query(Messages).all()
    conversation_id_here = None
    current_conversation = None
    current_conversation_count = None

    target_profile_picture = \
        session.query(Photo).filter_by(owner_id=target_user.id,
            num=1).one()
    folder = str(target_user.id)

    for a in all_messages:
        print 'this user id is ' + str(this_user.id)
        print 'target user id is ' + str(target_user.id)
        print 'a.user1 id is ' + str(a.user1_id) \
            + ' and a.user2.id is ' + str(a.user2_id)
        if a.user1_id == this_user.id and a.user2_id == target_user.id \
            or a.user1_id == target_user.id and a.user2_id \
            == this_user.id:
            print 'should have found id inside if users match up with id inside messages'
            conversation_id_here = a.conversation_id
            current_conversation_count = a.conversation_count
            print 'conversation id is inside if statement is equal to ' \
                + str(conversation_id_here)

    if request.method == 'POST':
        if conversation_id_here != None:
            conversation = Messages(user1_id=this_user.id,
                                    user2_id=target_user.id,
                                    message=request.form['message'],
                                    conversation_id=conversation_id_here,
                                    conversation_count=current_conversation_count
                                    + 1)
            print 'Current conversation id has been found. Conversation exists'
            last_message_sent = LastMessage(user1_id=this_user.id,
                    user2_id=target_user.id,
                    last_message=request.form['message'])
            session.add(conversation)
            session.add(last_message_sent)
            session.commit()
            current_conversation = \
                session.query(Messages).filter_by(conversation_id=conversation.conversation_id).all()

            return redirect(url_for('conversation',
                            target=target_user.id))
        if conversation_id_here == None:
            print 'conversation id is none, cannot find conversation'
            conversation = Messages(user1_id=this_user.id,
                                    user2_id=target_user.id,
                                    conversation_count=1,
                                    message=request.form['message'])
            conversation.conversation_id = conversation.id

            last_message_sent = LastMessage(user1_id=this_user.id,
                    user2_id=target_user.id,
                    last_message=request.form['message'])
            session.add(last_message_sent)
            session.add(conversation)
            session.commit()

            conversation.conversation_id = conversation.id
            session.add(conversation)
            session.commit()
            current_conversation = \
                session.query(Messages).filter_by(conversation_id=conversation.conversation_id).all()
            return redirect(url_for('conversation',
                            target=target_user.id))

    if conversation_id_here != None:

        print 'conversation_id_here was found'
        current_conversation = \
            session.query(Messages).filter_by(conversation_id=conversation_id_here).all()
        conversation_count = len(current_conversation)
        print conversation_count
        return render_template(
            'conversation.html',
            this_user=this_user,
            target_user=target_user,
            all_messages=all_messages,
            folder=folder,
            current_conversation=current_conversation,
            target_photo=target_profile_picture,
            )

    print 'conversation id was not found'
    print 'conversation id is equal to ' + str(conversation_id_here)
    return render_template(
        'conversation.html',
        this_user=this_user,
        target_user=target_user,
        all_messages=all_messages,
        folder=folder,
        target_photo=target_profile_picture,
        )


@app.route('/upload/<int:photo_num>/', methods=['GET', 'POST'])
@login_required
def upload_photo(photo_num):
    if request.method == 'POST':

        userinfo = \
            session.query(User).filter_by(id=current_user.id).one()
        all_photos = \
            session.query(Photo).filter_by(owner_id=current_user.id).all()
    if 'file' not in request.files:

        return redirect(request.url)
    file = request.files['file']

        # if user does not select file, browser also
        # submit a empty part without filename

    if file.filename == '':

            # flash('No selected file')

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

        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        for a in all_photos:
            if a.num == photo_num:
                print 'should delete the file'

                    # deleteThis = session.query(Photo).filter_by(owner_id = current_user.id, id = photo_num).one()

                session.delete(a)
                session.commit()

        newPhoto = Photo(name=filename, owner_id=userinfo.id,
                         num=photo_num)
        session.add(newPhoto)
        session.commit()

            # flash("Photo Added")

        user_photos = \
            session.query(Photo).filter_by(owner_id=current_user.id).all()

        return redirect(url_for('editProfile', this_user=userinfo,
                        photos=user_photos,
                        folder=str(current_user.id)))
    else:
        return 'didnt work'

if __name__ == '__main__':

    app.debug = False
    app.run(host='0.0.0.0')


			