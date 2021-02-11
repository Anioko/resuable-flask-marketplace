import json

from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required
from flask_rq import get_queue
from flask_uploads import UploadSet, IMAGES
from flask_wtf.file import FileAllowed
from wtforms import Flags

from app import db
from app.blueprints.admin.forms import BlogCategoryForm, BlogTagForm, BlogPostForm, BlogNewsLetterForm
from app.blueprints.admin.views import admin
from app.decorators import admin_required
from app.email import send_email
from app.models import User, Role, BlogCategory, BlogTag, BlogPost, current_user, BlogNewsLetter

images = UploadSet('images', IMAGES)


@admin.route('/blog', methods=['GET'])
@login_required
@admin_required
def blog_index():
    return render_template('admin/blog/index.html')


@admin.route('/blog/categories/<int:page>', methods=['GET'])
@admin.route('/blog/categories', defaults={'page': 1}, methods=['GET'])
@login_required
@admin_required
def blog_categories(page):
    categories = BlogCategory.query.order_by(BlogCategory.created_at.asc()).paginate(page, per_page=50)
    categories_count = BlogCategory.query.count()
    return render_template('admin/blog/categories/index.html', categories=categories, categories_count=categories_count)


@admin.route('/blog/categories/add', methods=['GET', 'POST'])
@login_required
@admin_required
def blog_category_create():
    form = BlogCategoryForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            cat = BlogCategory(
                name=form.name.data,
                is_featured=form.is_featured.data,
                order=form.order.data)
            db.session.add(cat)
            db.session.commit()
            flash('Category {} successfully created'.format(cat.name), 'success')
            return redirect(url_for('admin.blog_categories'))
    return render_template('admin/blog/categories/add-edit.html', form=form)


@admin.route('/blog/categories/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def blog_category_edit(category_id):
    category = BlogCategory.query.get_or_404(category_id)
    form = BlogCategoryForm(obj=category)
    if request.method == 'POST':
        if form.validate_on_submit():
            category.name = form.name.data
            category.is_featured = form.is_featured.data
            category.order = form.order.data
            db.session.add(category)
            db.session.commit()
            flash('Category {} successfully Updated'.format(category.name), 'success')
            return redirect(url_for('admin.blog_categories'))
    return render_template('admin/blog/categories/add-edit.html', form=form, category=category)


@admin.route('/blog/categories/<int:category_id>/_delete', methods=['POST'])
@login_required
@admin_required
def blog_category_delete(category_id):
    cat = BlogCategory.query.get_or_404(category_id)
    db.session.delete(cat)
    db.session.commit()
    flash('Successfully deleted Category.', 'success')
    return redirect(url_for('admin.blog_categories'))


@admin.route('/blog/tags/<int:page>', methods=['GET'])
@admin.route('/blog/tags', defaults={'page': 1}, methods=['GET'])
@login_required
@admin_required
def blog_tags(page):
    tags = BlogTag.query.order_by(BlogTag.created_at.asc()).paginate(page, per_page=50)
    tags_count = BlogTag.query.count()
    return render_template('admin/blog/tags/index.html', tags=tags, tags_count=tags_count)


@admin.route('/blog/tags/add', methods=['GET', 'POST'])
@login_required
@admin_required
def blog_tags_create():
    form = BlogTagForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            cat = BlogTag(
                name=form.name.data,
                )
            db.session.add(cat)
            db.session.commit()
            flash('Category {} successfully created'.format(cat.name), 'success')
            return redirect(url_for('admin.blog_tags'))
    return render_template('admin/blog/tags/add-edit.html', form=form)


@admin.route('/blog/tags/<int:tag_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def blog_tags_edit(tag_id):
    tag = BlogTag.query.get_or_404(tag_id)
    form = BlogTagForm(obj=tag)
    if request.method == 'POST':
        if form.validate_on_submit():
            tag.name = form.name.data
            db.session.add(tag)
            db.session.commit()
            flash('Category {} successfully Updated'.format(tag.name), 'success')
            return redirect(url_for('admin.blog_tags'))
    return render_template('admin/blog/tags/add-edit.html', form=form, tag=tag)


@admin.route('/blog/tags/<int:tag_id>/_delete', methods=['POST'])
@login_required
@admin_required
def blog_tag_delete(tag_id):
    cat = BlogTag.query.get_or_404(tag_id)
    db.session.delete(cat)
    db.session.commit()
    flash('Successfully deleted Blog Tag.', 'success')
    return redirect(url_for('admin.blog_tags'))


@admin.route('/blog/posts/<int:page>', methods=['GET'])
@admin.route('/blog/posts', defaults={'page': 1}, methods=['GET'])
@login_required
@admin_required
def blog_posts(page):
    posts = BlogPost.query.order_by(BlogPost.created_at.asc()).paginate(page, per_page=50)
    posts_count = BlogPost.query.count()
    return render_template('admin/blog/posts/index.html', posts=posts, posts_count=posts_count)


@admin.route('/blog/posts/add', methods=['GET', 'POST'])
@login_required
@admin_required
def blog_post_create():
    form = BlogPostForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            image_filename = ""
            if request.files['image']:
                image_filename = images.save(request.files['image'])
            cat = BlogPost(
                title=form.title.data,
                text=form.text.data,
                categories=form.categories.data,
                image=image_filename,
                creator=current_user,
                tags=form.tags.data)
            db.session.add(cat)
            db.session.commit()
            flash('Category {} successfully created'.format(cat.title), 'success')
            newsletter = form.newsletter.data
            all_users = form.all_users.data
            subs = []
            if newsletter:
                subs = db.session.query(BlogNewsLetter.email).all()
                subs = [sub[0] for sub in subs]

            users = []
            if all_users:
                users = db.session.query(User.email).all()
                users = [user[0] for user in users]
            all_emails = subs + users
            all_emails = list(set(all_emails))
            for e in all_emails:
                sent_to = User.query.filter_by(email=e).first()
                if sent_to:
                    sent_to = sent_to.id
                get_queue().enqueue(
                    send_email,
                    recipient=e,
                    subject='You may like this new update we have just posted on Mediville',
                    template='account/email/announcement',
                    user=current_user.id,
                    blog_post=cat.id,
                    sent_to=sent_to
                )
            return redirect(url_for('admin.blog_posts'))
    return render_template('admin/blog/posts/add-edit.html', form=form)


@admin.route('/blog/posts/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def blog_post_edit(post_id):
    post = BlogPost.query.get_or_404(post_id)
    form = BlogPostForm(obj=post)
    form.image.validators = [FileAllowed(images, 'Images only!')]
    form.image.flags = Flags()
    if request.method == 'POST':
        if form.validate_on_submit():
            post.title = form.title.data
            post.text = form.text.data
            post.categories = form.categories.data
            post.tags = form.tags.data
            db.session.add(post)
            db.session.commit()
            flash('Category {} successfully Updated'.format(post.title), 'success')
            return redirect(url_for('admin.blog_posts'))
    return render_template('admin/blog/posts/add-edit.html', form=form, post=post)


@admin.route('/blog/posts/<int:post_id>/_delete', methods=['POST'])
@login_required
@admin_required
def blog_post_delete(post_id):
    cat = BlogPost.query.get_or_404(post_id)
    db.session.delete(cat)
    db.session.commit()
    flash('Successfully deleted Blog Post.', 'success')
    return redirect(url_for('admin.blog_posts'))


@admin.route('/blog/subs/<int:page>', methods=['GET'])
@admin.route('/blog/subs', defaults={'page': 1}, methods=['GET'])
@login_required
@admin_required
def blog_subs(page):
    subs = BlogNewsLetter.query.order_by(BlogNewsLetter.created_at.asc()).paginate(page, per_page=50)
    subs_count = BlogNewsLetter.query.count()
    return render_template('admin/blog/subs/index.html', subs=subs, subs_count=subs_count)


@admin.route('/blog/subs/add', methods=['GET', 'POST'])
@login_required
@admin_required
def blog_subs_create():
    form = BlogNewsLetterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            sub = BlogNewsLetter(
                email=form.email.data,
                )
            db.session.add(sub)
            db.session.commit()
            flash('Subscription {} successfully added'.format(sub.email), 'success')
            return redirect(url_for('admin.blog_subs'))
    return render_template('admin/blog/subs/add-edit.html', form=form)


@admin.route('/blog/subs/<int:sub_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def blog_subs_edit(sub_id):
    sub = BlogNewsLetter.query.get_or_404(sub_id)
    form = BlogNewsLetterForm(obj=sub)
    if request.method == 'POST':
        if form.validate_on_submit():
            sub.email = form.email.data
            db.session.add(sub)
            db.session.commit()
            flash('Subscription {} successfully Updated'.format(sub.email), 'success')
            return redirect(url_for('admin.blog_subs'))
    return render_template('admin/blog/subs/add-edit.html', form=form, sub=sub)


@admin.route('/blog/subs/<int:sub_id>/_delete', methods=['POST'])
@login_required
@admin_required
def blog_sub_delete(sub_id):
    sub = BlogNewsLetter.query.get_or_404(sub_id)
    db.session.delete(sub)
    db.session.commit()
    flash('Successfully deleted Blog Newsletter Subscription.', 'success')
    return redirect(url_for('admin.blog_subs'))

