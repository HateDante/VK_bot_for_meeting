import os
import sqlalchemy as sq
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

load_dotenv()
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, unique=True)
    age = sq.Column(sq.Integer)
    gender = sq.Column(sq.Integer)
    city = sq.Column(sq.String)
    photos = relationship('Photo', back_populates='user')
    favorites = relationship('Favorite', back_populates='user')


class Photo(Base):
    __tablename__ = 'photos'
    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('users.user_id'))
    url = sq.Column(sq.String)
    likes = sq.Column(sq.Integer)
    user = relationship('User', back_populates='photos')


class Favorite(Base):
    __tablename__ = 'favorites'
    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('users.user_id'))
    favorite_user_id = sq.Column(sq.Integer)
    user = relationship('User', back_populates='favorites')


class Blacklist(Base):
    __tablename__ = 'blacklist'
    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('users.user_id'))
    blacklisted_user_id = sq.Column(sq.Integer)


def create_session():
    dsn = os.getenv('DATABASE_URL')
    engine = create_engine(dsn)
    session = sessionmaker(bind=engine)
    return session()


def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def add_user(session, user_id, user_params):
    existing_user = session.query(User).filter_by(user_id=user_id).first()
    if existing_user is None:
        new_user = User(user_id=user_id, age=user_params['age_from'], gender=user_params['sex'],
                        city=user_params['city'])
        session.add(new_user)
        try:
            session.commit()
            return new_user.user_id
        except Exception as e:
            session.rollback()
            print(f'Ошибка при добавлении пользователя: {e}')
            raise e
    else:
        return existing_user.user_id


def add_favorite_user(session, user_id, favorite_user_id):
    favorite = Favorite(user_id=user_id, favorite_user_id=favorite_user_id)
    session.add(favorite)

    try:
        session.commit()
    except Exception as e:
        session.rollback()
        print(f'Ошибка при добавлении пользователя в избранное: {e}')
        raise e


def add_photos(session, user_id, photo_urls):
    for url in photo_urls:
        photo = Photo(user_id=user_id, url=url)
        session.add(photo)
    session.commit()


def get_favorites(session, user_id):
    favorites = session.query(Favorite).filter_by(user_id=user_id).all()
    return favorites


def add_to_blacklist(session, user_id, blacklisted_user_id):
    blacklist = Blacklist(user_id=user_id, blacklisted_user_id=blacklisted_user_id)
    session.add(blacklist)
    session.commit()


if __name__ == "__main__":
    DSN = os.getenv('DATABASE_URL')
    engine = create_engine(DSN)
    create_tables(engine)
    session = create_session()
    session.close()
