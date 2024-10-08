"""Add SponsorID column to CampaignRequest model

Revision ID: 580419315288
Revises: 6dfcd2597dda
Create Date: 2024-08-09 18:42:34.292408

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '580419315288'
down_revision = '6dfcd2597dda'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('campaign_request', schema=None) as batch_op:
        batch_op.add_column(sa.Column('SponsorID', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_campaignrequest_sponsorid', 'sponsor', ['SponsorID'], ['SponsorID'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('campaign_request', schema=None) as batch_op:
        batch_op.drop_constraint('fk_campaignrequest_sponsorid', type_='foreignkey')
        batch_op.drop_column('SponsorID')

    # ### end Alembic commands ###
