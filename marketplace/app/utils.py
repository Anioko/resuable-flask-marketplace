import datetime
import json
import os
import random
import string
from html.parser import HTMLParser

import cv2
from flask import url_for, abort, session, current_app
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from wtforms.fields import Field
from wtforms.widgets import HiddenInput
from wtforms.compat import text_type

# from app.models import MCart

db = SQLAlchemy()
login_manager = LoginManager()

states = [
        ('AL', 'Alabama'),
        ('AL', 'Alabama'),
        ('AK', 'Alaska'),
        ('AZ', 'Arizona'),
        ('AR', 'Arkansas'),
        ('CA', 'California'),
        ('CO', 'Colorado'),
        ('CT', 'Connecticut'),
        ('DE', 'Delaware'),
        ('DC', 'District Of Columbia'),
        ('FL', 'Florida'),
        ('GA', 'Georgia'),
        ('HI', 'Hawaii'),
        ('ID', 'Idaho'),
        ('IL', 'Illinois'),
        ('IN', 'Indiana'),
        ('IA', 'Iowa'),
        ('KS', 'Kansas'),
        ('KY', 'Kentucky'),
        ('LA', 'Louisiana'),
        ('ME', 'Maine'),
        ('MD', 'Maryland'),
        ('MA', 'Massachusetts'),
        ('MI', 'Michigan'),
        ('MN', 'Minnesota'),
        ('MS', 'Mississippi'),
        ('MO', 'Missouri'),
        ('MT', 'Montana'),
        ('NE', 'Nebraska'),
        ('NV', 'Nevada'),
        ('NH', 'New Hampshire'),
        ('NJ', 'New Jersey'),
        ('NM', 'New Mexico'),
        ('NY', 'New York'),
        ('NC', 'North Carolina'),
        ('ND', 'North Dakota'),
        ('OH', 'Ohio'),
        ('OK', 'Oklahoma'),
        ('OR', 'Oregon'),
        ('PA', 'Pennsylvania'),
        ('RI', 'Rhode Island'),
        ('SC', 'South Carolina'),
        ('SD', 'South Dakota'),
        ('TN', 'Tennessee'),
        ('TX', 'Texas'),
        ('UT', 'Utah'),
        ('VT', 'Vermont'),
        ('VA', 'Virginia'),
        ('WA', 'Washington'),
        ('WV', 'West Virginia'),
        ('WI', 'Wisconsin'),
        ('WY', 'Wyoming')]
countries = [
        ('Afganistan', 'Afghanistan'),
        ('Albania', 'Albania'),
        ('Algeria', 'Algeria'),
        ('American Samoa', 'American Samoa'),
        ('Andorra', 'Andorra'),
        ('Angola', 'Angola'),
        ('Anguilla', 'Anguilla'),
        ('Antigua & Barbuda', 'Antigua & Barbuda'),
        ('Argentina', 'Argentina'),
        ('Armenia', 'Armenia'),
        ('Aruba', 'Aruba'),
        ('Australia', 'Australia'),
        ('Austria', 'Austria'),
        ('Azerbaijan', 'Azerbaijan'),
        ('Bahamas', 'Bahamas'),
        ('Bahrain', 'Bahrain'),
        ('Bangladesh', 'Bangladesh'),
        ('Barbados', 'Barbados'),
        ('Belarus', 'Belarus'),
        ('Belgium', 'Belgium'),
        ('Belize', 'Belize'),
        ('Benin', 'Benin'),
        ('Bermuda', 'Bermuda'),
        ('Bhutan', 'Bhutan'),
        ('Bolivia', 'Bolivia'),
        ('Bonaire', 'Bonaire'),
        ('Bosnia & Herzegovina', 'Bosnia & Herzegovina'),
        ('Botswana', 'Botswana'),
        ('Brazil', 'Brazil'),
        ('British Indian Ocean Ter', 'British Indian Ocean Ter'),
        ('Brunei', 'Brunei'),
        ('Bulgaria', 'Bulgaria'),
        ('Burkina Faso', 'Burkina Faso'),
        ('Burundi', 'Burundi'),
        ('Cambodia', 'Cambodia'),
        ('Cameroon', 'Cameroon'),
        ('Canada', 'Canada'),
        ('Canary Islands', 'Canary Islands'),
        ('Cape Verde', 'Cape Verde'),
        ('Cayman Islands', 'Cayman Islands'),
        ('Central African Republic', 'Central African Republic'),
        ('Chad', 'Chad'),
        ('Channel Islands', 'Channel Islands'),
        ('Chile', 'Chile'),
        ('China', 'China'),
        ('Christmas Island', 'Christmas Island'),
        ('Cocos Island', 'Cocos Island'),
        ('Colombia', 'Colombia'),
        ('Comoros', 'Comoros'),
        ('Congo', 'Congo'),
        ('Cook Islands', 'Cook Islands'),
        ('Costa Rica', 'Costa Rica'),
        ('Cote DIvoire', 'Cote DIvoire'),
        ('Croatia', 'Croatia'),
        ('Cuba', 'Cuba'),
        ('Curaco', 'Curacao'),
        ('Cyprus', 'Cyprus'),
        ('Czech Republic', 'Czech Republic'),
        ('Denmark', 'Denmark'),
        ('Djibouti', 'Djibouti'),
        ('Dominica', 'Dominica'),
        ('Dominican Republic', 'Dominican Republic'),
        ('East Timor', 'East Timor'),
        ('Ecuador', 'Ecuador'),
        ('Egypt', 'Egypt'),
        ('El Salvador', 'El Salvador'),
        ('Equatorial Guinea', 'Equatorial Guinea'),
        ('Eritrea', 'Eritrea'),
        ('Estonia', 'Estonia'),
        ('Ethiopia', 'Ethiopia'),
        ('Falkland Islands', 'Falkland Islands'),
        ('Faroe Islands', 'Faroe Islands'),
        ('Fiji', 'Fiji'),
        ('Finland', 'Finland'),
        ('France', 'France'),
        ('French Guiana', 'French Guiana'),
        ('French Polynesia', 'French Polynesia'),
        ('French Southern Ter', 'French Southern Ter'),
        ('Gabon', 'Gabon'),
        ('Gambia', 'Gambia'),
        ('Georgia', 'Georgia'),
        ('Germany', 'Germany'),
        ('Ghana', 'Ghana'),
        ('Gibraltar', 'Gibraltar'),
        ('Great Britain', 'Great Britain'),
        ('Greece', 'Greece'),
        ('Greenland', 'Greenland'),
        ('Grenada', 'Grenada'),
        ('Guadeloupe', 'Guadeloupe'),
        ('Guam', 'Guam'),
        ('Guatemala', 'Guatemala'),
        ('Guinea', 'Guinea'),
        ('Guyana', 'Guyana'),
        ('Haiti', 'Haiti'),
        ('Hawaii', 'Hawaii'),
        ('Honduras', 'Honduras'),
        ('Hong Kong', 'Hong Kong'),
        ('Hungary', 'Hungary'),
        ('Iceland', 'Iceland'),
        ('Indonesia', 'Indonesia'),
        ('India', 'India'),
        ('Iran', 'Iran'),
        ('Iraq', 'Iraq'),
        ('Ireland', 'Ireland'),
        ('Isle of Man', 'Isle of Man'),
        ('Israel', 'Israel'),
        ('Italy', 'Italy'),
        ('Jamaica', 'Jamaica'),
        ('Japan', 'Japan'),
        ('Jordan', 'Jordan'),
        ('Kazakhstan', 'Kazakhstan'),
        ('Kenya', 'Kenya'),
        ('Kiribati', 'Kiribati'),
        ('Korea North', 'Korea North'),
        ('Korea Sout', 'Korea South'),
        ('Kuwait', 'Kuwait'),
        ('Kyrgyzstan', 'Kyrgyzstan'),
        ('Laos', 'Laos'),
        ('Latvia', 'Latvia'),
        ('Lebanon', 'Lebanon'),
        ('Lesotho', 'Lesotho'),
        ('Liberia', 'Liberia'),
        ('Libya', 'Libya'),
        ('Liechtenstein', 'Liechtenstein'),
        ('Lithuania', 'Lithuania'),
        ('Luxembourg', 'Luxembourg'),
        ('Macau', 'Macau'),
        ('Macedonia', 'Macedonia'),
        ('Madagascar', 'Madagascar'),
        ('Malaysia', 'Malaysia'),
        ('Malawi', 'Malawi'),
        ('Maldives', 'Maldives'),
        ('Mali', 'Mali'),
        ('Malta', 'Malta'),
        ('Marshall Islands', 'Marshall Islands'),
        ('Martinique', 'Martinique'),
        ('Mauritania', 'Mauritania'),
        ('Mauritius', 'Mauritius'),
        ('Mayotte', 'Mayotte'),
        ('Mexico', 'Mexico'),
        ('Midway Islands', 'Midway Islands'),
        ('Moldova', 'Moldova'),
        ('Monaco', 'Monaco'),
        ('Mongolia', 'Mongolia'),
        ('Montserrat', 'Montserrat'),
        ('Morocco', 'Morocco'),
        ('Mozambique', 'Mozambique'),
        ('Myanmar', 'Myanmar'),
        ('Nambia', 'Nambia'),
        ('Nauru', 'Nauru'),
        ('Nepal', 'Nepal'),
        ('Netherland Antilles', 'Netherland Antilles'),
        ('Netherlands', 'Netherlands (Holland, Europe)'),
        ('Nevis', 'Nevis'),
        ('New Caledonia', 'New Caledonia'),
        ('New Zealand', 'New Zealand'),
        ('Nicaragua', 'Nicaragua'),
        ('Niger', 'Niger'),
        ('Nigeria', 'Nigeria'),
        ('Niue', 'Niue'),
        ('Norfolk Island', 'Norfolk Island'),
        ('Norway', 'Norway'),
        ('Oman', 'Oman'),
        ('Pakistan', 'Pakistan'),
        ('Palau Island', 'Palau Island'),
        ('Palestine', 'Palestine'),
        ('Panama', 'Panama'),
        ('Papua New Guinea', 'Papua New Guinea'),
        ('Paraguay', 'Paraguay'),
        ('Peru', 'Peru'),
        ('Phillipines', 'Philippines'),
        ('Pitcairn Island', 'Pitcairn Island'),
        ('Poland', 'Poland'),
        ('Portugal', 'Portugal'),
        ('Puerto Rico', 'Puerto Rico'),
        ('Qatar', 'Qatar'),
        ('Republic of Montenegro', 'Republic of Montenegro'),
        ('Republic of Serbia', 'Republic of Serbia'),
        ('Reunion', 'Reunion'),
        ('Romania', 'Romania'),
        ('Russia', 'Russia'),
        ('Rwanda', 'Rwanda'),
        ('St Barthelemy', 'St Barthelemy'),
        ('St Eustatius', 'St Eustatius'),
        ('St Helena', 'St Helena'),
        ('St Kitts-Nevis', 'St Kitts-Nevis'),
        ('St Lucia', 'St Lucia'),
        ('St Maarten', 'St Maarten'),
        ('St Pierre & Miquelon', 'St Pierre & Miquelon'),
        ('St Vincent & Grenadines', 'St Vincent & Grenadines'),
        ('Saipan', 'Saipan'),
        ('Samoa', 'Samoa'),
        ('Samoa American', 'Samoa American'),
        ('San Marino', 'San Marino'),
        ('Sao Tome & Principe', 'Sao Tome & Principe'),
        ('Saudi Arabia', 'Saudi Arabia'),
        ('Senegal', 'Senegal'),
        ('Seychelles', 'Seychelles'),
        ('Sierra Leone', 'Sierra Leone'),
        ('Singapore', 'Singapore'),
        ('Slovakia', 'Slovakia'),
        ('Slovenia', 'Slovenia'),
        ('Solomon Islands', 'Solomon Islands'),
        ('Somalia', 'Somalia'),
        ('South Africa', 'South Africa'),
        ('Spain', 'Spain'),
        ('Sri Lanka', 'Sri Lanka'),
        ('Sudan', 'Sudan'),
        ('Suriname', 'Suriname'),
        ('Swaziland', 'Swaziland'),
        ('Sweden', 'Sweden'),
        ('Switzerland', 'Switzerland'),
        ('Syria', 'Syria'),
        ('Tahiti', 'Tahiti'),
        ('Taiwan', 'Taiwan'),
        ('Tajikistan', 'Tajikistan'),
        ('Tanzania', 'Tanzania'),
        ('Thailand', 'Thailand'),
        ('Togo', 'Togo'),
        ('Tokelau', 'Tokelau'),
        ('Tonga', 'Tonga'),
        ('Trinidad & Tobago', 'Trinidad & Tobago'),
        ('Tunisia', 'Tunisia'),
        ('Turkey', 'Turkey'),
        ('Turkmenistan', 'Turkmenistan'),
        ('Turks & Caicos Is', 'Turks & Caicos Is'),
        ('Tuvalu', 'Tuvalu'),
        ('Uganda', 'Uganda'),
        ('United Kingdom', 'United Kingdom'),
        ('Ukraine', 'Ukraine'),
        ('United Arab Erimates', 'United Arab Emirates'),
        ('United States of America', 'United States of America'),
        ('Uraguay', 'Uruguay'),
        ('Uzbekistan', 'Uzbekistan'),
        ('Vanuatu', 'Vanuatu'),
        ('Vatican City State', 'Vatican City State'),
        ('Venezuela', 'Venezuela'),
        ('Vietnam', 'Vietnam'),
        ('Virgin Islands (Brit)', 'Virgin Islands (Brit)'),
        ('Virgin Islands (USA)', 'Virgin Islands (USA)'),
        ('Wake Island', 'Wake Island'),
        ('Wallis & Futana Is', 'Wallis & Futana Is'),
        ('Yemen', 'Yemen'),
        ('Zaire', 'Zaire'),
        ('Zambia', 'Zambia'),
        ('Zimbabwe', 'Zimbabwe')]


def register_template_utils(app):
    """Register Jinja 2 helpers (called from __init__.py)."""

    @app.template_test()
    def equalto(value, other):
        return value == other

    @app.template_global()
    def is_hidden_field(field):
        from wtforms.fields import HiddenField
        return isinstance(field, HiddenField)

    app.add_template_global(index_for_role)


def index_for_role(role):
    return url_for(role.index)


class CustomSelectField(Field):
    widget = HiddenInput()

    def __init__(self, label='', validators=None, multiple=False,
                 choices=[], allow_custom=True, **kwargs):
        super(CustomSelectField, self).__init__(label, validators, **kwargs)
        self.multiple = multiple
        self.choices = choices
        self.allow_custom = allow_custom

    def _value(self):
        return text_type(self.data) if self.data is not None else ''

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = valuelist[1]
            self.raw_data = [valuelist[1]]
        else:
            self.data = ''


def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
        diff = now - time
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(second_diff / 60) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(second_diff / 3600) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff / 7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff / 30) + " months ago"
    return str(day_diff / 365) + " years ago"


def jsonify_object(item):
    new_item = {}
    for item_attr in item.__dict__:
        if not item_attr.startswith('_'):
            value = item.__dict__[item_attr] if type(item.__dict__[item_attr]) is not datetime.datetime else str(
                item.__dict__[item_attr])
            new_item[item_attr] = value
    return new_item


def get_paginated_list(results):
    return_value = jsonify_object(results)
    items = []
    for item in results.items:
        items.append(jsonify_object(item))
    items.reverse()
    return_value['items'] = items
    del(return_value['query'])
    return return_value


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def get_cart():
    metadata = db.metadata
    ex_table = metadata.tables['marketplace_carts']
    cart_items_table = metadata.tables['marketplace_cart_items']
    if current_user.is_authenticated:
        cart = db.engine.execute(ex_table.select(ex_table.c.user_id==current_user.id)).first()
    else:
        cart = db.engine.execute(ex_table.select(ex_table.c.session_id==session['cart_id'])).first()
    if cart:
        products = db.engine.execute(cart_items_table.select(cart_items_table.c.cart_id==cart.id)).fetchall()
        return len(products)
    else:
        return ''


def json_load(string):
    return json.loads(string)


def image_size(val):
    curr = os.path.dirname(os.path.realpath(__file__))
    img = cv2.imread(curr+'/../../appstatic/photo/'+val, 0)
    if img is not None:
        height, width = img.shape[:2]
    else:
        height, width = 0, 0
    return json.dumps([width, height])


def random_char(y):
    return ''.join(random.choice(string.ascii_letters) for x in range(y))


class Struct:
    items = []

    def __init__(self, items=None):
        if items is None:
            items = []
        self.items = items
