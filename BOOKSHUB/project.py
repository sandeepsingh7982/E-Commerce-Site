from logging import debug
from flask import Flask, render_template, request,redirect,session,url_for
import sqlite3 as sql
import os

app=Flask(__name__)
app.secret_key=os.urandom(25)


# @app.before_first_request
# def before():
#     database='bookshouse.db'
#     with sql.connect(database) as conn:
#         Cursor=conn.cursor()
#         query1='''CREATE TABLE IF NOT EXISTS books
#                 (product_id INTEGER PRIMARY KEY, product_name TEXT[50],
#                 qty INTEGER, price INTEGER, desc TEXT[300], img_url TEXT[100])'''
#         Cursor.execute(query1)
#         query2='''CREATE TABLE IF NOT EXISTS details
#                 (sno INTEGER PRIMARY KEY AUTOINCREMENT, p_id INTEGER, name TEXT[50], email TEXT[60], mobile_no INTEGER,
#                 qty INTEGER, address TEXT[300])'''
#         Cursor.execute(query2)
#         query3='''CREATE TABLE IF NOT EXISTS buyerdetails
#                 (sno INTEGER PRIMARY KEY AUTOINCREMENT, p_id INTEGER, name TEXT[50], email TEXT[60], mobile_no INTEGER,
#                 qty INTEGER, address TEXT[300])'''
#         Cursor.execute(query3)
#         query4='''CREATE TABLE IF NOT EXISTS users
#                 (user_id integer primary key AUTOINCREMENT,name text[50],email text[50],password varchar[50])'''
#         Cursor.execute(query4)


@app.route('/',methods=['GET','POST'])
def home():
    if(request.method=='POST'):
        data=dict(request.form)
        values=list(data.values())
        with sql.connect('bookshouse.db') as conn:
            cursor=conn.cursor()
            query='select * from users where email=? and password=?'
            cursor.execute(query,values)
            user=cursor.fetchall()
            if len(user)>0:
                session['user_id']=user[0][0]
                session['user_name']=user[0][1].upper()
                return redirect(url_for('card'))
            else:
                return redirect('/')   
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if(request.method=='POST'):
        data=dict(request.form)
        values=list(data.values())
        with sql.connect('bookshouse.db') as conn:
            cursor=conn.cursor()
            query='INSERT INTO users(name,email,password) values(?,?,?)'
            cursor.execute(query,values)
            conn.commit()
        return redirect('/')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/card')
def card():
    with sql.connect('bookshouse.db') as conn:
        cursor=conn.cursor()
        cursor.execute("select * from books")
        b_data=cursor.fetchall()
        if 'user_id' in session:    
            return render_template('cards.html',b=b_data,s=session)
        else:
            return redirect('/')

@app.route('/insert',methods=['GET','POST'])
def insert():
    if 'user_id' in session:  
        if(request.method=='POST'):
            data=dict(request.form)
            values=list(data.values())
            with sql.connect('bookshouse.db') as conn:
                cursor=conn.cursor()
                query='INSERT INTO books(product_id,product_name,qty,price,desc,img_url) values(?,?,?,?,?,?)'
                cursor.execute(query,values)
                conn.commit()
            return render_template('insert.html',s=session)    
        return render_template('insert.html',s=session)
    else:
        return redirect('/')

   

@app.route('/view/<int:product_id>')
def view(product_id):
    if 'user_id' in session:  
        with sql.connect('bookshouse.db') as conn:
            cursor=conn.cursor()
            query="select * from books where product_id=?"
            cursor.execute(query,(product_id,))
            data=cursor.fetchall()
        return render_template('view.html',d=data,s=session)
    else:
        return redirect('/')

@app.route('/buynow/<int:product_id>')
def quantity(product_id):
    with sql.connect('bookshouse.db') as conn:
        cursor=conn.cursor()
        query="select * from books where product_id=?"
        cursor.execute(query,(product_id,))
        data=cursor.fetchall()
        if 'user_id' in session:  
            return render_template('buynow.html',q=data,s=session)
        else:
            return redirect('/')

@app.route('/buynow/<int:product_id>',methods=['GET','POST'])
def buynow(product_id):
    if(request.method=='POST'):
        data=dict(request.form)
        values=list(data.values())
        with sql.connect('bookshouse.db') as conn:
            cursor=conn.cursor()
            query='INSERT INTO details(p_id,name,email,mobile_no,qty,address) values(?,?,?,?,?,?)'
            cursor.execute(query,values)
            conn.commit()
    return redirect('/update')


@app.route('/buyerdetails')
def buyerdetails():
    if 'user_id' in session:  
        with sql.connect('bookshouse.db') as conn:
            cursor=conn.cursor()
            # now fetch data from buyerdetails table
            query="select * from buyerdetails"
            cursor.execute(query)
            data=cursor.fetchall()
        return render_template('buyerdetails.html',d=data,s=session)
    else:
        return redirect('/')


@app.route('/update')
def update():
    
        with sql.connect('bookshouse.db') as conn:
            # fetch data from details table
            cursor=conn.cursor()
            query="select * from details"
            cursor.execute(query)
            data=cursor.fetchall()
            values=data[0][1:7]
            
    # enter data into buyerdetails table 
            query='INSERT INTO buyerdetails(p_id,name,email,mobile_no,qty,address) values(?,?,?,?,?,?)'
            cursor.execute(query,values)
            conn.commit()
        with sql.connect('bookshouse.db') as conn:
            cursor=conn.cursor()
            query="select * from books"
            cursor.execute(query)
            b_data=cursor.fetchall()
            a=len(b_data)
            query="select * from details"
            cursor.execute(query)
            d_data=cursor.fetchall()
            if 'user_id' in session:  
                for i in range(a):
                    if len(d_data)!=0:
                        if (b_data[i][0]==d_data[0][1]):
                            temp=[]
                            temp.append(b_data[i][2]-d_data[0][5])
                            temp.append(b_data[i][0])
                            query='''update books 
                                    SET qty=?
                                    WHERE product_id=?'''
                            cursor.execute(query,temp)
                            conn.commit()
                
                            query='delete from details'
                            cursor.execute(query)
                            conn.commit()
                return render_template('done.html',d=data,s=session)
            else:
                return redirect('/')

# @app.route('/done')
# def done():
#     with sql.connect('bookshouse.db') as conn:
#         cursor=conn.cursor()
#         # now fetch data from buyerdetails table
#         query="select * from buyerdetails"
#         cursor.execute(query)
#         data=cursor.fetchall()
#     return render_template('buyerdetails.html',d=data)

@app.route('/deletebyid/<int:sno>')
def deletebyid(sno):
    if 'user_id' in session:  
        with sql.connect('bookshouse.db') as conn:
            cursor=conn.cursor()
            query='delete from buyerdetails where sno=?;'
            cursor.execute(query,(sno,))
            conn.commit()
        return redirect('/buyerdetails')
    else:
        return redirect('/')


@app.route('/updatebooks/<int:id>',methods=['GET','POST'])
def updatebooks(id):
    if 'user_id' in session:  
        a=id
        with sql.connect('bookshouse.db') as conn:
            cursor=conn.cursor()
            #query='''select * from books where product_id=id'''
            cursor.execute(f"select * from books where product_id={id}")
            data=cursor.fetchall()
            print(data)
            if (request.method=="POST"):
                data=dict(request.form)
                values=list(data.values())
                values.append(id)
                query='''update books 
                        SET product_id=?, product_name=?,
                        qty=?,price=?,desc=?,
                        img_url=?
                        WHERE product_id=?''' 
                cursor.execute(query,values)
                conn.commit()
                return redirect('/card')
        return render_template('update.html',d=data,a=a,s=session)
    else:
        return redirect('/')





app.run(debug=True)