from datetime import datetime



from flask_sqlalchemy import SQLAlchemy
from datetime import datetime



db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    UserID = db.Column(db.Integer, primary_key=True)
    FullName = db.Column(db.String(100), nullable=False)
    UserName = db.Column(db.String(100), unique=True, nullable=False)
    Email = db.Column(db.String(100), unique=True, nullable=False)
    PhoneNo = db.Column(db.String(15), nullable=False)
    Password = db.Column(db.String(100), nullable=False)
    Gender = db.Column(db.String(10), nullable=False)
    Nationality = db.Column(db.String(50), nullable=False)
    Role = db.Column(db.String(50), nullable=False)
    sponsor = db.relationship('Sponsor', backref='user', uselist=False)
    influencer = db.relationship('Influencer', backref='user', uselist=False)
    sent_messages = db.relationship('Message', foreign_keys='Message.SenderID', backref='sender', lazy=True)
    received_messages = db.relationship('Message', foreign_keys='Message.ReceiverID', backref='receiver', lazy=True)

class Sponsor(db.Model):
    __tablename__ = 'sponsor'
    SponsorID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('user.UserID'), nullable=False)
    CompanyName = db.Column(db.String(100), nullable=False)
    CompanyWebsite = db.Column(db.String(200), nullable=True)
    IndustryCategory = db.Column(db.String(100), nullable=False)
    campaigns = db.relationship('Campaign', backref='sponsor', lazy=True)

class Influencer(db.Model):
    __tablename__ = 'influencer'
    InfluencerID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('user.UserID'), nullable=False)
    PlatformPresence = db.Column(db.JSON, nullable=False)
    AccountURLs = db.Column(db.JSON, nullable=False)
    ContentNiche = db.Column(db.String(100), nullable=False)
    participations = db.relationship('CampaignAgreement', backref='influencer', lazy=True)
    requests = db.relationship('CampaignRequest', back_populates='influencer')

class Campaign(db.Model):
    __tablename__ = 'campaign'
    CampaignID = db.Column(db.Integer, primary_key=True)
    SponsorID = db.Column(db.Integer, db.ForeignKey('sponsor.SponsorID'), nullable=False)
    Title = db.Column(db.String(100), nullable=False)
    Description = db.Column(db.String(500), nullable=False)
    Niche = db.Column(db.String(100), nullable=False)
    StartDate = db.Column(db.Date, nullable=False)
    EndDate = db.Column(db.Date, nullable=False)
    Budget = db.Column(db.Float, nullable=False)
    Visibility = db.Column(db.String(50), nullable=False)
    agreements = db.relationship('CampaignAgreement', backref='campaign', lazy=True)
    progress_updates = db.relationship('CampaignProgress', backref='campaign', lazy=True)
    requests = db.relationship('CampaignRequest', back_populates='campaign')

class CampaignAgreement(db.Model):
    __tablename__ = 'campaign_agreement'
    AgreementID = db.Column(db.Integer, primary_key=True)
    CampaignID = db.Column(db.Integer, db.ForeignKey('campaign.CampaignID'), nullable=False)
    InfluencerID = db.Column(db.Integer, db.ForeignKey('influencer.InfluencerID'), nullable=False)
    Terms = db.Column(db.String(500), nullable=False)
    Payment = db.Column(db.Float, nullable=False)
    InfluencerName = db.Column(db.String(100), nullable=False)

class CampaignProgress(db.Model):
    __tablename__ = 'campaign_progress'
    ProgressID = db.Column(db.Integer, primary_key=True)
    CampaignID = db.Column(db.Integer, db.ForeignKey('campaign.CampaignID'), nullable=False)
    Status = db.Column(db.String(50), nullable=False)
    LastUpdated = db.Column(db.DateTime, nullable=False)

class Message(db.Model):
    __tablename__ = 'message'
    MessageID = db.Column(db.Integer, primary_key=True)
    SenderID = db.Column(db.Integer, db.ForeignKey('user.UserID'), nullable=False)
    ReceiverID = db.Column(db.Integer, db.ForeignKey('user.UserID'), nullable=False)
    Content = db.Column(db.String(500), nullable=False)
    Timestamp = db.Column(db.DateTime, nullable=False)
    CampaignID = db.Column(db.Integer, db.ForeignKey('campaign.CampaignID'), nullable=True)
    campaign = db.relationship('Campaign', backref='messages')


class CampaignRequest(db.Model):
    __tablename__ = 'campaign_request'
    RequestID = db.Column(db.Integer, primary_key=True)
    CampaignID = db.Column(db.Integer, db.ForeignKey('campaign.CampaignID'), nullable=False)
    InfluencerID = db.Column(db.Integer, db.ForeignKey('influencer.InfluencerID'), nullable=False)
    SponsorID = db.Column(db.Integer, db.ForeignKey('sponsor.SponsorID'), nullable=True)
    Status = db.Column(db.String(50), default='Pending')
    RequestedOn = db.Column(db.DateTime, default=datetime.utcnow)
    campaign = db.relationship('Campaign', back_populates='requests')
    influencer = db.relationship('Influencer', back_populates='requests')
    sponsor = db.relationship('Sponsor', backref='campaign_requests')

class ActiveCampaign(db.Model):
    __tablename__ = 'active_campaign'
    ActiveID = db.Column(db.Integer, primary_key=True)
    CampaignID = db.Column(db.Integer, db.ForeignKey('campaign.CampaignID'), nullable=False)
    InfluencerID = db.Column(db.Integer, db.ForeignKey('influencer.InfluencerID'), nullable=False)
    Progress = db.Column(db.Integer, nullable=False, default=0)
    influencer = db.relationship('Influencer', backref='active_campaigns')
    campaign = db.relationship('Campaign', backref='active_campaigns')


# Flagged entities models

class FlaggedCampaign(db.Model):
    __tablename__ = 'flagged_campaign'
    FlagID = db.Column(db.Integer, primary_key=True)
    CampaignID = db.Column(db.Integer, db.ForeignKey('campaign.CampaignID'), nullable=False)
    FlagReason = db.Column(db.String(500), nullable=False)
    Timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    campaign = db.relationship('Campaign', backref='flagged_entries')

class FlaggedSponsor(db.Model):
    __tablename__ = 'flagged_sponsor'
    FlagID = db.Column(db.Integer, primary_key=True)
    SponsorID = db.Column(db.Integer, db.ForeignKey('sponsor.SponsorID'), nullable=False)
    FlagReason = db.Column(db.String(500), nullable=False)
    Timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    sponsor = db.relationship('Sponsor', backref='flagged_entries')

class FlaggedInfluencer(db.Model):
    __tablename__ = 'flagged_influencer'
    FlagID = db.Column(db.Integer, primary_key=True)
    InfluencerID = db.Column(db.Integer, db.ForeignKey('influencer.InfluencerID'), nullable=False)
    FlagReason = db.Column(db.String(500), nullable=False)
    Timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    influencer = db.relationship('Influencer', backref='flagged_entries')


