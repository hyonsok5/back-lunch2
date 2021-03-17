import logging

import azure.functions as func

import json
import psycopg2

import uuid


DB_NAME = process.env["DB-NAME"]
DB_USER = process.env["DB-USER"]
DB_URL = process.env["DB-URL"]
DB_PASSWORD = process.env["DB-PASSWORD"]


def main(req: func.HttpRequest) -> func.HttpResponse:
    #logging.info('Python HTTP trigger function processed a request.')

    conn = psycopg2.connect(dbname=DB_NAME,
                        user=DB_USER,
                        host=DB_URL,
                        password=DB_PASSWORD,
                        sslmode='require')
    
    conn.autocommit = True  
    
    
    req_body = req.get_json()
    logging.info(req_body)
    
    date = req_body['date']
    name = req_body['name']
    projectid = req_body['projectid']
    menu = req_body['menu']
    division = req_body['division']
    

    
    cur = conn.cursor()
   
    cur.execute("""select name, menu,id 
                    from menu_selected
                    where date=%s
                    and name=%s 
                    and projectid=%s
                    and division=%s
                    """,[date,name,projectid,str(division)])
    
    record = cur.fetchone()
    
    id = uuid.uuid4()  
           
    if record:
        if(name == record[0]):
            if(record[1] == menu):
                cur.execute(""" delete from menu_selected
                                where id = %s """,[str(record[2])])
            else:
                cur.execute(""" update menu_selected
                                set menu = %s,
                                    updated = now() 
                                where id = %s """,[menu,str(record[2])])  
    else:
        cur.execute(""" insert into menu_selected
                                (id,name,date,menu,created, projectid,division)
                                values
                                (%s,%s,%s,%s,now(),%s,%s)   
                                """,[str(id),name,date,menu,projectid,str(division)])
    
    cur.close()
            
    data = json.dumps([])
     
    func.HttpResponse.mimetype = 'application/json'
    return func.HttpResponse(data)
