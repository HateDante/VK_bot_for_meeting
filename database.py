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
    age = sq.Column(sq.Integer)
    gender = sq.Column(sq.String)
    city = sq.Column(sq.String)
    photos = relationship('Photo', back_populates='user')
    favorites = relationship('Favorite', foreign_keys='[Favorite.user_id]', back_populates='user')


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
    user = relationship('User', foreign_keys=[user_id], back_populates='favorites')
    favorite_user = relationship('User', foreign_keys=[favorite_user_id], backref='favorited_by')


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


def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def add_user(session, age, gender, city):
    new_user = User(age=age, gender=gender, city=city)
    session.add(new_user)
    try:
        session.commit()
        return new_user.id
    except Exception as e:
        session.rollback()
        print(f'Ошибка при добавлении пользователя: {e}')
        raise e


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
