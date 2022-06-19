from ast import Bytes
import encodings
import re
import os
import hashlib
import codecs
import bcrypt

def email_check(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    val = True
    msg = ""
    if(re.fullmatch(regex, email)):
        msg = "Valid Email"     
    else:
        val = False
        msg = "Invalid Email"     

    return {"Value": val,"Message":msg}

def password_check(passwd):
      
    SpecialSym =['$', '@', '#', '%']
    val = True
    msg = []
    count = 0
    if len(passwd) < 6:
        msg.append('length should be at least 6')
        count += 1
        val = False
          
    if len(passwd) > 20:
        msg.append('length should be not be greater than 20')
        count += 1
        val = False
          
    if not any(char.isdigit() for char in passwd):
        msg.append('Password should have at least one numeral')
        val = False
          
    if not any(char.isupper() for char in passwd):
        msg.append('Password should have at least one uppercase letter')
        val = False
          
    if not any(char.islower() for char in passwd):
        msg.append('Password should have at least one lowercase letter')
        val = False
          
    if not any(char in SpecialSym for char in passwd):
        msg.append('Password should have at least one of the symbols $@#')
        val = False  

    resp = {"Value": val , "Message":msg}
    
    return resp

def password_hash(password):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    storage = codecs.decode(hashed,'latin-1')
    return storage

def password_verify(old_pass:str, new_pass:str):
    old_pass = codecs.encode(old_pass,'latin-1')
    new_pass = codecs.encode(new_pass,'utf-8')

    if bcrypt.checkpw(new_pass, old_pass):
        val = True
        msg = 'correct Password'
    else:
        val = False
        msg = 'incorrect Password'
    return {"Value":val,"Message":msg}

