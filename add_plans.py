import sqlalchemy as sa
import sqlalchemy.orm as so
from app import create_app, db
from app.models import Customer, Plan, Domain, Notification, Task

app = create_app()

def add_palns():
    app.app_context().push()
    plans = [{'id': 1, 'plan_duration': 2592000, 'plan_domain_limit': 1, 
              'plan_api_limits': 20,  'plan_name': 'Free', 'plan_type':'Monthly'},
              {'id': 2, 'plan_duration': 2592000, 'plan_domain_limit': 1, 
              'plan_api_limits': 100,  'plan_name': 'Bronze', 'plan_type':'Monthly'},
              {'id': 3, 'plan_duration': 2592000, 'plan_domain_limit': 20, 
              'plan_api_limits': 500,  'plan_name': 'Gold', 'plan_type':'Monthly'},
              {'id': 4, 'plan_duration': 2592000, 'plan_domain_limit': 50, 
              'plan_api_limits': 500,  'plan_name': 'Diamond', 'plan_type':'Monthly'},
              {'id': 5, 'plan_duration': 2592000, 'plan_domain_limit': 1, 
              'plan_api_limits': 20,  'plan_name': 'Free', 'plan_type':'Yearly'},
              {'id': 6, 'plan_duration': 2592000, 'plan_domain_limit': 1, 
              'plan_api_limits': 100,  'plan_name': 'Bronze', 'plan_type':'Yearly'},
              {'id': 7, 'plan_duration': 2592000, 'plan_domain_limit': 20, 
              'plan_api_limits': 500,  'plan_name': 'Gold', 'plan_type':'Yearly'},
              {'id': 8, 'plan_duration': 2592000, 'plan_domain_limit': 50, 
              'plan_api_limits': 500,  'plan_name': 'Diamond', 'plan_type':'Yearly'}]
    for plan in plans:
        pl = Plan(id=plan['id'], plan_duration=plan['plan_duration'],  
                  plan_name=plan['plan_name'], plan_domain_limit=plan['plan_domain_limit'], 
                  plan_api_call_limit=plan['plan_api_limits'],  plan_type=plan['plan_type'])
        db.session.add(pl)
    db.session.commit()
    print("plans added")

add_palns()