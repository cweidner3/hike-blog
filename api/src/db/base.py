'''
Provides the ORM model base class.
'''

import sqlalchemy.orm

class Mixin:
    ''' Model base mixin to provide method for serializing most models. '''
    @property
    def serialized(self) -> dict:
        ''' Convert instance to dict to allow for serialization into json string. '''
        it_ = self._sa_class_manager.keys()  # pylint: disable=protected-access
        it_ = map(lambda x: (x, getattr(self, x)), it_)
        return dict(it_)


Base = sqlalchemy.orm.declarative_base(cls=Mixin)
