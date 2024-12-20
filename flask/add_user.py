import sqlite3
import hashlib

def encrypt_string(hash_string):
    sha_signature = hashlib.sha256(hash_string.encode()).hexdigest()
    return sha_signature

dbcon = sqlite3.connect('database.db')
cursor = dbcon.cursor()

id = 5
username = "runner"
pas = "1234"

p_hash = encrypt_string(pas)

sql = "INSERT INTO users (id, username, hash_pw) VALUES (?, ?, ?)"
cursor.execute(sql,(id, username,p_hash))
dbcon.commit()

print("record inserted.")

dbcon.close()