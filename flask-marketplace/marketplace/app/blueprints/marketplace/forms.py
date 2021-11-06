from flask_uploads import UploadSet, IMAGES
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, MultipleFileField, TextAreaField, BooleanField, IntegerField, FloatField, SubmitField, \
    RadioField, SelectField
from wtforms.validators import InputRequired, Length, Email, Optional
from wtforms_alchemy import QuerySelectMultipleField, QuerySelectField, Unique, model_form_factory
from wtforms.fields.html5 import EmailField

from app import db
from app.models import MBrand, MVariant, MCategory, MCurrency, User
from app.utils import states, countries, conditions

images = UploadSet('images', IMAGES)
BaseModelForm = model_form_factory(FlaskForm)

class SVariantForm(FlaskForm):
    name = StringField('Variant name...', validators=[InputRequired()])
    symbol = StringField('Variant Symbol...', validators=[InputRequired()])
    submit = SubmitField('Submit')

class ReviewForm(FlaskForm):
    message = StringField('Write your review...', validators=[InputRequired()])
    score = FloatField('Score from 0 to 5', validators=[InputRequired()])
    submit = SubmitField('Submit')

class SearchForm(FlaskForm):
    query = StringField('Search...', validators=[InputRequired(), Length(1, 64)])


class SProductForm(FlaskForm):
    name = StringField('Product name', validators=[InputRequired(), Length(1, 64)])
    images = MultipleFileField('Product Images', validators=[InputRequired(), FileAllowed(images, 'Images only!')])
    description = TextAreaField('Description', [InputRequired()])
    categories = QuerySelectMultipleField(
        'Categories',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(MCategory).order_by('order')
    )
    #variants = QuerySelectMultipleField(
       # 'Variants',
        #validators=[InputRequired()],
        # get_label='name',
        #query_factory=lambda: db.session.query(MVariant).order_by('name')
    #)
    condition = SelectField(u'Select condition', choices=conditions)
    availability = BooleanField(u'Is it currently available?')
    min_order_quantity = IntegerField('Min number of units per order e.g 1', default=1)
    length = FloatField('Length in numbers only e.g 0.99')
    weight = FloatField('Weight in numbers only e.g 0.21')
    height = FloatField('Height in numbers only e.g 10')
    price = FloatField('Price, Figures only e.g 16.99')
    price_currency = QuerySelectField(
        'Price currency',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(MCurrency).order_by('name'))
    brand = QuerySelectField(
        'Brand',
        validators=[Optional()],
        get_label='name',
        query_factory=lambda: db.session.query(MBrand).order_by('name'))
    is_featured = BooleanField("Is Featured ?")
    lead_time = StringField('Delivery time')
    submit = SubmitField('Submit')


class SShippingForm(FlaskForm):
    first_name = StringField('First name', validators=[InputRequired()])
    last_name = StringField('Last name', validators=[InputRequired()])
    email = EmailField('Email', validators=[InputRequired(), Email()])
    mobile_phone = IntegerField('Phone numbers only', validators=[InputRequired()])
    state = StringField('State', validators=[InputRequired()])
    zip = StringField('Zip Code', validators=[InputRequired(), Length(1, 7)])
    country = SelectField(u'Select Country', choices=countries)
    city = StringField('City', validators=[InputRequired()])


class SShippingMethodForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    submit = SubmitField('Submit')

