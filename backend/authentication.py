from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user, LoginManager
from flask_bcrypt import Bcrypt
import sqlite3
import os
# from backend.forms import RegistrationForm, LoginForm, CampaignForm, AdRequestForm
from backend.models import *    

authentication = Blueprint('authentication', __name__)

bcrypt = Bcrypt()

@authentication.route("/register", methods=["GET", "POST"])
def user_register():
        if request.method == 'POST':
            email = request.form.get('email')
            username = request.form.get('username')
            password = request.form.get('password')
            role = request.form.get('dropdown')
            total_reach = request.form.get('total_reach')
            industry = request.form.get('industry')
            category = request.form.get('category')
            checkbox1 = 'facebook' in request.form
            checkbox2 = 'twitter' in request.form
            checkbox3 = 'instagram' in request.form
            checkbox4 = 'youtube' in request.form

            username_in_database = User.query.filter_by(username=username).first()
            email_in_database = User.query.filter_by(email=email).first()
            if username_in_database:
                flash('Username already exists', category = 'error')
                return render_template('register.html', msg = 'Username already exists')
            elif email_in_database:
                flash('Email already exists', category = 'error')
                return render_template('register.html', msg = 'Email already exists')
            else:    
                encrypted_password = generate_password_hash(password, method = 'scrypt')
                user = User(email = email, username = username, 
                               password = encrypted_password,
                               role = role, total_reach = total_reach, industry = industry, category = category,
                               facebook = checkbox1, twitter = checkbox2, instagram = checkbox3, youtube = checkbox4)
                db.session.add(user)
                db.session.commit()
                flash('Successfully Registered', category ='success')
        
                print(f"Email: {email}")
                print(f"Username: {username}")
                print(f"Password: {password}")
                # print(f"Social Networking Sites: {', '.join(presence)}")

            flash('Successfully Registered', category='success')
            return render_template('login.html', msg = 'Successfully Registered, please login to continue')
        return render_template("register.html")

@authentication.route("/login", methods=["GET", "POST"])
def user_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        # print(user.role)
        if user:
            if check_password_hash(user.password, password):
                if user.role == "influencer":
                    if user.flag == 0:
                        flash('Logged in successfully as an influencer', category='success')
                        login_user(user, remember=True)
                        return redirect(url_for('authentication.influencer_dashboard'))
                    else:
                        flash('User is flagged', category='error')
                        return render_template('login.html')    
                elif user.role == "admin":
                    flash('Logged in successfully as an admin', category='success')
                    login_user(user, remember=True)
                    return redirect(url_for('authentication.admin_dashboard'))
                elif user.role == "sponsor":
                    if user.flag == 0:
                        flash('Logged in successfully as a sponsor', category='success')
                        login_user(user, remember=True)
                        return redirect(url_for('authentication.sponsor_dashboard'))
                    else:
                        flash('User is flagged, please contact the Admin', category='error')
                        return render_template('login.html')
            else:
                flash('Incorrect password', category='error')
                return render_template('login.html')
        else:
            flash('User does not exist', category='error')
            return render_template('login.html')
    else:
        return render_template("login.html")
    
@authentication.route("/logout")
@login_required
def user_logout():
    logout_user()
    return redirect(url_for('authentication.user_login'))

@authentication.route("/influencer_dashboard", methods=["GET", "POST"])
@login_required
def influencer_dashboard():
    if current_user.role == "influencer":
        ad_data = []
        ad_requests = AdRequest.query.all()
        for ad_request in ad_requests:
            campaign = Campaign.query.filter_by(id = ad_request.campaign_id).first()
            if campaign.visibility != "Private":
                ad_data.append(
                    { 
                        'campaign_name': campaign.name,
                        'messages': ad_request.messages,
                        'End_Date': campaign.end_date,
                        'payment_amount': ad_request.payment_amount,
                        'status': ad_request.status,
                        "id": ad_request.id,
                        "request_type": ad_request.request_type
                    }
                )
            # sponsor = User.query.filter_by(id = campaign.sponsor_id).first()
        flash('Logged in successfully as an influencer', category='success')
        return render_template("influencer_dashboard.html", username = current_user.username, ad_requests = ad_data)
    else:
        return redirect(url_for('authentication.user_login'))
    
@authentication.route("/admin_dashboard", methods=["GET", "POST"])
@login_required
def admin_dashboard():
    if current_user.role == "admin":
        print(current_user.username)
        ad_requests = list()
        influencers = User.query.filter_by(role = "influencer").all()
        sponsors  = User.query.filter_by(role = "sponsor").all()
        campaigns = Campaign.query.all()
        ad_requests = AdRequest.query.all()
        # flags = Flag.query.all()
        for campaign in campaigns:
            Ad_Requests = AdRequest.query.filter_by(campaign_id = campaign.id).all()
            ad_requests.append(Ad_Requests)
            # sponsor.ad_requests = ad_requests
        flash('Logged in successfully as an admin', category='success')
        return render_template("admin_dashboard.html", username = current_user.username, 
                               influencers = influencers, sponsors = sponsors, 
                               campaigns = campaigns, ad_requests = ad_requests)
    else:
        return redirect(url_for('authentication.user_login'))

# sponsor_dashboard    
@authentication.route("/sponsor_dashboard", methods=["GET", "POST"])
@login_required
def sponsor_dashboard():
    if current_user.role == "sponsor":
        ad_data = list()
        flash('Logged in successfully as a sponsor', category='success')
        # print(current_user.id)
        campaigns = Campaign.query.filter_by(sponsor_id = current_user.id).all()
        if campaigns:
            for campaign in campaigns:
                ad_requests = AdRequest.query.filter_by(campaign_id = campaign.id).all()
                if ad_requests:
                    for ad_request in ad_requests:
                
                        ad_data.append(
                            { 
                                'campaign_name': campaign.name,
                                'messages': ad_request.messages,
                                'End_Date': campaign.end_date,
                                'payment_amount': ad_request.payment_amount,
                                'status': ad_request.status,
                                "id": ad_request.id,
                                "influencer_id": ad_request.influencer_id,
                                "request_type": ad_request.request_type
                            }
                        )  
            # print(ad_data)
            return render_template("sponsor_dashboard.html", username = current_user.username, campaigns = campaigns,
                                   ad_requests = ad_data)
        else:
            flash('No campaigns created yet!', category='error')
            return render_template("sponsor_dashboard.html", username = current_user.username)
    else:
        return redirect(url_for('authentication.user_login'))

# Create Campaign    
@authentication.route("/create_campaign", methods=["GET", "POST"])
@login_required
def create_campaign():
    if current_user.role == "sponsor":
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')
            niche = request.form.get('niche')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            budget = request.form.get('budget')
            visibility = request.form.get('visibility')
            goals = request.form.get('goals')

            # print(f"Name: {name}")
            # print(f"Description: {description}")
            # print(f"Niche: {niche}")
            # print(f"Start Date: {start_date}")
            # print(f"End Date: {end_date}")
            # print(f"Budget: {budget}")
            # print(f"Visibility: {visibility}")
            # print(f"Goals: {goals}")

            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

            # print(f"Name: {name}")
            # print(f"Description: {description}")
            # print(f"Niche: {niche}")
            # print(f"Start Date: {start_date}")
            # print(f"End Date: {end_date}")
            # print(f"Budget: {budget}")
            # print(f"Visibility: {visibility}")
            # print(f"Goals: {goals}")

            campaign = Campaign(name = name, description = description, niche = niche, start_date = start_date, updated_date = start_date,
                                end_date = end_date, budget = budget, visibility = visibility, goals = goals, 
                                sponsor_id = current_user.id)
            db.session.add(campaign)
            db.session.commit()
            flash('Campaign created successfully!', category='success')
            return redirect(url_for('authentication.sponsor_dashboard'))
        return render_template("create_campaign.html")
    else:
        return redirect(url_for('authentication.user_login'))  

#update campaign
@authentication.route("update_sponsor_campaign/<int:campaign_id>", methods=["GET", "POST"])
@login_required
def update_sponsor_campaign(campaign_id):
    if current_user.role == "sponsor":
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')
            updated_date = request.form.get('updated_date')
            end_date = request.form.get('end_date')
            budget = request.form.get('budget')
            visibility = request.form.get('visibility')
            goals = request.form.get('goals')

            if updated_date:
                updated_date = datetime.strptime(updated_date, '%Y-%m-%d')
            if end_date:    
                end_date = datetime.strptime(end_date, '%Y-%m-%d')

            # print(f"Name: {name}")
            # print(f"Description: {description}")
            # print(f"Updated Date: {updated_date}")
            # print(f"End Date: {end_date}")
            # print(f"Budget: {budget}")
            # print(f"Visibility: {visibility}")
            # print(f"Goals: {goals}")

            campaign = Campaign.query.filter_by(id = campaign_id).first()

            if campaign:
                if name:
                    campaign.name = name
                if description:    
                    campaign.description = description
                # campaign.start_date = campaign.start_date
                if updated_date:
                    campaign.updated_date = updated_date
                if end_date:    
                    campaign.end_date = end_date
                if budget:
                    campaign.budget = budget
                if visibility:
                    campaign.visibility = visibility
                if goals:
                    campaign.goals = goals    
                campaign.sponsor_id = current_user.id
                db.session.commit()
                flash('Campaign updated successfully!', category='success')
                return redirect(url_for('authentication.sponsor_dashboard'))
        else:
            campaign = Campaign.query.filter_by(id = campaign_id).first()
            name = campaign.name
            description = campaign.description
            updated_date = campaign.updated_date
            end_date = campaign.end_date
            budget = campaign.budget
            visibility = campaign.visibility
            goals = campaign.goals

            return render_template("update_sponsor_campaign.html", campaign_id = campaign_id, name = name, description = description,
                                   updated_date = updated_date, end_date = end_date, budget = budget, 
                                   visibility = visibility, goals = goals)
    else:
        flash('Something went wrong!', category='error')
        return redirect(url_for('authentication.user_login'))

# delete a Campaign
@authentication.route("/delete_sponsor_campaign/<int:campaign_id>", methods=["GET", "POST"])
@login_required
def delete_sponsor_campaign(campaign_id):
    if current_user.role == "sponsor":
        if request.method == "POST":
            campaign = Campaign.query.filter_by(id = campaign_id).first()
            db.session.delete(campaign)
            db.session.commit()
            flash('Campaign deleted successfully!', category='success')
            return redirect(url_for('authentication.sponsor_dashboard'))
        else:
            flash('Something went wrong!', category='error')
            return redirect(url_for('authentication.sponsor_dashboard'))
    else:
        flash('You are not authorized to view this page!', category='error')
        return redirect(url_for('authentication.user_login'))    

# create an ad request
@authentication.route("/create_ad_request/<int:campaign_id>", methods=["GET", "POST"])
@login_required
def create_ad_request(campaign_id):
    if current_user.role == "sponsor":
        if request.method == 'POST':
            messages = request.form.get('messages')
            requirements = request.form.get('requirements')
            payment_amount = request.form.get('payment_amount')
            status = request.form.get('status')

            # print(f"Messages: {messages}")
            # print(f"Requirements: {requirements}")
            # print(f"Payment Amount: {payment_amount}")
            # print(f"Status: {status}")

            ad_request = AdRequest(campaign_id = campaign_id, messages = messages, 
                                   requirements = requirements, payment_amount = payment_amount, 
                                   status = status, request_type = "sponsor-to-influencer" , influencer_id = 0)
            db.session.add(ad_request)
            db.session.commit()
            flash('Ad request created successfully!', category='success')
            return redirect(url_for('authentication.sponsor_dashboard'))
        return render_template("create_ad_request.html" , campaign_id = campaign_id)
    else:
        return redirect(url_for('authentication.user_login'))

# update an ad request
@authentication.route("/update_ad_request/<int:ad_request_id>", methods=["GET", "POST"])
@login_required
def update_ad_request(ad_request_id):
    if current_user.role == "sponsor":
        if request.method == 'POST':
            messages = request.form.get('messages')
            requirements = request.form.get('requirements')
            payment_amount = request.form.get('payment_amount')
            status = request.form.get('status')

            # print(f"Messages: {messages}")
            # print(f"Requirements: {requirements}")
            # print(f"Payment Amount: {payment_amount}")
            # print(f"Status: {status}")

            ad_request = AdRequest.query.get(ad_request_id)
            if ad_request:
                if messages:
                    ad_request.messages = messages
                if requirements:    
                    ad_request.requirements = requirements
                if payment_amount:
                    ad_request.payment_amount = payment_amount
                if status:
                    ad_request.status = status
                db.session.commit()
                flash('Ad request updated successfully!', category='success')
                return redirect(url_for('authentication.sponsor_dashboard'))
            flash('Invaild AdRequest id was queried!', category='error')
            return render_template("update_ad_request.html", ad_request_id = ad_request_id)
        else:
            variable =  AdRequest.query.filter_by(id = ad_request_id).first()
            messages = variable.messages
            requirements = variable.requirements
            payment_amount = variable.payment_amount
            status = variable.status

            return render_template("update_ad_request.html", ad_request_id = ad_request_id, messages = messages,
                                   requirements = requirements, payment_amount = payment_amount, status = status)
    else:
        flash('Something went wrong!', category='error')
        return redirect(url_for('authentication.user_login'))    

# delete an ad request
@authentication.route("/delete_ad_request/<int:ad_request_id>", methods=["GET", "POST"])
@login_required
def delete_ad_request(ad_request_id):
    if current_user.role == "sponsor":
        if request.method == "POST":
            ad_request = AdRequest.query.get(ad_request_id)
            db.session.delete(ad_request)
            db.session.commit()
            flash('Ad request deleted successfully!', category='success')
            return redirect(url_for('authentication.sponsor_dashboard'))
        else:
            flash('Something went wrong!', category='error')
            return redirect(url_for('authentication.sponsor_dashboard'))
    else:
        flash('You are not authorized to view this page!', category='error')
        return redirect(url_for('authentication.user_login'))      

# flag a user
@authentication.route("/flag_user/<int:user_id>", methods=["GET", "POST"])          
@login_required
def flag_user(user_id):
    if current_user.role == "admin":
        if request.method == "POST":
            user = User.query.filter_by(id = user_id).first()
            if user:
                if user.flag == 0:
                    user.flag = 1
                    db.session.commit()
            flash('User flagged successfully!', category='success')
            return redirect(url_for('authentication.admin_dashboard'))
        else:
            flash('Something went wrong!', category='error')
            return redirect(url_for('authentication.admin_dashboard'))

# delete a user
@authentication.route("/delete_user/<int:user_id>", methods=["GET", "POST"])
@login_required
def delete_user(user_id):
    if current_user.role == "admin":
        if request.method == "POST":
            user = User.query.filter_by(id = user_id).first()
            db.session.delete(user)
            db.session.commit()
            flash('User deleted successfully!', category='success')
            return redirect(url_for('authentication.admin_dashboard'))
        else:
            flash('Something went wrong!', category='error')
            return redirect(url_for('authentication.admin_dashboard'))
        
# accept ad request
@authentication.route("/accept_ad_request/<int:ad_request_id>", methods=["GET", "POST"])
@login_required
def accept_ad_request(ad_request_id):
    if current_user.role == "influencer":
        if request.method == "POST":
            Ad_Requests = AdRequest.query.filter_by(id = ad_request_id).first()
            Ad_Requests.status = "Accepted"
            Ad_Requests.influencer_id = current_user.id
            db.session.commit()
            # req = Request.query.filter_by(ad_request_id = ad_request_id).first()
            # db.session.delete(req)
            # db.session.commit()
            flash('Ad request accepted successfully!', category='success')
            return redirect(url_for('authentication.influencer_dashboard'))
        else:
            flash('Something went wrong!', category='error')
            return redirect(url_for('authentication.influencer_dashboard'))
    else:
        flash('You are not authorized to view this page!', category='error')
        return redirect(url_for('authentication.user_login'))
    
# reject ad request
@authentication.route("/reject_ad_request/<int:ad_request_id>", methods=["GET", "POST"])
@login_required
def reject_ad_request(ad_request_id):
    if current_user.role == "influencer":
        if request.method == "POST":
            Ad_Requests = AdRequest.query.filter_by(id = ad_request_id).first()
            Ad_Requests.status = "Rejected"
            Ad_Requests.influencer_id = current_user.id
            db.session.commit()
            flash('Ad request rejected successfully!', category='success')
            return redirect(url_for('authentication.influencer_dashboard'))
        else:
            flash('Something went wrong!', category='error')
            return redirect(url_for('authentication.influencer_dashboard'))
    else:
        flash('You are not authorized to view this page!', category='error')
        return redirect(url_for('authentication.user_login'))
    
# influencer my ad request
@authentication.route("/my_ad_request", methods=["GET", "POST"])
@login_required
def my_ad_request():
    if current_user.role == "influencer":
        if request.method == "POST":
            ad_requests = AdRequest.query.filter_by(influencer_id = current_user.id).all()
            data = Request.query.filter_by(influencer_id = current_user.id).all()
            return render_template("my_ad_request.html", ad_requests = ad_requests, data = data, username = current_user.username)
        else:
            flash('Something went wrong!', category='error')
            return redirect(url_for('authentication.influencer_dashboard'))
    else:
        flash('You are not authorized to view this page!', category='error')
        return redirect(url_for('authentication.user_login'))

# unflag a user    
@authentication.route("/unflag_user/<int:user_id>", methods=["GET", "POST"])
@login_required
def unflag_user(user_id):
    if current_user.role == "admin":
        if request.method == "POST":
            user = User.query.filter_by(id = user_id).first()
            if user:
                if user.flag == 1:
                    user.flag = 0
                    db.session.commit()
            flash('User unflagged successfully!', category='success')
            return redirect(url_for('authentication.admin_dashboard'))
        else:
            flash('Something went wrong!', category='error')
            return redirect(url_for('authentication.admin_dashboard'))
    else:
        flash('You are not authorized to view this page!', category='error')
        return redirect(url_for('authentication.user_login'))

# sponsor search
@authentication.route("/sponsor_search", methods=["GET", "POST"])    
@login_required
def sponsor_search():
    if request.method == "POST":
        L = []
        search_query = request.form.get("search", "")
        filter = request.form.get("radio")

        if current_user.role == "sponsor":
            if search_query:
                if filter == "influencer":
                    users = User.query.filter(User.username.like(f"%{search_query}%")).all()
                    return render_template("sponsor_search.html", users = users, filter = filter, 
                                           username = current_user.username, role = current_user.role)
                elif filter == "category":
                    user_category = User.query.filter(User.category.like(f"%{search_query}%")).all()
                    print(user_category)
                    for user in user_category:
                        if user.category == search_query:
                            L.append(user)
                        else:
                            continue        
                    return render_template("sponsor_search.html", L = L, filter = filter, 
                                            username = current_user.username, role = current_user.role)
                elif filter == "reach":
                    user_reach = User.query.filter(User.total_reach.like(f"%{search_query}%")).all()
                    for user in user_reach:                        
                        L.append(user)
                    return render_template("sponsor_search.html", L = L, filter = filter, 
                                            username = current_user.username, role = current_user.role)

                else:
                        flash('Nothing found!', category='error')
                        return redirect(url_for('authentication.sponsor_dashboard'))
                
    else:
        flash('Something went wrong!', category='error')
        return redirect(url_for('authentication.sponsor_search'))

# influencer search
@authentication.route("/influencer_search", methods=["GET", "POST"])
@login_required
def influencer_search():
    if request.method == "POST":
        search_query = request.form.get("search", "")
        filter = request.form.get("radio")

        if current_user.role == "influencer":
            if search_query:
                if filter == "campaign":
                    campaigns = Campaign.query.filter(Campaign.name.like(f"%{search_query}%")).all()
                    if campaigns:
                        
                        return render_template("influencer_search.html", campaigns = campaigns, filter = filter, username = current_user.username, role = current_user.role)
                    
                    else:
                        flash('No campaigns found!', category='error')
                        return render_template("influencer_search.html", campaigns = [], username = current_user.username, role = current_user.role)
                
                if filter == "niche":
                    ad_data = []
                    campaigns = Campaign.query.filter(Campaign.niche.like(f"%{search_query}%")).all()
                    if campaigns:
                        for campaign in campaigns:
                            print(campaign.id)
                            ad_request = Campaign.query.filter_by(id = campaign.id).first()
                            print(ad_request)
                        
                            ad_data.append(
                                { 
                                    'campaign_name': ad_request.name,
                                    "description": ad_request.description,
                                    'End_Date': ad_request.end_date,
                                    "niche": ad_request.niche,
                                    'start_date': ad_request.start_date,
                                    'end_date': ad_request.end_date,
                                    "id": ad_request.id,
                                    "budget": ad_request.budget,
                                    "goals": ad_request.goals,
                                    "visibility": campaign.visibility
                                }
                            )    
                        return render_template("influencer_search.html", adrequests = ad_data, filter = filter, 
                                               username = current_user.username, role = current_user.role)
                    
                    else:
                        flash('No adrequests found!', category='error')
                        return redirect(url_for('authentication.sponsor_dashboard'))
                
                else:
                    return render_template("influencer_search.html", users=[], username=current_user.username, role = current_user.role)
                
    else:
        flash('Something went wrong!', category='error')
        return redirect(url_for('authentication.influencer_search'))
    
# admin search
@authentication.route("/admin_search", methods=["GET", "POST"])    
@login_required
def admin_search():
    if request.method == "POST":
        L = []
        search_query = request.form.get("search", "")
        filter = request.form.get("radio")

        if current_user.role == "admin":
            if search_query:
                if filter == "influencer":
                    influencers = User.query.filter(User.username.like(f"%{search_query}%")).all()
                    if influencers:
                        for influencer in influencers:
                            if influencer.role == "influencer":
                                L.append(influencer)
                        return render_template("admin_search.html", users = L, filter = filter, username = current_user.username,
                                               role = current_user.role)
                    else:
                        flash('No influencers found!', category='error')
                        return redirect(url_for('authentication.admin_dashboard'))
                        
                elif filter == "sponsor":
                    sponsors = User.query.filter(User.username.like(f"%{search_query}%")).all()
                    print(sponsors)
                    if sponsors:
                        for sponsor in sponsors:
                            print(sponsor.role)
                            if sponsor.role == "sponsor":
                                L.append(sponsor)
                        return render_template("admin_search.html", users = L, filter = filter, username = current_user.username,
                                               role = current_user.role)
                    else:
                        flash('No sponsors found!', category='error')
                        return redirect(url_for('authentication.admin_dashboard'))    
                
                else:
                    users = User.query.filter(User.username.like(f"%{search_query}%")).all()
                    campaigns = Campaign.query.filter(Campaign.name.like(f"%{search_query}%")).all()
                    adrequests = AdRequest.query.filter(AdRequest.messages.like(f"%{search_query}%")).all()

                    return render_template("admin_search.html", users=users, campaigns = campaigns, adrequests = adrequests,
                                           username=current_user.username, role = current_user.role)
            
            else:
                flash('Something went wrong!', category='error')
                return redirect(url_for('authentication.admin_dashboard'))
        
        else:
            flash('Something went wrong!', category='error')
            return redirect(url_for('authentication.user_login'))

# reset ad request status
@authentication.route("/reset_ad_request_status/<int:ad_request_id>", methods=["GET", "POST"])
@login_required
def reset_ad_request_status(ad_request_id):
    if current_user.role == "sponsor":
        if request.method == "POST":
            ad_request = AdRequest.query.get(ad_request_id)
            if ad_request:
                if ad_request.status == "Rejected":
                    ad_request.status = "Pending"
                    ad_request.influencer_id = 0
                    db.session.commit()
                    flash('Ad request status reset successfully!', category='success')
                    return redirect(url_for('authentication.sponsor_dashboard'))
        else:
            flash('Something went wrong!', category='error')
            return redirect(url_for('authentication.sponsor_dashboard'))

    else:
        flash('You are not authorized to view this page!', category='error')
        return redirect(url_for('authentication.user_login'))

# invite influencer to an ad request
@authentication.route("/invite_influencer/<int:user_id>", methods=["GET", "POST"])
@login_required
def invite_influencer(user_id):
    if current_user.role == "sponsor":
        if request.method == 'POST':            
            influencer = User.query.filter_by(id = user_id).first()
            id = request.form.get('id')
            messages = request.form.get('messages')
            requirements = request.form.get('requirements')
            payment_amount = request.form.get('payment_amount')
            status = request.form.get('status')
            if influencer:
                invitation = Request(ad_request_id = id, messages = messages, 
                                       requirements = requirements, payment_amount = payment_amount, 
                                       status = status, influencer_id = user_id, sponsor_id = current_user.id)
                db.session.add(invitation)
                db.session.commit()
                flash('Influencer invited successfully!', category='success')
                return redirect(url_for('authentication.sponsor_dashboard'))
            else:
                flash('Influencer not found!', category='error')
                return redirect(url_for('authentication.sponsor_dashboard'))
        else:  
            ad_requests = []  
            campaigns = Campaign.query.filter_by(sponsor_id = current_user.id).all()
            for campaign in campaigns:
                ad_requests.append(AdRequest.query.filter_by(campaign_id = campaign.id).first())
            return render_template("invite_influencer.html", user_id = user_id, ad_requests = ad_requests)
    else:
        flash('You are not authorized to view this page!', category='error')
        return redirect(url_for('authentication.user_login'))

# influencer notifications
@authentication.route("/influencer_notifications", methods=["GET", "POST"])
@login_required
def influencer_notifications():
    if request.method == "POST":
        if current_user.role == "influencer":
            
            requests = Request.query.filter_by(influencer_id = current_user.id).all()
            
            return render_template("influencer_notifications.html", requests = requests, username = current_user.username)
        else:
            flash('You are not authorized to view this page!', category='error')
            return redirect(url_for('authentication.user_login'))
    else:
        return render_template("influencer_notifications.html", username = current_user.username)

# reject an ad request invitation
@authentication.route("/reject_ad_request_invitation/<int:request_id>", methods=["GET", "POST"])
@login_required
def reject_ad_request_invitation(request_id):
    if current_user.role == "influencer":
        if request.method == "POST":
            req = Request.query.filter_by(id = request_id).first()
            ad_request = AdRequest.query.filter_by(id = req.ad_request_id).first()
            req.status = "Rejected"
            ad_request.status = "Rejected"
            db.session.commit()
            req = Request.query.filter_by(id = request_id).first()
            db.session.delete(req)
            db.session.commit()            
            flash('Ad request invitation rejected successfully!', category='success')
            return redirect(url_for('authentication.influencer_notifications'))
        else:
            flash('Something went wrong!', category='error')
            return redirect(url_for('authentication.influencer_notifications'))
    else:
        flash('You are not authorized to view this page!', category='error')
        return redirect(url_for('authentication.user_login'))

# accept an ad request invitation
@authentication.route("/accept_ad_request_invitation/<int:request_id>", methods=["GET", "POST"])
@login_required
def accept_ad_request_invitation(request_id):
    if current_user.role == "influencer":
        if request.method == "POST":
            req = Request.query.filter_by(id = request_id).first()
            ad_request = AdRequest.query.filter_by(id = req.ad_request_id).first()
            req.status = "Accepted"
            ad_request.status = "Accepted"
            ad_request.influencer_id = current_user.id
            db.session.add(ad_request)
            db.session.add(req)
            db.session.commit()
            # data = Request.query.filter_by(id = request_id).all()
            flash('Ad request invitation accepted successfully!', category='success')
            return redirect(url_for('authentication.my_ad_request'))
        else:
            flash('Something went wrong!', category='error')
            return redirect(url_for('authentication.my_ad_request'))
    else:
        flash('You are not authorized to view this page!', category='error')
        return redirect(url_for('authentication.user_login'))

# Influencer requests for a specific ad request which belongs to a public campaign    
# @authentication.route("/sponsor_notification/<int:ad_request_id>", methods=["GET", "POST"])
# @login_required
# def influencer_request(ad_request_id):
#     if request.method == "POST":
#         if current_user.role == "influencer":
#             ad_requests = User.query.filter_by(id = ad_request_id).first()
#             id = request.form.get('id')
#             messages = request.form.get('messages')
#             requirements = request.form.get('requirements')
#             payment_amount = request.form.get('payment_amount')
#             status = request.form.get('status')
#             if ad_requests:
#                 invitation = Request(ad_request_id = id, messages = messages, 
#                                        requirements = requirements, payment_amount = payment_amount, 
#                                        status = status, influencer_id = current_user.id, sponsor_id = 0)
#                 db.session.add(invitation)
#                 db.session.commit()
#                 flash('Influencer requested successfully!', category='success')
#                 return redirect(url_for('authentication.influencer_dashboard'))
#         else:
#             flash('You are not authorized to view this page!', category='error')
#             return redirect(url_for('authentication.user_login'))
#     else:
#         return render_template("influencer_request.html", ad_request_id = ad_request_id, user_id = current_user.id,
#                                 username = current_user.username)   

@authentication.route("/campaign_request/<int:campaign_id>", methods=["GET", "POST"])    
@login_required
def campaign_request(campaign_id):
    if request.method == "POST":
        if current_user.role == "influencer":
            campaign = Campaign.query.filter_by(id = campaign_id).first()
            
            camp_name = request.form.get('camp_name')
            messages = request.form.get('messages')
            requirements = request.form.get('requirements')
            payment_amount = request.form.get('payment_amount')

            invitation = AdRequest(campaign_id = campaign_id, messages = messages, 
                                   requirements = requirements, payment_amount = payment_amount, 
                                   influencer_id = current_user.id, request_type = "influencer-to-sponsor")
            db.session.add(invitation)
            db.session.commit()
            flash('Sponsor invitation sent successfully!', category='success')
            return redirect(url_for('authentication.influencer_dashboard'))

    else:
        campaigns = Campaign.query.all()
        return render_template("campaign_request.html", campaign_id = campaign_id, campaigns = campaigns,
                                 user_id = current_user.id, username = current_user.username)


@authentication.route("/accept_offer/<int:ad_request_id>", methods=["GET", "POST"])
@login_required
def accept_offer(ad_request_id):
    if current_user.role == "sponsor":
        if request.method == "POST":
            ad_request = AdRequest.query.filter_by(id = ad_request_id).first()

            ad_request.status = "Accepted"
            # db.session.add(ad_request)
            db.session.commit()

            flash('Ad request invitation accepted successfully!', category='success')
            return redirect(url_for('authentication.sponsor_dashboard'))
        
        else:
            flash('Something went wrong!', category='error')
            return redirect(url_for('authentication.sponsor_dashboard'))
    
    else:
        flash('You are not authorized to view this page!', category='error')
        return redirect(url_for('authentication.user_login'))
    
@authentication.route("/reject_offer/<int:ad_request_id>", methods=["GET", "POST"])
@login_required
def reject_offer(ad_request_id):
    if current_user.role == "sponsor":
        if request.method == "POST":
            ad_request = AdRequest.query.filter_by(id = ad_request_id).first()

            ad_request.status = "Rejected"
            db.session.add(ad_request)
            db.session.commit()


            flash('Ad request invitation rejected successfully!', category='success')
            return redirect(url_for('authentication.sponsor_dashboard'))
        
        else:
            flash('Something went wrong!', category='error')
            return redirect(url_for('authentication.spnsor_dashboard'))

    else:
        flash('You are not authorized to view this page!', category='error')
        return redirect(url_for('authentication.user_login'))    

@authentication.route("/delete_offer/<int:ad_request_id>", methods=["GET", "POST"])
@login_required
def delete_offer(ad_request_id):
    if current_user.role == "sponsor":
        if request.method == "POST":
            ad_request = AdRequest.query.filter_by(id = ad_request_id).first()
            db.session.delete(ad_request)
            db.session.commit()
            flash('Ad request invitation deleted successfully!', category='success')
            return redirect(url_for('authentication.sponsor_dashboard'))
        
        else:
            flash('Something went wrong!', category='error')
            return redirect(url_for('authentication.sponsor_dashboard'))

    else:
        flash('You are not authorized to view this page!', category='error')
        return redirect(url_for('authentication.user_login'))

# @authentication.route("/sponsor_notification/<int:campaign_id>", methods=["GET", "POST"])
# @login_required
# def sponsor_notifications(campaign_id):
#     if current_user.role == "influencer":
#         if request.method == "POST":
#             id = request.form.get('id')
#             messages = request.form.get('messages')
#             requirements = request.form.get('requirements')
#             payment_amount = request.form.get('payment_amount')
#             status = request.form.get('status')
#             if id:
#                 invitation = Request(ad_request_id = id, messages = messages,
#                                        requirements = requirements, payment_amount = payment_amount,
#                                        status = status, influencer_id = current_user.id, sponsor_id = 0)
#                 db.session.add(invitation)
#                 db.session.commit()
#                 flash('Influencer requested successfully!', category='success')
#                 return redirect(url_for('authentication.sponsor_notifications'))
#         else:
#             flash('Something went wrong!', category='error')
#             return redirect(url_for('authentication.sponsor_notifications', campaign_id = campaign_id))
#     else:
#         flash('You are not authorized to view this page!', category='error')
#         return redirect(url_for('authentication.user_login'))


# getting username given the user id python db code
def get_username_for_user_id(user_id):
    user = db.session.query(User.username).join(Request, User.id == Request.sponsor_id).filter(User.id == user_id).first()
    return user.username if user else None  

# getting campaign name given the sponsor id python db code
def campaign_name(id):
    conn = None
    rows = None
    db_path = "instance/application.sqlite3"
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found at {db_path}")
    else:
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            query = '''select c.name from user as u, request as r, campaign as c, ad_request as ar 
                        where r.ad_request_id = ar.id and ar.campaign_id = c.id and c.sponsor_id = u.id
                        and r.sponsor_id = ?'''
            cur.execute(query, (id,))
            rows = cur.fetchall()
            for row in rows:
                print(row)    
        except Exception.DatabaseError as e:
            print("Error:", e)
        finally:
            if conn is not None:
                conn.close()
        return rows

# getting sponsor name given the sponsor id python db code
def sponsor_name(id):
    conn = None
    rows = None
    db_path = "instance/application.sqlite3"
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found at {db_path}")
    else:
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            query = '''select u.username from user as u, request as r, campaign as c, ad_request as ar 
                        where r.ad_request_id = ar.id and ar.campaign_id = c.id and c.sponsor_id = u.id
                        and r.sponsor_id = ?'''
            cur.execute(query, (id,))
            rows = cur.fetchall()
            for row in rows:
                print(row)    
        except Exception.DatabaseError as e:
            print("Error:", e)
        finally:
            if conn is not None:
                conn.close()
        return rows

# getting all public ad request ids given the ad request id python db code
def public_campaign_ad_request():
    conn = None
    rows = None
    db_path = "instance/application.sqlite3"
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found at {db_path}")
    else:
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            query = '''select ar.id from user as u, campaign as c, ad_request as ar 
                        where ar.campaign_id = c.id and c.sponsor_id = u.id and c.visibility = "Public"'''
            cur.execute(query)
            rows = cur.fetchall()
            for row in rows:
                print(row)    
        except Exception:
            print("Error")
        finally:
            if conn is not None:
                conn.close()
        return rows      