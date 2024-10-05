from flask import render_template
from flask import redirect, url_for, flash
from datetime import date
from app import create_app
from .models import *
from flask import jsonify


app = create_app()

from flask import Flask 
from flask import current_app as app # Alias for current running app
from flask import Flask, render_template, redirect, url_for, request, session
from backend.models import *
from werkzeug.security import generate_password_hash
from datetime import datetime


@app.route('/')
def home():
    return render_template('home.html')



@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')


@app.route('/admin_dashboard_data')
def admin_dashboard_data():
    data = {
        'total_influencers': Influencer.query.count(),
        'total_sponsors': Sponsor.query.count(),
        'total_users': User.query.count(),
        'total_campaigns': Campaign.query.count(),
        'total_campaign_requests': CampaignRequest.query.count(),
        'total_active_campaigns': ActiveCampaign.query.count(),
        'total_flagged_campaigns': FlaggedCampaign.query.count(),
        'total_flagged_influencers': FlaggedInfluencer.query.count(),
        'total_flagged_sponsors': FlaggedSponsor.query.count(),
        'total_messages': Message.query.count(),
        'influencer_distribution': {
            'categories': [inf.ContentNiche for inf in Influencer.query.with_entities(Influencer.ContentNiche).distinct()],
            'counts': [Influencer.query.filter_by(ContentNiche=inf.ContentNiche).count() for inf in Influencer.query.with_entities(Influencer.ContentNiche).distinct()]
        },
        'sponsor_distribution': {
            'categories': [sponsor.IndustryCategory for sponsor in Sponsor.query.with_entities(Sponsor.IndustryCategory).distinct()],
            'counts': [Sponsor.query.filter_by(IndustryCategory=sponsor.IndustryCategory).count() for sponsor in Sponsor.query.with_entities(Sponsor.IndustryCategory).distinct()]
        },
        'campaign_distribution': {
            'categories': [campaign.Niche for campaign in Campaign.query.with_entities(Campaign.Niche).distinct()],
            'counts': [Campaign.query.filter_by(Niche=campaign.Niche).count() for campaign in Campaign.query.with_entities(Campaign.Niche).distinct()]
        },
        'active_campaign_distribution': {
            'statuses': ['Active', 'Completed'], 
            'counts': [ActiveCampaign.query.filter_by(Progress=status).count() for status in ['Active', 'Completed']]
        }
    }
    return jsonify(data)




@app.route("/login", methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        uname = request.form.get("uname")
        pwd = request.form.get("password")
        usr = User.query.filter_by(UserName=uname, Password=pwd).first()  # get existing user matched

        if usr:
            if usr.Role == 'Sponsor':
                sponsor = Sponsor.query.filter_by(UserID=usr.UserID).first()
                if sponsor:
                    flagged_sponsor = FlaggedSponsor.query.filter_by(SponsorID=sponsor.SponsorID).first()
                    if flagged_sponsor:
                        # Render the flag reason
                        return render_template("flag_msg.html", reason=flagged_sponsor.FlagReason)
                    return redirect(url_for('user_s_home', sponsor_id=sponsor.SponsorID))
            elif usr.Role == 'Influencer':
                influencer = Influencer.query.filter_by(UserID=usr.UserID).first()
                if influencer:
                    flagged_influencer = FlaggedInfluencer.query.filter_by(InfluencerID=influencer.InfluencerID).first()
                    if flagged_influencer:
                        # Render the flag reason
                        return render_template("flag_msg.html", reason=flagged_influencer.FlagReason)
                    return redirect(url_for('user_i_home', influencer_id=influencer.InfluencerID))
            elif usr.Role == 'Admin':
                return redirect(url_for('user_a_home'))
        else:
            return render_template("index.html", msg="Invalid Credentials!!!")

    return render_template("index.html")




@app.route('/a_home', methods=['GET', 'POST'])
def user_a_home():

    # Get IDs of flagged campaigns
    flagged_campaign_ids = [fc.CampaignID for fc in FlaggedCampaign.query.all()]
    
    
    # Fetch active campaigns with related campaign, sponsor, and influencer
    active_campaigns = db.session.query(ActiveCampaign).\
        join(Campaign, ActiveCampaign.CampaignID == Campaign.CampaignID).\
        join(Sponsor, Campaign.SponsorID == Sponsor.SponsorID).\
        join(Influencer, ActiveCampaign.InfluencerID == Influencer.InfluencerID).\
        filter(Campaign.EndDate >= date.today(), Campaign.CampaignID.notin_(flagged_campaign_ids)).all()
    
    # Fetch flagged campaigns, sponsors, and influencers
    flagged_campaigns = FlaggedCampaign.query.all()
    flagged_sponsors = FlaggedSponsor.query.all()
    flagged_influencers = FlaggedInfluencer.query.all()

    action = request.args.get('action')

    campaign_details = None
    influencer_details = None
    sponsor_details = None

    campaign_info = None
    influencer_info = None
    sponsor_info = None


    if action == 'view':
        campaign_id = request.args.get('campaign_id')
        influencer_id = request.args.get('influencer_id')
        sponsor_id = request.args.get('sponsor_id')

        if campaign_id and influencer_id and sponsor_id:
            campaign_details = Campaign.query.get(campaign_id)
            influencer_details = Influencer.query.get(influencer_id)
            sponsor_details = Sponsor.query.get(sponsor_id)
        elif campaign_id:
            campaign_info = Campaign.query.get(campaign_id)
        elif sponsor_id:
            sponsor_info = Sponsor.query.get(sponsor_id)
        elif influencer_id:
            influencer_info = Influencer.query.get(influencer_id)




    # Handle flag removal
    if request.method == 'POST':
        remove_flag_type = request.form.get('flag_type')
        remove_flag_id = request.form.get('flag_id')

        if remove_flag_type == 'campaign':
            flag = FlaggedCampaign.query.get(remove_flag_id)
        elif remove_flag_type == 'sponsor':
            flag = FlaggedSponsor.query.get(remove_flag_id)
        elif remove_flag_type == 'influencer':
            flag = FlaggedInfluencer.query.get(remove_flag_id)
        
        if flag:
            db.session.delete(flag)
            db.session.commit()

        return redirect(url_for('user_a_home'))

    return render_template('a_home.html', 
                           active_campaigns=active_campaigns, 
                           campaign_details=campaign_details, 
                           influencer_details=influencer_details, 
                           sponsor_details=sponsor_details,
                           campaign_info=campaign_info,
                           sponsor_info=sponsor_info,
                           influencer_info=influencer_info,
                           flagged_campaigns=flagged_campaigns,
                           flagged_sponsors=flagged_sponsors,
                           flagged_influencers=flagged_influencers)





@app.route('/a_find', methods=['GET', 'POST'])
def user_a_find():
    # These IDs come from the POST form or GET request
    campaign_id = request.form.get('campaign_id') or request.args.get('campaign_id')
    sponsor_id = request.form.get('sponsor_id') or request.args.get('sponsor_id')
    influencer_id = request.form.get('influencer_id') or request.args.get('influencer_id')

    # Determine if we are flagging or viewing something
    flagging_campaign = campaign_id is not None and request.method == 'POST'
    flagging_sponsor = sponsor_id is not None and request.method == 'POST'
    flagging_influencer = influencer_id is not None and request.method == 'POST'

    search_query = request.args.get('search', '')

    if search_query:
        # Search in campaigns
        campaigns = Campaign.query.filter(
            Campaign.Title.ilike(f'%{search_query}%')
        ).all()

        # Search in sponsors
        sponsors = Sponsor.query.join(User).filter(
            User.FullName.ilike(f'%{search_query}%')
        ).all()

        # Search in influencers
        influencers = Influencer.query.join(User).filter(
            User.FullName.ilike(f'%{search_query}%')
        ).all()
    else:
        campaigns = Campaign.query.all()
        sponsors = Sponsor.query.all()
        influencers = Influencer.query.all()

    # Update campaigns, sponsors, influencers to include flagged status
    for campaign in campaigns:
        campaign.is_flagged = FlaggedCampaign.query.filter_by(CampaignID=campaign.CampaignID).first() is not None

    for sponsor in sponsors:
        sponsor.is_flagged = FlaggedSponsor.query.filter_by(SponsorID=sponsor.SponsorID).first() is not None

    for influencer in influencers:
        influencer.is_flagged = FlaggedInfluencer.query.filter_by(InfluencerID=influencer.InfluencerID).first() is not None

    campaign_details = None
    influencer_details = None
    sponsor_details = None

    action = request.args.get('action')

    if action == 'view':
        if campaign_id:
            campaign_details = Campaign.query.get(campaign_id)
        elif influencer_id:
            influencer_details = Influencer.query.get(influencer_id)
        elif sponsor_id:
            sponsor_details = Sponsor.query.get(sponsor_id)

    return render_template('a_find.html', 
                           campaigns=campaigns,
                           sponsors=sponsors,
                           influencers=influencers,
                           flagging_campaign=flagging_campaign,
                           flagging_sponsor=flagging_sponsor,
                           flagging_influencer=flagging_influencer,
                           campaign_id=campaign_id,
                           sponsor_id=sponsor_id,
                           influencer_id=influencer_id,
                           campaign_details=campaign_details, 
                           influencer_details=influencer_details, 
                           sponsor_details=sponsor_details)



@app.route('/flag_campaign/<int:campaign_id>', methods=['POST'])
def flag_campaign(campaign_id):
    reason = request.form.get('reason')
    if reason:
        flagged_campaign = FlaggedCampaign(CampaignID=campaign_id, FlagReason=reason)
        db.session.add(flagged_campaign)
        db.session.commit()
        flash('Campaign flagged successfully.', 'success')
    else:
        flash('Failed to flag campaign. Please provide a reason.', 'danger')
    return redirect(url_for('user_a_find'))

@app.route('/flag_sponsor/<int:sponsor_id>', methods=['POST'])
def flag_sponsor(sponsor_id):
    reason = request.form.get('reason')
    if reason:
        flagged_sponsor = FlaggedSponsor(SponsorID=sponsor_id, FlagReason=reason)
        db.session.add(flagged_sponsor)
        db.session.commit()
        flash('Sponsor flagged successfully.', 'success')
    else:
        flash('Failed to flag sponsor. Please provide a reason.', 'danger')
    return redirect(url_for('user_a_find'))

@app.route('/flag_influencer/<int:influencer_id>', methods=['POST'])
def flag_influencer(influencer_id):
    reason = request.form.get('reason')
    if reason:
        flagged_influencer = FlaggedInfluencer(InfluencerID=influencer_id, FlagReason=reason)
        db.session.add(flagged_influencer)
        db.session.commit()
        flash('Influencer flagged successfully.', 'success')
    else:
        flash('Failed to flag influencer. Please provide a reason.', 'danger')
    return redirect(url_for('user_a_find'))




@app.route('/s_home', methods=['GET'])
def user_s_home():
    sponsor_id = request.args.get('sponsor_id')
    if not sponsor_id:
        return redirect(url_for('user_login'))

    sponsor = Sponsor.query.get_or_404(sponsor_id)

    # Get IDs of flagged campaigns
    flagged_campaign_ids = [fc.CampaignID for fc in FlaggedCampaign.query.all()]
    
    

    active_campaigns = db.session.query(ActiveCampaign).join(Campaign).filter(Campaign.SponsorID == sponsor_id, Campaign.CampaignID.notin_(flagged_campaign_ids) , Campaign.EndDate >=date.today()).all()

    
    
    new_requests = CampaignRequest.query.filter_by(Status='Pending', SponsorID=None).join(Campaign).filter_by(SponsorID=sponsor_id).all()
    new_messages = Message.query.filter_by(ReceiverID=sponsor.UserID).all()

    # Handle actions and data retrieval
    action = request.args.get('action')
    campaign_details, influencer_details, message_details , message , influencer_show , user_details= None, None, None , None , None , None

    if action == 'view':
        campaign_id = request.args.get('campaign_id')
        influencer_id = request.args.get('influencer_id')
        request_id = request.args.get('request_id')
        message_id = request.args.get('message_id')
        influencer_user_id = request.args.get('influencer_user_id')

        if campaign_id and influencer_id:
            campaign_details = Campaign.query.get(campaign_id)
            influencer_details = Influencer.query.get(influencer_id)
        elif request_id:
            campaign_request = CampaignRequest.query.filter_by(RequestID=request_id, SponsorID=None).first()


            if campaign_request:
                influencer_details = Influencer.query.get(campaign_request.InfluencerID)
        elif message_id:
            message_details = Message.query.get(message_id)

        elif influencer_user_id:
            user_details = User.query.get(influencer_user_id)
            if user_details:
                influencer_show = Influencer.query.filter_by(UserID=user_details.UserID).first()
                

    elif action == 'reply':
        message_id = request.args.get('message_id')
        if message_id:
            message  = Message.query.get(message_id)
            # No need to set influencer_details for reply action unless required

    return render_template("s_home.html", sponsor=sponsor, active_campaigns=active_campaigns, new_requests=new_requests, new_messages=new_messages, campaign_details=campaign_details, influencer_details=influencer_details, message_details=message_details , message= message , influencer_show= influencer_show , user_details = user_details)



@app.route('/reply_message', methods=['POST'])
def reply_message():
    # message_details = Message.query.get_or_404(message_id)
    sender_id = request.form.get('sender_id')
    receiver_id = request.form.get('receiver_id')
    content = request.form.get('content')
    campaign_id = request.form.get('campaign_id')  # Get the campaign ID

    if not sender_id or not receiver_id or not content:
        flash('All fields are required!', 'danger')
        # return redirect(url_for('user_s_home', sponsor_id=sponsor_id))

    if sender_id and receiver_id and content:
        new_message = Message(
            SenderID=sender_id,
            ReceiverID=receiver_id,
            Content=content,
            Timestamp=datetime.utcnow(),
            CampaignID=campaign_id  # Set the campaign ID
        )
    
    db.session.add(new_message)
    db.session.commit()
    
    flash('Reply sent successfully!', 'success')
    return redirect(request.referrer)



@app.route('/accept_request/<int:request_id>', methods=['POST'])
def accept_request(request_id):
    # Fetch the sponsor ID from the query parameters
    sponsor_id = request.form.get('sponsor_id')

    # Ensure the sponsor_id is present
    if not sponsor_id:
        # Handle the case where sponsor_id is not provided, e.g., redirect to login or home page
        return redirect(url_for('user_login'))

    # Fetch the campaign request
    campaign_request = CampaignRequest.query.get(request_id)
    if campaign_request:
        # Fetch the campaign to update its visibility
        campaign = Campaign.query.get(campaign_request.CampaignID)
        if campaign:
            # Set campaign visibility to 'private'
            campaign.Visibility = 'private'

            # Add to active campaigns
            active_campaign = ActiveCampaign(
                CampaignID=campaign_request.CampaignID,
                InfluencerID=campaign_request.InfluencerID,
                Progress=0
            )
            db.session.add(active_campaign)
            
            # Delete the campaign request
            db.session.delete(campaign_request)
            
            # Commit all changes to the database
            db.session.commit()
    
    # Redirect back to the sponsor's home page
    return redirect(url_for('user_s_home', sponsor_id=sponsor_id))



@app.route('/reject_request/<int:request_id>', methods=['POST'])
def reject_request(request_id):
    sponsor_id = request.form.get('sponsor_id')
    campaign_request = CampaignRequest.query.get(request_id)
    if campaign_request:
        db.session.delete(campaign_request)
        db.session.commit()
    return redirect(url_for('user_s_home', sponsor_id=sponsor_id))


@app.route('/accept_sponsor_request/<int:request_id>', methods=['POST'])
def accept_sponsor_request(request_id):
    # Fetch the sponsor ID from the query parameters
    influencer_id = request.form.get('influencer_id')

    # Ensure the sponsor_id is present
    if not influencer_id:
        # Handle the case where sponsor_id is not provided, e.g., redirect to login or home page
        return redirect(url_for('user_login'))

    # Fetch the campaign request
    campaign_request = CampaignRequest.query.get(request_id)
    if campaign_request:
        # Fetch the campaign to update its visibility
        campaign = Campaign.query.get(campaign_request.CampaignID)
        if campaign:
            # Set campaign visibility to 'private'
            campaign.Visibility = 'private'

            # Add to active campaigns
            active_campaign = ActiveCampaign(
                CampaignID=campaign_request.CampaignID,
                InfluencerID=campaign_request.InfluencerID,
                Progress=0
            )
            db.session.add(active_campaign)
            
            # Delete the campaign request
            db.session.delete(campaign_request)
            
            # Commit all changes to the database
            db.session.commit()
    
    # Redirect back to the sponsor's home page
    return redirect(url_for('user_i_home', influencer_id=influencer_id))


@app.route('/reject_sponsor_request/<int:request_id>', methods=['POST'])
def reject_sponsor_request(request_id):
    influencer_id = request.form.get('influencer_id')
    campaign_request = CampaignRequest.query.get(request_id)
    if campaign_request:
        db.session.delete(campaign_request)
        db.session.commit()
    return redirect(url_for('user_i_home', influencer_id=influencer_id))





from datetime import date

@app.route('/s_campaign/<int:sponsor_id>', methods=['GET', 'POST'])
def s_campaign(sponsor_id):
    # Fetch the sponsor from the database
    sponsor = Sponsor.query.get_or_404(sponsor_id)
    
    # Get IDs of flagged campaigns
    flagged_campaign_ids = [fc.CampaignID for fc in FlaggedCampaign.query.all()]
    
    # Fetch campaigns that are not flagged and are still active
    campaigns = Campaign.query.filter(
        Campaign.SponsorID == sponsor_id,
        Campaign.EndDate >= date.today(),
        Campaign.CampaignID.notin_(flagged_campaign_ids)
    ).all()

    view_campaign_id = request.args.get('view_campaign_id')
    edit_campaign_id = request.args.get('edit_campaign_id')
    find_campaign_id = request.args.get('find_campaign_id')

    view_campaign = None
    edit_campaign = None
    find_campaign = None

    if view_campaign_id:
        view_campaign = Campaign.query.get(view_campaign_id)
    if edit_campaign_id:
        edit_campaign = Campaign.query.get(edit_campaign_id)
    if find_campaign_id:
        find_campaign = Campaign.query.get(find_campaign_id)

    return render_template(
        's_campaign.html',
        sponsor=sponsor,
        campaigns=campaigns,
        view_campaign=view_campaign,
        edit_campaign=edit_campaign,
        find_campaign=find_campaign,
        sponsor_id=sponsor_id
    )


@app.route('/s_find/<int:sponsor_id>', methods=['GET'])
def s_find(sponsor_id):
    # Fetch the sponsor and campaigns from the database
    sponsor = Sponsor.query.get_or_404(sponsor_id)
    campaigns = Campaign.query.filter_by(SponsorID=sponsor_id).filter(Campaign.EndDate < date.today()).all()
    view_campaign_id = request.args.get('view_campaign_id')

    view_campaign = None

    if view_campaign_id:
        view_campaign = Campaign.query.get(view_campaign_id)

        
    return render_template(
        's_find.html',
        sponsor=sponsor,
        campaigns=campaigns,
        view_campaign=view_campaign,
        sponsor_id=sponsor_id
    )




@app.route('/add_campaign', methods=['POST'])
def add_campaign():
    sponsor_id = request.form.get('sponsor_id')
    if not sponsor_id:
        return redirect(url_for('login'))  # Redirect to login if sponsor ID is not found

    title = request.form.get('title')
    description = request.form.get('description')
    image = request.form.get('image')
    niche = request.form.get('niche')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    budget = request.form.get('budget')
    visibility = request.form.get('visibility')

    new_campaign = Campaign(
        SponsorID=sponsor_id,
        Title=title,
        Description=description,
        Niche=niche,
        StartDate=datetime.strptime(start_date, '%Y-%m-%d'),
        EndDate=datetime.strptime(end_date, '%Y-%m-%d'),
        Budget=float(budget),
        Visibility=visibility
    )

    db.session.add(new_campaign)
    db.session.commit()

    return redirect(url_for('s_campaign', sponsor_id=sponsor_id))




@app.route('/logout')
def logout():
    # Clear any user-related data in your application (if needed)
    return redirect(url_for('user_login'))
    

@app.route('/view_campaign/<int:campaign_id>', methods=['GET'])
def view_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    sponsor_id = campaign.SponsorID
    campaigns = Campaign.query.filter_by(SponsorID=sponsor_id).all()
    return render_template('s_campaign.html', campaigns=campaigns, view_campaign=campaign, edit_campaign=None, sponsor_id=sponsor_id)

@app.route('/edit_campaign/<int:campaign_id>', methods=['GET', 'POST'])
def edit_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    sponsor_id = campaign.SponsorID
    if request.method == 'POST':
        campaign.Title = request.form['title']
        campaign.Description = request.form['description']
        campaign.Niche = request.form['niche']
        campaign.StartDate = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        campaign.EndDate = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        campaign.Budget = float(request.form['budget'])
        campaign.Visibility = request.form['visibility']
        db.session.commit()
        return redirect(url_for('s_campaign', sponsor_id=sponsor_id))
    campaigns = Campaign.query.filter_by(SponsorID=sponsor_id).all()
    return render_template('s_campaign.html', campaigns=campaigns, view_campaign=None, edit_campaign=campaign, sponsor_id=sponsor_id)



@app.route('/delete_campaign/<int:campaign_id>', methods=['POST'])
def delete_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    sponsor_id = campaign.SponsorID
    db.session.delete(campaign)
    db.session.commit()
    return redirect(url_for('s_campaign', sponsor_id=sponsor_id))



@app.route('/request_campaign/<int:campaign_id>')
def request_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    # Implement the logic for requesting a campaign
    return "Request campaign logic here"



@app.route('/sponsor_profile/<int:sponsor_id>', methods=['GET', 'POST'])
def sponsor_profile(sponsor_id):
    sponsor = Sponsor.query.get_or_404(sponsor_id)
    user = User.query.get_or_404(sponsor.UserID)
    
    if request.method == 'POST':
        # Update sponsor and user information from form data
        user.FullName = request.form['full_name']
        user.UserName = request.form['user_name']
        user.Email = request.form['email']
        user.PhoneNo = request.form['phone_no']
        user.Gender = request.form['gender']
        user.Nationality = request.form['nationality']
        
        sponsor.CompanyName = request.form['company_name']
        sponsor.CompanyWebsite = request.form['company_website']
        sponsor.IndustryCategory = request.form['industry_category']
        
        db.session.commit()
        
        return redirect(url_for('sponsor_profile', sponsor_id=sponsor.SponsorID))
    
    return render_template('s_profile.html', sponsor=sponsor, user=user)



@app.route('/register', methods=['GET', 'POST'])
def user_signup():
    if request.method == 'POST':
        full_name = request.form['name']
        username = request.form['uname']
        email = request.form['email']
        phone_no = request.form['phone']
        password = request.form['password']
        confirm_password = request.form.get('confirmPassword')
        gender = request.form['gender']
        nationality = request.form['nationality']
        role = request.form['role']

        if password != confirm_password:
            return "Passwords do not match", 400

        # Create User instance
        user = User(
            FullName=full_name,
            UserName=username,
            Email=email,
            PhoneNo=phone_no,
            Password=password,
            Gender=gender,
            Nationality=nationality,
            Role=role
        )

        db.session.add(user)
        db.session.commit()

        # Handle role-specific data
        if role == 'Sponsor':
            company_name = request.form.get('companyName')
            company_website = request.form.get('websiteURL')
            industry_category = request.form.get('industry')
            sponsor = Sponsor(
                UserID=user.UserID,
                CompanyName=company_name,
                CompanyWebsite=company_website,
                IndustryCategory=industry_category
            )
            db.session.add(sponsor)
            db.session.commit()

        elif role == 'Influencer':
            # Retrieve social media URLs dynamically
            platforms = ['instagram', 'youtube', 'twitter', 'tiktok']
            platform_urls = {platform: request.form.get(platform) for platform in platforms if request.form.get(platform)}

            # PlatformPresence should reflect the keys of platform_urls
            platform_presence = list(platform_urls.keys())

            # Add influencer specific data
            influencer = Influencer(
                UserID=user.UserID,
                PlatformPresence=platform_presence,
                AccountURLs=platform_urls,
                ContentNiche=request.form.get('contentNiche')
            )
            db.session.add(influencer)
            db.session.commit()

        return redirect(url_for('user_login'))  # Redirect to a home or success page

    return render_template('signup.html')


@app.route('/i_home')
def user_i_home():
    influencer_id = request.args.get('influencer_id')
   
    if not influencer_id:
        return redirect(url_for('user_login'))

    influencer = Influencer.query.get_or_404(influencer_id)
    
     # Get IDs of flagged campaigns
    flagged_campaign_ids = [fc.CampaignID for fc in FlaggedCampaign.query.all()]
    
    

    active_campaigns = db.session.query(ActiveCampaign).\
        join(Campaign, ActiveCampaign.CampaignID == Campaign.CampaignID).\
        join(Sponsor, Campaign.SponsorID == Sponsor.SponsorID).\
        join(Influencer, ActiveCampaign.InfluencerID == Influencer.InfluencerID).\
        filter(Campaign.EndDate >= date.today() , Campaign.CampaignID.notin_(flagged_campaign_ids)).all()
    
    new_requests = (CampaignRequest.query
                .filter(CampaignRequest.Status == 'Pending', CampaignRequest.SponsorID != None)
                .join(Campaign, CampaignRequest.CampaignID == Campaign.CampaignID)
                .join(Sponsor, Campaign.SponsorID == Sponsor.SponsorID)
                .join(Influencer, CampaignRequest.InfluencerID == Influencer.InfluencerID)
                .filter(Influencer.InfluencerID == influencer_id)
                .all())

    new_messages = Message.query.filter_by(ReceiverID=influencer.UserID).all()

    # Handle actions and data retrieval
    action = request.args.get('action')
    campaign_details, influencer_details, message_details , message , sponsor_show , user_details= None, None, None , None , None , None

    if action == 'view':
        campaign_id = request.args.get('campaign_id')
        influencer_id = request.args.get('influencer_id')
        request_id = request.args.get('request_id')
        message_id = request.args.get('message_id')
        sponsor_user_id = request.args.get('sponsor_user_id')

        if campaign_id and influencer_id:
            campaign_details = Campaign.query.get(campaign_id)
            influencer_details = Influencer.query.get(influencer_id)
        elif request_id:
            campaign_request = CampaignRequest.query.get(request_id)
            if campaign_request:
                campaign_details = Campaign.query.get(campaign_request.CampaignID)
        elif message_id:
            message_details = Message.query.get(message_id)

        elif sponsor_user_id:
            user_details = User.query.get(sponsor_user_id)
            if user_details:
                sponsor_show = Sponsor.query.filter_by(UserID=user_details.UserID).first()
                print(f"User Details: {user_details}, Sponsor Show: {sponsor_show}")
                

    elif action == 'reply':
        message_id = request.args.get('message_id')
        if message_id:
            message  = Message.query.get(message_id)
            # No need to set influencer_details for reply action unless required

    return render_template("i_home.html", influencer= influencer, active_campaigns=active_campaigns, new_requests= new_requests , new_messages=new_messages, campaign_details=campaign_details, influencer_details=influencer_details, message_details=message_details , message= message , sponsor_show= sponsor_show , user_details = user_details)



@app.route('/influencer_profile/<int:influencer_id>', methods=['GET', 'POST'])
def influencer_profile(influencer_id):
    influencer = Influencer.query.get_or_404(influencer_id)
    
    if request.method == 'POST':
        try:
            # Update influencer information from the form
            influencer.user.FullName = request.form.get('full_name')
            influencer.user.UserName = request.form.get('user_name')
            influencer.user.Email = request.form.get('email')
            influencer.user.PhoneNo = request.form.get('phone_no')
            influencer.user.Gender = request.form.get('gender')
            influencer.user.Nationality = request.form.get('nationality')
            influencer.ContentNiche = request.form.get('content_niche')

            # Update account URLs
            account_urls = {
                'instagram': request.form.get('url_instagram'),
                'youtube': request.form.get('url_youtube'),
                'tiktok': request.form.get('url_tiktok'),
                'twitter': request.form.get('url_twitter'),
                'facebook': request.form.get('url_facebook')
            }

            # Filter out empty URLs
            account_urls = {platform: url for platform, url in account_urls.items() if url}
            influencer.AccountURLs = account_urls

            # Update platform presence
            platform_presence = [platform for platform, url in account_urls.items() if url]
            influencer.PlatformPresence = platform_presence

            db.session.commit()
            return redirect(url_for('influencer_profile', influencer_id=influencer.InfluencerID))
        except Exception as e:
            print("Error updating influencer profile:", e)
            db.session.rollback()
    
    # Pre-fill the form with existing influencer information
    account_urls = influencer.AccountURLs if influencer.AccountURLs else {}

    return render_template('i_profile.html', influencer=influencer, account_urls=account_urls)


@app.route('/find_campaigns/<int:influencer_id>', methods=['GET'])
def find_campaigns(influencer_id):
    influencer = Influencer.query.get_or_404(influencer_id)
    search_query = request.args.get('search', '')
    filter_niche = request.args.get('filter', '')
    campaign_id = request.args.get('campaign_id')
    action = request.args.get('action')
    # show_message_modal = request.args.get('show_message_modal', None)
    # receiver_id = request.args.get('', None)

    # Query campaigns
    campaigns = Campaign.query.filter(Campaign.Visibility == 'public')
    
    if search_query:
        campaigns = campaigns.filter(Campaign.Title.ilike(f'%{search_query}%'))
    
    if filter_niche:
        campaigns = campaigns.filter(Campaign.Niche == filter_niche)
    
    campaigns = campaigns.all()

    # Get distinct niches for filtering
    niches = db.session.query(Campaign.Niche).distinct().all()
    niches = [niche[0] for niche in niches]

    # Initialize sponsor to avoid UnboundLocalError
    campaign = None 
    receiver_id = None
    

    # Check if the action is to view the campaign
    modal_campaign = None
    if campaign_id:
        if action == 'view':
            modal_campaign = Campaign.query.get(campaign_id)
            campaign = Campaign.query.get_or_404(campaign_id)
            receiver_id = Sponsor.query.get(campaign.SponsorID)
        
        
    # Fetch campaign requests for the influencer
    requests = {r.CampaignID: r for r in CampaignRequest.query.filter_by(InfluencerID=influencer_id).all()}

    return render_template(
    'i_find.html',
    campaigns=campaigns,
    niches=niches,
    requests=requests,
    modal_campaign=modal_campaign,
    influencer=influencer,
    influencer_id=influencer_id,
    campaign=campaign,
    receiver_id=receiver_id
)



        
@app.route('/prev_campaigns/<int:influencer_id>', methods=['GET'])
def prev_campaigns(influencer_id):
    influencer = Influencer.query.get_or_404(influencer_id)
    search_query = request.args.get('search', '')
    
    campaign_id = request.args.get('campaign_id')
    action = request.args.get('action')
   
    # Base query to get all previous campaigns for the influencer
    campaigns_query = db.session.query(Campaign)\
                                .join(ActiveCampaign, ActiveCampaign.CampaignID == Campaign.CampaignID)\
                                .filter(ActiveCampaign.InfluencerID == influencer_id)\
                                .filter(Campaign.EndDate < date.today())

    # Apply search filter if there's a search query
    if search_query:
        campaigns_query = campaigns_query.filter(Campaign.Title.ilike(f'%{search_query}%'))

    
    # Execute the query to get the campaigns
    campaigns = campaigns_query.all()

    
    # Initialize sponsor to avoid UnboundLocalError
    campaign = None 
    receiver_id = None

    # Check if the action is to view the campaign
    modal_campaign = None
    if campaign_id:
        if action == 'view':
            modal_campaign = Campaign.query.get(campaign_id)
            campaign = Campaign.query.get_or_404(campaign_id)
            receiver_id = Sponsor.query.get(campaign.SponsorID)

    return render_template(
        'i_prev_campaign.html',
        campaigns=campaigns,
        modal_campaign=modal_campaign,
        
        influencer=influencer,
        influencer_id=influencer_id,
        campaign=campaign,
        receiver_id=receiver_id
    )

    


@app.route('/find_influencers/<int:sponsor_id>/<int:campaign_id>', methods=['GET'])
def find_influencers(sponsor_id, campaign_id):
    sponsor = Sponsor.query.get_or_404(sponsor_id)
    search_query = request.args.get('search', '')
    filter_niche = request.args.get('filter', '')
    influencer_id = request.args.get('influencer_id')
    action = request.args.get('action')
    show_message_modal = request.args.get('show_message_modal', None)
    receiver_id = request.args.get('receiver_id', None)

    # Query influencers based on search and filter criteria
    influencers = Influencer.query.join(User).filter(User.Role == 'Influencer')

    if search_query:
        influencers = influencers.filter(User.FullName.ilike(f'%{search_query}%'))

    if filter_niche:
        influencers = influencers.filter(Influencer.ContentNiche == filter_niche)

    influencers = influencers.all()

    # Get distinct niches for filtering
    niches = db.session.query(Influencer.ContentNiche).distinct().all()
    niches = [niche[0] for niche in niches]

    # Initialize modal variables
    modal_influencer = None

    # Handle the action to view influencer details
    if action == 'view' and influencer_id:
        modal_influencer = Influencer.query.get(influencer_id)

    campaign_requests = CampaignRequest.query.filter_by(CampaignID=campaign_id, SponsorID=sponsor_id).all()

    # Create a dictionary to track existing requests
    existing_requests = {request.InfluencerID: request for request in campaign_requests}


    return render_template(
        's_campaign_find.html',
        sponsor=sponsor,
        campaign_id=campaign_id,
        influencers=influencers,
        niches=niches,
        modal_influencer=modal_influencer,
        show_message_modal=show_message_modal,
        receiver_id=receiver_id,
        sponsor_id=sponsor_id,
        existing_requests=existing_requests
    )



@app.route('/message_campaign/<int:influencer_id>/<int:campaign_id>', methods=['GET', 'POST'])
def message_campaign(influencer_id, campaign_id):
    influencer = Influencer.query.get_or_404(influencer_id)
    campaign = Campaign.query.get_or_404(campaign_id)
    sponsor = Sponsor.query.get(campaign.SponsorID)
    receiver_id = sponsor.UserID if sponsor else None

    if request.method == 'POST':
        sender_id = request.form.get('sender_id')
        content = request.form.get('content')
        
        if not receiver_id:
            flash('No recipient found for the message.', 'error')
            return redirect(url_for('find_campaigns', influencer_id=influencer_id))

        # Save the message to the database
        new_message = Message(
            SenderID=sender_id,
            ReceiverID=receiver_id,
            Content=content,
            Timestamp=datetime.utcnow(),
            CampaignID = campaign_id
        )
        db.session.add(new_message)
        db.session.commit()

        flash('Message sent successfully!', 'success')
        return redirect(url_for('find_campaigns', influencer_id=influencer_id))

    # For GET request, render the message modal or form
    show_message_modal = request.args.get('show_message_modal', None)
    return render_template(
        'i_find.html',
        influencer=influencer,
        campaign=campaign,
        receiver_id=receiver_id,
        show_message_modal=show_message_modal
    )


@app.route('/message_influencer/<int:sponsor_id>/<int:campaign_id>', methods=['POST'])
def message_influencer(sponsor_id,campaign_id):
    sponsor = Sponsor.query.get_or_404(sponsor_id)
    campaign = Campaign.query.get_or_404(campaign_id)
    
    
    sender_id = request.form.get('sender_id')
    receiver_id = request.form.get('receiver_id')
    print(f'Receiver ID: {receiver_id}')
    content = request.form.get('content')

    if not receiver_id:
        flash('No recipient found for the message.', 'error')
        return redirect(url_for('find_influencers', sponsor_id=sponsor_id, campaign_id=campaign_id))

    influencer = Influencer.query.get_or_404(receiver_id)
    u_id = influencer.UserID 

    if not influencer:
        flash('No recipient found for the message.', 'error')
        return redirect(url_for('find_influencers', sponsor_id=sponsor_id, campaign_id=campaign_id))

    # Save the message to the database
    new_message = Message(
        SenderID=sender_id,
        ReceiverID=u_id,
        Content=content,
        Timestamp=datetime.utcnow(),
        CampaignID=campaign_id
    )
    db.session.add(new_message)
    db.session.commit()

    flash('Message sent successfully!', 'success')
    return redirect(url_for('find_influencers', sponsor_id=sponsor_id, campaign_id=campaign_id, show_request_modal=True))




@app.route('/send_request/<int:influencer_id>/<int:campaign_id>', methods=['POST'])
def send_request(influencer_id, campaign_id):
    new_request = CampaignRequest(
        InfluencerID=influencer_id,
        CampaignID=campaign_id,
        Status='Pending'
    )
    db.session.add(new_request)
    db.session.commit()
    flash('Request sent successfully!', 'success')
    return redirect(url_for('find_campaigns' , influencer_id= influencer_id))



@app.route('/cancel_request/<int:request_id>', methods=['POST'])
def cancel_request(request_id):
    request = CampaignRequest.query.get(request_id)
    if request:
        influencer_id = request.InfluencerID
        db.session.delete(request)
        db.session.commit()
        flash('Request cancelled successfully!', 'success')
    else:
        flash('Request not found.', 'error')
        influencer_id = None

    if influencer_id:
        return redirect(url_for('find_campaigns', influencer_id=influencer_id))
    else:
        # Handle the case where the request was not found and influencer_id is None
        return redirect(url_for('some_default_page'))


@app.route('/request_influencer/<int:influencer_id>/<int:campaign_id>/<int:sponsor_id>', methods=['POST'])
def request_influencer(influencer_id, campaign_id, sponsor_id):
    # Check if the route is hit
    print(f"Request received for InfluencerID: {influencer_id}, CampaignID: {campaign_id}, SponsorID: {sponsor_id}")

    # Check if the request already exists
    request_exists = CampaignRequest.query.filter_by(CampaignID=campaign_id, InfluencerID=influencer_id).first()
    if not request_exists:
        print("No existing request found, creating a new one.")
        new_request = CampaignRequest(CampaignID=campaign_id, InfluencerID=influencer_id, SponsorID=sponsor_id)
        db.session.add(new_request)
        try:
            db.session.commit()
            print("New request committed to the database.")
        except Exception as e:
            print(f"Error committing to the database: {e}")
    else:
        print("Request already exists, not creating a new one.")

    return redirect(url_for('find_influencers', sponsor_id=sponsor_id, campaign_id=campaign_id, show_request_modal=True))


@app.route('/cancel_influencer_request/<int:request_id>', methods=['POST'])
def cancel_influencer_request(request_id):
    request_to_cancel = CampaignRequest.query.get(request_id)
    if request_to_cancel:
        campaign_id = request_to_cancel.CampaignID
        sponsor_id = request_to_cancel.SponsorID
        db.session.delete(request_to_cancel)
        db.session.commit()
    return redirect(url_for('find_influencers', sponsor_id=sponsor_id, campaign_id=campaign_id, show_request_modal=False))




