"""
@author: Amen Wondwosen
"""

import re
import os

# illegal_filename_characters = r"[#%&{}\\<>*?\/ $!\'\":@]"
ichars = '\\/:"*?<>|'

def remove_illegal_characters(s: str, ichars=ichars, filler="_", sp=False):
    '''
    Replaces any illegal characters in s with filler and returns the
    modified string.
    '''

    if not s:
        return s

    s = s.rstrip(".")   # Remove any trailing dots

    if sp:
        # remove special characters        
        s = re.sub(r'[^\x00-\x7F]', ' ', s)
    
    s = re.sub(r'[\\/:"*?<>|]', filler, s)

    return re.sub(r'\s{2,}', ' ', s)


def replace_spchars(s, filler=""):
    '''
    Replaces every special character in
    the string with its ascii equivalent.
    '''
    return re.sub(r'[^\x00-\x7F]+', filler, s)