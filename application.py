from flask import Flask, render_template, request, redirect, url_for,abort, flash
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os, uuid
import json, csv
from flask_login import LoginManager, login_required, logout_user, login_user, current_user
from flask_bcrypt import Bcrypt
from functions.forms import LoginForm,JobPostingForm,UserSignupForm
from werkzeug.utils import secure_filename
import datetime
import shutil

UPLOAD_FOLDER = 'static/uploaded_files/user'#save to S3 eventually
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','csv'}


import stripe

application = Flask(__name__)


with application.app_context():   
    application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    application.config['STRIPE_PUBLIC_KEY'] = 'pk_test_51JwRkQEZnfYhIETsWxXVh4JjvubnWHSZUJhgP7rzWBLYvr1PfJw9Z65FjgjZLqafJ54XvPstgneOxvEPAQyw7Wf100vVilZYVL'
    application.config['STRIPE_SECRET_KEY'] = 'sk_test_51JwRkQEZnfYhIETszhqjVlZtzUbWwuM4kyfBVBYzq8fSZMwfuSeURxwrK9RCzxZRxD3WlVobY9Gp8HzoFlNzEKSw00xBsjR0Us'
    application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    application.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuob9'
    db = SQLAlchemy(application)

    stripe.api_key = application.config['STRIPE_SECRET_KEY']

    ###Class DB###
    class User(db.Model):
        """
        :param str username: username
        :param str password: encrypted password for the user

        """
        __tablename__ = 'user'

        username = db.Column(db.String, primary_key=True)
        email = db.Column(db.String)
        phonenumber = db.Column(db.String)
        firstname = db.Column(db.String)
        lastname = db.Column(db.String)
        city = db.Column(db.String)
        state = db.Column(db.String)
        password = db.Column(db.String)
        authenticated = db.Column(db.Boolean, default=False)
        buyer = db.Column(db.Boolean, default=False)
        seller = db.Column(db.Boolean, default=False)


        def is_active(self):
            """True, as all users are active."""
            return True

        def get_id(self):
            """Return the username to satisfy Flask-Login's requirements."""
            return self.username

        def is_authenticated(self):
            """Return True if the user is authenticated."""
            return self.authenticated

        def is_anonymous(self):
            """False, as anonymous users aren't supported."""
            return False

    class JobPost(db.Model):
        """An admin user capable of viewing reports.

        :param str username: username
        :param str password: encrypted password for the user

        """
        __tablename__ = 'jobpost'

        username = db.Column(db.String)
        jobid = db.Column(db.String,primary_key=True)
        contactemail = db.Column(db.String)
        contactphone = db.Column(db.String)
        website = db.Column(db.String)
        companydescription = db.Column(db.String)
        jobtype = db.Column(db.String)
        jobdescription = db.Column(db.String)
        payoffered = db.Column(db.String)
        jobduration = db.Column(db.String)
        startdate = db.Column(db.String)
        longdescription = db.Column(db.String)
        authenticated = db.Column(db.Boolean, default=False)

        def is_active(self):
            """True, as all users are active."""
            return True

        def get_id(self):
            """Return the username to satisfy Flask-Login's requirements."""
            return self.username

        def is_authenticated(self):
            """Return True if the user is authenticated."""
            return self.authenticated

        def is_anonymous(self):
            """False, as anonymous users aren't supported."""
            return False

    class FileUpload(db.Model):
        __tablename__ = 'checkfileupload'

        username = db.Column(db.String, primary_key=True)
        authenticateddriverslicense = db.Column(db.Boolean, default=False)
        uploadeddriverslicense = db.Column(db.Boolean, default=False)
        authenticatedprequal = db.Column(db.Boolean, default=False)
        uploadedprequal = db.Column(db.Boolean, default=False)
        prequalfilename = db.Column(db.String, default='')
        driverslicensefilename = db.Column(db.String, default='')
        prequalamount = db.Column(db.String, default='')
        uploadedprequaldate = db.Column(db.DateTime)
        uploadeddriverslicensedate = db.Column(db.DateTime)
        authenticateddriverslicensedate = db.Column(db.DateTime)
        authenticatedprequaldate = db.Column(db.DateTime)

    class Listings(db.Model):
        __tablename__ = 'homelistings'

        username = db.Column(db.String, primary_key=True)
        listingprice = db.Column(db.String, default='')
        beds = db.Column(db.String, default='')
        baths = db.Column(db.String, default='')
        sqft = db.Column(db.String, default='')
        address = db.Column(db.String, default='')
        city = db.Column(db.String, default='')
        state = db.Column(db.String, default='')
        zipcode = db.Column(db.String, default='')
        mlsid = db.Column(db.String, default='')
        

    db.create_all()
    login_manager = LoginManager()
    login_manager.init_app(application)
    bcrypt = Bcrypt()

    @login_manager.user_loader
    def user_loader(user_id):
        """Given *user_id*, return the associated User object.

        :param unicode user_id: user_id (username) user to retrieve

        """
        return User.query.get(user_id)


    #######################Global Functions##############################
    def allowed_file(filename):
        return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    #######################Global Functions##############################


    #######################Global Routes##############################

    @application.route('/')
    def welcome():
        #test listing
        seeker = Listings.query.get('cbj3585')
        if not seeker:
            mm = Listings(
                username = 'cbj3585',
                listingprice = '595000',
                beds = '6',
                baths = '5',
                sqft = '5500',
                address = '110 3rd Street',
                city = 'Radford',
                state = 'Virginia',
                zipcode = '24141',
                mlsid = '0123456789',
            )
            db.session.add(mm)
            db.session.commit()
            if not os.path.exists(os.path.join(application.config['UPLOAD_FOLDER'],'cbj3585','listingphotos')):
                filename = 'first_house.jpeg'
                os.makedirs(os.path.join(application.config['UPLOAD_FOLDER'],'cbj3585','listingphotos'))
                dest = os.path.join(application.config['UPLOAD_FOLDER'],'cbj3585','listingphotos',filename)
                shutil.copyfile(filename, dest)
        seeker = Listings.query.get('har122222')
        if not seeker:
            mm = Listings(
                username = 'har122222',
                listingprice = '500000',
                beds = '6',
                baths = '5',
                sqft = '5500',
                address = '123 5th Street',
                city = 'Blacksburg',
                state = 'Virginia',
                zipcode = '24141',
                mlsid = '9876543210',
            )
            db.session.add(mm)
            db.session.commit()
            if not os.path.exists(os.path.join(application.config['UPLOAD_FOLDER'],'har122222','listingphotos')):
                filename = 'first_house.jpeg'
                os.makedirs(os.path.join(application.config['UPLOAD_FOLDER'],'har122222','listingphotos'))
                dest = os.path.join(application.config['UPLOAD_FOLDER'],'har122222','listingphotos',filename)
                shutil.copyfile(filename, dest)
        return render_template('welcome.html', )
        
    @application.route("/listing_table")
    def listing_table():
        if current_user.is_authenticated:
            if current_user.buyer == True:
                buyer = current_user.username
                listings = Listings.query.all()
                poster_data = User.query.filter(User.username == buyer)
                for mm in poster_data:
                    by = mm.buyer
                if by == True:
                    ut = 'Home Buyer'
                else:
                    ut = 'Home Seller'
                return render_template('listing_table_buyer.html', homelistings=listings, buyer=buyer, tabtitle='Symply Home Listings',ut=ut)
        else:
            listings = Listings.query.all()
            return render_template('listing_table.html', homelistings=listings, tabtitle='Symply Home Listings')

        
    @application.route("/save_profile_changes", methods=["GET", "POST"])
    @login_required
    def save_profile_changes():
        poster = User.query.get(current_user.username) 
        poster.username=request.form.get("username")
        poster.email=request.form.get("email")
        poster.phonenumber=request.form.get("phonenumber")
        poster.firstname=request.form.get("firstname")
        poster.lastname=request.form.get("lastname")
        poster.city=request.form.get("city")
        poster.state=request.form.get("state")
        db.session.commit()
        msg='Data Updated'
        form = UserSignupForm()
        buyer = current_user.username
        upload_data = FileUpload.query.filter(FileUpload.username == buyer)
        poster_data = User.query.filter(User.username == buyer)
        for mm in poster_data:
            by = mm.buyer
        if by == True:
            ut = 'Home Buyer'
        else:
            ut = 'Home Seller'
        return render_template('user_profile.html', buyer=buyer, poster_data=poster_data, form=form, upload_data=upload_data, msg=msg,ut=ut)

    @application.route('/job_information/<jobid>', methods=["GET"])
    def job_information(jobid):
        if current_user.is_authenticated:
            poster_information = JobPost.query.get(jobid)
            long_desc = poster_information.longdescription
            poster = current_user.username
            return render_template('job_information_login.html', long_desc=long_desc, jobid=jobid, poster=poster)
        else:
            poster_information = JobPost.query.get(jobid)
            long_desc = poster_information.longdescription
            return render_template('job_information.html', long_desc=long_desc, jobid=jobid)

    @application.route("/edit_post/<jobid>", methods=["GET", "POST"])
    @login_required
    def edit_post(jobid):
        post_information = JobPost.query.get(jobid)
        form = JobPostingForm()
        poster = current_user.username
        return render_template('edit_post.html', poster=poster, form=form, pi=post_information)

    @application.route("/save_post_changes/<jobid>", methods=["GET", "POST"])
    @login_required
    def save_post_changes(jobid):
        poster = JobPost.query.get(jobid)
        poster.jobid=request.form.get("jobid") 
        poster.username=current_user.username
        poster.contactemail=request.form.get("contactemail")
        poster.contactphone=request.form.get("contactphone")
        poster.website=request.form.get("website")
        poster.companydescription=request.form.get("companydescription")
        poster.jobtype=request.form.get("jobtype")
        poster.jobdescription=request.form.get("jobdescription")
        poster.payoffered=request.form.get("payoffered")
        poster.jobduration=request.form.get("jobduration")
        poster.startdate=request.form.get("startdate")
        poster.longdescription=request.form.get("longdescription")
        db.session.commit()
        poster = current_user.username
        return redirect(url_for('poster_dashboard'))

    @application.route("/post_post", methods=["GET", "POST"])
    @login_required
    def post_post():
        form = JobPostingForm()
        poster = current_user.username
        jobpost = JobPost(
                username=poster,
                jobid=form.jobid.data,
                contactemail=form.contactemail.data,
                contactphone=form.contactphone.data,
                website=form.website.data,
                companydescription=form.companydescription.data,
                jobtype=form.jobtype.data,
                jobdescription=form.jobdescription.data,
                payoffered=form.payoffered.data,
                jobduration=form.jobduration.data,
                startdate=form.startdate.data,
                longdescription=form.longdescription.data,)
        db.session.add(jobpost)
        db.session.commit()
        myposts = JobPost.query.filter(JobPost.username == poster)
        msg='Post Added!'
        return redirect(url_for('buyer_dashboard'))
    #    return render_template('poster_dashboard.html', poster=poster, form=form, myposts=myposts, msg=msg)

    @application.route("/delete_post/<jobid>", methods=["GET", "POST"])
    @login_required
    def delete_post(jobid):
        msg = 'REALLY DELETE POST WITH JOBID: '+str(jobid)+' ?!?!'
        form = JobPostingForm()
        poster = current_user.username
        post_information = JobPost.query.get(jobid)
        return render_template('delete_post.html', poster=poster, form=form, pi=post_information, msg=msg)

    @application.route("/confirm_delete_post/<jobid>", methods=["GET", "POST"])
    @login_required
    def confirm_delete_post(jobid):
        num_rows_deleted = JobPost.query.filter(JobPost.jobid == jobid).delete()
        db.session.commit()
        msg = 'JOBID: '+str(jobid)+' DELETED...'
        form = JobPostingForm()
        poster = current_user.username
        post_information = JobPost.query.get(jobid)
        return redirect(url_for('poster_dashboard'))
    #    return render_template('delete_post.html', poster=poster, form=form, pi=post_information, msg=msg)

    #######################Global Routes##############################


    ################BUYER#####################################


    @application.route('/buyer_dashboard')
    @login_required
    def buyer_dashboard():
        buyer = current_user.username
        upload_data = FileUpload.query.filter(FileUpload.username == buyer)
        poster_data = User.query.filter(User.username == buyer)
        for mm in poster_data:
            by = mm.buyer
        if by == True:
            ut = 'Home Buyer'
        else:
            ut = 'Home Seller'
        return render_template('buyer_dashboard.html', buyer=buyer, upload_data=upload_data, ut=ut)


    @application.route('/upload_file', methods=['GET', 'POST'])
    @login_required
    def upload_file():
        buyer = current_user.username
        upload_data = FileUpload.query.filter(FileUpload.username == buyer)
        poster_data = User.query.filter(User.username == buyer)
        for mm in poster_data:
            by = mm.buyer
        if by == True:
            ut = 'Home Buyer'
        else:
            ut = 'Home Seller'
        if request.method == 'POST':
            try:
                file = request.files['driverslicense']
                fname = file.filename
            except:
                file = request.files['prequal']
                fname = file.filename
            if file.filename == '':
                flash('No selected file...Click to Remove')
                upload_data = FileUpload.query.filter(FileUpload.username == buyer)
                return render_template('buyer_dashboard.html', buyer=buyer, upload_data=upload_data,ut=ut)
            if 'driverslicense' in request.files.keys():
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    #move to cloud eventually
                    if not os.path.exists(os.path.join(application.config['UPLOAD_FOLDER'],str(buyer),'dl')):
                        os.makedirs(os.path.join(application.config['UPLOAD_FOLDER'],str(buyer),'dl'))
                    file.save(os.path.join(application.config['UPLOAD_FOLDER'],str(buyer),'dl', filename))#save file as type and name and date, update a file metadata db as well
                    ###
                    flash('Uploaded File Successfully!...Click to Remove')
                    data_to_update = dict(uploadeddriverslicense=True, driverslicensefilename=fname,authenticateddriverslicense=True, uploadeddriverslicensedate=datetime.datetime.utcnow(), authenticateddriverslicensedate=datetime.datetime.utcnow())
                    upload_data.update(data_to_update)
                    db.session.commit()
                    upload_data = FileUpload.query.filter(FileUpload.username == buyer)
                    return render_template('buyer_dashboard.html', buyer=buyer, upload_data=upload_data,ut=ut)
            elif 'prequal' in request.files.keys():
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    if not os.path.exists(os.path.join(application.config['UPLOAD_FOLDER'],str(buyer),'pq')):
                        os.makedirs(os.path.join(application.config['UPLOAD_FOLDER'],str(buyer),'pq'))
                    file.save(os.path.join(application.config['UPLOAD_FOLDER'],str(buyer),'pq', filename))#save file as type and name and date, update a file metadata db as well
                    flash('Uploaded File Successfully!...Click to Remove')
                    data_to_update = dict(uploadedprequal=True, prequalfilename=fname,authenticatedprequal=True, prequalamount='500000', uploadedprequaldate=datetime.datetime.utcnow(), authenticatedprequaldate=datetime.datetime.utcnow())
                    upload_data.update(data_to_update)
                    db.session.commit()
                    upload_data = FileUpload.query.filter(FileUpload.username == buyer)
                    return render_template('buyer_dashboard.html', buyer=buyer, upload_data=upload_data,ut=ut)
                else:
                    upload_data = FileUpload.query.filter(FileUpload.username == buyer)
                    return render_template('buyer_dashboard.html', buyer=buyer,upload_data=upload_data,ut=ut)
        upload_data = FileUpload.query.filter(FileUpload.username == buyer)
        return render_template('buyer_dashboard.html', buyer=buyer,upload_data=upload_data,ut=ut)
    

    
    ################BUYER#####################################









    ################USER#######################################

    @application.route("/user_login", methods=["GET", "POST"])
    def user_login():
        if current_user.is_authenticated:
            seeker = User.query.get(current_user.username)
            if seeker.buyer == True:
                return redirect(url_for('buyer_dashboard'))
            else:
                return redirect(url_for('job_posting_table'))
        form = LoginForm()
        if form.validate_on_submit():
            seeker = User.query.get(form.username.data) 
            if seeker:
                if bcrypt.check_password_hash(seeker.password, form.password.data):
                    seeker.authenticated = True
                    db.session.add(seeker)
                    db.session.commit()
                    login_user(seeker, remember=True)
                    if seeker.buyer == True:
                        return redirect(url_for('buyer_dashboard'))
                    else:
                        return redirect(url_for('job_posting_table'))
        return render_template('user_login.html', form=form, tabtitle='Symply Login')


    @application.route("/user_signup", methods=["GET", "POST"])
    def user_signup():
        if current_user.is_authenticated:
            return redirect(url_for('user_profile'))
        form = UserSignupForm()
        if form.validate_on_submit():
            seeker = User.query.get(form.username.data)
            if seeker:
                return render_template("user_signup.html", form=form, tabtitle='Symply SignUp',msg='Username taken, please choose another!')
            else:
                usertype = form.usertype.data
                if usertype == 'buyer':
                    seeker = User(
                        username=form.username.data,
                        email=form.email.data,
                        phonenumber=form.phonenumber.data,
                        firstname=form.firstname.data,
                        lastname=form.lastname.data,
                        city=form.city.data,
                        state=form.state.data,
                        buyer=True,
                        password=bcrypt.generate_password_hash(form.password.data))
                    db.session.add(seeker)
                    db.session.commit()
                    ff = FileUpload(
                        username = form.username.data,
                        prequalamount='0')
                    db.session.add(ff)
                    db.session.commit()
                else:
                    seeker = User(
                        username=form.username.data,
                        email=form.email.data,
                        phonenumber=form.phonenumber.data,
                        firstname=form.firstname.data,
                        lastname=form.lastname.data,
                        city=form.city.data,
                        state=form.state.data,
                        seller=True,
                        password=bcrypt.generate_password_hash(form.password.data))
                    db.session.add(seeker)
                    db.session.commit()
                seeker.authenticated = True
                login_user(seeker, remember=True)
                return redirect(url_for("user_profile"))
        return render_template("user_signup.html", form=form, tabtitle='SignUp', msg='')

    @application.route('/user_profile',methods=["GET", "POST"])
    @login_required
    def user_profile():
        form = UserSignupForm()
        buyer = current_user.username
        poster_data = User.query.filter(User.username == buyer)
        upload_data = FileUpload.query.filter(FileUpload.username == buyer)
        for tt in upload_data:
            pq = tt.prequalfilename
            dl = tt.driverslicensefilename
        for mm in poster_data:
            by = mm.buyer
        if by == True:
            ut = 'Home Buyer'
        else:
            ut = 'Home Seller'
        return render_template('user_profile.html', buyer=buyer, poster_data=poster_data, form=form, pq=pq,dl=dl, ut=ut)
    ################USER#####################################





    @application.route('/purchase', methods=["GET", "POST"])
    @login_required
    def purchase():
        username=current_user.username
        contactemail=request.form.get("contactemail")
        website=request.form.get("website")
        jobid=request.form.get("jobid")
        companydescription=request.form.get("companydescription")
        jobtype=request.form.get("jobtype")
        jobdescription=request.form.get("jobdescription")
        payoffered=request.form.get("payoffered")
        jobduration=request.form.get("jobduration")
        startdate=request.form.get("startdate")
        post_data = [username,jobid,contactemail,website,companydescription,jobtype,jobdescription,payoffered,jobduration,startdate]
        post_data = json.dumps(post_data)
        return render_template(
            'purchase.html', post_data=post_data
            #checkout_session_id=session['id'], 
            #checkout_public_key=app.config['STRIPE_PUBLIC_KEY']
        )

    @application.route('/stripe_pay')
    @login_required
    def stripe_pay():
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': 'price_1JxAaZEZnfYhIETsUpgZmfEX',
                'quantity': 1,
            }],
            mode='payment',
    #        success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            success_url=url_for('job_posting_table', _external=True),
            cancel_url=url_for('welcome', _external=True),
        )
        return {
            'checkout_session_id': session['id'], 
            'checkout_public_key': application.config['STRIPE_PUBLIC_KEY']
        }

    @application.route('/thanks')
    @login_required
    def thanks():
        return render_template('thanks.html')

    @application.route("/logout", methods=["GET"])
    @login_required
    def logout():
        """Logout the current user."""
        user = current_user
        user.authenticated = False
        db.session.add(user)
        db.session.commit()
        logout_user()
        return render_template("welcome.html", tabtitle='Symply Logout Job Poster')


    @application.route('/stripe_webhook', methods=["GET","POST"])
    def stripe_webhook():
        print('WEBHOOK CALLED')

        payload = request.get_data()
        sig_header = request.environ.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = 'whsec_DhFvgZxQch4rKcUbglvmg5WUCNcynRId'
        event = None

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError as e:
            # Invalid payload
            print('INVALID PAYLOAD')
            return {}, 400
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            print('INVALID SIGNATURE')
            return {}, 400

        # Handle the checkout.session.completed event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            print('Checkout Session complete')
            line_items = stripe.checkout.Session.list_line_items(session['id'], limit=1)

        return {}


    if __name__ == "__main__":
        application.run(debug=True)