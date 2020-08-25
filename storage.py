"""
Copyright 2019 (c) GlibGlob Ltd.
Author: Laurence Psychic
Email: vesper.porta@protonmail.com

Provide the cryptographic means to handle encryption of data and decryption of
data to and from disk using a public and private AES-RSA key.
"""

from sqlalchemy import (
    Column, Integer, Unicode, Binary, Boolean, DateTime, ForeignKey
)
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine


# engine = create_engine('sqlite:///:memory:')
engine = create_engine('sqlite:///output/data.sqlite')
Session = sessionmaker(bind=engine)
Base = declarative_base()
session = Session()


"""
Create an AE-RSA key for each bytes length of data being encoded and keep the
key in DB associated with the file. This key and filename are encrypted with a
master AES-RSA key where by the database data becomes usable and can restore
files from the database and filesystem storing the files.

This code and database are intended to be distributed along with the directory
or external drive as a means to ensure trasnportability, in this case it is a
requirement that the code is MD5 checksumed of itself and that the files
encrypted on the drive are erased and replaced with 🍆's.
"""


class CryptoStore(Base):
    __tablename__ = 'cryptostore'
    id = Column(Integer, primary_key=True)
    public_key = Column(Unicode())
    private_key = Column(Unicode())
    filename = Column(Unicode())
    checksum = Column(Unicode())
    filesize = Column(Integer())
    cryptofile_id = Column(Integer, ForeignKey('cryptofile.id'))
    cryptofile = relationship('CryptoFile', backref='cryptostores')

    def __repr__(self):
        return '<CryptoStore(id="{}", filename="{}", filesize="{}")>'.format(
            self.id, self.filename, self.filesize,
        )


class CryptoFile(Base):
    __tablename__ = 'cryptofile'
    id = Column(Integer, primary_key=True)
    # public_key = Column(Unicode())
    private_key = Column(Unicode())
    test_copy = Column(Unicode())
    test_encrypted = Column(Unicode())
    filename = Column(Unicode())
    is_dir = Column(Boolean())

    def __repr__(self):
        return '<CryptoFile(id="{}", filename="{}")>'.format(
            self.id, self.filename,
        )


CryptoStore.metadata.create_all(engine)
CryptoFile.metadata.create_all(engine)
