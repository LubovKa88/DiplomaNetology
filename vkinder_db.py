import sqlalchemy as sq

from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import Session
from config import db_url_object

metadata = MetaData()
Base = declarative_base()
engine = create_engine(db_url_object)


class Viewed(Base):
    __tablename__ = 'viewed_vkinder_users'
    user_id = sq.Column(sq.Integer, primary_key=True)
    searched_profile_id = sq.Column(sq.Integer, primary_key=True)


def add_user(engine, user_id, searched_profile_id):
    with Session(engine) as session:
        to_bd = Viewed(user_id=user_id, searched_profile_id=searched_profile_id)
        session.add(to_bd)
        session.commit()


def check_user(engine, user_id, searched_profile_id):
    with Session(engine) as session:
        from_bd = session.query(Viewed).filter(
            Viewed.user_id == user_id,
            Viewed.searched_profile_id == searched_profile_id
        ).first()
        return True if from_bd else False


if __name__ == '__main__':
    engine = create_engine(db_url_object)
    Base.metadata.create_all(engine)

    # add_user(engine, 2113, 124512)
    # res = check_user(engine, 2113, 1245121)
    # print(res)