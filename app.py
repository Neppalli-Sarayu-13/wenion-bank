from flask import Flask,request,redirect,url_for,render_template,make_response
from datetime import datetime
app=Flask(__name__)
userdata={}
statements={}
def get_logged_in_user():
    useremail = request.cookies.get('userid')

    if not useremail or useremail not in userdata:
        return None

    return useremail
@app.route('/',methods=['GET'])
def home():
    return render_template('welcome.html')
@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=="POST":
        print(request.form)
        username=request.form['username']
        useremail=request.form['useremail']
        password=request.form['userpassword']
        userpinno = request.form['pinno'].strip()
        if useremail not in userdata:
            userdata[useremail]={'username':username,'userpassword':password,'userpinno':userpinno,'Amount':0}
            if useremail not in statements:
                statements[useremail]={'deposit_statements':[],'withdraw_statements':[]}
            return redirect(url_for('login'))
        else:
            return 'user already exists'
    return render_template('register.html') 
@app.route('/login',methods=['GET','POST'])   
def login():
    if request.method=="POST":
        print(request.form)
        login_useremail=request.form['useremail']
        login_password = request.form['userpassword']
        if login_useremail in userdata:
            if userdata[login_useremail]['userpassword'] == login_password:
                resp=make_response(redirect(url_for('dashboard')))
                resp.set_cookie('userid',login_useremail)
                return resp
            else:
                return 'password was wrong'
        else:
            return 'Invalid user email'
    return render_template('login.html')
@app.route('/dashboard')
def dashboard():
    useremail = get_logged_in_user()

    if useremail is None:
        resp = make_response(redirect(url_for('login')))
        resp.delete_cookie('userid')
        return resp
    return render_template('dashboard.html')
@app.route('/deposit',methods=['GET','POST'])
def deposit():
    if request.cookies.get('userid'):
        if request.method=='POST':
            useremail=request.cookies.get('userid')
            deposit_amount = int(request.form['amount'])
            if deposit_amount>0:
                if deposit_amount%100==0:
                    if deposit_amount<=50000:
                        userdata[useremail]['Amount']=userdata[useremail]['Amount']+deposit_amount
                        deposit_time=datetime.now()#generate time
                        deposit_data=(deposit_amount,deposit_time)
                        statements[useremail]['deposit_statements'].append(deposit_data)
                        return redirect(url_for('balance'))
                    else:
                        return f'Amount exceeded than 50000'
                return f'Amount should be multiple of 100'
            return f'Amount should be greater than 0'
        return render_template('deposit.html')
    else:
        return redirect(url_for('login'))
@app.route('/withdraw',methods=['GET','POST'])
def withdraw():
    if request.cookies.get('userid'):
        if request.method=='POST':
            useremail=request.cookies.get('userid')
            withdraw_amount=int(request.form['amount'])
            if withdraw_amount>0:
                if withdraw_amount%100==0:
                    if withdraw_amount<=userdata[useremail]['Amount']:
                        userdata[useremail]['Amount']=userdata[useremail]['Amount']-withdraw_amount
                        withdraw_time=datetime.now()
                        withdraw_data=(withdraw_amount,withdraw_time)
                        statements[useremail]['withdraw_statements'].append(withdraw_data)
                        return redirect(url_for('balance'))
                    else:
                        return f'Amount Exceeded than balance amount'
                return f'Amount should be multiple of 100'
            return f'Amount should be greater than 0'
        return render_template('withdraw.html')
    else:
        return redirect(url_for('login'))
@app.route('/balance')
def balance():
    useremail = request.cookies.get('userid')

    if not useremail:
        return redirect(url_for('login'))

    # Check whether this user exists in the current application data
    if useremail not in userdata:
        resp = make_response(redirect(url_for('login')))
        resp.delete_cookie('userid')
        return resp

    balance_amount = userdata[useremail]['Amount']

    return render_template(
        'balance.html',
        balance_amount=balance_amount
    )
# @app.route('/dummy')
# def dummy():
#     name='sarayu'
#     age=23
#     return render_template('dummy.html',username=name,age=age)
# def dummy():
#     return render_template('dummy.html',userdata=userdata)
@app.route('/userstatements')
def userstatements():
    if request.cookies.get('userid'):
        useremail = request.cookies.get('userid')

        # Safely get transaction statements
        user_data = statements.get(useremail, {
            'deposit_statements': [],
            'withdraw_statements': []
        })

        user_deposit_statements = user_data.get(
            'deposit_statements', []
        )
        user_withdraw_statements = user_data.get(
            'withdraw_statements', []
        )

        # Safely get the account balance
        account_data = userdata.get(useremail, {})
        balance_amount = account_data.get('Amount', 0)

        return render_template(
            'userstatements.html',
            user_deposit_statements=user_deposit_statements,
            user_withdraw_statements=user_withdraw_statements,
            balance_amount=balance_amount
        )

    else:
        return redirect(url_for('login'))
@app.route('/logout')
def logout():
    if request.cookies.get('userid'):
        resp=make_response(redirect(url_for('login')))
        resp.delete_cookie('userid')
        return resp
    else:
        return redirect(url_for('login'))
if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)