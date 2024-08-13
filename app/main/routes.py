from datetime import datetime, timezone
from flask import render_template, flash, redirect, url_for, request, g, \
    current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
import sqlalchemy as sa
from langdetect import detect, LangDetectException
from app import db, Config
from app.main.forms import EditProfileForm, EmptyForm, ContactForm
from app.models import Notification, Plan, Domain, Customer, Activity
from flask import jsonify
from app.translate import translate
from app.main import bp
from app import create_app, db
from app.email import send_email
from app.utils.wordpress_helpers import wp_domain,pages


### write a seperate route for home page
@bp.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home/index.html', title=_('Home'))

@bp.route('/products', methods=['GET'])
def products():
    return render_template('home/products.html', title=_('Products'))

@bp.route('/aboutus', methods=['GET'])
def aboutus():
    return render_template('home/page-about-us.html', title=_('About Us'))

@bp.route('/contactus', methods=['GET', 'POST'])
def contactus():
    form = ContactForm()
    if form.validate_on_submit():
        send_email(
            'You got a msg',
            sender= Config.ADMINS[0], recipients=['info@company.com'],
            text_body=render_template('email/contactus.txt', email=form.email.data, 
                                      msg=form.msg.data),
            html_body=render_template('email/export_posts.html', user=Customer),
            sync=True)
    return render_template('home/page-contact-us.html', title=_('Contact Us'), form=form, 
                           msg='Thank you for contacting us! you should hear from us soon')



@bp.route('/explore')
@login_required
def explore():
    return render_template('old_layout/index.html', title=_('Explore'))


@bp.route('/customer/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(Customer).where(Customer.username == username))
    form = EmptyForm()
    return render_template('old_layout/user.html', user=user, form=form)


@bp.route('/customer/<username>/popup')
@login_required
def user_popup(username):
    user = db.first_or_404(sa.select(Customer).where(Customer.username == username))
    form = EmptyForm()
    return render_template('old_layout/user_popup.html', user=Customer, form=form)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.customer_email = form.email.data
        current_user.customer_phone = form.phone.data
        if form.New_password.data != "":
            current_user.set_password(form.New_password.data)
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.customer_email
        form.phone.data = current_user.customer_phone
    return render_template('old_layout/edit_profile.html', title=_('Edit Profile'),
                           form=form)


@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        # Handle Plan Update
        if 'plan' in request.form:
            current_user.plan_id = request.form['plan']
            db.session.commit()
            flash('Your plan has been updated successfully!', 'success')
            return redirect(url_for('main.settings'))
    
    # Render the settings page
    domains =  Domain.query.filter_by(customer_id = current_user.id).all()
    plan = Plan.query.filter_by(id=current_user.plan_id).first()
    return render_template('home/settings.html', current_plan=plan, domains=domains)


@bp.route('/update-plan', methods=['POST'])
@login_required
def update_plan():
    new_plan_id = request.form['plan']
    current_user.plan_id = new_plan_id
    db.session.commit()
    flash('Plan updated successfully!', 'success')
    return redirect(url_for('main.settings'))


@bp.route('/cancel-plan', methods=['POST'])
@login_required
def cancel_plan():
    current_user.plan_id = 1  # Or you can set it to a default plan
    db.session.commit()
    flash('Your plan has been canceled.', 'info')
    return redirect(url_for('main.settings'))


@bp.route('/add-domain', methods=['POST'])
@login_required
def add_domain():
    domain_name = request.form['domain']
    platform = request.form['domain_platform']
    username = request.form['domain_username']
    password = request.form['domain_password']

    if Domain.query.filter_by(domain_name=domain_name, customer_id=current_user.id).first():
        flash('This domain is already registered.', 'warning')
    else:
        if current_user.add_domain(name=domain_name, platform=platform, user_name=username, 
                                   password=password):
            db.session.commit()
            flash('Domain added successfully!', 'success')
        else:
            flash('Domain plan limit exceeded!', 'danger')
    return redirect(url_for('main.settings'))


@bp.route('/edit-domain/<int:domain_id>', methods=['POST'])
@login_required
def edit_domain(domain_id):
    domain = Domain.query.get_or_404(domain_id)
    name = request.form['domain_name']
    platform = request.form['domain_platform']
    username = request.form['domain_username']
    password = request.form['domain_password']
    if domain.customer_id != current_user.id:
        flash('You do not have permission to edit this domain.', 'danger')
        return redirect(url_for('main.settings'))
    
    domain.domain_name=name
    domain.domain_platform=platform
    domain.domain_login_username=username 
    domain.domain_login_password=password

    db.session.commit()
    flash('Domain edited successfully.', 'success')
    return redirect(url_for('main.settings'))



@bp.route('/delete-domain/<int:domain_id>', methods=['POST'])
@login_required
def delete_domain(domain_id):
    domain = Domain.query.get_or_404(domain_id)
    if domain.customer_id != current_user.id:
        flash('You do not have permission to delete this domain.', 'danger')
        return redirect(url_for('main.settings'))
    
    db.session.delete(domain)
    new_domain_count = current_user.domain_count - 1
    current_user.domain_count = new_domain_count
    db.session.commit()
    flash('Domain deleted successfully.', 'success')
    return redirect(url_for('main.settings'))


@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    data = request.get_json()
    return {'text': translate(data['text'],
                              data['source_language'],
                              data['dest_language'])}



@bp.route('/export_posts')
@login_required
def export_posts():
    if current_user.get_task_in_progress('export_posts'):
        flash(_('An export task is currently in progress'))
    else:
        current_user.launch_task('export_posts', _('Exporting posts...'))
        db.session.commit()
    return redirect(url_for('main.user', username=current_user.username))


@bp.route('/notifications')
@login_required
def notifications():
    since = request.args.get('since', 0.0, type=float)
    query = current_user.notifications.select().where(
        Notification.timestamp > since).order_by(Notification.timestamp.asc())
    notifications = db.session.scalars(query)
    return [{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notifications]



@bp.route('/domain')
@login_required
def index():
    domains =  Domain.query.filter_by(customer_id = current_user.id).all()
    return render_template('old_layout/pages.html', domains=domains)

@bp.route('/get_pages/<int:domain_id>')
def get_pages(domain_id):
    dm =  Domain.query.filter_by(id = domain_id).first()
    domain = wp_domain(dm)
    pages_list = domain.get_all_wordpress_pages()
    return jsonify(pages_list)


@bp.route('/get_posts/<int:domain_id>')
def get_posts(domain_id):
    dm =  Domain.query.filter_by(id = domain_id).first()
    domain = wp_domain(dm)
    posts_list = domain.get_all_wordpress_posts()
    return jsonify(posts_list)