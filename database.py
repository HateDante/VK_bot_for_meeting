import os
import sqlalchemy as sq
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()
load_dotenv()


class User(Base):
    __tablename__ = 'users'
    id = sq.Column(sq.Integer, primary_key=True)
    age = sq.Column(sq.Integer)
    gender = sq.Column(sq.String)
    city = sq.Column(sq.String)
    photos = relationship('Photo', back_populates='user')


class Photo(Base):
    __tablename__ = 'photos'
    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('users.id'))
    url = sq.Column(sq.String)
    likes = sq.Column(sq.Integer)
    user = relationship('User', back_populates='photos')


class Favorite(Base):
    __tablename__ = 'favorites'
    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('users.id'))
    favorite_user_id = sq.Column(sq.Integer, sq.ForeignKey('users.id'))


class Blacklist(Base):
    __tablename__ = 'blacklist'
    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('users.id'))
    blacklisted_user_id = sq.Column(sq.Integer, sq.ForeignKey('users.id'))


def create_session():
    DSN = os.getenv('DATABASE_URL')
    engine = create_engine(DSN)
    Session = sessionmaker(bind=engine)
    return Session()


# Создание таблиц в базе данных
def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def add_to_favorites(session, user_id, favorite_user_id):
    """Добавление пользователя в избранное."""
    favorite = Favorite(user_id=user_id, favorite_user_id=favorite_user_id)
    session.add(favorite)
    session.commit()


def add_to_blacklist(session, user_id, blacklisted_user_id):
    """Добавление пользователя в черный список."""
    blacklist = Blacklist(user_id=user_id, blacklisted_user_id=blacklisted_user_id)
    session.add(blacklist)
    session.commit()


def add_photos(session, user_id, photo_urls):
    """Добавление фотографии пользователя."""
    for url in photo_urls:
        photo = Photo(user_id=user_id, url=url)
        session.add(photo)
    session.commit()


if __name__ == "__main__":
    DSN = os.getenv('DATABASE_URL')
    engine = create_engine(DSN)
    create_tables(engine)
    session = create_session()
    session.close()
