import datetime
from email.policy import default
from flask import Flask, flash, redirect, render_template, request, session, url_for

from dbconnection.datamanipulation import sql_edit_insert, sql_query, sql_query2
from flask import jsonify


email=Flask(__name__)

email.secret_key='supersecretkey'

@email.route('/')
def home():
    return render_template('index.html')

@email.route('/registrationtable')
def registrationtable():
    return render_template('registration.html')

@email.route('/register',methods=['POST'])
def register():
    name=request.form['name']
    gender=request.form['gender']
    address=request.form['address']
    country=request.form['country']
    phonenumber=request.form['phonenumber']
    username=request.form['username']
    password=request.form['password']
    sql_edit_insert('insert into Register_tb values(NULL,?,?,?,?,?,?,?)',(name,gender,address,country,phonenumber,username+"@mymail.com",password))
    flash('Registration is successfull')
    return redirect(url_for('registrationtable'))

@email.route('/get_username')
def get_username():
    user=request.args.get('as')
    data=sql_query2("select * from Register_tb where username=?",[user+'@mymail.com'])
    if len(data)>0:
        ab="exist"
    else:
        ab="not exist"
    return jsonify({'valid':ab})

@email.route('/view')
def view():
    id=session['id']
    ab=sql_query2('select * from Register_tb where id=?',[id])
    return render_template("view.html",a=ab)

@email.route('/login')
def login():
    return render_template('login.html') 

@email.route('/page')
def page():
    return render_template('page.html')

@email.route('/loginclick',methods=['POST'])
def loginclick():
    username=request.form['username'] 
    password=request.form['password']
    ba=sql_query2('select * from Register_tb where username=? and password=?',(username,password))
    if len(ba)>0:
        session['id']=ba[0][0]
        flash('logined successfully..')
        return redirect(url_for('page'))
        
    else:
        flash('failed to login..')
        return render_template(url_for('registration.html'))    
 

@email.route('/sendmail')
def sendmail():
    return render_template('sendmail.html')

@email.route('/found_user')
def found_user():
    user=request.args.get('ab')
    data=sql_query2('select * from Register_tb where username=?',[user])
    if len(data)>0:
        an='found'
    else:
        an='not found' 
    return jsonify({'valid':an}) 

@email.route('/mail',methods=['post'])
def mail():
    senderid=session['id']
    reciver=request.form['recivername']
    message=request.form['message']  
    subject=request.form['subject']
    date=datetime.date.today()
    time=datetime.datetime.now().strftime("%H:%M")
    status="pending"
    b=sql_query2('select * from Register_tb where username=?',[reciver])
    reciverid=b[0][0]
    sql_edit_insert('insert into Mail_tb values (NULL,?,?,?,?,?,?,?)',(senderid,reciverid,message,subject,date,time,status))
    flash('mail sended')
    return redirect(url_for('sendmail'))

@email.route('/mailview')
def mailview():
    senderid=session['id']
    ba=sql_query2('select Register_tb.username,Mail_tb.* from Register_tb inner join Mail_tb on Register_tb.id=Mail_tb.reciverid where senderid=? and status!=?',[senderid,"deleted by sender"])
    return render_template('mailview.html',b=ba)

@email.route('/update')
def update():
    id=request.args.get('ab')
    a=sql_query2('select * from Mail_tb where id=?',[id])
    status=a[0][7]
    if status=='pending':
        ab=sql_edit_insert('update Mail_tb set status=? where id=?',("deleted by sender",id))
    else:
        sql_edit_insert('delete from Mail_tb where id=?',[id])
    return redirect('mailview')

@email.route('/reciverview')
def reciverview():
    reciverid=session['id']
    ab=sql_query2('select Register_tb.username,Mail_tb.* from Register_tb inner join Mail_tb on Register_tb.id=Mail_tb.senderid where reciverid=? and Mail_tb.id not in(select messageid from Trash_tb where userid=?)',[reciverid,reciverid])    
    return render_template('reciverview.html',a=ab)

@email.route('/fowardmessage')
def fowardmessage():
    id=request.args.get('ab')
    ab=sql_query2('select * from Mail_tb where id=?',[id])
    return render_template('fowardmessage.html',n=ab)

@email.route('/foward',methods=['post'])
def foward():
    senderid=session['id']
    reciver=request.form['recivername']
    message=request.form['message']  
    subject=request.form['subject']
    date=datetime.date.today()
    time=datetime.datetime.now().strftime("%H:%M")
    status="pending"
    b=sql_query2('select * from Register_tb where username=?',[reciver])
    reciverid=b[0][0]
    sql_edit_insert('insert into Mail_tb values (NULL,?,?,?,?,?,?,?)',(senderid,reciverid,message,subject,date,time,status))
    flash('mail sended')
    return redirect(url_for('reciverview'))

@email.route('/replymessage')
def replymessage():
    am=request.args.get('an')
    ab=sql_query2('select Register_tb.username,Mail_tb.senderid from Register_tb inner join Mail_tb on Register_tb.id=Mail_tb.senderid where Mail_tb.id=?',[am])
    return render_template('replymessage.html',m=ab)

@email.route('/reply',methods=['post'])
def reply():
    senderid=session['id']
    reciver=request.form['username']
    message=request.form['message']  
    subject=request.form['subject']
    date=datetime.date.today()
    time=datetime.datetime.now().strftime("%H:%M")
    status="pending"
    b=sql_query2('select * from Register_tb where username=?',[reciver])
    reciverid=b[0][0]
    sql_edit_insert('insert into Mail_tb values (NULL,?,?,?,?,?,?,?)',(senderid,reciverid,message,subject,date,time,status))
    return redirect(url_for('reciverview'))

@email.route('/trashtable',methods=['post'])
def trashtable():
    senderid=session['id']
    date=datetime.date.today()
    time=datetime.datetime.now().strftime('%H:%M')
    check=request.form.getlist('checkboxes')
    for messageid in check:
        
        ab=sql_edit_insert('insert into Trash_tb values (NULL,?,?,?,?)',(messageid,senderid,date,time))
    flash('mail move to trashbox')
    return redirect(url_for('reciverview'))
@email.route('/trashview')
def trashview():
    senderid=session['id']
    an=sql_query2('select Register_tb.username,Trash_tb.date,Trash_tb.time,Mail_tb.* from(Register_tb inner join Mail_tb on Register_tb.id=Mail_tb.senderid)inner join Trash_tb on Mail_tb.id=Trash_tb.messageid where userid=?',[senderid])
    return render_template('viewtrash.html',b=an)

@email.route('/deletetrash')
def deletetrash():
    id=request.args.get('am')
    a=sql_query2('select * from Mail_tb where id=?',[id])
    status=a[0][7]
    if status=='pending':
        am=sql_edit_insert('update Mail_tb set status=? where id=?',('deleted by user',id))
    else:    
        sql_edit_insert('delete from Mail_tb where id=?',[id])
    sql_edit_insert('delete from Trash_tb where messageid=?',[id])
    return redirect(url_for('trashview'))

@email.route('/updateprofile')
def updateprofile():
    id=request.args.get('ab')
    ab=sql_query2('select * from Register_tb where id=?',[id])
    return render_template('updateprofile.html',a=ab)

@email.route('/updation',methods=['post'])
def updation():
    id=session['id']
    name=request.form['name']
    gender=request.form['gender']
    address=request.form['address']
    country=request.form['country']
    phonenumber=request.form['phonenumber']
    username=request.form['username']
    password=request.form['password']
    sql_edit_insert('update Register_tb set name=?,gender=?,address=?,country=?,phonenumber=?,username=?,password=? where id=?',(name,gender,address,country,phonenumber,username,password,id))
    flash('updated sucessfully')
    return redirect(url_for('view'))

@email.route('/deleteprofile')
def deleteprofile():
    id=request.args.get('ab')
    sql_edit_insert('delete from Register_tb where id=?',[id])
    return redirect(url_for('view'))

@email.route('/logout')
def logout():
    session.clear()
    return redirect('login')
    






    




if __name__=='__main__':
    email.run()
