from flask_ckeditor import CKEditorField
from flask_uploads import UploadSet, IMAGES
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.fields import PasswordField, StringField, SubmitField, BooleanField, IntegerField, FloatField, \
    MultipleFileField, TextAreaField, SelectField, FileField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Email, EqualTo, InputRequired, Length
from wtforms_alchemy import Unique, ModelForm, model_form_factory

from app import db
from app.models import Role, User, MBrand, MVariant, MCurrency, MShippingMethod,\
     MCategory, BlogCategory, BlogTag, BlogNewsLetter
from app.utils import conditions

images = UploadSet('images', IMAGES)
BaseModelForm = model_form_factory(FlaskForm)


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

class MBrandForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    image = FileField('Brand Image', validators=[InputRequired(), FileAllowed(images, 'Images only!')])
    submit = SubmitField('Submit')

class MSettingsForm(FlaskForm):
    stripe_public_key = StringField('Stripe Public Key', validators=[InputRequired()])
    stripe_secret_key = StringField('Stripe Public Key', validators=[InputRequired()])
    brand_image = FileField('Brand image', validators=[InputRequired(), FileAllowed(images, 'Images only!')])
    brand_description = StringField('Description', validators=[InputRequired()])
    submit = SubmitField('Submit')

class MBannerForm(FlaskForm):
    main_image = FileField('Main image', validators=[InputRequired(), FileAllowed(images, 'Images only!')])
    feature_header_one = StringField('Header one', validators=[InputRequired()])
    feature_icon_one = FileField('Icon one', validators=[InputRequired(), FileAllowed(images, 'Images only!')])
    feature_description_one = StringField('Description one', validators=[InputRequired()])
    feature_header_two = StringField('Header two', validators=[InputRequired()])
    feature_icon_two = FileField('Icon two', validators=[InputRequired(), FileAllowed(images, 'Images only!')])
    feature_description_two = StringField('Description two', validators=[InputRequired()])
    feature_header_three = StringField('Header three', validators=[InputRequired()])
    feature_icon_three = FileField('Icon three', validators=[InputRequired(), FileAllowed(images, 'Images only!')])
    feature_description_three = StringField('Description three', validators=[InputRequired()])
    submit = SubmitField('Submit')


class BlogCategoryForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    order = IntegerField('Order', validators=[InputRequired()])
    is_featured = BooleanField("Is Featured ?")
    submit = SubmitField('Submit')


class BlogTagForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    submit = SubmitField('Submit')


class BlogNewsLetterForm(BaseModelForm):
    email = EmailField('Email', validators=[InputRequired(), Length(1, 64), Email(), Unique(BlogNewsLetter.email)])
    submit = SubmitField('Submit')


class BlogPostForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    text = CKEditorField('Body', validators=[InputRequired()])
    image = FileField('Image', validators=[InputRequired(), FileAllowed(images, 'Images only!')])
    categories = QuerySelectMultipleField(
        'Categories',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(BlogCategory).order_by('order'))
    tags = QuerySelectMultipleField(
        'Tags',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(BlogTag).order_by('created_at'))
    newsletter = BooleanField('Send Announcement To Subscribers.')
    all_users = BooleanField('Send Announcement To All Users.')

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
        query_factory=lambda: db.session.query(MCategory).order_by('order')
    )
    variants = QuerySelectMultipleField(
        'Variants',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(MVariant).order_by('name')
    )
    condition = SelectField(u'Select condition', choices=conditions)
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
    brand = QuerySelectField(
        'Brand',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(MBrand).order_by('name'))
    is_featured = BooleanField("Is Featured ?")
    lead_time = StringField('Delivery time')
    submit = SubmitField('Submit')


