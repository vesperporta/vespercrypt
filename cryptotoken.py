"""Tokenisation of objects for simple authentication."""

import random

from datetime import timedelta, datetime
from Crypto.Cipher import AES
from Crypto.Hash import SHA256

from sqlalchemy import Table, Column, Integer, Unicode, Binary, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


HASH_FIELD_ALPHABET = 'abcdefghijklmnopqrstuvwxyz1234567890'
HASH_FIELD_ALPHABET += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
HASH_FIELD_ALPHABET += '1234567890'
AES_KEY_AUTHENTICATION = 'XH5dFRNwUfPCJo9mB0ErcGDjT3Yi8q4V'
AES_IV456_AUTHENTICATION = 'm80uUNH4qo5eyFXD'
TOKEN_RANDOM_KEY_LENGTH = 32
TOKEN_RANDOM_VALUE_LENGTH = 64
TOKEN_SALT_START = 'Kx(62Q~o0kjRyl|_sr1<*z8+.HN>b/5ci4LtMqmT,Y3@^`fJEh'
TOKEN_SALT_END = 'HDQcA&yv<^Chf2u*L>wJ]BOtW;K=9$x8Zl?Viz!7,3Xp[1.:0s'


Base = declarative_base()


class TokenManager:

    def get_cipher(self):
        """Create AES cipher to manage the storage of values.

        @:return Crypto.cipher.AES
        """
        return AES.new(
            AES_KEY_AUTHENTICATION,
            AES.MODE_CBC,
            AES_IV456_AUTHENTICATION,
        )

    def get_value(self, token):
        """Using known values attempt to decrypt a tokens value.

        @:param token: Token object.

        @:returns str
        """
        aes_object = self.get_cipher()
        return aes_object.decrypt(bytes(token.value)).rstrip()

    def generate_sha256(self, seed=None):
        """Generate a random hexadecimal str, 2 salts are used.

        @:param seed: str to set for hashing or now timestamp is used.

        @:return str
        """
        sha_hash = SHA256.new()
        if not seed:
            seed = str(datetime.timestamp(datetime.now()))
        hashing = f'{TOKEN_SALT_START}{seed}{TOKEN_SALT_END}'
        sha_hash.update(hashing.encode('utf-8'))
        return sha_hash.hexdigest()

    def create_random(self, expiry=None, single_use=True):
        """Generate a token based on a random key and value.

        @:param expiry: datetime the token will expire.
        @:param single_use: bool determines a one off use.

        @:return Token
        """
        return self.create_token(
            ''.join(
                [
                    random.choice(HASH_FIELD_ALPHABET)
                    for i in range(TOKEN_RANDOM_KEY_LENGTH)
                ]
            ),
            token_value=''.join(
                [
                    random.choice(HASH_FIELD_ALPHABET)
                    for i in range(TOKEN_RANDOM_VALUE_LENGTH)
                ]
            ),
            expiry=expiry,
            single_use=single_use,
        )

    def create_token(
        self, token_key, token_value=None, expiry=None, single_use=True
    ):
        """Create a token.

        @:param token_key: str the key to identify this Token by.
        @:param token_value: str optional value to store as validation value.
        @:param expiry: datetime the token will expire.
        @:param single_use: bool determines a one off use.

        @:return Token
        """
        expire_in_day = datetime.timestamp(datetime.now()) + timedelta(days=1)
        expiry_expected = expiry if expiry else expire_in_day
        aes_object = self.get_cipher()
        if not token_value:
            token_value = self.generate_sha256(token_key)
        cipher_text = aes_object.encrypt(token_value)
        self.filter(
            key=token_key,
            validated=False,
        ).update(deleted_at=datetime.timestamp(datetime.now()))
        return Token.objects.create(
            key=token_key,
            value=cipher_text,
            expiry=expiry_expected,
            single_use=single_use,
        )

    def validation(self, token_key, token_value):
        """Validate a key value pair.

        @:param token_key: str identifier.
        @:param token_value: str value stored in cipher.

        @:return bool
        """
        token = Token.objects.filter(key=token_key).first()
        return token.validate(token_value)


class Token(Base):
    """Simple token object."""

    id = Column(Integer, primary_key=True)
    key = Column(Unicode())
    value = Column(Binary())
    single_use = Column(Boolean())
    validated = Column(Boolean())
    expiry = Column(DateTime())
    created_at = Column(DateTime())
    modified_at = Column(DateTime())
    deleted_at = Column(DateTime())

    def validate(self, expected_value):
        """Validate the stored value against an expected.

        @:param expected_value: str value expected to match.

        @:return bool
        """
        if not self.value:
            return False
        now = datetime.timestamp(datetime.now())
        expired = self.expiry < now
        is_valid = self.objects.get_value(self) == expected_value
        if expired or is_valid:
            self.validated = True
            self.expiry = now
            self.save()
        if expired or self.single_use:
            self.delete()
        if expired:
            return False
        return is_valid
