import operator
import pandas as pd
from datetime import datetime, timedelta

from flask import Blueprint, render_template, url_for, make_response, current_app, request, send_from_directory

from app.models import User, Organisation

sitemaps = Blueprint('sitemaps', __name__)



#@sitemaps.route('/robots.txt')
##@sitemaps.route('/sitemap_main.xml')
##def static_from_root():
    ##return send_from_directory(app.static_folder, request.path[1:])

####uncomment to work on linux server
###@sitemaps.route('/robots.txt')
##@sitemaps.route('/<path:filename>')
##def static_from_root(filename):
    ##file = request.url.split("/")[-1]
    ##urlset = generate_sitemap(file)
    ##return return_xml('public/sitemap.html', urlset=urlset)

####uncomment to work on linux server
#def return_xml(view, **kwargs):
    #data = render_template(view, **kwargs)
    #response = make_response(data)
    #response.headers["Content-Type"] = "application/xml"
    #return response


##def generate_sitemap(link):
    ##file = link.split("/")[-1].split("\\")[-1].split(".")[0]
    ##filename = url_for('static', filename=file+'.txt')
    ## commented out while running on windows. Should change folder names
    ##df = pd.read_csv("/home/ec2-user/healthcareprofessionals/healthcareprofessionals/app/"+filename, sep="\n", header = None)
    ##urlset = []
    ##ten_days_ago = datetime.now() - timedelta(days=10)
    ##for route in range(0,len(df)):
       ##urlset.append({'loc': df[0][route],
                       ##'lastmod': '{}'.format(sitemap_date(ten_days_ago)),
                       ##'changefreq': 'daily'})
    ##return urlset

def routes():
    rules = []
    for rule in current_app.url_map.iter_rules():
        if "GET" in rule.methods and len(rule.arguments) == 0:
            methods = ','.join(sorted(rule.methods))
            rules.append((rule.endpoint, methods, str(rule)))

    sort_by_rule = operator.itemgetter(2)
    routes = []
    for endpoint, methods, rule in sorted(rules, key=sort_by_rule):
        if 'public.' in endpoint or 'seo' in endpoint:
            route = {'endpoint': endpoint, 'methods': methods, 'rule': rule}
            routes.append(route)
    return routes


def sitemap_date(val):
    return datetime.date(val)


@sitemaps.route('/sitemap.xml')
def index():
    sitemaps_list = [
        {'loc': url_for('sitemaps.main_xml', _external=True)},
        {'loc': url_for('sitemaps.companies_xml', _external=True)},
        {'loc': url_for('sitemaps.profiles_xml', _external=True)},
        {'loc':"https://mediville.com/sitemap_one_london.xml"},
        {'loc':"https://mediville.com/sitemap_one_dallas.xml"},
        {'loc':"https://mediville.com/sitemap_one_philadelphia.xml"},
        {'loc':"https://mediville.com/sitemap_one_houston.xml"},
        {'loc':"https://mediville.com/sitemap_one_chicago.xml"},
        {'loc':"https://mediville.com/sitemap_one_losangeles.xml"},
        {'loc':"https://mediville.com/sitemap_one_newyork.xml"},
        {'loc':"https://mediville.com/sitemap_practitioners_one_usa_cities.xml"}
    ]
    return return_xml('public/sitemapindex.html', sitemaps=sitemaps_list)


@sitemaps.route('/main.xml')
def main_xml():
    urlset = []
    ten_days_ago = datetime.now() - timedelta(days=10)
    for route in routes():
        urlset.append({'loc': url_for(route['endpoint'], _external=True),
                       'lastmod': '{}'.format(sitemap_date(ten_days_ago)),
                       'changefreq': 'daily'})
    return return_xml('public/sitemap.html', urlset=urlset)


@sitemaps.route('/companies.xml')
def companies_xml():
    urlset = []
    companies = Organisation.query.all()
    for company in companies:
        urlset.append({'loc': url_for('organisations.org_view', org_id=company.id, _external=True),
                       'lastmod': '{}'.format(sitemap_date(company.updated_at) if company.updated_at is not None else ''),
                       'changefreq': 'daily'})
    return return_xml('public/sitemap.html', urlset=urlset)


@sitemaps.route('/public_profiles.xml')
def profiles_xml():
    urlset = []
    users = User.query.all()
    for user in users:
        urlset.append({'loc': url_for('main.user_detail', user_id=user.id, _external=True),
                       'lastmod': '{}'.format(sitemap_date(user.updated_at) if user.updated_at is not None else ''),
                       'changefreq': 'daily'})
    return return_xml('public/sitemap.html', urlset=urlset)
