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
from app.translate import translate
from app.main import bp
from app import create_app, db
from app.email import send_email


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
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.customer_email
        form.phone.data = current_user.customer_phone
    return render_template('old_layout/edit_profile.html', title=_('Edit Profile'),
                           form=form)



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
