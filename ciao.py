class CompanyForm(Form):
    ticker = StringField('ticker', [validators.Length(min=1, max=50)])


@app.route('/company', methods = ['GET','POST'])
def getCompany():
    form = CompanyForm(request.form)
    if request.method == 'POST':
        ticker = request.form['ticker']
        
    return render_template('company.html', form = form)