"""
Copyright 2019 (c) GlibGlob Ltd.
Author: Laurence Psychic
Email: vesper.porta@protonmail.com

Initiate the VesperCrypt System, provide a UI to take a file and encrypt the
file using the provided AES-RSA encryption key in block sizes equal to
512 bytes of information per encoding. An SQL database is used to maintain the
validity of the data stored on disk and retain concurency in data.
"""

import click
from math import ceil
from Crypto.Cipher import AES
from hashlib import md5

from diskio import read_location, write_location, detail_location, get_path
from storage import CryptoStore, CryptoFile, session
from password import Password


AES_IV456_AUTHENTICATION = '84d1a35654ab9af8'
DEFAULT_OUTPUT_DIRECTORY = './output'
FILE_BYTE_LENGTH = 1024
IGNORE_LIST = [
    '.DS_Store',
]


def get_encryptable_password():
    password_store = str(Password())
    while len(password_store.encode()) % 16:
        password_store = get_encryptable_password()
    return password_store


def get_available_filename():
    filename = str(Password(alphabet=['Filename Safe']))
    path = get_path('{}/{}'.format(DEFAULT_OUTPUT_DIRECTORY, filename))
    while path.exists() or len(path.name.encode()) % 16:
        path = get_available_filename()
    return path


def encrypt_location(location, cypher, password_key, password_iv):
    skip_file = [s for s in IGNORE_LIST if s in location.name]
    if skip_file:
        return None
    location = get_path(location)
    byte_length = FILE_BYTE_LENGTH
    test_copy = get_encryptable_password()
    file = CryptoFile(
        # public_key=password_key,
        private_key=password_iv,
        test_copy=test_copy,
        test_encrypted=cypher.encrypt(test_copy).hex(),
        filename=location.name,
        is_dir=location.is_dir(),
    )
    session.add(file)
    session.commit()
    files = []
    if location.is_file():
        read = read_location(location).hex()
        length = len(read)
        i = 0
        iv456 = md5(str(Password()).encode()).hexdigest()[:16]
        for i in range(ceil(length / byte_length)):
            password_store = get_encryptable_password()
            password = md5(password_store.encode()).hexdigest()
            file_location = get_available_filename()
            text_value = read[i * byte_length: (i + 1) * byte_length]
            text_length = len(text_value)
            if len(text_value) < byte_length:
                text_value += ''.join(['0'] * (byte_length - len(text_value)))
            aes_object = AES.new(password, AES.MODE_CBC, iv456)
            write_location(file_location, aes_object.encrypt(text_value).hex())
            file_store = CryptoStore(
                public_key=cypher.encrypt(password_store).hex(),
                private_key=cypher.encrypt(iv456).hex(),
                filename=cypher.encrypt(file_location.name).hex(),
                filesize=text_length,
                cryptofile=file
            )
            files.append(file_store)
            session.add(file_store)
    if files:
        session.commit()
    return file


def dencrypt_hash(data, cypher):
    pass


def encrypt_detailed_location(details, aes_pass, password_key, password_iv):
    detail_files = []
    for key in details.keys():
        path = details[key]
        if type(path) is dict:
            encrypt_detailed_location(path)
        else:
            file = encrypt_location(path, aes_pass, password_key, password_iv)
            if file and path.is_file():
                detail_files.append(file)
            # elif key == '.':
            #     current_dir = file
    # for file in detail_files:
    #     file.directory = current_dir
    session.commit()


def main():
    """
    Main method for application.
    """
    app_name = '- VesperCrypt System -'
    print(app_name)
    password = click.prompt('Password', hide_input=True)
    password_key = md5(password.encode()).hexdigest()
    password_iv = md5(AES_IV456_AUTHENTICATION.encode()).hexdigest()[:16]
    aes_pass = AES.new(password_key, AES.MODE_CBC, password_iv)
    crypt_type = click.prompt('Store / Retrieve? [s/r]')
    if crypt_type == 's':
        location_details = detail_location('./input/')
        encrypt_detailed_location(
            location_details, aes_pass, password_key, password_iv)
    elif crypt_type == 'r':
        output = get_path('./restore')
        output.mkdir(exist_ok=True)
        all_files = session.query(CryptoFile).all()
        for file in all_files:
            tested = aes_pass.decrypt(file.test_encrypted)
            """
            # Matches of decrypting do not pass
            # Encryption of same copy does not match stored
            # Test password 'lolliepop'

            (Pdb) aes_pass.decrypt(file.test_encrypted)
            b'\xfd U\xbe\xec\xed\xe7n\x01?\x7f\xe4\x8b\xfa\x9b\xb4\xee\x1e\t\x8d\x02\xaa#\x83\x8f\xd6c+\x94t\x04\xa9\xdf5\x02=\xc8\x07\xc8>u\xab\xf7CSP\xfe:#\xd5/0\xc1f\x04y\x0e\r\x07\xc2WP\xb4\x86#\xd3\xce\x82\xb3&\x0b\xb0\x16\xbe\xd0\xea3\x8f\xe9D\x16\x10I\xe58\x1aj\xd0\xe8u\xe7\xcd1G\\(\x92u\rn\xa1\xf5K9-\xc5\n&\xf31V\xc6,\xfd%\x1d\xfa\xd5zfu\x9b\xf9\x00&v\xc4P5\xc3\xec\x0b\x90^$ZS\x16 \t:\r\xbf\xb3\x9f\x9a\xbb\xb3T\xc3Y\x0e\xa0;\xfc\x1cS\xce\xd8\x15gVf\'\xff\xa7\xc2^\xb8F\xcf\xd9n\xf2\xc7\xaeY\x9f\xdc\xc8\x84_G\xeb\xc7:\x81\x0b\xb6\xd1<\xc4`<w\x82\xc2Et\xac\xaa9O/\x0e*\xc7)8\x1c\x1dH\xd4\xc9\x0b\x06\xe4iuO(\x14b\xb9L\x07,\x12\x98\xa5z\x91\x88\x00\x17\x07\xf9.\x95U\x8d\xc9\x95\xb3\xe8\xf0n\xd4\xf0\xe8\x98m\xdb\xe5\xaa\xdd`U\xaa\xfc\x8d*\xc7\xb1_\xa2\x94/\x94\xd2\x9fE\x1c!o\x06\xeb\xd2\xca\xbe\xc7\xe64<\x0e\x8b\x0c\x14\xfcTu\xbe\x1e\xb7\xc3\x06\xa7V{\xdf7\xd6\x93\x11z=\xdc"\xbe\xe3c\xcd\xa1d\xda\xd6r\x97\x7f\x9a;\xdf\xffw\xb1\x13\xf7\x01\xac\xf0]yK\x80\xf85\xfb?\xcc\xaei\x87\xc0\x9ffl\xc8\x84\xcb\x93\xc0\xdf\x12\xe2#\x9d[\xf4\xf3x\xdc|\xaa\xbd\xd8\x88Z\x06\x1b\\\x9c,\xed\x94\xaf\x85\x9b:\xb7\xac\x14\x08\xe6\xfd'
            (Pdb) aes_pass.encrypt(file.test_copy)
            b'\rntH\xf3\xaa(T6\x84\xc8\xbb=\xb9\xae*\xde6\xa2\xfb2\xe37m\xc6\x0f\x1d\x02\xdb\xbc\xa3\x1c\xbb\x9b\x1d\xe2S\x81\x04\x94\xaa=\xde\x85\x82\xea\xfbN\x1f\x866U\x06Y`\xafu\xa5\xc2\xca\xaf\xc6\x11)PL\x98\xe7\x9dw\x81\xc3\x1d\xc27\xd7S\x8c\xb3\x9d\x82\xa5\xaa^e(\xca\xe2+\xd4\x07k\xd0\x82\xd6w\x1e:\x03T\xdf\xd3\xbf\xeb>3\xeb\xfa\xbb\x97\x90\xa5\xba\xf6\x08\x01>\x91\x18\x10\xcbO\x81Pi{\xe0\xcaCf\xd9 F\x129M/\x9c\x9aE\x050\xe9\xcb\x82xR0\xc5\x1eW\xc83\xe9\x1a\xf2\rw\xe8\xf7k5\xd6\x8c\x01Q\xa1\xd9\xb0\x89@\xe4\x940\r\xdd+\xef\x7f\xb6\x04ixn\xabxSE\xd9\x11\xbf\xfa'
            (Pdb) file.test_encrypted
            '7ba7b9460e027c305e5256020d7e52ef3658e2127b762f65fe43df357902fa36fe31a25d37415be747536efb50e403e37903e1fe181a7a1982e663f60ab0a4c3bfbe9a884f251dea9aa7309b2418282601c4809e23c43e323b6e5ec481be5b3abf74e4711585c60afe5c229018e836e91f8f89a84c3dd8f60d54e361210e086faab66857704cc686c0d247ce0f017bea3f16fe61f4cc164cac6fb1eac04ecaedb8d5d1bbbefd8df3a3bdb3e21f36e7236e1d4eb1f358d21afbd6d8e5647060f0'
            (Pdb)
            """
            import pdb; pdb.set_trace()
            if tested != file.test_copy:
                continue
            path = get_path(
                '{}/{}'.format(DEFAULT_OUTPUT_DIRECTORY, file.filename))
            output_path = get_path('{}/{}'.format(output, file.filename))
            add_output = output_path.open(mode='a')
            add_output.write()
            write_location(output_path, read_location(path).hex())
        # session.query(CryptoStore).filter_by(cryptofile_id=4).all()
        import pdb; pdb.set_trace()


if __name__ == '__main__':
    main()
