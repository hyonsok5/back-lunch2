import logging

import azure.functions as func
import json
import psycopg2


DB_NAME = process.env["DB-NAME"]
DB_USER = process.env["DB-USER"]
DB_URL = process.env["DB-URL"]
DB_PASSWORD = process.env["DB-PASSWORD"]

   
def main(req: func.HttpRequest) -> func.HttpResponse:
    # logging.info('Python HTTP trigger function processed a request.')

    conn = psycopg2.connect(dbname=DB_NAME,
                        user=DB_USER,
                        host=DB_URL,
                        password=DB_PASSWORD,
                        sslmode='require')
     
    date = req.params.get('date')
    password = req.params.get('password')
    division = req.params.get('division')
      
    cur = conn.cursor()
    cur.execute("""select distinct a.menu, a.name
                              from menu_selected a, projects b 
                              where a.name != 'null' 
                              and a.date=%s
                              and a.projectid=b.id  
                              and b.name =%s
                              and a.division =%s
                              order by menu      
                               """,[date,password,division])
    
    rows = cur.fetchall()
   
    cur.close()

    columns = ('menu','name')
    resultsJson =[]
    for row in rows:
        resultsJson.append(dict(zip(columns,row)))

    data = json.dumps(resultsJson)

    func.HttpResponse.mimetype = 'application/json'
    return func.HttpResponse(data)
 
 
 
 
