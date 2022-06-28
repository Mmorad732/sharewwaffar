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

async def db_connect():
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

async def getFromdb(connection,table):
    try:
            with connection.cursor(dictionary=True,buffered=True) as cursor:
                
                if(table.lower()=='product'):
                    cursor.execute(
                      " SELECT product.id,product.image,product.name,product.price,\
                        product.cart_count,product.purch_count,product.wl_count,\
                        category.name AS category,brand.name AS brand ,supplier.name AS supplier, \
                        offer.quantity AS quantity, offer.discount AS discount \
                        FROM product \
                        JOIN category ON product.category = category.id \
                        JOIN brand ON product.brand = brand.id \
                        JOIN supplier ON product.supplier = supplier.id \
                        JOIN offer ON product.offer = offer.id "
                    )
                    connection.commit()
                    result = cursor.fetchall()
                    for prod in result:
                        prod['offer'] = str(prod.pop('quantity'))+' - '+str(prod.pop('discount'))+'%'
                   

                elif(table.lower()=='user'):
                    cursor.execute(
                        ' SELECT user.id,user.email,user.first_name,user.last_name,\
                          user.address,user.wallet, authorization.authorization AS authorization \
                          FROM user \
                          JOIN authorization ON user.authorization = authorization.id'
                        )
                    connection.commit()
                    result = cursor.fetchall()
                        
                else:
                    cursor.execute("SELECT * FROM "+table)
                    connection.commit()
                    result = cursor.fetchall()
                cursor.close()
                connection.close()
                return {'Value':True,'Result':result}
    except conn.Error as e:
            return {'Value':False,'Result':"Error"}

async def authUser(connection,userInfo):
    check_query = ("SELECT * FROM user WHERE email = %s")
    try:
            with connection.cursor(dictionary=True,buffered = True) as cursor:
                cursor.execute(check_query, [userInfo['email']])
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
                    user.pop('password')
                    return {'Value':True,'Message':"Authorized",'id':user.pop('id'),'auth':user.pop('authorization'),'user':user}
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
                with connection.cursor(dictionary = True,buffered = True) as cursor:
                    cond,val = makeCond(content)
                    check_query = ('SELECT * FROM '+ table +' WHERE '+cond)
                    cursor.execute(check_query, val)
                    connection.commit()
                    row_count = cursor.rowcount
                    if row_count >= 1:
                        result = cursor.fetchone()
                        cursor.close()
                        connection.close()
                        return {'Value':False, 'Message':table+" already exists", 'Result':result}
                    insert_query,values = await makeInsertQuery(content,table) 
                    cursor.execute(insert_query, values)
                    connection.commit()
                    cursor.close()
                    connection.close()
                    return {'Value':True, 'Message':"Created successfuly"}
            except conn.Error as e:
                    if('image' in content.keys()):
                        await deleteIm(content['image'])
                    return {'Value':False, 'Message':"Error"}
    else:
        return {'Value':False, 'Message':"Error"}

def makeCond(content):
    count = 0
    values = []
    cond = ''
    im = ''
    price = ''
    quantity = ''
    cart = ''
    wishlist = ''
    if 'image' in content:
        im = content.pop('image')
    if 'price' in content:
        price = content.pop('price')
    if 'quantity' in content:
        quantity = content.pop('quantity')
    if 'cart' in content:
        cart = content.pop('cart')
    if 'wishlist' in content:
        wishlist = content.pop('wishlist')
    for key,val in content.items():
        if count == len(content)-1:
            cond += key+"= %s"
            values.append(val)
        else:
            cond += key+"= %s and "
            values.append(val)
        count += 1
    if(bool(quantity)):
        content['quantity'] = quantity
    if(bool(price)):
        content['price'] = price
    if(bool(im)):
        content['image'] = im
    if(bool(cart)):
        content['cart'] = cart
    if(bool(wishlist)):
        content['wishlist'] = wishlist
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
            try:
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
            except conn.Error as e:
                print(e)
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
            return {'Value':True, 'Message':table+" updated successfully",'Result':result}
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
    stmt = (update_query + q_body  + " WHERE id = " + str(id)  )
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
            
async def productQuery(connection,id):
    try:
        with connection.cursor(dictionary=True,buffered=True) as cursor:
            
            cursor.execute(
                " SELECT product.price,product.cart_count,product.wl_count,\
                    offer.quantity AS quantity, offer.discount AS discount \
                    FROM product \
                    JOIN offer ON product.offer = offer.id and product.id = %s",[id]
                )
            connection.commit()
            row_count = cursor.rowcount
            if row_count == 0:    
                cursor.close()
                connection.close()
                return {'Value':False, 'Message':"Product not found"}
            result = cursor.fetchone() 
            cursor.close()
            connection.close()
            return {'Value':True, 'Result':result}
            
    except conn.Error as e:
        return {'Value':False,'Message':"Error"}

async def getFromList(connection,table,content):
    query = ('SELECT * FROM '+table+' WHERE user = %s and product = %s')     
    try:
        with connection.cursor(dictionary=True,buffered = True) as cursor:
            cursor.execute(query,[content['user'],content['product']])
            connection.commit()
            row_count = cursor.rowcount
            if row_count == 0:    
                cursor.close()
                connection.close()
                return {'Value':False, 'Message':table+" item not Found"}
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            return {'Value':True,'Result':result}
    except conn.Error as e:
        return {'Value':False, 'Message':'Error'}

async def productIncDec(connection,content,op):
    update_query = 'UPDATE product SET '+ content['column']+' = '+content['column']+' '+op +' '+content['quantity'] + ' WHERE id = %s'
    try:
        with connection.cursor() as cursor:
            cursor.execute(update_query,[content['prod_id']])
            connection.commit()
            row_count = cursor.rowcount
            if row_count == 0:    
                cursor.close()
                connection.close()
                return {'Value':False, 'Message':"Product not Found"}
            cursor.close()
            connection.close()
            return {'Value':True, 'Message':"Product Updated successfully"}
    except conn.Error as e:
        return {'Value':False, 'Message':'Error'}

async def getListItems(connection,table,user,cond=''):
    try:
        with connection.cursor(dictionary=True,buffered=True) as cursor:
            if not bool(cond):
                cursor.execute(
                            " SELECT product.id,product.name\
                            FROM history \
                            JOIN product ON history.product = product.id and history.user = %s",[user])
            else:
                cursor.execute(
                            " SELECT product.id , product.image,product.name,product.price,history.quantity as quantity\
                            FROM history \
                            JOIN product ON product.id = history.product and "+cond+"=1 and history.user = %s",[user])
            connection.commit()
            row_count = cursor.rowcount
            if row_count == 0:    
                cursor.close()
                connection.close()
                return {'Value':False, 'Message':"Empty "+table}
            result = cursor.fetchall() 
            cursor.close()
            connection.close()
            return {'Value':True, 'Result':result}
    except conn.Error as e:
        return {'Value':False,'Message':"Error"}

async def getFilteredProducts(connection,cond = ''):
    try:
        with connection.cursor(dictionary=True,buffered=True) as cursor:
            condition = ''
            if len(cond)!=0:
                if(('category' in cond) and not ('brand' in cond)):
                    condition = ' AND (category.name = "'+str(cond['category'])+'" or category.id = "'+str(cond['category'])+'" ) '
                elif(not ('category' in cond) and ('brand' in cond)):
                    condition = ' AND (brand.name = "'+str(cond['brand'])+'" or brand.id = "'+str(cond['brand'])+'" ) '
                elif(('category' in cond) and ('brand' in cond)):
                    condition = ' AND (category.name = "'+str(cond['category'])+'" or category.id = "'+str(cond['category'])+'" ) ' + 'AND' \
                        '(brand.name = "'+str(cond['brand'])+'" or brand.id = "'+str(cond['brand'])+'" ) '

            cursor.execute(
                " SELECT product.id,product.image,product.name,product.price,\
                    category.name AS category,brand.name AS brand ,supplier.name AS supplier, \
                    offer.quantity AS quantity, offer.discount AS discount \
                    FROM product \
                    JOIN category ON product.category = category.id \
                    JOIN brand ON product.brand = brand.id "+condition+" \
                    JOIN supplier ON product.supplier = supplier.id \
                    JOIN offer ON product.offer = offer.id "
                )
            connection.commit()
            if cursor.rowcount == 0:
                cursor.close()
                connection.close()
                return {'Value':False,'Message':'No Products'}
            result = cursor.fetchall()
            for prod in result:
                prod['offer'] = str(prod.pop('quantity'))+' - '+str(prod.pop('discount'))+'%'
            return {'Value':True,'Result':result}
    except conn.Error as e:
        return {'Value':False,'Message':'Error'}

async def getProduct(connection,id):
    try:
        with connection.cursor(dictionary=True,buffered=True) as cursor:

            cursor.execute(
                " SELECT product.id,product.image,product.name,product.price,\
                    category.name AS category,brand.name AS brand ,supplier.name AS supplier, \
                    offer.quantity AS quantity, offer.discount AS discount \
                    FROM product \
                    JOIN category ON product.category = category.id \
                    JOIN brand ON product.brand = brand.id \
                    JOIN supplier ON product.supplier = supplier.id \
                    JOIN offer ON product.offer = offer.id  AND product.id = "+str(id)
                )
            connection.commit()
            if cursor.rowcount == 0:
                cursor.close()
                connection.close()
                return {'Value':False,'Message':'No Products'}
            result = cursor.fetchone()
            result['offer'] = str(result.pop('quantity'))+' - '+str(result.pop('discount'))+'%'
            return {'Value':True,'Result':result}
    except conn.Error as e:
        return {'Value':False,'Message':'Error'}

async def deleteHist(connection,user,prod,cond):
    condition = ''
    if cond.lower() == 'cart':
        condition = 'cart'
    elif cond.lower() == 'wishlist':
        condition = 'wishlist' 
    elif cond.lower() == 'purchase':
        condition = 'purchase'    
    delete_query = 'DELETE FROM history WHERE '+condition+' =  user = %s and product = %s' 
    try:
        with connection.cursor(dictionary=True,buffered = True) as cursor:
            cursor.execute(delete_query,[1,user,prod])
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

async def getHist(connection,prod,cond):
    condition = ''
    vals = []
    if cond.lower() == 'interested':
        condition = '(cart = %s or wishlist = %s)'
        vals.append(1)
        vals.append(1)
    elif cond.lower() == 'purchase':
        condition = 'purchase = %s'
        vals.append(1)    
    query = 'SELECT user FROM history WHERE '+condition+'  and product = %s'
    vals.append(prod) 
    try:
        with connection.cursor(dictionary=True,buffered = True) as cursor:
            cursor.execute(query,vals)
            connection.commit()
            row_count = cursor.rowcount
            if row_count == 0:    
                cursor.close()
                connection.close()
                return {'Value':False, 'Message':"Error"}
            result = cursor.fetchall()
            cursor.close()
            connection.close()
            return {'Value':True, 'Result':result}
    except conn.Error as e:
            return {'Value':False, 'Message':'Error'}

async def addDeal(connection,content):
    try:
        with connection.cursor(dictionary = True,buffered = True) as cursor:
            check_query = ('SELECT * FROM deal WHERE start_date = %s or end_date in (%s,%s) and product = %s')
            cursor.execute(check_query,[content['start_date'],content['start_date'],content['end_date'],content['product']])
            connection.commit()
            row_count = cursor.rowcount
            if row_count >= 1:   
                result = cursor.fetchone()
                cursor.close()
                connection.close()
                return {'Value':True, 'Result':result}
            insert_query,values = await makeInsertQuery(content,'deal') 
            cursor.execute(insert_query, values)
            connection.commit()
            cursor.close()
            connection.close()
            return {'Value':True, 'Message':"Created successfuly"}
    except conn.Error as e:
            return {'Value':False, 'Message':"Error11"}
    
async def addNotifications(connection, content):
    try:
        with connection.cursor(dictionary=True,buffered = True) as cursor:
            check_query = ('SELECT user FROM notification WHERE product = %s and end_date = %s')
            cursor.execute(check_query,[content[0]['product'],content[0]['end_date']])
            connection.commit()
            row_count = cursor.rowcount
            if row_count > 0: 
                if row_count == len(content):
                    cursor.close()
                    connection.close()
                    return {'Value':False, 'Message':"Notifications already exists"}
                else:
                    result = cursor.fetchall()
                    newres = []
                    newcontent = []
                    for res in range(len(result)):
                        newres.append(result[res]['user'])
                    for i in range(len(content)):
                        if not int(content[i]['user']) in newres:
                            newcontent.append(content[i])
                    content = newcontent
            
            insert_query = 'INSERT INTO notification (user,product,message,end_date) \
                values (%(user)s, %(product)s, %(message)s,%(end_date)s)'
            if len(content)>0:
                cursor.executemany(insert_query, content)
                connection.commit()
                cursor.close()
                connection.close()
                return {'Value':True, 'Message':"Notifications created successfuly"}
            else:
                cursor.close()
                connection.close()
                return {'Value':True, 'Message':"All user notified"}
    except conn.Error as e:
            return {'Value':False, 'Message':"Error"}

async def getNotifications(connection, content):
    try:
        with connection.cursor(dictionary=True,buffered = True) as cursor:
            check_query = ('SELECT message FROM notification WHERE user = %s and end_date >= %s')
            cursor.execute(check_query,[content['user'],content['date']])
            connection.commit()
            row_count = cursor.rowcount
            if row_count == 0:   
                cursor.close()
                connection.close()
                return {'Value':False, 'Message':"No Notifications"}
            result = cursor.fetchall() 
            cursor.close()
            connection.close()
            return {'Value':True, 'Result':result}
    except conn.Error as e:
            return {'Value':False, 'Message':"Error"}
