from flask import Flask, request
from flask import render_template
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import *

import pymysql
from py2neo import Graph,Node,Relationship
import csv

application = app = Flask(__name__)
# api = Api(app)
bootstrap = Bootstrap(app)
def getConnection():
    return pymysql.connect(host="cs411.cd9xk2f9aw5m.us-east-2.rds.amazonaws.com",
                           user="yilunzhao",
                           password="mysqlcs411",
                           db="sample",
                           charset='utf8')


def insert_data(date, country, ISO_code, Uncertainty_bound, number):
    sql = "INSERT INTO mortality_rate VALUES ('{}', '{}', '{}', '{}', '{}')".format(date, country, ISO_code, Uncertainty_bound, number)
    db = getConnection()
    cur = db.cursor()
    cur.execute(sql)
    db.commit()
    cur.close()
    db.close()

def search_country(country):
    sql = "SELECT * FROM mortality_rate  WHERE country = '{}'".format(country)
    db = getConnection()
    cur = db.cursor()
    cur.execute(sql)
    u = cur.fetchall()
    cur.close()
    db.close()
    return render_template('dataM.html',u=u)

def interest_query1(country):
    sql = "SELECT * FROM mortality_rate mr NATURAL JOIN mortality_number mn WHERE mr.country = '{}'".format(country)
    db = getConnection()
    cur = db.cursor()
    cur.execute(sql)
    u = cur.fetchall()
    cur.close()
    db.close()
    return render_template('dataM.html', u=u)
def interest_query2(country1, country2):
    sql = " SELECT AVG(rate), country FROM mortality_rate WHERE country = '{}' GROUP BY country  UNION  SELECT AVG(rate),country FROM mortality_rate  WHERE country = '{}' GROUP BY country ".format(country1, country2)
    db = getConnection()
    cur = db.cursor()
    cur.execute(sql)
    u = cur.fetchall()
    print("result",u)
    cur.close()
    db.close()
    return render_template('dataM.html', u=u)

# delete the data of one country
def delete_country(country):
    sql = "DELETE FROM mortality_rate WHERE country = '{}'".format(country)
    db = getConnection()
    cur = db.cursor()
    cur.execute(sql)
    db.commit()
    cur.close()
    db.close()


# uodate the number of one country and uncertainty is "Lower"
def update_country_number(country, number):
    sql = "UPDATE mortality_rate SET rate = '{}' WHERE country = '{}' AND Uncertainty_bounds = 'Lower'".format(number, country)
    db = getConnection()
    cur = db.cursor()
    cur.execute(sql)
    db.commit()
    cur.close()
    db.close()

# def visulization(country, startyear, endyear, uncertitybound):
#
#     print("pass", country, startyear, endyear, uncertitybound)
def list_cause_name():
    graph = getConnection_neo4j()
    query = "MATCH (n) WHERE EXISTS(n.cause_name) RETURN n.cause_name AS cause_name LIMIT 25 UNION ALL MATCH ()-[r]-() WHERE EXISTS(r.cause_name) RETURN DISTINCT r.cause_name AS cause_name LIMIT 25"
    query_result = graph.run(query).data()
    result = []
    for n in query_result:
        result.append(n['cause_name'])
    return result

def visulization(country, startyear, endyear, uncertitybound):
    threeline = False

    # assign default value
    if (startyear == "0"):
        startyear = "1985"
    if (endyear == "0"):
        endyear = "2018"
    if (uncertitybound == "0"):
        threeline = True
        uncertitybound = "Lower"

    sql = "SELECT date, rate FROM mortality_rate WHERE country = '{}' AND Uncertainty_bounds = '{}' AND date >= {} AND date <= {}".format(
        country, uncertitybound, float(startyear), float(endyear))
    sql1 = "SELECT rate FROM mortality_rate WHERE country = '{}' AND Uncertainty_bounds = 'Median' AND date >= 1985.5 AND date <= 2039.5 ORDER BY date ".format(
        country)
    db = getConnection()
    cur = db.cursor()
    cur.execute(sql)
    see = cur.fetchall()
    cur.execute(sql1)
    see1 = cur.fetchall()

    xvals = []
    mortality_rate = []
    large_rate = []

    for data in see:
        xvals.append(data[0])
        mortality_rate.append(data[1])

    for data in see1:
        large_rate.append(data[0])

    return xvals, mortality_rate, large_rate


def getConnection_neo4j():
    return Graph('bolt://18.221.191.154:7687', username='neo4j', password='YgCeDtCqosS3')


def search_neo4j_by_cause_name(cause_name):
    graph = getConnection_neo4j()
    # query = "MATCH p=(ca:Cause{cause_name:'${}'})-[caco:cause_death]->(co:Country) RETURN p ORDER BY caco.cause_death_per_country DESC LIMIT 100".format(reason)
    query = "MATCH (c:Country) <- [r:cause_death] - (ca:Cause) WHERE ca.cause_name = '{}' RETURN c.country_name AS country, r.cause_death_per_country AS rate ORDER BY rate DESC LIMIT 10".format(cause_name)
    query_result = graph.run(query).data()
    country_data = []
    for n in query_result:
        country_dict = {}
        country_dict['name'] = n['country']
        country_dict['value'] = [n['rate'], n['country']]
        country_data.append(country_dict)
    data = [{"time": cause_name, "data": country_data}]
    #data = json.dumps(data)
    return data

def csvM(country1, country2,country3,country4,country5,country6):

    print("in csvm",country1, country2)

    # open csv to read
    csvFile = open("static/src/country-data.csv", "r")
    reader = csv.reader(csvFile)

    # open csv to write
    fileHeader = ["name", "type","value","date"]
    tempcsvFile = open("tempcsv.csv", "w")
    writer = csv.writer(tempcsvFile)
    writer.writerow(fileHeader)


    for item in reader:
        # 忽略第一行
        d = []
        if (item[0] == country1 or item[0] == country2 or item[0] == country3 or item[0] == country4 or item[0] == country5 or item[0] == country6):
            # print(item[0])
            # print("/n")
            d.append(item[0])
            d.append(item[1])
            d.append(item[2])
            d.append(item[3])

            writer.writerow(d)

        # result[item[0]] = item[1]

    csvFile.close()

    tempcsvFile.close()

    return



def csvData(country1, country2,country3,country4,country5,country6):

    print("in csvm",country1, country2)

    # open csv to read
    csvFile = open("static/src/country-data.csv", "r")
    reader = csv.reader(csvFile)

    d = "name,type,value,date\n"

    # d = ["name", "type","value","date"]
    for item in reader:
        # 忽略第一行

        if (item[0] == country1 or item[0] == country2 or item[0] == country3 or item[0] == country4 or item[0] == country5 or item[0] == country6):
            # print(item[0])
            # print("/n")
            # d.append(item[0])
            # d.append(item[1])
            # d.append(item[2])
            # d.append(item[3])
            d = d + item[0] + ","
            d = d + item[1] + ","
            d = d + item[2] + ","
            d = d + item[3]
            d = d + "\n"


        # result[item[0]] = item[1]

    csvFile.close()

    # print(d)

    return d

@app.route('/', methods=['GET','POST'])
def home():
        return render_template('home.html')

@app.route('/story', methods=['GET','POST'])
def story():
        return render_template('story.html')

@app.route('/email', methods=['GET','POST'])
def email():
        return render_template('email.html')

@app.route('/rundata', methods=['GET','POST'])
def run():
        # print("running")
        if request.method == "POST":
            if request.form['input'] == "Visualization":

                country1 = request.form.get('country1')
                country2 = request.form.get('country2')
                country3 = request.form.get('country3')
                country4 = request.form.get('country4')
                country5 = request.form.get('country5')
                country6 = request.form.get('country6')
                # country2 = "hahahah"
                print("country1 is ",country1,"country2 is ",country2)
        else:
            country1 = ""
            country2 = ""
            country3 = ""
            country4 = ""
            country5 = ""
            country6 = ""
        db = getConnection()
        cur = db.cursor()
        # SELECT date, number FROM mortality_rate WHERE
        sql2 = "SELECT DISTINCT country FROM mortality_rate"
        cur.execute(sql2)
        u2 = cur.fetchall()
        db.close()

        csvM(country1,country2,country3,country4,country5,country6)
        d = csvData(country1,country2,country3,country4,country5,country6)
        print(d)

        # data_file = open('app/Dog-Data.csv')



        return render_template ('rundata.html', u2 = u2,country1 = country1, country2 = country2, d = d)

@app.route('/map', methods=['GET','POST']) #页面链接该路由名称
def map():
    if request.method == "POST":
        if request.form['input'] == "map_visualization":
            cause_name = request.form.get('cause_name')
            print(cause_name)
            datas = search_neo4j_by_cause_name(cause_name)
    else:
        datas = []
    u = list_cause_name()
    return render_template('map.html', u = u, datas = datas)

#
# @app.route('/jstest', methods=['GET','POST'])
# def jstest():
#         if request.method == "POST":
#             if request.form['input'] == "Visualization":
#
#                 country1 = request.form.get('country1')
#                 country2 = request.form.get('country2')
#                 # country2 = "hahahah"
#                 print("country1 is ",country1,"country2 is ",country2)
#         else:
#             country1 = ""
#             country2 = ""
#
#
#
#         db = getConnection()
#         cur = db.cursor()
#         # SELECT date, number FROM mortality_rate WHERE
#         sql2 = "SELECT DISTINCT country FROM mortality_rate"
#         cur.execute(sql2)
#         u2 = cur.fetchall()
#         db.close()
#         return render_template ('jstest.html', u2 = u2,country1 = country1, country2 = country2)
#
#         # return render_template('jstest.html')

@app.route('/graph', methods=['GET','POST'])
def graph():
    if request.method == "POST":
        if request.form['input'] == "Visualization":
            charitysupport = request.form.get('charitysupport')
            deathreason = request.form.get('deathreason')
            socialreason = request.form.get('socialreason')



    else:
        charitysupport = {}
        deathreason = {}
        socialreason = {}
    print(charitysupport,deathreason,socialreason)
    return render_template('graph.html', deathreason = deathreason, charitysupport = charitysupport, socialreason = socialreason)


searchM = False
searchq1 = False
searchq2 = False
@app.route('/dataM', methods=['GET','POST'])
def dataM():
    global searchM
    global searchq1
    global searchq2
    global country
    global c1
    global c2
    global interest_country
    if request.method == "POST":
        if request.form['input'] == "Insert":
            searchM = False
            searchq1 = False
            searchq2 = False
            form = request.form.to_dict()

            # data to read
            date = form['inputDate']
            country = form['inputCountryName']
            ISO_code = form['inputISO_code']
            Uncertainty_bound = form['inputUncertaintyBounds']
            number = form['inputMortalityNumber']

            insert_data(date, country, ISO_code, Uncertainty_bound, number)
        if request.form['input'] == "Search":
            form = request.form.to_dict()
            country = form['inputSearchedCountry']
            searchM = True
            searchq1 = False
            searchq2 = False
        if request.form['input'] == "Delete":
            searchM = False
            searchq1 = False
            searchq2 = False
            form = request.form.to_dict()
            country = form['inputDeletedCountry']
            delete_country(country)
        if request.form['input'] == "Update":
            searchM = False
            searchq1 = False
            searchq2 = False
            form = request.form.to_dict()
            country = form['inputUpdatedCountry']
            number = form['inputUpdatedNumber']
            update_country_number(country, number)
        if request.form['input'] == "Visualization":
            searchM = False
            searchq1 = False
            searchq2 = False
            country = request.form.get('country')
            startyear = request.form.get('startyear')
            endyear = request.form.get('endyear')
            uncertitybound = request.form.get('uncertitybound')
            visulization(country, startyear, endyear, uncertitybound)
        if request.form['input'] == "Interest Query 1":
            searchM = False
            form = request.form.to_dict()
            interest_country = form['interest_country']
            searchq1 = True
            searchq2 = False
        if request.form['input'] == "Interest Query 2":
            searchM = False
            form = request.form.to_dict()
            c1 = form['interest_query2_country1']
            c2 = form['interest_query2_country2']
            searchq1 = False
            searchq2 = True




    if searchM:
        return search_country(country)
    elif searchq1:
        return interest_query1(interest_country)
    elif searchq2:
        return interest_query2(c1,c2)
    else:
        db = getConnection()
        cur = db.cursor()
        sql = "SELECT * FROM mortality_rate"
        cur.execute(sql)
        u = cur.fetchall()
        db.close()
        return render_template('dataM.html',u=u)

# @app.route('/dataV', methods=['GET','POST']) #页面链接该路由名称
# def f_infor():
#     if request.method == "POST":
#         if request.form['input'] == "Visualization":
#             searchM = False
#             country = request.form.get('country')
#             startyear = request.form.get('startyear')
#             endyear = request.form.get('endyear')
#             uncertitybound = request.form.get('uncertitybound')
#             visulization(country, startyear, endyear, uncertitybound)
#     db = getConnection()
#     cur = db.cursor()
#     sql = "SELECT * FROM mini_sample"
#     cur.execute(sql)
#     u = cur.fetchall()
#     db.close()
#     return render_template('dataV.html',u=u)  # send_file('/templates/testhtm.html') #

@app.route('/dataV', methods=['GET','POST']) #页面链接该路由名称
def f_infor():
    if request.method == "POST":
        if request.form['input'] == "Visualization":
            searchM = False
            country = request.form.get('country')
            startyear = request.form.get('startyear')
            endyear = request.form.get('endyear')
            uncertitybound = request.form.get('uncertitybound')
            xvals, mortality_rate, large_rate = visulization(country, startyear, endyear, uncertitybound)
            print("large:")
            print(large_rate)
            print("len_large")
            print(len(large_rate))
    else:
        xvals = {}
        mortality_rate = {}
        large_rate = {}

    db = getConnection()
    cur = db.cursor()
    sql = "SELECT * FROM mortality_rate"
    cur.execute(sql)
    u = cur.fetchall()
    db.close()

    db = getConnection()
    cur = db.cursor()
    # SELECT date, number FROM mortality_rate WHERE
    sql2 = "SELECT DISTINCT country FROM mortality_rate"
    cur.execute(sql2)
    u2 = cur.fetchall()
    db.close()


    all_year = []
    for i in range(1985,2040):#2018
        all_year.append(i + 0.5)
    print(all_year)
    print("len_year")
    print(len(all_year))

    return render_template ('dataV.html', u=u, u2 = u2, xvals = xvals, mortality_rate = mortality_rate, all_year = all_year, large_rate = large_rate)  # send_file('/templates/testhtm.html') #


@app.route('/manpage', methods=['GET','POST'])
def manpage():
        return render_template('manpage.html')


@app.route('/rawdata') #页面链接该路由名称
def raw():

    db = getConnection()
    cur = db.cursor()
    sql = "SELECT * FROM mortality_rate"
    cur.execute(sql)
    u = cur.fetchall()
    db.close()
    return render_template('rawdata.html',u=u)  # send_file('/templates/testhtm.html') #


@app.route('/forms', methods=['GET','POST']) #页面链接该路由名称
def forms():

    if request.method == "POST":
        if request.form['input'] == "Visualization":
            newdata = request.form.get('country')


    csvFile = open("static/every.csv", "rw")
    reader = csv.reader(csvFile)

    d = []

    # d = ["name", "type","value","date"]
    for item in reader:
        d.append(item)


    csvFile.close()


    d.append(newdata)
    print(d)




    return render_template('forms.html',d = d)  # send_file('/templates/testhtm.html') #

# @app.route('/datablank') #页面链接该路由名称
# def db():
#     db = getConnection()
#     cur = db.cursor()
#     sql = "SELECT * FROM mini_sample"
#     cur.execute(sql)
#     u = cur.fetchall()
#     db.close()
#
#
#     return render_template('datablank.html',u=u)  # send_file('/templates/testhtm.html') #

# @app.route('/temp', methods=['GET','POST']) #页面链接该路由名称
# def temps():
#     return render_template('temp.html')  # send_file('/templates/testhtm.html') #

if __name__ == '__main__':
    app.debug = True
    app.run()
