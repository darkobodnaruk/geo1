import time
import datetime

from geo1 import app
from flask import Flask, render_template, request, flash, session, redirect, url_for
from forms import SignupForm, SigninForm
from flask.ext.mail import Message, Mail
from models import db, User, VisitorLocation, LastLocation
from geoip import geolite2
from uuid import uuid4

mail = Mail()


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
     
    if request.method == 'POST':
        if form.validate() == False:
            return render_template('signup.html', form=form)
        else:   
            newuser = User(form.email.data, form.password.data)
            db.session.add(newuser)
            db.session.commit()

            session['email'] = newuser.email

            return redirect(url_for('main'))
     
    elif request.method == 'GET':
        return render_template('signup.html', form=form)


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    form = SigninForm()
     
    if request.method == 'POST':
        if form.validate() == False:
            return render_template('signin.html', form=form)
        else:
            session['email'] = form.email.data
            return redirect(url_for('main'))
                   
    elif request.method == 'GET':
        return render_template('signin.html', form=form)


@app.route('/signout')
def signout():
    if 'email' not in session:
        return redirect(url_for('signin'))
     
    session.pop('email', None)
    return redirect(url_for('main'))


@app.route('/set_location', methods=['POST'])
def set_location():
    if request.method == 'POST':
        if 'email' in session:
            user_id = User.query.filter_by(email = session['email']).first().uid
        else:
            user_id = None

        now = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

        last_location = LastLocation.query.filter_by(visitor_id=session['visitor_id']).first()
        if not last_location:
            last_location = LastLocation()
            last_location.visitor_id = session['visitor_id']
        last_location.uid = user_id
        last_location.lat = request.form['lat']
        last_location.lng = request.form['lng']
        last_location.dt = now
        db.session.add(last_location)
        db.session.commit()

        return "ok"


@app.route('/main', methods=['GET', 'POST'])
def main():
    if 'visitor_id' not in session:
        session['visitor_id'] = str(uuid4())

    remote_addr = request.environ['REMOTE_ADDR']    
    # TEMP, until we're on a public IP
    # remote_addr = "84.255.241.198"
    # remote_addr = "173.245.58.53"
    
    try:
        lat, lng = geolite2.lookup(remote_addr).location
    except Exception, e:
        lat, lng = None, None
    
    if 'email' in session:
        user_id = User.query.filter_by(email = session['email']).first().uid
    else:
        user_id = None

    now = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

    # save last visitor location in a separate table
    last_location = LastLocation.query.filter_by(visitor_id=session['visitor_id']).first()
    if not last_location:
        last_location = LastLocation()
        last_location.visitor_id = session['visitor_id']
    last_location.uid = user_id
    last_location.lat = lat
    last_location.lng = lng
    last_location.dt = now
    db.session.add(last_location)
    db.session.commit()
    
    # save visitor location for uniques-by-hour
    # XXX: this should totally be done in some more scalable way:
    #  - a non-relational datastore
    #  - parsed hourly from logs
    #  - at least a cronjob to periodically delete these entries
    visitor_location = VisitorLocation(user_id, session['visitor_id'], lat, lng, now)
    db.session.add(visitor_location)
    db.session.commit()

    # get number of unique visitors in last 24 hours
    last_24_hours = db.session.query("hour", "num_uniques").from_statement( \
        "SELECT CONCAT(DAY(dt), '/', MONTH(dt), ' ', HOUR(dt)) as hour, COUNT(DISTINCT visitor_id) as num_uniques FROM visitor_locations \
        WHERE dt >= DATE_SUB(NOW(), INTERVAL 24 HOUR) GROUP BY HOUR(dt) ORDER BY dt").all()

    # visitors in last minute
    num_current_visitors = LastLocation.query. \
      filter(LastLocation.dt > (datetime.datetime.utcnow() - datetime.timedelta(minutes=1))). \
      count()

    # visitors by proximity
    max_dist = 50
    since_dt = datetime.datetime.utcnow() - datetime.timedelta(minutes=1)
    visitors_by_proximity = db.session.query("email", "distance").from_statement( \
        "SELECT email, (6371 * acos(cos(radians(%f)) * cos(radians(lat)) * cos(radians(lng) - radians(%f)) + sin(radians(%f)) * sin(radians(lat)))) AS distance \
        FROM last_locations LEFT JOIN users ON last_locations.uid = users.uid \
        WHERE dt > '%s' \
        HAVING distance < %d \
        ORDER BY distance LIMIT 0, 20;" % (lat, lng, lat, since_dt, max_dist)) \
        .all()

    return render_template('main.html', last_24_hours=last_24_hours, num_current_visitors=num_current_visitors, visitors_by_proximity=visitors_by_proximity)


