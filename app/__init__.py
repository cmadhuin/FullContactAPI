
import os, csv, json,  pathlib, urllib.request, time
from flask import Flask, render_template, flash, request, redirect

from config import app_config
from app.forms import IndexForm
from werkzeug.utils import secure_filename
from . import fullcontactapi

def create_app(config_name):
    app =  Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])

    current_dir = pathlib.Path(__file__).parent
    ALLOWED_EXTENSIONS = set(['txt', 'csv'])
    def allowed_file(filename):
    	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    ###########################################
    column_names = ['email','fullName','ageRange','gender','location','title','organization','twitter','linkedin',
                    'facebook','bio','avatar','website', 'name_given','name_family','name_middle','name_prefix',
                    'name_suffix','name_nickname', 'birthday', 'age_range','age_value', 'gender', 'phones','profiles' ,'employment_name',
                    'employment_domain','employment_status','employment_title','employment_start','employment_end', 
                    'photos_label','photos_value', 'education_name','education_degree','education_end','urls_label','urls_value',
                    'interests_name','interests_id','interests_affinity','interests_parentIds','interests_category', 'topics',
                    'keypeople_name', 'keypeople_title', 'keypeople_avatar','addon_id', 'addon_name', 'addon_enabled', 'addon_applied',
                    'addon_description', 'addon_docLink','updated']
                    
    def get_csv_row(x,email):
        ret = []    
        for column in column_names:
            ret.append(x.get(column, ''))
        ret[0] = email
        if len(x) == 0:
            return ret
        if x.get('details'):
            try:
                if x.get('details').get('name'):
                    ret[13] = x.get('details').get('name').get('given','')
                    ret[14] = x.get('details').get('name').get('family','')
                    ret[15] = x.get('details').get('name').get('middle','')
                    ret[16] = x.get('details').get('name').get('prefix','')
                    ret[17] = x.get('details').get('name').get('suffix','')
                    ret[18] = x.get('details').get('name').get('nickname','')
            except ValueError as e:
                print("Value error in x.get('details').get('name'):{}".format(email))
            try:
                if x.get('details').get('age'):
                    ret[19] = x.get('details').get('age').get('birthday','')
                    ret[20] = x.get('details').get('age').get('range','')
                    ret[21] = x.get('details').get('age').get('value','')
            except ValueError as e:
                print("Value error in x.get('details').get('age'):{}".format(email))
            try:
                if x.get('details').get('gender'):
                    ret[22] = x.get('details').get('gender','')
            except ValueError as e:
                print("Value error in x.get('details').get('gender'):{}".format(email))
            try:
                ret[23] = x.get('details').get('phones','')
                ret[24] = x.get('details').get('profiles','')
            except ValueError as e:
                print("Value error in x.get('details').get('phone&profile'):{}".format(email))
            try:                    
                if x.get('details').get('employment'):
                    ret[25] = x.get('details').get('employment').get('name','')
                    ret[26] = x.get('details').get('employment').get('domain','')
                    ret[27] = x.get('details').get('employment').get('current','')
                    ret[28] = x.get('details').get('employment').get('title','')
                    ret[29] = x.get('details').get('employment').get('start','')
                    ret[30] = x.get('details').get('employment').get('end','')
            except ValueError as e:
                print("Value error in x.get('details').get('employment'):{}".format(email))
            try:
                if x.get('details').get('photos'):
                    ret[31] = x.get('details').get('photos').get('label','')
                    ret[32] = x.get('details').get('photos').get('value','')
            except ValueError as e:
                print("Value error in x.get('details').get('photos'):{}".format(email))
            try:
                if x.get('details').get('education'):
                    for education in x.get('details').get('education'):
                        ret[33] = ret[33] + ' | ' + str(education.get('name',''))
                        ret[34] = ret[34] + ' | ' + str(education.get('degree',''))
                        ret[35] = ret[35] + ' | ' + str(education.get('end',''))
            except ValueError as e:
                print("Value error in x.get('details').get('education'):{}".format(email))
            try:
                if x.get('details').get('urls'):
                    ret[36] = x.get('details').get('urls').get('label','')
                    ret[37] = x.get('details').get('urls').get('value','')
            except ValueError as e:
                print("Value error in x.get('details').get('urls'):{}".format(email))
            try:
                if x.get('details').get('interests'):
                    ret[38] = x.get('details').get('interests').get('name','')
                    ret[39] = x.get('details').get('interests').get('id','')
                    ret[40] = x.get('details').get('interests').get('affinity','')
                    ret[41] = x.get('details').get('interests').get('parentIds','')
                    ret[42] = x.get('details').get('interests').get('category','')
                ret[43] = x.get('details').get('topics','')
            except ValueError as e:
                print("Value error in x.get('details').get('interests'):{}".format(email))
            try:
                if x.get('details').get('keyPeople'):
                    for keypeople in x.get('details').get('keyPeople'):
                        ret[44] =ret[44] + ' | ' + str(keypeople.get('fullName'))
                        ret[45] =ret[45] + ' | ' + str(keypeople.get('title'))
                        ret[46] =ret[46] + ' | ' + str(keypeople.get('avatar'))
            except ValueError as e:
                print("Value error in x.get('details').get('keypeople'):{}".format(email))
                

        if x.get('dataAddOns'):
            for dataAdd in x.get('dataAddOns'):
                try:
                    ret[47] =ret[47] + ' | ' + str(dataAdd.get('id'))
                    ret[48] =ret[48] + ' | ' + str(dataAdd.get('name'))
                    ret[49] =ret[49] + ' | ' + str(dataAdd.get('enabled'))
                    ret[50] =ret[50] + ' | ' + str(dataAdd.get('applied'))
                    ret[51] =ret[51] + ' | ' + str(dataAdd.get('description'))
                    ret[52] =ret[52] + ' | ' + str(dataAdd.get('docLink'))
                except ValueError as e:
                    print("Value error in x.get('details').get('dataAddOns'):{}".format(email))
        # print(ret)    
        return ret
    ###########################################

    @app.route('/')
    def index():
        form = IndexForm()
        return render_template('index.html', title='Scraper via FullContactAPI', form=form)
    @app.route('/', methods=['GET', 'POST'])
    def index_submit():
        form = IndexForm()
        if request.method == 'POST':
            
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            if file.filename == '':
                flash('No file selected for uploading')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_dir,"tmp",filename))
                
            else:
                flash('Allowed file types are txt or csv')
                return redirect(request.url)
                
           
            api_key=form.api_key.data
            if form.validate_on_submit():
                
                ##################################
                
                with open(os.path.join(current_dir,"tmp",filename)) as input_file, open('output.csv','w') as output:
                    csv_reader = csv.reader(input_file, delimiter=',')
                    csv_out = csv.writer(output,delimiter=',')
                    csv_out.writerow(column_names)

                    line_count = 0
                    for row in csv_reader:
                        if row:
                            email = row[0]
                            line_count += 1
                            if line_count%100 == 0:
                                time.sleep(30)
                            try: 
                                # response = call_fullcontact(email, api_key)
                                req = urllib.request.Request('https://api.fullcontact.com/v3/person.enrich')
                                req.add_header('Authorization', 'Bearer {}'.format(api_key))
                        
                                data = json.dumps({
                                    "email": "{}".format(email)
                                })

                                response = urllib.request.urlopen(req, data.encode())
                            
                                x = response.read().decode('utf-8')
                                xx = json.loads(x)
                                # f = csv.writer(open("output.csv", "w"))
                                # f.writerow(column_names)
                                csv_out.writerow(get_csv_row(xx, email))
                            except urllib.error.HTTPError as e:
                                print('API HTTPrequest handling error{0}:{1}'.format(e.getcode(), email))
                                if e.getcode() == 403:
                                    time.sleep(300)
                                    print('rised x-limit, so please for a while...')
                                xx = {}
                                csv_out.writerow(get_csv_row(xx, email))
                            except urllib.error.URLError as e:
                                # Not an HTTP-specific error (e.g. connection refused)
                                # ...
                                print('URLError: {0}:{1}'.format(e.reason, email))
                                xx = {}
                                csv_out.writerow(get_csv_row(xx, email))           
                                
                    flash('Hello, Success!')  
                    
                ##################################

            else:
                flash('Error: All Fields are Required')

        # load registration template
        return render_template('index.html', title='Scraper via FullContactAPI', form=form)

    return app