from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, current_user, logout_user, login_required
from datetime import datetime

db = SQLAlchemy()


from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'admin', 'sponsor', 'influencer'
    industry = db.Column(db.String(20), nullable=True)
    category = db.Column(db.String(20), nullable=True)
    facebook = db.Column(db.Boolean, nullable=True, default=False)
    twitter = db.Column(db.Boolean, nullable=True, default=False)
    instagram = db.Column(db.Boolean, nullable=True, default=False)
    youtube = db.Column(db.Boolean, nullable=True, default=False)
    total_reach = db.Column(db.Integer, nullable=True, default=0)
    flag = db.Column(db.Boolean, nullable=True, default=False)
    # Self-referential relationship for influencer
    influencer = db.relationship('User', remote_side=[id], backref='followers', lazy=True)
    
    # Relationships to other tables
    campaigns = db.relationship('Campaign',cascade="all,delete", backref='sponsor', lazy=True)
    ad_requests = db.relationship('AdRequest',cascade="all,delete", backref='influencer', lazy=True)

class Campaign(db.Model):
    __tablename__ = 'campaign'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    niche = db.Column(db.String(20), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    visibility = db.Column(db.String(10), nullable=False)  # 'public', 'private'
    goals = db.Column(db.Text, nullable=False)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ad_requests = db.relationship('AdRequest', cascade="all,delete", backref='campaign', lazy=True)

    # requests = db.relationship('Request', backref='campaign', lazy=True)


class AdRequest(db.Model):
    __tablename__ = 'ad_request'
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    messages = db.Column(db.Text, nullable=True)
    requirements = db.Column(db.Text, nullable=False)
    payment_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(10), nullable=False, default='Pending')  # 'Pending', 'Accepted', 'Rejected'
    request_type = db.Column(db.String(50)) #sus
    # requests = db.relationship('Request',cascade="all,delete", backref='ad_request', lazy=True)

    requests = db.relationship('Request',cascade="all,delete", backref='ad_request', lazy=True)

class Request(db.Model):
    __tablename__ = 'request'
    id = db.Column(db.Integer, primary_key=True)
    influencer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id')) #sus
    ad_request_id = db.Column(db.Integer, db.ForeignKey('ad_request.id'), nullable=False)
    messages = db.Column(db.Text, nullable=True)
    requirements = db.Column(db.Text, nullable=False)
    payment_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(10), nullable=False, default='Pending')  # 'Pending', 'Accepted', 'Rejected'
    # request_type = db.Column(db.String(50)) #sus
    # ad_request = db.relationship('AdRequest',cascade="all,delete", backref='requests', lazy=True)