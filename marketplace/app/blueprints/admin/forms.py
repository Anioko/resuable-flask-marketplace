from flask_uploads import UploadSet, IMAGES
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.fields import PasswordField, StringField, SubmitField, BooleanField, IntegerField, FloatField, \
    MultipleFileField, TextAreaField, SelectField, FileField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Email, EqualTo, InputRequired, Length, Optional

from app import db
from app.models import Role, User, MCurrency, MShippingMethod, MCategory, LandingImage, LandingSetting 

images = UploadSet('images', IMAGES)


class ChangeUserNameForm(FlaskForm):
    first_name = StringField(
        'First name', validators=[InputRequired()])
    last_name = StringField(
        'Last name', validators=[InputRequired()])
    submit = SubmitField('Update first name and last name')


class ChangeUserEmailForm(FlaskForm):
    email = EmailField(
        'New email', validators=[InputRequired(),
                                 Length(1, 64),
                                 Email()])
    submit = SubmitField('Update email')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class ChangeAccountTypeForm(FlaskForm):
    role = QuerySelectField(
        'New account type',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(Role).order_by('permissions'))
    submit = SubmitField('Update role')


class ConfirmAccountForm(FlaskForm):
    confirmed = BooleanField('True: Tick this checkbox to confirm the users account manually',
                             validators=[InputRequired()])
    submit = SubmitField('Confirm')


class InviteUserForm(FlaskForm):
    role = QuerySelectField(
        'Account type',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(Role).order_by('permissions'))
    first_name = StringField(
        'First name', validators=[InputRequired(),
                                  Length(1, 64)])
    last_name = StringField(
        'Last name', validators=[InputRequired(),
                                 Length(1, 64)])
    email = EmailField(
        'Email', validators=[InputRequired(),
                             Length(1, 64),
                             Email()])
    submit = SubmitField('Invite')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class NewUserForm(InviteUserForm):
    password = PasswordField(
        'Password',
        validators=[
            InputRequired(),
            EqualTo('password2', 'Passwords must match.')
        ])
    password2 = PasswordField('Confirm password', validators=[InputRequired()])

    submit = SubmitField('Create')


class MCategoryForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    image = FileField('Image', validators=[InputRequired(), FileAllowed(images, 'Images only!')])
    order = IntegerField('Order', validators=[InputRequired()])
    is_featured = BooleanField("Is Featured ?")
    parent = QuerySelectField(
        'Parent Category',
        get_label='name',
        allow_blank=True,
        blank_text="No Parent",
        query_factory=lambda: db.session.query(MCategory).filter_by(parent_id=None).order_by('name'))
    submit = SubmitField('Submit')


class MCurrencyForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    symbol = StringField('Symbol', validators=[InputRequired()])
    default = BooleanField('Is Default ?')
    submit = SubmitField('Submit')


class MShippingMethodForm(FlaskForm):
    seller = QuerySelectField(
        'Seller',
        validators=[InputRequired()],
        get_label='full_name',
        query_factory=lambda: db.session.query(User).filter_by(is_seller=True).order_by('first_name'))
    name = StringField('Name', validators=[InputRequired()])
    submit = SubmitField('Submit')


class MProductForm(FlaskForm):
    name = StringField('Product name', validators=[InputRequired(), Length(1, 64)])
    images = MultipleFileField('Product Images', validators=[InputRequired(), FileAllowed(images, 'Images only!')])
    description = TextAreaField('Description', [InputRequired()])
    categories = QuerySelectMultipleField(
        'Categories',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(MCategory).order_by('order'))
    availability = BooleanField(u'Is it currently available?')
    min_order_quantity = IntegerField('Min number of units per order e.g 1', default=1)
    length = FloatField('Length in numbers only e.g 0.99')
    weight = FloatField('Weight in numbers only e.g 0.21')
    height = FloatField('Height in numbers only e.g 10')
    price = FloatField('Price, Figures only e.g 16.99')
    seller = QuerySelectField(
        'Seller',
        validators=[InputRequired()],
        get_label='full_name',
        query_factory=lambda: db.session.query(User).filter_by(is_seller=True).order_by('first_name'))
    price_currency = QuerySelectField(
        'Price currency',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(MCurrency).order_by('name'))
    is_featured = BooleanField("Is Featured ?")
    lead_time = StringField('Delivery time')
    submit = SubmitField('Submit')



class LandingSettingForm(FlaskForm):
    site_name = StringField('Site Name e.g bookstore.ng', validators=[InputRequired(), Length(1, 128)])
    title = StringField('Website Title', validators=[InputRequired(), Length(1, 128)])
    description = StringField('Website description', validators=[InputRequired(), Length(1, 180)])
    twitter_name = StringField('Twitter accname only')
    facebook_name = StringField('Facebook pagename only')
    instagram_name = StringField('Instagram username only')
    tiktok_name = StringField('Tiktok username only')
    linkedin_name = StringField('Linkedin pagename only')
    snap_chat_name = StringField('Snap chat username only')
    youtube = StringField('Youtube page name only')
    blog = StringField('e.g blog')
    about = StringField('e.g about')
    contact = StringField('e.g contact')
    faq = StringField('e.g faq')
    
    logo = FileField('Logo', validators=[InputRequired(), FileAllowed(images, 'Images only!')])
    #images = MultipleFileField('Images', validators=[InputRequired(), FileAllowed(images, 'Images only!')])
    h1 = StringField('H1 text', validators=[InputRequired(), Length(1, 180)])
    h2 = StringField('H2 Text')
    h3 = StringField('H3 Text')
    h4 = StringField('H4 Text')
    h5 = StringField('H5 Text')
  
    featured_title_one = StringField('e.g Fast delivery')
    featured_title_one_text = StringField('Write about 90 words')
    featured_title_one_icon = StringField('e.g fa-truck')
    featured_title_two = StringField('e.g Creative Strategy')
    featured_title_two_text = StringField('Write about 90 words')
    featured_title_two_icon = StringField('e.g fa-landmark')
    featured_title_three = StringField('e.g High secured')
    featured_title_three_text = StringField('Write about 90 words')
    featured_title_three_icon = StringField('e.g fa-lock')
    
    google_analytics_id = StringField('Google Analytics ID')
    other_tracking_analytics_one = StringField('Insert Analytics Script')
    other_tracking_analytics_two = StringField('Insert Analytics Script')
    other_tracking_analytics_three = StringField('Insert Analytics Script')
    other_tracking_analytics_four = StringField('Insert Analytics Script')
    block_content_one = TextAreaField('Description')
    html_code_one = TextAreaField('Insert raw html')
    html_code_two = TextAreaField('Insert raw html')
    html_code_three = TextAreaField('Insert raw html')
    html_code_four = TextAreaField('Insert raw html')
    submit = SubmitField('Submit')

class LandingImageForm(FlaskForm):

    image = FileField('Image', validators=[Optional(), FileAllowed(images, 'Images only!')])
    submit = SubmitField('Submit')

class OurBrandForm(FlaskForm):
    ### these are brands which we own in house
    
    brand_name_one = StringField('e.g Mediville')
    brand_name_two = StringField('e.g Networkedng')
    brand_name_three = StringField('e.g Intel')
    brand_name_four = StringField('e.g teamsworkspace')
    brand_name_five = StringField('e.g teamsworkspace')
    brand_url_one = StringField('e.g mediville.com')
    brand_url_two = StringField('e.g https://networked.ng')
    brand_url_three = StringField('e.g http://intel.com')
    brand_url_four = StringField('e.g teamsworkspace.com.ng')
    brand_url_five = StringField('e.g https://teamsworkspace.com.ng')
    submit = SubmitField('Submit')

class NewsLinkForm(FlaskForm):
    ### these are news sites that write about us
    
    news_site_one = StringField('e.g CNN')
    news_site_two = StringField('e.g BBC')
    news_site_three = StringField('e.g FoxNews')
    news_site_four = StringField('e.g PunchNews')
    news_site_five = StringField('e.g Vanguard')
    news_url_one = StringField('e.g cnn.com/link_to_news')
    news_url_two = StringField('e.g https://bbc.com/link_to_news')
    news_url_three = StringField('e.g http://foxnews.com/link_to_news')
    news_url_four = StringField('e.g punch.ng/link_to_news')
    news_url_five = StringField('e.g https://vanguard.com/link_to_news')
    submit = SubmitField('Submit')
