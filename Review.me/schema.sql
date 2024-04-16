CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    resume_id int,
    FOREIGN KEY (resume_id) REFERENCES resumes(resume_id),
    username varchar(40),
    first_name varchar(40),
    last_name varchar(40),
    email varchar(40),
    occupation varchar(40),
    profile_pic bytea
);

CREATE TABLE resumes (
    resume_id SERIAL PRIMARY KEY,
    user_id int,
    title varchar(40),
    descript varchar(300),
    resume_pdf bytea,
    ts timestamp DEFAULT CURRENT_TIMESTAMP,
    comments_count int,
    occupation varchar(40),
    industry varchar(40),
    experience varchar(40),
    resume_img bytea,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
);

CREATE TABLE comments (
    comment_id SERIAL PRIMARY KEY,
    resume_id int,
    user_id int,
    comment varchar(300),
    edited boolean DEFAULT false,
    ts timestamp DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resume_id) REFERENCES resumes(resume_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);