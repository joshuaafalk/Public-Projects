from flask import Flask, request, render_template, redirect, jsonify, url_for, session, send_file
from authlib.integrations.flask_client import OAuth
from urllib.parse import quote_plus, urlencode
import json
import db
import psycopg2
import os
import base64
from io import BytesIO
import fitz # pdf to image
from profanity import profanity 
import requests
from PIL import Image
import colorsys
import convertapi
import docx
import openai



def create_app():
    app = Flask(__name__, 
                static_url_path='', 
                static_folder='static',
                template_folder='templates')
    app.secret_key = os.environ.get("APP_SECRET_KEY")
    with app.app_context():
        db.setup()
    return app

app = create_app()
# app.config['UPLOAD_FOLDER'] = 'AItest'
oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=os.environ.get("AUTH0_CLIENT_ID"),
    client_secret=os.environ.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{os.environ.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

def generate_colors(base_hue, match_list, saturation=1, start_lightness=0.3, end_lightness=0.7, hue_variation=0):
    lightness_range = end_lightness - start_lightness
    shades = {}
    total_matches = len(match_list) - 1 if len(match_list) > 1 else 1
    for i, match in enumerate(match_list):
        # Calculate the lightness for this tag
        lightness = start_lightness + (lightness_range * i / total_matches)
        # Adjust hue for each color to provide variation
        adjusted_hue = (base_hue + hue_variation * i) % 360
        hsl_color = (adjusted_hue, saturation, lightness)
        # Convert HSL to RGB for web usage
        rgb_color = colorsys.hls_to_rgb(hsl_color[0] / 360, hsl_color[2], hsl_color[1])
        # Format RGB to HEX
        hex_color = '#{:02x}{:02x}{:02x}'.format(int(rgb_color[0] * 255), int(rgb_color[1] * 255), int(rgb_color[2] * 255))
        shades[match] = hex_color
    return shades


occupation_to_color = ['Software Engineer','Data Analyst', 'Product Manager', 'Sales', 'Marketing', 'Finance', 'Human Resources', 'Operations', 'Other']
industry_to_color = ['Technology', 'Healthcare', 'Finance', 'Retail', 'Manufacturing', 'Education', 'Government', 'Non-Profit', 'Other']
experience_to_color = ['Intern', 'Entry Level', 'Mid Level', 'Senior Level', 'Director', 'Executive']

occupation_colors = generate_colors(210, occupation_to_color, hue_variation=5)
industry_colors = generate_colors(100, industry_to_color, end_lightness=.5, hue_variation=3)
experience_colors = generate_colors(340, experience_to_color, hue_variation=5)


@app.route('/')
def home():
    if session.get('user') != None:
        num_logins = session.get('user').get('userinfo')['logins']
        session['user_id'] = db.get_curr_user_id(session.get('user').get('userinfo')['email'])[0][0]
    resumes = []
    # contains ordered list of resumes by comment count
    resumes_by_comments = []
    get_resumes_response = db.get_resumes_preview()
    get_resumes_response_by_comments = db.get_resumes_by_comments()
    # resume_id, title, descript, occupation, industy, experience, resume_img
    for i in range(len(get_resumes_response)):
        if get_resumes_response[i][6] is None:
            continue
        image_bytes = bytes(get_resumes_response[i][6]).decode('utf-8')

        resumes.append((image_bytes, get_resumes_response[i][1], get_resumes_response[i][2], get_resumes_response[i][3], get_resumes_response[i][4], get_resumes_response[i][5], get_resumes_response[i][0]))
    
    for i in range(len(get_resumes_response_by_comments)):
        if get_resumes_response_by_comments[i][6] is None:
            continue
        image_bytes = bytes(get_resumes_response_by_comments[i][6]).decode('utf-8')

        resumes_by_comments.append((image_bytes, get_resumes_response_by_comments[i][1], get_resumes_response_by_comments[i][2], get_resumes_response_by_comments[i][3], get_resumes_response_by_comments[i][4], get_resumes_response_by_comments[i][5], get_resumes_response_by_comments[i][0]))

    resumes = resumes[:6]
    resumes_by_comments = resumes_by_comments[:6]
    return render_template('home.html', user=session.get('user'),resumes=resumes, resumes_by_comments=resumes_by_comments, colors=[occupation_colors, industry_colors, experience_colors])

@app.route('/profile') #  need to add a parameter to this route
def profile():
    if not session.get('user'):
        return redirect('/login')
    
    if request.args.get('id') == None:
        user_details = db.get_user_details(session.get('user')['userinfo']['email'])[0]
    else:
        user_id = request.args.get('id')
        user_email = db.get_email_by_user_id(user_id)[0][0]
        user_details = db.get_user_details(user_email)[0]

    user_comments = db.get_comments_by_user_id(user_details[0])
    resume = []
    get_resumes_response = db.get_resume_by_user_id(user_details[0])
    if get_resumes_response != []:
        image_bytes = bytes(get_resumes_response[0][6]).decode('utf-8')
        resume.append((image_bytes, get_resumes_response[0][1], get_resumes_response[0][2], get_resumes_response[0][3], get_resumes_response[0][4], get_resumes_response[0][5], get_resumes_response[0][0]))
    profile_pic_bytes = bytes(user_details[8]).decode('utf-8') if user_details[8] else None
    resume = resume[0] if resume else None
    return render_template('profile.html', user_id=session.get('user_id'), user=user_details, user_comments=user_comments, profile_pic=profile_pic_bytes, resume=resume)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if not session.get('user'):
        return redirect('/login')
    if request.method == 'POST':
        # get the form data and save it to the database
        title, description = request.form.get('resume-title'), request.form.get('description')
        tags = [request.form.get('occ-tag'), request.form.get('ind-tag'), request.form.get('exp-tag')]
        
        file = request.files.get('file-upload')
        if not file:
            return redirect('/create')
        session['filename'] = file.filename
        file_base64 = base64.b64encode(file.read())
        resume_bytes = bytes(file_base64).decode('utf-8')
        # turn into bytesio
        resume_bytes = BytesIO(base64.b64decode(resume_bytes))
        #  open the document from bytes
        doc = fitz.open(stream=resume_bytes, filetype="pdf")
        page = doc.load_page(0)  # first page
        pix = page.get_pixmap()
        img_io = pix.tobytes("png")
        base64_img = base64.b64encode(img_io)
        db.add_resume_post(title, description, file_base64, tags, base64_img, session.get('user_id'))
        return redirect('/')
    
    occupation = ["Software Engineer", "Data Analyst", "Product Manager", "Sales", "Marketing", "Finance", "Human Resources", "Operations", "Other"]
    industry = ["Technology", "Healthcare", "Finance", "Retail", "Manufacturing", "Education", "Government", "Non-Profit", "Other"]
    yoe = [ "Intern", "Entry Level", "Mid Level", "Senior Level", "Director", "Executive"]

    return render_template('create_post.html', user=session.get('user'), all_tags=[occupation, industry, yoe])

@app.route('/search_results', methods=['GET', 'POST']) #  need to add a parameter to this route
def search_results():
    
    if request.args.get('usernameFilter') == None:
        usernameFilter = 'true'
    else:
        usernameFilter = request.args.get('usernameFilter')

    if request.args.get('titleFilter') == None:
        titleFilter = 'true'
    else:
        titleFilter = request.args.get('titleFilter')

    if request.args.get('tagFilter') == None:
        tagFilter = 'true'
    else:
        tagFilter = request.args.get('tagFilter')
    

    search = request.args.get('search')
    filters = {"usernameFilter": usernameFilter, "titleFilter": titleFilter, "tagFilter": tagFilter}

    resumes = db.get_resume_by_search(titleFilter, tagFilter, usernameFilter, search)

    # resumes = db.get_resumes()

    for i in range(len(resumes)):
        resumes[i][1] = bytes(resumes[i][1]).decode('utf-8')
        resumes[i][9] = bytes(resumes[i][9]).decode('utf-8') if resumes[i][9] else None

    return render_template('search_results.html', user=session.get('user'), resumes=resumes, filters=filters, search=search, tag_colors=[occupation_colors, industry_colors, experience_colors])

@app.route('/login')
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route('/first_login', methods=["GET", "POST"])
def first_login():
    userinfo = session.get('user').get('userinfo')
    response = requests.get(userinfo.get('picture'))
    profile = BytesIO(response.content)
    profile = 'data:image/png;base64,' + base64.b64encode(profile.getvalue()).decode('ascii')
    if request.method == 'GET':
        return render_template('first_time_login.html',
        first_name=userinfo.get('given_name', ""),
        last_name=userinfo.get('family_name', ""),
        profile_pic=profile,
        email=userinfo.get('email', ""))
    elif request.method == 'POST':
        if request.files.get('pfp'):     # First, check if user uploaded a profile pic
            raw_pic = request.files.get('pfp')
            profile_pic = 'data:image/png;base64,' + bytes(base64.b64encode(raw_pic.read())).decode('utf-8')
        else:
            profile_pic = profile
        db.add_user(request.form.get('first_name'), request.form.get('last_name'), request.form.get('username'), request.form.get('email'), request.form.get('occupation'), profile_pic)
        return redirect("/")

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    userinfo = session.get('user').get('userinfo')
    if userinfo['logins'] == 1:
        return redirect("/first_login")
    else:
        return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + os.environ.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": os.environ.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

@app.route('/resume') 
def resume():
    resume_id = request.args.get('id')
    gpt = request.args.get('gpt')
    resume = db.get_resumes_by_id(resume_id)
    resume[0][3] = bytes(resume[0][3]).decode('utf-8')
    occupation, industry, experience = resume[0][4], resume[0][5], resume[0][6]
    
    user_info = db.get_user_info(resume_id)
    for i in range(len(user_info)):
        user_info[i][2] = bytes(user_info[i][2]).decode('utf-8') if user_info[i][2] else None

    comments = db.get_comments_by_resume(resume_id)
    for i in range(len(comments)):
        comments[i][14] = bytes(comments[i][14]).decode('utf-8') if comments[i][14] else None

    return render_template('resume.html', user=session.get('user'), resume=resume[0], 
                           comments=comments, tags=[occupation, industry, experience], 
                           user_id=session.get('user_id'), tag_colors=[occupation_colors, industry_colors, experience_colors], 
                           user_info=user_info[0], gpt=gpt, gptResponse=session.get('response'))


#Comment endpoints
@app.route('/addComment', methods=['GET', 'POST'])
def addComment():
    if not session.get('user'):
        return redirect('/login')
    comment = profanity.censor(request.form['comment'])
    db.add_comment(comment, request.form)
    db.increment_comment_count(request.form['resume_id'])

    return redirect('/resume?id='+request.form['resume_id'])

@app.route('/editComment', methods=['GET', 'POST'])
def editComment():
    comment = profanity.censor(request.form['comment'])
    db.edit_comment(comment, request.args.get('comment_id'))
    return redirect('/resume?id='+request.form['resume_id'])

@app.route('/deleteComment', methods=['GET', 'POST'])
def deleteComment():
    comment_id = request.args.get('comment_id')
    resume_id = request.args.get('resume_id')
    db.delete_comment(comment_id)
    db.decrement_comment_count(resume_id)
    return redirect('/resume?id='+resume_id)


@app.route('/reviewResume', methods=['GET', 'POST'])
def reviewResume():
    resume_id = request.args.get('id')
    resume = db.get_resumes_by_id(resume_id)
    decoded_string = base64.b64decode(bytes(resume[0][3]).decode('utf-8'))
    with open('decoded_file.pdf', 'wb') as file:
        file.write(decoded_string)

    convertapi.api_secret = os.environ.get("CONVERTAPI_SECRET")
    result = convertapi.convert('docx', {'File': "decoded_file.pdf" })
    doc = docx.Document(BytesIO(result.file.io.getvalue()))

    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
    fullText = '\n'.join(fullText)
    occupation, industry, experience = resume[0][4], resume[0][5], resume[0][6]

    prompt = "Review this resume and incorporate these topics: {}, {}, {}\n {}".format(occupation, industry, experience, fullText)

    client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": "You are a resume reviewer, personalizing recommendations towards specific given resumes. Give 4 to 6 improvements for a resume as a bulleted list with two newlines after every point. Do not recommend adding a summary section."},
            {"role": "user", "content": prompt}
        ]
    )
    session['response'] = response.choices[0].message.content
    return redirect('/resume?gpt=true&id=' + resume_id)

@app.route('/deleteResume', methods=['GET', 'POST'])
def deleteResume():
    resume_id = request.args.get('id')
    db.delete_resume(resume_id)
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
