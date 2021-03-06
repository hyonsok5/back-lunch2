import logging

import azure.functions as func

import json
import psycopg2

import uuid
import os

import requests

DB_NAME = os.environ["DB_NAME"]
DB_USER = os.environ["DB_USER"]
DB_URL = os.environ["DB_URL"]
DB_PASSWORD = os.environ["DB_PASSWORD"]



def main(req: func.HttpRequest, doc) -> func.HttpResponse:
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
                newproduct_ela = {
                    "menu": menu, 
                    "date": date,
                    "name": name,
                    "projectid": projectid,
                    "division": str(division)
                }
                newproduct_cos = newproduct_ela.copy()
                id = str(id)
                newproduct_cos["id"] = id
                insert_cosmosDB(doc, newproduct_cos)
                insert_elasticsearch(doc, newproduct_ela, id)
    else:
        cur.execute(""" insert into menu_selected
                                (id,name,date,menu,created, projectid,division)
                                values
                                (%s,%s,%s,%s,now(),%s,%s)   
                                """,[str(id),name,date,menu,projectid,str(division)])
        
        newproduct_ela = {
            "menu": menu, 
            "date": date,
            "name": name,
            "projectid": projectid,
            "division": str(division)
        }
        newproduct_cos = newproduct_ela.copy()
        id = str(id)
        newproduct_cos["id"] = id
        insert_cosmosDB(doc, newproduct_cos)
        insert_elasticsearch(doc, newproduct_ela, id)
    
    cur.close()
            
    data = json.dumps([])
     
    func.HttpResponse.mimetype = 'application/json'
    return func.HttpResponse(data)


def insert_elasticsearch(doc, json, id):
    host = 'lunch2.koreacentral.cloudapp.azure.com'
    index = 'lunch2-index'
    type = '_doc'
    url = host + '/' + index + '/' + type + '/'

    headers = { "Content-Type": "application/json" }
    r = requests.post(url + id, json=json, headers=headers)

def insert_cosmosDB(doc, dict):
    newdocs = func.DocumentList() 
    
    newdocs.append(func.Document.from_dict(dict))
    doc.set(newdocs)
