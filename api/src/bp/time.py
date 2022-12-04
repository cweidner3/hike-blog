import flask
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models import Timezone
from src.db.core import engine

bp_time = flask.Blueprint('time', __name__, url_prefix='/timezones')

@bp_time.get('')
def list_timezones():
    with Session(engine) as session:
        ret = session.execute(
            select(Timezone.name)
        ).all()
        ret = map(lambda x: x[0], ret)
        ret = list(ret)
        return {'timezones': ret}
