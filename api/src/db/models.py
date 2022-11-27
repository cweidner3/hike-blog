from sqlalchemy import Column, Integer, Text, Date

from src.db.base import Base


class Hike(Base):
    __tablename__ = 'hikes'

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    start = Column(Date)
    end = Column(Date)
