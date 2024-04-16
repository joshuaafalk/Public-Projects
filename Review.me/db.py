""" database access
docs:
* http://initd.org/psycopg/docs/
* http://initd.org/psycopg/docs/pool.html
* http://initd.org/psycopg/docs/extras.html#dictionary-like-cursor
"""

from contextlib import contextmanager
import logging
import os
import re

from flask import current_app, g

import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import DictCursor

pool = None

def setup():
    global pool
    DATABASE_URL = os.environ['DATABASE_URL']
    current_app.logger.info(f"creating db connection pool")
    pool = ThreadedConnectionPool(1, 100, dsn=DATABASE_URL, sslmode='require')


@contextmanager
def get_db_connection():
    try:
        connection = pool.getconn()
        yield connection
    finally:
        pool.putconn(connection)


@contextmanager
def get_db_cursor(commit=False):
    with get_db_connection() as connection:
      cursor = connection.cursor(cursor_factory=DictCursor)
      # cursor = connection.cursor()
      try:
          yield cursor
          if commit:
              connection.commit()
      finally:
          cursor.close()

def add_user(first, last, username, email, occupation, profile_pic):
    with get_db_cursor(True) as cur:
        cur.execute("INSERT INTO users (first_name, last_name, username, email, occupation, profile_pic) values (%s, %s, %s, %s, %s, %s);", (first, last, username, email, occupation, profile_pic))

def get_user_details(email):
    with get_db_cursor() as cur:
        cur.execute("select * from users where email= %s", [email])
        return cur.fetchall()

def add_resume_post(title, description, resume_pdf, tags, resume_image, user_id):
    with get_db_cursor(True) as cur:
        cur.execute("INSERT INTO resumes (title, descript, resume_pdf, occupation, industry, experience, resume_img, comments_count, user_id) values (%s, %s, %s, %s, %s, %s, %s, %s, %s);", (title, description, psycopg2.Binary(resume_pdf), tags[0], tags[1], tags[2], psycopg2.Binary(resume_image), 0, user_id))

def get_resumes():
    with get_db_cursor() as cur:
        cur.execute("select * from resumes ORDER BY ts DESC")
        return cur.fetchall()

def get_resume_by_user_id(user_id):
    with get_db_cursor() as cur:
        cur.execute("select resumes.resume_id, resumes.title, resumes.descript, resumes.occupation, resumes.industry, resumes.experience, resumes.resume_img from resumes JOIN users ON users.user_id = resumes.user_id WHERE users.user_id= %s", [user_id])
        return cur.fetchall()

def get_resumes_preview():
    with get_db_cursor() as cur:
        cur.execute("select resume_id, title, descript, occupation, industry, experience, resume_img from resumes ORDER BY ts DESC")
        return cur.fetchall()

def get_resumes_by_comments():
    with get_db_cursor() as cur:
        cur.execute("select resume_id, title, descript, occupation, industry, experience, resume_img from resumes ORDER BY comments_count DESC")
        return cur.fetchall()

def increment_comment_count(resume_id):
    with get_db_cursor(True) as cur:
        cur.execute("UPDATE resumes SET comments_count = comments_count + 1 WHERE resume_id= %s", [resume_id])

def decrement_comment_count(resume_id):
    with get_db_cursor(True) as cur:
        cur.execute("UPDATE resumes SET comments_count = comments_count - 1 WHERE resume_id= %s", [resume_id])

def get_resumes_by_id(id):
    with get_db_cursor() as cur:
        cur.execute("select resume_id, title, descript, resume_pdf, occupation, industry, experience from resumes where resume_id = %s", [id])
        return cur.fetchall()

# similarity(
# CASE WHEN %s = 'true' THEN resumes.title ELSE '' END
# CASE WHEN %s = 'true' THEN resumes.occupation || resumes.industry || resumes.experience ELSE '' END ||
# CASE WHEN %s = 'true' THEN users.username ELSE '' END, %s
# ) > 0.1
def get_resume_by_search(title, tag, username, search):
    with get_db_cursor() as cur:
        current_app.logger.info(title + "" + tag + "" + username)
        cur.execute('''select resumes.resume_id, resumes.resume_img, resumes.title, resumes.descript, resumes.occupation, resumes.industry, resumes.experience, users.first_name, users.last_name, users.profile_pic
                        FROM resumes JOIN users ON users.user_id = resumes.user_id
                        WHERE
                        CASE WHEN %s = 'true' THEN similarity(resumes.title, %s) > 0.1 ELSE False END OR
                        CASE WHEN %s = 'true' THEN similarity(resumes.occupation || resumes.industry || resumes.experience, %s)> 0.1 ELSE False END OR
                        CASE WHEN %s = 'true' THEN similarity(users.first_name ||  users.last_name, %s) > 0.1 ELSE False END;''', [title, search, tag, search, username, search])
        resumes = cur.fetchall()
        current_app.logger.info(resumes)
        return resumes

def get_user_info(resume_id):
    with get_db_cursor() as cur:
        cur.execute("SELECT users.user_id, users.occupation, users.profile_pic, users.first_name, users.last_name FROM users JOIN resumes ON resumes.user_id = users.user_id WHERE resumes.resume_id = %s", [resume_id])
        return cur.fetchall()

def get_curr_user_id(user_email):
    with get_db_cursor() as cur:
        cur.execute("SELECT users.user_id FROM users WHERE email = %s", [user_email])
        return cur.fetchall()

# Comment Queries
def add_comment(comment, comment_info):
    with get_db_cursor(True) as cur:
        current_app.logger.info("Added Comment")
        cur.execute("INSERT INTO comments (resume_id, comment, user_id) values (%s, %s, %s);", (comment_info['resume_id'], comment, comment_info['user_id']))

def get_comments():
    with get_db_cursor() as cur:
        cur.execute("select * from comments ORDER BY ts DESC")
        return cur.fetchall()

def get_comments_by_resume(resume_id):
    with get_db_cursor() as cur:
        cur.execute("select * from comments JOIN users ON comments.user_id = users.user_id where comments.resume_id = %s ORDER BY ts DESC", [resume_id])
        return cur.fetchall()

def edit_comment(comment, comment_id):
    with get_db_cursor(True) as cur:
        current_app.logger.info(comment)
        current_app.logger.info(comment_id)
        cur.execute("update comments set comment = %s, edited = True where comment_id = %s", [comment, comment_id])
        cur.execute('commit')

def delete_comment(comment_id):
    with get_db_cursor(True) as cur:
        cur.execute("delete from comments where comment_id = %s", [comment_id])
        cur.execute('commit')

def get_comments_by_user_id(user_id):
    with get_db_cursor() as cur:
        cur.execute("SELECT comments.resume_id, comment FROM users JOIN comments ON users.user_id = comments.user_id where users.user_id = %s", [user_id])
        return cur.fetchall()

def get_email_by_user_id(user_id):
    with get_db_cursor() as cur:
        cur.execute("SELECT email FROM users where user_id = %s", [user_id])
        return cur.fetchall()
    
def delete_resume(resume_id):
    with get_db_cursor(True) as cur:
        cur.execute("delete from resumes where resume_id = %s", [resume_id])
        cur.execute('commit')