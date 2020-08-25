"""
Copyright 2019 (c) GlibGlob Ltd.
Author: Laurence Psychic
Email: vesper.porta@protonmail.com

Deal with the filesystem and remove files and directories from a location or
write content supplied or Aubergine.
"""

import os
from random import choice
from pathlib import Path


file_sizes = []


def get_path(location):
    """
    Validate locatio is a PathPosix instance.
    """
    return Path(location)


def detail_location(location):
    """
    Search through all child files of a directory and return a dict object with
    relative filenames and the full Path object related, no data will be read
    from disk.
    """
    location = get_path(location)
    if not location.exists():
        return None
    if location.is_symlink():
        sym_target = os.readlink(location)
        return detail_location(sym_target)
    if location.is_file():
        return {location.name: location}
    rtn = {}
    sub_list = [x for x in location.iterdir()]
    for x in sub_list:
        rtn.update(detail_location(x) if x.is_dir() else {x.name: x})
    return rtn


def aubergine_file(size, file_path):
    """
    Write a file to disk matching the bytes as an argument with '🍆'.
    """
    if type(file_path) is not Path:
        return
    chr_length = 4
    i = 0
    length = 16
    filename = ''
    while i < length:
        i += 1
        filename += chr(choice(range(97, 122)))
    size += chr_length - (size % chr_length)
    file_path.write_text(''.join(['🍆'] * int(size / chr_length)))


def read_location(location):
    location = get_path(location)
    if not location.exists():
        return None
    read_file = location.read_bytes()  # TODO: Large file handling required
    return read_file


def write_location(location, contents, write_bytes=False):
    location = get_path(location)
    if write_bytes:
        location.write_bytes(contents)
        return
    location.write_text(contents)


def remove_location(location):
    """
    Remove the location Path object, sybolic links will be removed after the
    target of the symbolic link is removed.
    """
    if location.is_symlink():
        sym_target = os.readlink(location)
        file_sizes.append(sym_target.stat().st_size)
        remove_location(sym_target)
    if location.is_file():
        file_sizes.append(location.stat().st_size)
        os.remove(location)
    else:
        try:
            os.rmdir(location)
        except FileNotFoundError:
            pass
        except OSError:
            remove_disk_contents([location])


def remove_disk_contents(locations=None):
    """
    Recurse through a list of file locations and remove all files and folders
    in directories and remove all files listed independantly.
    """
    if not locations:
        return
    for location in locations:
        path = get_path(location)
        if path.is_dir():
            sub_list = [x for x in path.iterdir()]
            for sub_loc in sub_list:
                remove_location(sub_loc)
        remove_location(path)
