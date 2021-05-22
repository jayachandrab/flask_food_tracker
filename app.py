from flask import Flask,render_template,g,request
import sqlite3
from datetime import datetime

app = Flask(__name__)

def db_connect():
    sql=sqlite3.connect('foog_log.db')
    sql.row_factory=sqlite3.Row
    return sql
def get_db():
    if not hasattr(g,'sqlite3'):
        g.sqlite_db=db_connect()
    return g.sqlite_db

@app.route('/',methods=['POST',"GET"])
def index():
    db=get_db()
    if request.method=="POST":
        date=request.form['date']
        dt=datetime.strptime(date,"%Y-%m-%d")
        database_date=datetime.strftime(dt,'%Y%m%d')
        db.execute("insert into log_date(entry_date) values(?)",[database_date])
        db.commit()
    
        
    cur=db.execute('''select log_date.entry_date, sum(food.protein) as protein, sum(food.carbohydrates) as carbohydrates,
    sum(food.fat) as fat,(food.calaories)  as calaories from log_date left join food_date 
    on food_date.log_date_id=log_date.id left join food on food.id=food_date.food_id
    group by log_date.id  order by log_date.entry_date desc''')
    results=cur.fetchall()
    date_results=[]
    for i in results:
        single_date={}
        single_date['entry_date']=i['entry_date']
        single_date['protein']= i['protein']
        single_date['carbohydrates']= i['carbohydrates']
        single_date['fat']= i['fat']
        single_date['calaories']=i['calaories']

        d=datetime.strptime(str(i['entry_date']),'%Y%m%d')
        single_date['pretty_date']=datetime.strftime(d,'%B %d, %Y')
        date_results.append(single_date)
    print("results",date_results)
    return render_template('home.html',results=date_results)

@app.route('/view/<date>',methods=["POST","GET"])
def view(date):
    db=get_db()
    cur=db.execute("select id,entry_date from log_date where entry_date=?",[date])
    results=cur.fetchone()
    if request.method=="POST":
        db.execute("insert into food_date(food_id,log_date_id) values(?,?)",[request.form['food-select'],results['id']])
        db.commit()
    
    d=datetime.strptime(str(results['entry_date']),'%Y%m%d')
    pretty_date=datetime.strftime(d,'%B %d,%Y')
    print(pretty_date)

    food_cur=db.execute('select id,name from food')
    food_results=food_cur.fetchall()

    log_cur=db.execute("select food.name,food.protein,food.carbohydrates,food.fat,food.calaories from log_date join food_date on food_date.log_date_id=log_date.id join food on food.id=food_date.food_id\
    where log_date.entry_date=?",[date])
    log_results=log_cur.fetchall()

    totals={}
    totals['protein']=0
    totals['carbohydrates']=0
    totals['fat']=0
    totals['calaories']=0

    for food in log_results:
        totals['protein']+=food['protein']
        totals['carbohydrates']+=food['carbohydrates']
        totals['fat']+=food['fat']
        totals['calaories']+=food['calaories']


    return render_template('day.html',entry_date=results['entry_date'],pretty_date=pretty_date,food_results=food_results,log_results=log_results,totals=totals)

@app.route('/food',methods=["GET","POST"])
def food():
    db=get_db()
    if request.method=='POST':
        name=request.form['food_name']
        protein=int(request.form['protein'])
        carbo=int(request.form['carbo'])
        fat=int(request.form['fat'])
        calories=protein*4+carbo*4+fat*9
        db=get_db()
        db.execute('insert into food(name,protein,carbohydrates,fat,calaories) values(?,?,?,?,?)',[name,protein,carbo,fat,calories])
        db.commit()
    cur=db.execute('select name,protein,carbohydrates,fat,calaories from food')
    results=cur.fetchall()
        #return "<h1>Name:{} Protein:{} carbs:{} fat{}</h1>".format(request.form['food_name'],request.form['protein'],request.form['carbo'],request.form['fat'])
    

    return render_template('add_food.html',results=results)

if __name__=='__main__':
    app.run(debug=True)