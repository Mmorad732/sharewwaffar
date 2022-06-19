import mysql.connector as conn
import help_funcs as hf
import cloudinary
import cloudinary.uploader
import cloudinary.api


cloudinary.config( 
  cloud_name = "ditvzji07", 
  api_key = "693958374426433", 
  api_secret = "6BO4issZw7-7LG8ukvOeSAdeWfY",
  secure = True
  
)

def db_connect():
    try:
        return conn.connect(host="us-cdbr-east-05.cleardb.net",database="heroku_f4873a695e38634",user="b17e6f10ba95ab",password="e7b27c74") 
    except conn.Error as e:
        return e

async def createUser(connection,user):
    user['email'] = user['email'].lower()
    email_val = hf.email_check(user['email'])
    password_val = hf.password_check(user['password'])
    if email_val['Value']:
        if password_val['Value']:
            check_query = ("SELECT id FROM user WHERE email = %s")
            try:
                    with connection.cursor(buffered = True) as cursor:
                        cursor.execute(check_query, [user['email']] )
                        connection.commit()
                        row_count = cursor.rowcount
                        if row_count >= 1:    
                            cursor.close()
                            connection.close()
                            return {'Value':False,'Message':"Email already exists"}
                        hashed_pass = hf.password_hash(user['password'])
                        user['password'] = hashed_pass
                        query,values = await makeInsertQuery(user)
                        cursor.execute(query, values)
                        connection.commit()
                        cursor.close()
                        connection.close()
                        return {'Value':True,'Message':"User created successfuly"}
            except conn.Error as e:
                    return {'Value':False,'Message':"Error"}
        else:
           return password_val 
    else:
        return email_val

def getFromdb(connection,table):
    try:
            with connection.cursor(dictionary=True,buffered=True) as cursor:
                cursor.execute("SELECT * FROM "+table)
                connection.commit()
                result = cursor.fetchall()
                if(table.lower()=='product'):
                    for i in range(len(result)):
                        cursor.execute("SELECT name FROM category WHERE id =%s",[result[i]['category']])
                        connection.commit()
                        res = cursor.fetchone()
                        result[i]['category'] = res['name']

                        cursor.execute("SELECT name FROM supplier WHERE id =%s",[result[i]['supplier']])
                        connection.commit()
                        res = cursor.fetchone()
                        result[i]['supplier'] = res['name']

                        cursor.execute("SELECT name FROM brand WHERE id =%s",[result[i]['brand']])
                        connection.commit()
                        res = cursor.fetchone()
                        result[i]['brand'] = res['name'] 

                        cursor.execute("SELECT * FROM offer WHERE id =%s",[result[i]['offer']])
                        connection.commit()
                        res = cursor.fetchone()
                        result[i]['offer'] = str(res['quantity'])+' - '+str(res['discount'])+'%'

                elif(table.lower()=='user'):
                    for i in range(len(result)):
                        cursor.execute("SELECT authorization FROM authorization WHERE id =%s",[result[i]['authorization']])
                        connection.commit()
                        res = cursor.fetchone()
                        result[i]['authorization'] = res['authorization']
                cursor.close()
                connection.close()
                return {'Value':True,'Result':result}
    except conn.Error as e:
            return {'Value':False,'Result':"Error"}

def authUser(connection,userInfo):
    check_query = ("SELECT * FROM user WHERE email = %s")
    try:
            with connection.cursor(dictionary=True,buffered = True) as cursor:
                cursor.execute(check_query, [userInfo['email']] )
                connection.commit()
                row_count = cursor.rowcount
                if row_count == 0:    
                    cursor.close()
                    connection.close()
                    return {'Value':False,'Message':"Email doesn't exist"}
                user = cursor.fetchone()
                cursor.close()
                connection.close() 
                check_pass = hf.password_verify(user['password'],userInfo['password'])
                if check_pass['Value']:
                    return {'Value':True,'Message':"Authorized",'id':user['id'],'auth':user['authorization']}
                else:
                    return check_pass
            
    except conn.Error as e:
            return {'Value':False,'Message':'Error'}

async def insertIntoTable(connection,content):
    table = content.pop('table')
    if checkDict(content):
        if table.lower() == 'user':
            resp = await createUser(connection,content)
            return resp
        else:
            try:
                with connection.cursor(buffered = True) as cursor:
                    cond,val = makeCond(content)
                    check_query = ('SELECT * FROM '+ table +' WHERE '+cond)
                    cursor.execute(check_query, val)
                    connection.commit()
                    row_count = cursor.rowcount
                    if row_count >= 1:    
                        cursor.close()
                        connection.close()
                        return {'Value':False, 'Message':table+" already exist"}
                    insert_query,values = await makeInsertQuery(content,table)  
                    cursor.execute(insert_query, values)
                    connection.commit()
                    cursor.close()
                    connection.close()
                    return {'Value':True, 'Message':"Created successfuly"}
            except conn.Error as e:
                    if('image' in content.keys()):
                        await deleteIm(content['image'])
                    return {'Value':False, 'Message':"Error 1"}
    else:
        return {'Value':False, 'Message':"Error 1"}

def makeCond(content):
    count = 0
    values = []
    cond = ''
    im = ''
    if 'image' in content:
        im = content.pop('image')
    for key,val in content.items():
        if count == len(content)-1:
            cond += key+"= %s"
            values.append(val)
        else:
            cond += key+"= %s and "
            values.append(val)
        count += 1
    if(bool(im)):
        content['image'] = im
    return cond,values

def checkDict(dict):
    for i in dict:
        if not dict[i]:
            return False
    return True

async def makeInsertQuery(content,table='user'):
    columns = "("
    placeholder = "("
    values = []
    content_len = len(content)
    count = 0
    
    for i in content:
        if i == 'image' and content[i]:
            response = await uploadIm(content['image'])  
            if response:
                content[i] = response['secure_url']
            
        if count == content_len-1:
            columns += i 
            placeholder += "%s" 
        else:
            columns += i + ","
            placeholder += "%s,"
        
        values.append(content[i])
        count += 1
    columns += ")"
    placeholder += ")" 
    insert_query =  ("INSERT INTO " + table +" "+columns+" VAlUES "+placeholder)
    return insert_query,values

async def getIdFromdb(connection,table,id,content='*'):
    get_query = ("SELECT "+content+" FROM "+ table +" WHERE id = %s")
    try:
                with connection.cursor(dictionary=True,buffered = True) as cursor:
                    cursor.execute(get_query, [id])
                    connection.commit()
                    row_count = cursor.rowcount
                    if row_count == 0:    
                        cursor.close()
                        connection.close()
                        return {'Value':False, 'Message':table+" not found"}
                    result = cursor.fetchone() 
                    cursor.close()
                    connection.close()
                    return {'Value':True, 'Result':result}
    except conn.Error as e:
            return {'Value':False, 'Message':'Error'}

async def updateItem(connection,content,id):
    if 'image' in content.keys():
        del_resp = await deleteIm(content.pop('origImage'))
        if del_resp['result'] == 'ok' or del_resp['result'] == 'not found':
            response =  await uploadIm(content['image'])
            content['image'] = response['secure_url']
        else:
            return {'Value':False,'Message':"Error"}
    elif 'email' in content.keys():
        content['email'] = content['email'].lower()
    elif 'password' in content.keys():
        try:
            with connection.cursor(dictionary=True,buffered=True) as cursor:
                cursor.execute("SELECT password FROM user WHERE id = %s",[id])
                connection.commit()
                res = cursor.fetchone()
                cursor.close()
        except conn.Error as e:
                return {'Value':False, 'Message':"Error"}
        dup_check = hf.password_verify(res['password'],content['password'])
        if(not dup_check['Value']):
            pass_val = hf.password_check(content['password'])
            if pass_val['Value']:
                hashed = hf.password_hash(content['password'])
                content['password'] = hashed
            else:
                return pass_val
        else:
            return {'Value':False, 'Message':"Change password"}
    table = content.pop('table')
    try:
        with connection.cursor(dictionary = True, buffered = True) as cursor:
            
            if (table.lower() == 'product'):
                get_query = ('SELECT name,supplier FROM '+ table +' WHERE id = %s')
            elif(table.lower() == 'user'):
                get_query = ('SELECT email FROM '+ table +' WHERE id = %s')
            else:
                get_query = ('SELECT * FROM '+ table +' WHERE id = %s')
            cursor.execute(get_query, [id])
            connection.commit()
            result = cursor.fetchone()
            if('id' in result):
                result.pop('id')
            for k,v in content.items():
                if k in result:
                    result[k] = v
            cond,val = makeCond(result)
            check_query = ('SELECT * FROM ' + table + ' WHERE ' + cond + ' and id != %s')
            val.append(str(id))
            cursor.execute(check_query,val)
            connection.commit()
            row_count = cursor.rowcount
            if row_count > 0:    
                cursor.close()
                connection.close()
                return {'Value':False, 'Message':table+" already exist"}
            update_query,values = await makeUpdateQuery(content,table,id)
            cursor.execute(update_query,values)
            connection.commit()
            row_count = cursor.rowcount
            if row_count == 0:    
                cursor.close()
                connection.close()
                return {'Value':False, 'Message':"No change"}
            cursor.close()
            connection.close()
            return {'Value':True, 'Message':table+" updated successfully"}
    except conn.Error as e:
            return {'Value':False, 'Message':"Error"}

async def makeUpdateQuery(content,table,id):
    update_query = "UPDATE "+table +" " 
    q_body = 'SET '
    values =[]
    count = 0
    for key,val in content.items():
        if count == len(content)-1:
            q_body += key+"= %s"
            values.append(val)
        else:
            q_body += key+"= %s,"
            values.append(val)
        count += 1
    stmt = (update_query + q_body  + " WHERE id = " + id  )
    return stmt,values

async def deleteById(connection, table , id):
    delete_query = ('DELETE FROM '+table+' WHERE id = %s')      
    try:
        with connection.cursor(dictionary=True,buffered = True) as cursor:
            if table.lower() == 'product':
                get_im_query = ('SELECT image FROM '+table+' WHERE id = %s')
                try:
                    cursor.execute(get_im_query,[id])
                    connection.commit()
                    result = cursor.fetchone()
                    await deleteIm(result['image'])
                except conn.Error as e:
                    return {'Value':False, 'Message':'Error'}
            cursor.execute(delete_query,[id])
            connection.commit()
            row_count = cursor.rowcount
            if row_count == 0:    
                cursor.close()
                connection.close()
                return {'Value':False, 'Message':"Error"}
            cursor.close()
            connection.close()
            return {'Value':True, 'Message':"Deleted successfully"}
    except conn.Error as e:
            return {'Value':False, 'Message':'Error'}

async def uploadIm(im):
    im = bytearray(await im.read())
    response =  cloudinary.uploader.upload(im ,folder='shareWwaffar',width = 300, height = 200,resize='fit')
    return response 

async def deleteIm(im):
    try:
        url = im.split('/')
        url[-1] = url[-1].split('.')[0]
        del_resp = cloudinary.uploader.destroy(url[-2]+'/'+url[-1])
        return del_resp
    except:
        return ""