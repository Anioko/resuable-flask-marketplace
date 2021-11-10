from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user
from app.models import EditableHTML, BackgroundImage, ContactMessage, LandingSetting, OurBrand, User, MCategory, MProduct, MSettings, MBrand, MBanner, SiteLogo, BackgroundImage, MCurrency, SeoItems, SeoLocations
from app.blueprints.marketplace.forms import SearchForm

seo_world = Blueprint('seo_world', __name__)

ROWS_PER_PAGE = 5


@seo_world.route('/<keywordone>-<keywordtwo>-<location>')
@seo_world.route('/<keywordone>-<keywordtwo>-in-<location>')
def data_location(keywordone, keywordtwo, location):
    form = SearchForm()
    banner = MBanner.query.first()
    background = BackgroundImage.query.first()
    logo = SiteLogo.query.first()
    settings = LandingSetting.query.first()
    website_settings = MSettings.query.first()
    brands = MBrand.query.order_by(MBrand.created_at.asc()).limit(5).all()
    featured_products = MProduct.query.filter_by(availability=True).filter_by(
        is_featured=True).order_by(MProduct.created_at.asc()).limit(4).all()  # .limit(5).all()
    new_arrived_products = MProduct.query.filter_by(
        availability=True).order_by(MProduct.created_at.desc()).limit(4).all()
    featured_categories = MCategory.query.filter_by(is_featured=True).all()
    categories = MCategory.query.limit(6).all()

    products_count = MProduct.query.count()
    page = request.args.get('page', 1, type=int)
    products = MProduct.query.paginate(page, per_page=ROWS_PER_PAGE)

    query = request.args.get('query')
    page = request.args.get('page')
    search_type = request.args.get('type')
    sort_by = request.args.get('sort_by')
    sort_dir = request.args.get('sort_dir')


    query = query if query is not None else ''
    page = page if page is not None else 1
    try:
        page = int(page)
    except:
        page = 1
    search_type = search_type if search_type is not None else ''
    sort_by = sort_by if sort_by is not None else ''
    sort_dir = sort_dir if sort_dir is not None else ''
    if len(query) < 3:
        flash("Search Query must be at least 3 characters", "error")
        return render_template('seo/seo_search_results.html', keywordone=keywordone, keywordtwo=keywordtwo, location=location, form=form,
                           featured_categories=featured_categories, categories=categories, featured_products=featured_products,
                           new_arrived_products=new_arrived_products, settings=settings, website_settings=website_settings, brands=brands,
                           banner=banner,
                           logo=logo, products=products, background=background, products_count=products_count,
                           query=query, search_type=search_type, sort_by=sort_by,
                           sort_dir=sort_dir, results=[])
    results = []
    if search_type == '':
##        job_results = Job.query.whooshee_search(query, order_by_relevance=0).all()
##        user_results = User.query.whooshee_search(query, order_by_relevance=0).all()
##        questions_results = Question.query.whooshee_search(query, order_by_relevance=0).all()
        products_results = MProduct.query.whooshee_search(query).all()
        categories_results = MCategory.query.whooshee_search(query).all()
        organizations_results = Organisation.query.whooshee_search(query).all()

##        job_results_count = Job.query.whooshee_search(query, order_by_relevance=0).count()
##        user_results_count = User.query.whooshee_search(query, order_by_relevance=0).count()
##        questions_results_count = Question.query.whooshee_search(query, order_by_relevance=0).count()
        products_results_count = MProduct.query.whooshee_search(query, order_by_relevance=0).count()
        categories_results_count = MCategory.query.whooshee_search(query, order_by_relevance=0).count()
        organizations_results_count = Organisation.query.whooshee_search(query, order_by_relevance=0).count()
        
##        all_results = job_results + user_results + questions_results + products_results
##        all_count = job_results_count + user_results_count + questions_results_count + products_results_count
        all_results = products_results + categories_results_count + organizations_results_count
        all_count = products_results_count + categories_results + organizations_results
        results = sorted(all_results, key=operator.attrgetter("score"))
        results.reverse()
        results = results[(page-1)*8:page*8]
        paginator = Pagination(items=results, page=page, per_page=8, query=None, total=all_count)
        results = paginator

##    elif search_type == 'people':
##        results = User.query.whooshee_search(query, order_by_relevance=-1).paginate(page, per_page=40)
##        # results = sorted(user_results, key=operator.attrgetter("score"))
##    elif search_type == 'jobs':
##        results = Job.query.whooshee_search(query, order_by_relevance=-1).paginate(page, per_page=40)
##        # results = sorted(job_results, key=operator.attrgetter("score"))
##    elif search_type == 'questions':
##        results = Question.query.whooshee_search(query, order_by_relevance=-1).paginate(page, per_page=40)
##        # results = sorted(questions_results, key=operator.attrgetter("score"))
    elif search_type == 'products':
        results = MProduct.query.whooshee_search(query, order_by_relevance=10).paginate(page, per_page=8)
    elif search_type == 'categories':
        results = MCategory.query.whooshee_search(query, order_by_relevance=10).paginate(page, per_page=8)
    elif search_type == 'organizations':
        results = Organisation.query.whooshee_search(query, order_by_relevance=10).paginate(page, per_page=8)

    return render_template('seo/seo_search_results.html', keywordone=keywordone, keywordtwo=keywordtwo, location=location, form=form,
                           featured_categories=featured_categories, categories=categories, featured_products=featured_products,
                           new_arrived_products=new_arrived_products, settings=settings, website_settings=website_settings, brands=brands,
                           banner=banner,
                           logo=logo, products=products, background=background, products_count=products_count,
                           query=query, search_type=search_type, sort_by=sort_by,
                           sort_dir=sort_dir, results=results)





@seo_world.route('/product/category/<location>', methods=['GET'], defaults={"page": 1})
@seo_world.route('/product/category/<location>/<int:page>', methods=['GET'])
def product_category_location(page, location):
    form = SearchForm()
    banner = MBanner.query.first()
    background = BackgroundImage.query.first()
    logo = SiteLogo.query.first()
    settings = LandingSetting.query.first()
    website_settings = MSettings.query.first()
    brands = MBrand.query.order_by(MBrand.created_at.asc()).limit(5).all()
    featured_products = MProduct.query.filter_by(availability=True).filter_by(
        is_featured=True).order_by(MProduct.created_at.asc()).limit(4).all()  # .limit(5).all()
    new_arrived_products = MProduct.query.filter_by(
        availability=True).order_by(MProduct.created_at.desc()).limit(4).all()
    featured_categories = MCategory.query.filter_by(is_featured=True).all()
    categories = MCategory.query.limit(6).all()
    #products = MProduct.query.limit(6).all()
    seo_locations = SeoLocations.query.all()

    #products_count = MProduct.query.count()
    page = page
    location=location
    iterable_items = SeoItems.query.all()
    seo_items = SeoItems.query.paginate(page, per_page=20)
    return render_template('seo/list_of_products_by_categories_by_location.html', form=form, location=location, featured_categories=featured_categories, categories=categories, featured_products=featured_products,
                           new_arrived_products=new_arrived_products, settings=settings, website_settings=website_settings, brands=brands, banner=banner,
                           logo=logo, background=background, seo_items=seo_items, iterable_items = iterable_items, seo_locations=seo_locations)#, product_pagination=product_pagination)




@seo_world.route('/sitemap', methods=['GET'], defaults={"page": 1})
@seo_world.route('/locations', methods=['GET'], defaults={"page": 1})
@seo_world.route('/sitemap/<int:page>', methods=['GET'])
def locations(page):
    form = SearchForm()
    banner = MBanner.query.first()
    background = BackgroundImage.query.first()
    logo = SiteLogo.query.first()
    settings = LandingSetting.query.first()
    website_settings = MSettings.query.first()
    brands = MBrand.query.order_by(MBrand.created_at.asc()).limit(5).all()
    featured_products = MProduct.query.filter_by(availability=True).filter_by(
        is_featured=True).order_by(MProduct.created_at.asc()).limit(4).all()  # .limit(5).all()
    new_arrived_products = MProduct.query.filter_by(
        availability=True).order_by(MProduct.created_at.desc()).limit(4).all()
    featured_categories = MCategory.query.filter_by(is_featured=True).all()
    categories = MCategory.query.limit(6).all()
    #products = MProduct.query.limit(6).all()
    seo_locations = SeoLocations.query.paginate(page, per_page=8)

    #products_count = MProduct.query.count()
    page = page
    iterable_items = SeoItems.query.all()
    seo_items = SeoItems.query.paginate(page, per_page=8)
    return render_template('seo/index.html', form=form, featured_categories=featured_categories, categories=categories, featured_products=featured_products,
                           new_arrived_products=new_arrived_products, settings=settings, website_settings=website_settings, brands=brands, banner=banner,
                           logo=logo, background=background, seo_items=seo_items, iterable_items = iterable_items, seo_locations=seo_locations)#, product_pagination=product_pagination)



@seo_world.route('/<keywordone>-<keywordtwo>-<location>')
@seo_world.route('/<keywordone>-<keywordtwo>-in-<location>', methods=('GET', 'POST'))
def seo_search_results(keywordone, keywordtwo, location):
    form = SearchForm()
    banner = MBanner.query.first()
    background = BackgroundImage.query.first()
    logo = SiteLogo.query.first()
    settings = LandingSetting.query.first()
    website_settings = MSettings.query.first()
    brands = MBrand.query.order_by(MBrand.created_at.asc()).limit(5).all()
    featured_products = MProduct.query.filter_by(availability=True).filter_by(
        is_featured=True).order_by(MProduct.created_at.asc()).limit(4).all()  # .limit(5).all()
    new_arrived_products = MProduct.query.filter_by(
        availability=True).order_by(MProduct.created_at.desc()).limit(4).all()
    featured_categories = MCategory.query.filter_by(is_featured=True).all()
    categories = MCategory.query.limit(6).all()

    products_count = MProduct.query.count()
    page = request.args.get('page', 1, type=int)
    products = MProduct.query.paginate(page, per_page=ROWS_PER_PAGE)

    query = request.args.get('query')
    page = request.args.get('page')
    search_type = request.args.get('type')
    sort_by = request.args.get('sort_by')
    sort_dir = request.args.get('sort_dir')


    query = query if query is not None else ''
    page = page if page is not None else 1
    try:
        page = int(page)
    except:
        page = 1
    search_type = search_type if search_type is not None else ''
    sort_by = sort_by if sort_by is not None else ''
    sort_dir = sort_dir if sort_dir is not None else ''
    if len(query) < 3:
        flash("Search Query must be at least 3 characters", "error")
        return render_template('seo/seo_search_results.html', keywordone=keywordone, keywordtwo=keywordtwo, location=location, form=form,
                           featured_categories=featured_categories, categories=categories, featured_products=featured_products,
                           new_arrived_products=new_arrived_products, settings=settings, website_settings=website_settings, brands=brands,
                           banner=banner,
                           logo=logo, products=products, background=background, products_count=products_count,
                           query=query, search_type=search_type, sort_by=sort_by,
                           sort_dir=sort_dir, results=[])
    results = []
    if search_type == '':
##        job_results = Job.query.whooshee_search(query, order_by_relevance=0).all()
##        user_results = User.query.whooshee_search(query, order_by_relevance=0).all()
##        questions_results = Question.query.whooshee_search(query, order_by_relevance=0).all()
        products_results = MProduct.query.whooshee_search(query).all()
        categories_results = MCategory.query.whooshee_search(query).all()
        organizations_results = Organisation.query.whooshee_search(query).all()

##        job_results_count = Job.query.whooshee_search(query, order_by_relevance=0).count()
##        user_results_count = User.query.whooshee_search(query, order_by_relevance=0).count()
##        questions_results_count = Question.query.whooshee_search(query, order_by_relevance=0).count()
        products_results_count = MProduct.query.whooshee_search(query, order_by_relevance=0).count()
        categories_results_count = MCategory.query.whooshee_search(query, order_by_relevance=0).count()
        organizations_results_count = Organisation.query.whooshee_search(query, order_by_relevance=0).count()
        
##        all_results = job_results + user_results + questions_results + products_results
##        all_count = job_results_count + user_results_count + questions_results_count + products_results_count
        all_results = products_results + categories_results_count + organizations_results_count
        all_count = products_results_count + categories_results + organizations_results
        results = sorted(all_results, key=operator.attrgetter("score"))
        results.reverse()
        results = results[(page-1)*8:page*8]
        paginator = Pagination(items=results, page=page, per_page=8, query=None, total=all_count)
        results = paginator

##    elif search_type == 'people':
##        results = User.query.whooshee_search(query, order_by_relevance=-1).paginate(page, per_page=40)
##        # results = sorted(user_results, key=operator.attrgetter("score"))
##    elif search_type == 'jobs':
##        results = Job.query.whooshee_search(query, order_by_relevance=-1).paginate(page, per_page=40)
##        # results = sorted(job_results, key=operator.attrgetter("score"))
##    elif search_type == 'questions':
##        results = Question.query.whooshee_search(query, order_by_relevance=-1).paginate(page, per_page=40)
##        # results = sorted(questions_results, key=operator.attrgetter("score"))
    elif search_type == 'products':
        results = MProduct.query.whooshee_search(query, order_by_relevance=10).paginate(page, per_page=8)
    elif search_type == 'categories':
        results = MCategory.query.whooshee_search(query, order_by_relevance=10).paginate(page, per_page=8)
    elif search_type == 'organizations':
        results = Organisation.query.whooshee_search(query, order_by_relevance=10).paginate(page, per_page=8)

    return render_template('seo/seo_search_results.html', keywordone=keywordone, keywordtwo=keywordtwo, location=location, form=form,
                           featured_categories=featured_categories, categories=categories, featured_products=featured_products,
                           new_arrived_products=new_arrived_products, settings=settings, website_settings=website_settings, brands=brands,
                           banner=banner,
                           logo=logo, products=products, background=background, products_count=products_count,
                           query=query, search_type=search_type, sort_by=sort_by,
                           sort_dir=sort_dir, results=results)
#, product_pagination=product_pagination)
