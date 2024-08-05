from datetime import datetime, timezone, timedelta
from hashlib import md5
import json
import secrets
from time import time
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask import current_app, url_for
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import redis
import rq
from app import db, login


class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = db.paginate(query, page=page, per_page=per_page,
                                error_out=False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page,
                                **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page,
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources.has_prev else None
            }
        }
        return data


class Plan(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    plan_duration: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer)
    plan_domain_limit: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer)
    plan_api_call_limit: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer)
    plan_name: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
                                             unique=True)
    plan_type: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
                                             unique=True)
    def __repr__(self):
        return '<Plan {}>'.format(self.body)

    

class Customer(PaginatedAPIMixin, UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)
    customer_full_name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)
    customer_company_name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)
    customer_email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
                                             unique=True)
    customer_phone: so.Mapped[Optional[str]] = so.mapped_column(sa.String(120), index=True,
                                             unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))  
    token: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(32), index=True, unique=True)
    token_expiration: so.Mapped[Optional[datetime]]
    plan_id: so.Mapped[Optional[int]] = so.mapped_column(sa.ForeignKey(Plan.id),
                                               index=True)
    domain_count: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer)
    domains: so.WriteOnlyMapped['Domain'] = so.relationship(
        back_populates='owner')
    activites: so.WriteOnlyMapped['Activity'] = so.relationship(
        back_populates='activity_owner')
    api_call_count: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer)
    notifications: so.WriteOnlyMapped['Notification'] = so.relationship(
        back_populates='customer')
    tasks: so.WriteOnlyMapped['Task'] = so.relationship(back_populates='customer')
    wordpress_auth: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    def __repr__(self):
        return '<Customer {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')
    
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except Exception:
            return
        return db.session.get(Customer, id)
    
    
    def launch_task(self, name, description, *args, **kwargs):
        rq_job = current_app.task_queue.enqueue(f'app.tasks.{name}', self.id,
                                                *args, **kwargs)
        task = Task(id=rq_job.get_id(), name=name, description=description,
                    user=self)
        db.session.add(task)
        return task
    

    def get_tasks_in_progress(self):
        query = self.tasks.select().where(Task.complete == False)
        return db.session.scalars(query)
    

    def get_task_in_progress(self, name):
        query = self.tasks.select().where(Task.name == name,
                                          Task.complete == False)
        return db.session.scalar(query)
    

    def add_notification(self, name, data):
        db.session.execute(self.notifications.delete().where(
            Notification.name == name))
        n = Notification(name=name, payload_json=json.dumps(data), user=self)
        db.session.add(n)
        return n
    

    def to_dict(self, include_email=False):
        data = {
            'id': self.id,
            'username': self.username,
            'customer_first_name': self.customer_full_name,
            'customer_last_name': self.customer_company_name,
            'plan': "place_holder", #should update this after api
            'domain_count': self.domain_count,
            'api_call_count':  self.api_call_count,
            'api_call_limit': 'place_holder' #should update this after api
        }

        if include_email:
            data['customer_email'] = self.email
        return data

    def from_dict(self, data, new_user=False):
        for field in ['username', 'email']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])

    
    def update_api_count(self, api_count):
        plan = db.session.scalar(
            sa.select(Plan).where(Plan.id == self.plan_id))
        api_limit = plan.plan_api_call_limit
        if self.api_call_count + api_count > api_limit:
            return 404
        else:
            self.api_call_count = self.api_call_count + api_count
            return True
    

    def add_domain(self, name):
        plan = db.session.scalar(
            sa.select(Plan).where(Plan.id == self.plan_id))
        domain_limit = plan.plan_domain_limit
        if self.domain_count + 1 > domain_limit:
            return 404
        else:
            domain = db.session.scalar(
            sa.select(Domain).where(Domain.domain_name == name))
            if domain is not None:
                return 505
            domain = Domain(domain_name=name, domain_start_date=datetime.now(timezone.utc), 
                             customer_id=self.id, owner=Customer)
            self.domain_count = self.domain_count + 1
            return True
    

    def delete_api_count(self, api_count):
        self.api_call_count = self.api_call_count - api_count
        return True
    

    def set_wordpress_auth(self, wordpress_password):
        self.wordpress_auth = wordpress_password
        return True

class Domain(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    domain_name: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
                                             unique=True)
    domain_start_date: so.Mapped[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc))
    customer_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Customer.id),
                                               index=True)
    owner: so.Mapped[Customer] = so.relationship(back_populates='domains')

    def __repr__(self):
        return '<Domain {}>'.format(self.body)



class Activity(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    activity_name: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
                                             unique=True)
    activity_msg: so.Mapped[str] = so.mapped_column(sa.String(150), index=True,
                                             unique=True)
    activity_timestamp: so.Mapped[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc))
    domain_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Domain.id),
                                               index=True)
    activity_owner: so.Mapped[Customer] = so.relationship(back_populates='activites')
    customer_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Customer.id),
                                               index=True)
    def __repr__(self):
        return '<Activity {}>'.format(self.body)


@login.user_loader
def load_customer(id):
    return db.session.get(Customer, int(id))


class Notification(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(128), index=True)
    customer_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Customer.id),
                                               index=True)
    timestamp: so.Mapped[float] = so.mapped_column(index=True, default=time)
    payload_json: so.Mapped[str] = so.mapped_column(sa.Text)

    customer: so.Mapped[Customer] = so.relationship(back_populates='notifications')

    def get_data(self):
        return json.loads(str(self.payload_json))


class Task(db.Model):
    id: so.Mapped[str] = so.mapped_column(sa.String(36), primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(128), index=True)
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    customer_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Customer.id))
    complete: so.Mapped[bool] = so.mapped_column(default=False)

    customer: so.Mapped[Customer] = so.relationship(back_populates='tasks')

    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100
