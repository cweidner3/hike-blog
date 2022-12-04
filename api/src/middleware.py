'''
Functions that can be added to the start of blueprints to control the ingest of a route.
'''

from flask import request, g
import werkzeug.exceptions
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.core import engine
from src.db.models import ApiSession


def auth_user():
    ''' Authenticate session and set the global user field. '''
    api_key = ''
    if request.headers.has_key('Api-Session'):
        api_key = request.headers['Api-Session']
    elif 'Api-Session' in request.cookies:
        api_key = request.cookies['Api-Session']
    else:
        return
    with Session(engine) as session:
        ret = session.execute(
            select(ApiSession)
            .where(ApiSession.key == api_key)
        ).scalar_one_or_none()
        if ret is None:
            return
        g.user = ret


def auth_as_admin():
    ''' Authenticate session, assert that user is admin, then set user field. '''
    api_key = ''
    if 'Api-Session' in request.headers:
        api_key = request.headers['Api-Session']
    elif 'Api-Session' in request.cookies:
        api_key = request.cookies['Api-Session']
    else:
        raise werkzeug.exceptions.Unauthorized()
    with Session(engine) as session:
        ret = session.execute(
            select(ApiSession)
            .where(ApiSession.key == api_key)
        ).scalar_one_or_none()
        if ret is None:
            raise werkzeug.exceptions.Unauthorized()
        if not ret.admin:
            raise werkzeug.exceptions.Unauthorized()
        g.user = ret
