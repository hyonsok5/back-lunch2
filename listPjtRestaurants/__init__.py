import logging

import azure.functions as func
import json
import psycopg2
import os

DB_NAME = os.environ["DB_NAME"]
DB_USER = os.environ["DB_USER"]
DB_URL = os.environ["DB_URL"]
DB_PASSWORD = os.environ["DB_PASSWORD"]


def main(req: func.HttpRequest) -> func.HttpResponse:
    #logging.info('Python HTTP trigger function processed a request.')

    pjtName = req.params.get('pjtName')
    
    conn = psycopg2.connect(dbname=DB_NAME,
                        user=DB_USER,
                        host=DB_URL,
                        password=DB_PASSWORD,
                        sslmode='require')
    
    cur = conn.cursor()  
    cur.execute("""select a.name, 
                          a.projectid,
                          b.name as pjtname,
                          c.cnt as cnt 
                from restaurants a left join 
                        (select menu , projectid, count(*) as cnt 
                        from menu_selected  
                        where substring(date,1,7) = to_char(now(),'YYYY/MM')
                        group by menu, projectid) c 
                on a.name = c.menu  
                and a.projectid =c.projectid, projects b
                where a.projectid = b.id
                and b.name=%s  
                and b.useyn='Y'
                and a.useyn='Y'
                order by a.name
                """,[pjtName])
    
    rows = cur.fetchall()
    
    cur.close()
    
    columns = ('name','projectid','pjtname','cnt')
    resultsJson =[]  
    for row in rows:
        resultsJson.append(dict(zip(columns,row)))

    data = json.dumps(resultsJson)

    func.HttpResponse.mimetype = 'application/json'
    return func.HttpResponse(data)