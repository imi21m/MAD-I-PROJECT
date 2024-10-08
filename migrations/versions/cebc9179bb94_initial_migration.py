"""Initial migration.

Revision ID: cebc9179bb94
Revises: 
Create Date: 2024-07-30 14:55:54.979943

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cebc9179bb94'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('UserID', sa.Integer(), nullable=False),
    sa.Column('FullName', sa.String(length=100), nullable=False),
    sa.Column('UserName', sa.String(length=100), nullable=False),
    sa.Column('Email', sa.String(length=100), nullable=False),
    sa.Column('PhoneNo', sa.String(length=15), nullable=False),
    sa.Column('Password', sa.String(length=100), nullable=False),
    sa.Column('Gender', sa.String(length=10), nullable=False),
    sa.Column('Nationality', sa.String(length=50), nullable=False),
    sa.Column('Role', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('UserID'),
    sa.UniqueConstraint('Email'),
    sa.UniqueConstraint('UserName')
    )
    op.create_table('influencer',
    sa.Column('InfluencerID', sa.Integer(), nullable=False),
    sa.Column('UserID', sa.Integer(), nullable=False),
    sa.Column('PlatformPresence', sa.JSON(), nullable=False),
    sa.Column('AccountURLs', sa.JSON(), nullable=False),
    sa.Column('ContentNiche', sa.String(length=100), nullable=False),
    sa.ForeignKeyConstraint(['UserID'], ['user.UserID'], ),
    sa.PrimaryKeyConstraint('InfluencerID')
    )
    op.create_table('message',
    sa.Column('MessageID', sa.Integer(), nullable=False),
    sa.Column('SenderID', sa.Integer(), nullable=False),
    sa.Column('ReceiverID', sa.Integer(), nullable=False),
    sa.Column('Content', sa.String(length=500), nullable=False),
    sa.Column('Timestamp', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['ReceiverID'], ['user.UserID'], ),
    sa.ForeignKeyConstraint(['SenderID'], ['user.UserID'], ),
    sa.PrimaryKeyConstraint('MessageID')
    )
    op.create_table('sponsor',
    sa.Column('SponsorID', sa.Integer(), nullable=False),
    sa.Column('UserID', sa.Integer(), nullable=False),
    sa.Column('CompanyName', sa.String(length=100), nullable=False),
    sa.Column('CompanyWebsite', sa.String(length=200), nullable=True),
    sa.Column('IndustryCategory', sa.String(length=100), nullable=False),
    sa.ForeignKeyConstraint(['UserID'], ['user.UserID'], ),
    sa.PrimaryKeyConstraint('SponsorID')
    )
    op.create_table('campaign',
    sa.Column('CampaignID', sa.Integer(), nullable=False),
    sa.Column('SponsorID', sa.Integer(), nullable=False),
    sa.Column('Title', sa.String(length=100), nullable=False),
    sa.Column('Description', sa.String(length=500), nullable=False),
    sa.Column('Niche', sa.String(length=100), nullable=False),
    sa.Column('StartDate', sa.Date(), nullable=False),
    sa.Column('EndDate', sa.Date(), nullable=False),
    sa.Column('Budget', sa.Float(), nullable=False),
    sa.Column('Visibility', sa.String(length=50), nullable=False),
    sa.ForeignKeyConstraint(['SponsorID'], ['sponsor.SponsorID'], ),
    sa.PrimaryKeyConstraint('CampaignID')
    )
    op.create_table('active_campaign',
    sa.Column('ActiveID', sa.Integer(), nullable=False),
    sa.Column('CampaignID', sa.Integer(), nullable=False),
    sa.Column('InfluencerID', sa.Integer(), nullable=False),
    sa.Column('Progress', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['CampaignID'], ['campaign.CampaignID'], ),
    sa.ForeignKeyConstraint(['InfluencerID'], ['influencer.InfluencerID'], ),
    sa.PrimaryKeyConstraint('ActiveID')
    )
    op.create_table('campaign_agreement',
    sa.Column('AgreementID', sa.Integer(), nullable=False),
    sa.Column('CampaignID', sa.Integer(), nullable=False),
    sa.Column('InfluencerID', sa.Integer(), nullable=False),
    sa.Column('Terms', sa.String(length=500), nullable=False),
    sa.Column('Payment', sa.Float(), nullable=False),
    sa.Column('InfluencerName', sa.String(length=100), nullable=False),
    sa.ForeignKeyConstraint(['CampaignID'], ['campaign.CampaignID'], ),
    sa.ForeignKeyConstraint(['InfluencerID'], ['influencer.InfluencerID'], ),
    sa.PrimaryKeyConstraint('AgreementID')
    )
    op.create_table('campaign_progress',
    sa.Column('ProgressID', sa.Integer(), nullable=False),
    sa.Column('CampaignID', sa.Integer(), nullable=False),
    sa.Column('Status', sa.String(length=50), nullable=False),
    sa.Column('LastUpdated', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['CampaignID'], ['campaign.CampaignID'], ),
    sa.PrimaryKeyConstraint('ProgressID')
    )
    op.create_table('campaign_request',
    sa.Column('RequestID', sa.Integer(), nullable=False),
    sa.Column('CampaignID', sa.Integer(), nullable=False),
    sa.Column('InfluencerID', sa.Integer(), nullable=False),
    sa.Column('Status', sa.String(length=50), nullable=True),
    sa.Column('RequestedOn', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['CampaignID'], ['campaign.CampaignID'], ),
    sa.ForeignKeyConstraint(['InfluencerID'], ['influencer.InfluencerID'], ),
    sa.PrimaryKeyConstraint('RequestID')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('campaign_request')
    op.drop_table('campaign_progress')
    op.drop_table('campaign_agreement')
    op.drop_table('active_campaign')
    op.drop_table('campaign')
    op.drop_table('sponsor')
    op.drop_table('message')
    op.drop_table('influencer')
    op.drop_table('user')
    # ### end Alembic commands ###
