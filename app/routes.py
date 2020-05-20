from flask import render_template, redirect, url_for, request
from app import app
from app.form import IncomeForm
from app.validation import Validator, encode
from app.mongodb import mongodb


db = mongodb()

@app.route('/form', methods=['GET', 'POST'])
def form():
    form = IncomeForm()
    if form.validate_on_submit():
        f = request.files['payslip']
        fn = f.filename
        if fn == '':
            return redirect(url_for('failure'))
        
        # run image validation
        img_str = encode(f.read())
        validator = Validator()
        validator.validate(img_str, request.form.get('name'), request.form.get('income'), request.form.get('age'), request.form.get('cpf'))

        if validator.status_code == 400: # image scan failed
            return redirect(url_for('failure'))
        elif validator.status_code == 500: # internal backend error, allow raw img to send
            print(validator.error)
            db.insert_record(
                request.form.get('name'), request.form.get('nric'), request.form.get('age'), 
                request.form.get('income'), request.form.get('cpf'),
                request.form.get('address'), request.form.get('lease_id'), img_str
            )
        
        else: # status = 200, all good
            db.insert_record(
                request.form.get('name'), request.form.get('nric'), request.form.get('age'), 
                request.form.get('income'), request.form.get('cpf'),
                request.form.get('address'), request.form.get('lease_id'), 
                img_str, validator.income, validator.highlight, validator.verified, validator.renewable, validator.verify_fail, validator.renew_fail
            )

        return redirect(url_for('success'))

    return render_template('form.html', title='Homepage', form=form)

@app.route('/success')
def success():
    return "Upload Successful. Thank you for using our app!"

@app.route('/failure')
def failure():
    return "Upload unsuccessful. Please ensure a payslip image is submitted, and the image quality is clear."

@app.route('/admin')
def admin():
    records = db.get_records()
    return render_template('admin.html', title='Branch', records=records)

@app.route('/post_updates')
def post_updates():
    resp = request.args
    update_success = db.update_record(resp['id'], resp['income'], resp['verified'], resp['renew'])
    return update_success

@app.route('/archive')
def archive():
    resp = request.args
    archive_record = db.archive(resp['id'])
    return archive_record