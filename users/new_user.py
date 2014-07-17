import os
import sys
import re
import hashlib

from sqlalchemy import create_engine, Column, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from keyczar import keyczar

PG_CONFIG = 'postgres://flask_admin:admin_pass@localhost:5432/od_survey'
SALT = '03a06110-0ded-11e4-9191-0800200c9a66'
KEYS = os.path.join(os.getenv('HOME'), 'api/keys')

Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key = True)
    first = Column(Text)
    last = Column(Text)
    username = Column(Text)
    password_hash = Column(Text)

    def __init__(self, first, last, username, password_hash):
        self.first = first
        self.last = last
        self.username = username
        self.password_hash = password_hash

    def __repr__(self):
        return '<User: Name: %r %r, Username:%r >' %\
            (self.first, self.last, self.username)

class Crypter(object): 
    crypter = None 
     
    def __init__(self, keys): 
        #TODO verify keys file exist and handle errors with reading keys 
        self.crypter = keyczar.Crypter.Read(keys) 
 
    def Encrypt(self, message): 
        return self.crypter.Encrypt(message) 
 
    def Decrypt(self, cipher): 
        return self.crypter.Decrypt(cipher)

if __name__ == '__main__':
    crypter = Crypter(KEYS)
    
    if len(sys.argv) == 5:
        first = sys.argv[1]
        last = sys.argv[2]
        username = sys.argv[3]
        password = sys.argv[4]

        # create database engine and session
        engine = create_engine(PG_CONFIG)
        Session = sessionmaker(bind=engine)
        session = Session()
       
        password_hash = hashlib.sha256(password + SALT).hexdigest()
        print password_hash

        new_user = Users(first, last, username, password_hash)
        session.add(new_user)
        session.commit()
        print "added new user {0} {1}".format(first, last)
        #user = session.query(Users).filter_by(username=username).first()


    else:
        print "incorrect parameters"
        print "expecting.. python new_user.py <first> <last> <username> <password>"


    #new_user = Users(first, last, username, crypter.Encrypt(password))
    #session.add(new_user)
    #session.commit()
    #user = session.query(Users).filter_by(username=username).first()
   
    
    #print crypter.Decrypt(user.password_hash)





