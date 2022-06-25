from fastapi import FastAPI , Request
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
import tokenfns as t
import db_funcs as db
import recommender
import dealHandler as deal
from fastapi.staticfiles import StaticFiles
import pkg_resources
import starlette.status as status
from fastapi.templating import Jinja2Templates
import pandas as pd
import numpy as np
from datetime import date, timedelta



templates = Jinja2Templates(directory="Admin_pages/")


app = FastAPI()
app.mount("/static", StaticFiles(directory=pkg_resources.resource_filename(__name__, 'static')), name="static")
app.add_middleware(
    HTTPSRedirectMiddleware
    # CORSMiddleware,
    # allow_origins= ["*"],
    # allow_credentials=True,
    # allow_methods=["*"],
    # allow_headers=["*"]
)

# User
@app.post('/user')
async def signin(req:Request):
    try:
        if bool(await req.body()):
            user = await req.json()
            auth = await db.authUser(await db.db_connect(),user)
            if (auth['Value']): 
                resp = JSONResponse(content = {'Value':auth['Value'],'Message': auth['Message'],'User':auth['user']})
                resp.set_cookie(key="Token",value=t.create_access_token({'id':auth['id'],'role':auth['auth']},180),secure=True,httponly=True)
                return resp
            else:
                resp = JSONResponse(content = {'Value':auth['Value'],'Message': auth['Message']})
                return resp
        elif bool(req.cookies):
            try:
                bool(req.cookies['Token'])
            except:
                return {'Value':False ,'Message':"Error"}
            tok = t.auth_token(req.cookies['Token'])
            if tok['Value'] and tok['role']==2:
                user = await db.getIdFromdb(await db.db_connect(),'User',tok['id'],content='email,first_name,last_name,address,wallet')
                resp = JSONResponse(content = {'Value':tok['Value'],'Message': "Authorized User",'User':user['Result']}) 
                resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
                return resp
            else:
                resp = JSONResponse(content = {'Value':False,'Message': "Guest"})
                resp.delete_cookie('Token')
                return resp
        resp = JSONResponse(content = {'Value':False,'Message': "Guest"})
        return resp
    except:
        return {'Value':False ,'Message':"Error"}
  
@app.post('/logout')
async def logout(req:Request):
    try:
        respo = RedirectResponse('/user')
        if(bool(req.cookies)):
            respo.delete_cookie('Token')
        return respo
    except:
            return {'Value':False,'Meassage':"Error"}

@app.post('/signup')
async def signup(req:Request):
    try:
        if bool(await req.body()):
            user = await req.json()
            resp = await db.createUser(await db.db_connect(),user)
            if resp['Value']:
                return JSONResponse(content ={'Value':resp['Value'],'Message':resp['Message']})
            else:
                return JSONResponse(content ={'Value':resp['Value'],'Message':resp['Message']})
        else:
            return JSONResponse(content = {'Value':False,'Message': "Invalid input"})
    except:
        return JSONResponse(content = {'Value':False,'Message': "Error"}) 

@app.post('/cartitems')
async def getCartItems(req:Request):
    try:
        if bool(req.cookies):
            try:
                bool(req.cookies['Token'])
            except:
                return JSONResponse(content = {'Value':False,'Message': "UnAuthozied"})
            tok = t.auth_token(req.cookies['Token'])
            if tok['Value']:
                user = tok['id']
                items = await db.getListItems(await db.db_connect(),'Cart',user)
                if items['Value']:
                    resp = JSONResponse(content = {'Value':True,'Result': items['Result']}) 
                    resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
                    return resp
                else:
                    resp = JSONResponse(content = {'Value':False,'Message': items['Message']}) 
                    resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
                    return resp

        resp = JSONResponse(content = {'Value':False,'Message': "UnAuthozied"}) 
        return resp    
    except:
        resp = JSONResponse(content = {'Value':False,'Message': "Error"}) 
        if bool(req.cookies): 
            try:
                bool(req.cookies['Token'])
                resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
            except:
                return resp
        return resp  

@app.post('/addcartitem')
async def addToCart(req:Request):
    try:
        if bool(req.cookies): 
            try:
                bool(req.cookies['Token'])
            except:
                return JSONResponse(content = {'Value':False,'Message': "UnAuthozied"})
            tok = t.auth_token(req.cookies['Token'])
            if tok['Value']:
                if(bool(await req.body())):
                    cart_item = await req.json()
                    check_wl = await db.getFromList(await db.db_connect(),'Wishlist',{'user':tok['id'],'product':cart_item['prod_id']})
                    if(not check_wl['Value']):
                        product_fetch = await db.productQuery(await db.db_connect(),cart_item['prod_id'])
                        if(int(cart_item['quantity'])>0):
                            if(product_fetch['Value']):
                                quantity = int(cart_item['quantity'])
                                content = {'table':'Cart','user':tok['id'],'product':int(cart_item['prod_id']),'quantity':cart_item['quantity'],'price': float(product_fetch['Result']['price'])*quantity}
                                result = await db.insertIntoTable(await db.db_connect(),content)
                                if result['Value']:
                                    prod_cart_count = int(product_fetch['Result']['cart_count'])+quantity
                                    update_content = {'column':'cart_count','prod_id':cart_item['prod_id'],'quantity':str(quantity)}
                                    update_product = await db.productIncDec(await db.db_connect(),update_content,'+')
                                    if(update_product['Value']):
                                        hist_content = {'table':'History','user':tok['id'],'product':int(cart_item['prod_id']),'cart':1,'date':str(date.today())}
                                        history_insert = await db.insertIntoTable(await db.db_connect(),hist_content)
                                        if history_insert['Value']:
                                            if(product_fetch['Result']['quantity']<= (prod_cart_count+product_fetch['Result']['wl_count'])):
                                                deal_content = {'product':int(cart_item['prod_id']),'quantity':product_fetch['Result']['quantity'],'discount':product_fetch['Result']['discount'],'start_date':str(date.today()),'end_date':str(date.today()+timedelta(days=1))}
                                                deal_result = await db.addDeal(await db.db_connect(),deal_content)
                                                if deal_result['Value']:
                                                    if 'Result' in deal_result.keys():
                                                        endDate = deal_result['Result']['end_date']
                                                    else:
                                                        endDate = deal_content['end_date']
                                                    await deal.dealShoutOut(cart_item['prod_id'],endDate)
                                            resp = JSONResponse(content = {'Value':product_fetch['Value'],'Message': result['Message']}) 
                                            resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
                                            return resp
                                    else:
                                        resp = JSONResponse(content = {'Value':product_fetch['Value'],'Message': "Error"}) 
                                        resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
                                        return resp
                                else:
                                    resp = JSONResponse(content = {'Value':result['Value'],'Message': result['Message']}) 
                                    resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
                                    return resp
                            else:
                                resp = JSONResponse(content = {'Value':product_fetch['Value'],'Message': product_fetch['Message']}) 
                                resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
                                return resp
                    else:
                        resp = JSONResponse(content = {'Value':False,'Message': "Product is in your wishlist"}) 
                        resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
                        return resp
                
                    resp = JSONResponse(content = {'Value':False,'Message': "Bad Request"}) 
                    resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
                    return resp
            
        resp = JSONResponse(content = {'Value':False,'Message': "UnAuthozied"}) 
        return resp
    except:
        resp = JSONResponse(content = {'Value':False,'Message': "Error"})
        try:
            bool(req.cookies['Token'])
            resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
        except:
            return resp
        return resp

@app.post('/deletecartitem')
async def deleteFromCart(req:Request):
    try:
        if bool(req.cookies): 
            try:
                bool(req.cookies['Token'])
            except:
                return JSONResponse(content = {'Value':False,'Message': "UnAuthozied"})
            tok = t.auth_token(req.cookies['Token'])
            if tok['Value']:
                if(bool(await req.body())):
                    cart_item = await req.json()
                    cart_info = await db.getFromList(await db.db_connect(),'Cart',{'user':tok['id'],'product':cart_item['prod_id']})
                    if(cart_info['Value']):
                        delete_item = await db.deleteById(await db.db_connect(),'Cart',cart_info['Result']['id'])
                        if delete_item['Value']:
                            update_content = {'column':'cart_count','prod_id':cart_item['prod_id'],'quantity':str(cart_info['Result']['quantity'])}
                            update_product = await db.productIncDec(await db.db_connect(),update_content,'-')
                            delete_hist = await db.deleteHist(await db.db_connect(),tok['id'],cart_item['prod_id'],'cart')
                        resp = JSONResponse(content = {'Value':delete_item['Value'],'Message': delete_item['Message']}) 
                        resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
                        return resp
                    else:
                        resp = JSONResponse(content = {'Value':False,'Message': "Error"}) 
                        resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
                        return resp
                else:
                    resp = JSONResponse(content = {'Value':False,'Message': "Bad Request"}) 
                    resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
                    return resp
        resp = JSONResponse(content = {'Value':False,'Message': "UnAuthozied"}) 
        return resp    

    except:
        resp = JSONResponse(content = {'Value':False,'Message': "Error"})
        try:
            bool(req.cookies['Token'])
        except:
            return resp
        return resp               
    
@app.post('/updatecartitem')
async def updateCartItem(req:Request):
    try:
        if bool(req.cookies):
            try:
                bool(req.cookies['Token'])
            except:
                return JSONResponse(content = {'Value':False,'Message': "UnAuthozied"})
            tok = t.auth_token(req.cookies['Token'])
            if tok['Value']:
                if(bool(await req.body())):
                    cart_item = await req.json()
                    cart_info = await db.getFromList(await db.db_connect(),'Cart',{'user':tok['id'],'product':cart_item['prod_id']})
                    if(cart_info['Value'] and int(cart_item['quantity']) > 0 ):
                        unit_price = float(cart_info['Result']['price'])/int(cart_info['Result']['quantity'])
                        update_content = {'table':'Cart','quantity': cart_item['quantity'],'price':str(unit_price*int(cart_item['quantity']))}
                        update_item = await db.updateItem(await db.db_connect(),update_content,cart_info['Result']['id'])
                        if update_item['Value']:
                            if(cart_info['Result']['quantity'] > int(cart_item['quantity'])):
                                op = '-'
                            else:
                                op = '+'
                            quantity = abs(cart_info['Result']['quantity'] - int(cart_item['quantity']))        
                            update_content = {'column':'cart_count','prod_id':cart_item['prod_id'],'quantity':str(quantity)}
                            update_product = await db.productIncDec(await db.db_connect(),update_content,op)
                            if(update_product['Value']):
                                product_fetch = await db.productQuery(await db.db_connect(),cart_item['prod_id'])
                                if(product_fetch['Result']['quantity']<= (product_fetch['Result']['cart_count']+product_fetch['Result']['wl_count'])):
                                    deal_content = {'product':int(cart_item['prod_id']),'quantity':product_fetch['Result']['quantity'],'discount':product_fetch['Result']['discount'],'start_date':str(date.today()),'end_date':str(date.today()+timedelta(days=1))}
                                    deal_result = await db.addDeal(await db.db_connect(),deal_content)
                                    if deal_result['Value']:
                                        if 'Result' in deal_result.keys():
                                            endDate = deal_result['Result']['end_date']
                                        else:
                                            endDate = deal_content['end_date']
                                        await deal.dealShoutOut(cart_item['prod_id'],endDate)
                                                
                                resp = JSONResponse(content = {'Value':update_item['Value'],'Message': update_item['Message']}) 
                                resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
                                return resp
                        else:
                            resp = JSONResponse(content = {'Value':update_item['Value'],'Message': update_item['Message']}) 
                            resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
                            return resp
                    else:
                        resp = JSONResponse(content = {'Value':cart_info['Value'],'Message': cart_info['Message']}) 
                        resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
                        return resp
                
                resp = JSONResponse(content = {'Value':False,'Message': "Bad Request"}) 
                resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
                return resp
        resp = JSONResponse(content = {'Value':False,'Message': "UnAuthozied"}) 
        return resp    

    except:
        resp = JSONResponse(content = {'Value':False,'Message': "Error"}) 
        if bool(req.cookies) and bool(req.cookies['Token']):
            resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
        return resp                       
                         
@app.post('/addwishlistitem')
async def addToWishList(req:Request):
    try:
        if bool(req.cookies):
            try:
                bool(req.cookies['Token'])
            except:
                return JSONResponse(content = {'Value':False,'Message': "UnAuthozied"})
            tok = t.auth_token(req.cookies['Token'])
            if tok['Value']:
                if(bool(await req.body())):
                    wl_item = await req.json()
                    check_cart = await db.getFromList(await db.db_connect(),'Cart',{'user':tok['id'],'product':wl_item['prod_id']})
                    if(not check_cart['Value']):
                        product_fetch = await db.productQuery(await db.db_connect(),wl_item['prod_id'])
                        if(product_fetch['Value']):
                            content = {'table':'Wishlist','user':tok['id'],'product':wl_item['prod_id']}
                            result = await db.insertIntoTable(await db.db_connect(),content)
                            if result['Value']:
                                update_content = {'column':'wl_count','prod_id':wl_item['prod_id'],'quantity':'1'}
                                update_product = await db.productIncDec(await db.db_connect(),update_content,'+')
                                if(update_product['Value']):
                                    hist_content = {'table':'History','user':tok['id'],'product':int(wl_item['prod_id']),'wishlist':1,'date':str(date.today())}
                                    history_insert = await db.insertIntoTable(await db.db_connect(),hist_content)
                                    if(history_insert['Value']):
                                        if(product_fetch['Result']['quantity'] <= (product_fetch['Result']['cart_count'])+product_fetch['Result']['wl_count']+1):
                                            deal_content = {'product':int(wl_item['prod_id']),'quantity':product_fetch['Result']['quantity'],'discount':product_fetch['Result']['discount'],'start_date':str(date.today()),'end_date':str(date.today()+timedelta(days=1))}
                                            deal_result = await db.addDeal(await db.db_connect(),deal_content)
                                            if deal_result['Value']:
                                                if 'Result' in deal_result.keys():
                                                    endDate = deal_result['Result']['end_date']
                                                else:
                                                    endDate = deal_content['end_date']
                                                await deal.dealShoutOut(wl_item['prod_id'],endDate)
                                            
                                    resp = JSONResponse(content = {'Value':product_fetch['Value'],'Message': result['Message']}) 
                                    resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
                                    return resp
                                else:
                                    resp = JSONResponse(content = {'Value':product_fetch['Value'],'Message': "Error"}) 
                                    resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
                                    return resp
                            else:
                                resp = JSONResponse(content = {'Value':result['Value'],'Message': result['Message']}) 
                                resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
                                return resp
                        else:
                            resp = JSONResponse(content = {'Value':product_fetch['Value'],'Message': product_fetch['Message']}) 
                            resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
                            return resp
                    else:
                        resp = JSONResponse(content = {'Value':False,'Message': "Product is in your cart"}) 
                        resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
                        return resp
                        

                resp = JSONResponse(content = {'Value':False,'Message': "Bad Request"}) 
                resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
                return resp
            
        resp = JSONResponse(content = {'Value':False,'Message': "UnAuthozied"}) 
        return resp
    except:
        resp = JSONResponse(content = {'Value':False,'Message': "Error"})
        try:
            bool(req.cookies['Token'])
            resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
        except:
            return resp
        return resp

@app.post('/deletewishlistitem')
async def deleteFromWishList(req:Request):
    try:
        if bool(req.cookies):
            try:
                bool(req.cookies['Token'])
            except:
                return JSONResponse(content = {'Value':False,'Message': "UnAuthozied"})
            tok = t.auth_token(req.cookies['Token'])
            if tok['Value']:
                if(bool(await req.body())):
                    wl_item = await req.json()
                    wl_info = await db.getFromList(await db.db_connect(),'Wishlist',{'user':tok['id'],'product':wl_item['prod_id']})
                    if(wl_info['Value']):
                        delete_item = await db.deleteById(await db.db_connect(),'Wishlist',wl_info['Result']['id'])
                        if delete_item['Value']:
                            update_content = {'column':'wl_count','prod_id':wl_item['prod_id'],'quantity':'1'}
                            update_product = await db.productIncDec(await db.db_connect(),update_content,'-')
                            delete_hist = await db.deleteHist(await db.db_connect(),tok['id'],wl_item['prod_id'],'wishlist')
                            resp = JSONResponse(content = {'Value':delete_item['Value'],'Message': delete_item['Message']}) 
                            resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
                            return resp
                        else:
                            resp = JSONResponse(content = {'Value':delete_item['Value'],'Message': delete_item['Message']}) 
                            resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
                            return resp
                    else:
                        resp = JSONResponse(content = {'Value':False,'Message': "Error"}) 
                        resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
                        return resp
                else:
                    resp = JSONResponse(content = {'Value':False,'Message': "Bad Request"}) 
                    resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
                    return resp
        resp = JSONResponse(content = {'Value':False,'Message': "UnAuthozied"}) 
        return resp    

    except:
        resp = JSONResponse(content = {'Value':False,'Message': "Error"})
        try:
            bool(req.cookies['Token'])
            resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
        except:
            return JSONResponse(content = {'Value':False,'Message': "UnAuthozied"}) 
        return resp          

@app.post('/wishlistitems')
async def getWishListItems(req:Request):
    try:
        if bool(req.cookies):
            try:
                bool(req.cookies['Token'])
            except:
                return JSONResponse(content = {'Value':False,'Message': "UnAuthozied"})
            tok = t.auth_token(req.cookies['Token'])
            if tok['Value']:
                user = tok['id']
                items = await db.getListItems(await db.db_connect(),'Wishlist',user)
                if items['Value']:
                    resp = JSONResponse(content = {'Value':True,'Result': items['Result']}) 
                    resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
                    return resp
                else:
                    resp = JSONResponse(content = {'Value':False,'Message': items['Message']}) 
                    resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
                    return resp

        resp = JSONResponse(content = {'Value':False,'Message': "UnAuthozied"}) 
        return resp    
    except:
        resp = JSONResponse(content = {'Value':False,'Message': "Error"})
        try:
            bool(req.cookies['Token'])
            resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
        except:
            return JSONResponse(content = {'Value':False,'Message': "UnAuthozied"})
        return resp                       

@app.post('/products')
async def products(req:Request):
    try:
        cond = ''
        if(bool(await req.body())):
            cond = await req.json()
        items = await db.getFilteredProducts(await db.db_connect(),cond)
        resp = JSONResponse(content = {'Value':True,'Result': items['Result']}) 
        if(bool(req.cookies)):
            try:
                bool(req.cookies['Token'])
                resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
            except:
                return resp
        return resp
    except:
        resp = JSONResponse(content = {'Value':False,'Message': "Error"}) 
        try:
            bool(req.cookies['Token'])
            resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
        except:
            return resp
        return resp                       

@app.post('/products/{id}')
async def products(req:Request,id):
    try:
        items = await db.getProduct(await db.db_connect(),id)
        resp = JSONResponse(content = {'Value':True,'Result': items['Result']}) 
        if(bool(req.cookies)):
            try:
                bool(req.cookies['Token'])
                resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
            except:
                return resp
        return resp
    except:
        resp = JSONResponse(content = {'Value':False,'Message': "Error"})
        try:
            bool(req.cookies['Token'])
            resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
        except:
            return resp
        return resp

@app.post('/recommends')
async def recommends(req:Request):
    try:
        if bool(req.cookies):
            try:
                bool(req.cookies['Token'])
            except:
                return JSONResponse(content = {'Value':False,'Message': "UnAuthozied"})
            tok = t.auth_token(req.cookies['Token'])
            if tok['Value']:
                user = tok['id']
                products = await db.getFilteredProducts(await db.db_connect())
                if bool(products):
                    usercart = await db.getListItems(await db.db_connect(),'Cart',user)
                    intrests = []
                    carttemp = []
                    if(usercart['Value']):
                        carttemp = [i['id'] for i in usercart['Result']]
                    userwl = await db.getListItems(await db.db_connect(),'Wishlist',user) 
                    wltemp = [] 
                    if(userwl['Value']):
                        wltemp = [i['id'] for i in userwl['Result']]
                    intrests = carttemp + wltemp
                    if(len(intrests)>0 ):
                        x = np.array(intrests)
                        intrests = np.unique(x)
                        df =  pd.DataFrame(products['Result'])
                        recommends = recommender.recommend(df,intrests)
                        if len(recommends)>0:
                            result = []
                            for prod in products['Result']:
                                if int(prod['id']) in recommends:
                                    result.append(prod)
                            resp = JSONResponse(content = {'Value':True,'Result': result}) 
                            resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
                            return resp
                    else:
                        resp = JSONResponse(content = {'Value':False,'Message': "No recommends"}) 
                        resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
                        return resp    
          

        resp = JSONResponse(content = {'Value':False,'Message': "UnAuthozied"}) 
        return resp    
    except:
        resp = JSONResponse(content = {'Value':False,'Message': "Error"}) 
        resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
        return resp                       

@app.post('/categories')
async def getCategories(req:Request):
    try:
        items = await db. getFromdb(await db.db_connect(),'Category')
        resp = JSONResponse(content = {'Value':True,'Result': items['Result']}) 
        if(bool(req.cookies)):
            try:
                bool(req.cookies['Token'])
                resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
            except:
                return resp
        return resp
    except:
        resp = JSONResponse(content = {'Value':False,'Message': "Error"}) 
        try:
            bool(req.cookies['Token'])
            resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
        except:
            return resp
            
        return resp                       

@app.post('/brands')
async def getBrands(req:Request):
    try:   
        items = await db. getFromdb(await db.db_connect(),'Brand')
        resp = JSONResponse(content = {'Value':True,'Result': items['Result']}) 
        if(bool(req.cookies)):
            try:
                bool(req.cookies['Token'])
                resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
            except:
                return resp
        return resp
    except:
        resp = JSONResponse(content = {'Value':False,'Message': "Error"}) 
        try:
            bool(req.cookies['Token'])
            resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
        except:
            return resp
        return resp    

@app.post('/notifications')
async def getNotifications(req:Request):
    try:
        if bool(req.cookies):
            try:
                bool(req.cookies['Token'])
            except:
                return JSONResponse(content = {'Value':False,'Message': "UnAuthozied"})
            tok = t.auth_token(req.cookies['Token'])
            if tok['Value']:
                notifications = await db.getNotifications(await db.db_connect(),{'user':tok['id'],'date':str(date.today())})
                if notifications['Value']:
                    resp = JSONResponse(content = {'Value':notifications['Value'],'Result': notifications['Result']}) 
                    resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
                    return resp 
                else:
                    resp = JSONResponse(content = {'Value':notifications['Value'],'Result': notifications['Message']}) 
                    resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
                    return resp 

        resp = JSONResponse(content = {'Value':False,'Message': "UnAuthozied"}) 
        return resp    
    except:
        resp = JSONResponse(content = {'Value':False,'Message': "Error"}) 
        resp.set_cookie(key="Token",value=req.cookies['Token'],secure=True,httponly=True)
        return resp 





# Admin
@app.get('/admin')
async def index(req:Request):
    try:
        if(bool(req.cookies)):
            tok = t.auth_token(req.cookies['Token'])
            if tok['Value']:
                if tok['role']==1:    
                    return HTMLResponse(pkg_resources.resource_string(__name__, 'Admin_pages/index.html'))
                else:
                    resp = HTMLResponse(pkg_resources.resource_string(__name__, 'Admin_pages/login.html'))
                    resp.delete_cookie('Token')
                    return resp
                
        return HTMLResponse(pkg_resources.resource_string(__name__, 'Admin_pages/login.html')) 
    except:
            return {'Value':False,'Meassage':"Error"}
   
@app.post('/adminLogout')
async def logout(req:Request):
    try:
        respo = RedirectResponse('/admin', status_code=status.HTTP_302_FOUND)
        if(bool(req.cookies)):
            respo.delete_cookie('Token')
        return respo
    except:
            return {'Value':False,'Meassage':"Error"}

@app.post('/adminauth')
async def adminAuth(req:Request):
    try:
        user = await req.form()
        user_dict = {}
        for i in user:
            user_dict[i] = user[i]
        resp = RedirectResponse('/admin',status_code=status.HTTP_302_FOUND)
        auth = await db.authUser(await db.db_connect(),user_dict)
        if (auth['Value'] and auth['auth']==1): 
            resp.set_cookie(key="Token",value=t.create_access_token({"id":auth['id'],"role":auth['auth']},60),secure=True,httponly=True)
        return resp
    except:
            return {'Value':False,'Meassage':"Error"}

@app.post('/tokenauth')
async def index(req:Request):
    try:
        if bool(req.cookies):
            tok = t.auth_token(req.cookies['Token'])
            if(tok['Value']):
                if tok['Value']:    
                    return {'Value':True , 'Message':"Authorized token"}
                else:
                    return {'Value':False , 'Message':"UnAuthorized"}
        return {'Value':False ,'Message':"UnAuthorized"}
    except:
        return{'Value':False,'Message':"Error"}

@app.post('/form')
async def form(req:Request):
    try:
        if(bool(req.cookies)):
            tok = t.auth_token(req.cookies['Token'])
            if tok['Value'] and tok['role']==1:   
                type = await req.json()
                form = type+"_form.html"
                return {'Value':True,'Result':HTMLResponse(pkg_resources.resource_string(__name__, 'Admin_pages/'+form))}
        return {'Value':401,'Message': "UnAuthorized"}
    except:
            return {'Value':False,'Meassage':"Error"}
    
@app.post('/dbfetch')
async def fetchdb(req:Request):
    try:
        if(bool(req.cookies)):
            tok = t.auth_token(req.cookies['Token'])
            if tok['Value'] and  tok['role']==1:
                table = await req.json()
                result = await db.getFromdb(await db.db_connect(),table)
                return result
        return {'Value':401,'Message': "Unauthorized"}
    except:
            return {'Value':False,'Meassage':"Error"}

@app.post('/dbfetch/{id}')
async def fetchdbById(req:Request,id:int):
    try:
        if(bool(req.cookies)):
            tok = t.auth_token(req.cookies['Token'])
            if tok['Value'] and tok['role']==1:
                table = await req.json()
                result = await db.getIdFromdb(await db.db_connect(),table,id)
                return result
        return {'Value':401,'Message': "Unauthorized"}
    except:
            return {'Value':False,'Meassage':"Error"}

@app.post('/dbinsert')
async def dbInsert(req:Request):
    try:
        if(bool(req.cookies)):
            tok = t.auth_token(req.cookies['Token'])
            if tok['Value'] and tok['role']==1:  
                content = await req.form()
                content_dict = {}
                for i in content:
                    content_dict[i] = content[i]
                result = await db.insertIntoTable(await db.db_connect(),content_dict)
                return result
        return {'Value':401,'Message': "Unauthorized"}
    except:
            return {'Value':False,'Meassage':"Error"}

@app.post('/dbinsert/{id}')
async def dbInsertById(req:Request,id):
    try:
        if(bool(req.cookies)):
            tok = t.auth_token(req.cookies['Token'])
            if tok['Value'] and tok['role']==1:
                content = await req.form()
                content_dict = {}
                for i in content:
                    content_dict[i] = content[i]
                result = await db.updateItem(await db.db_connect(),content_dict,id)
                return result
        return {'Value':401,'Message': "Unauthorized"}
    except:
            return {'Value':False,'Meassage':"Error"}

@app.post('/dbdelete/{id}')
async def dbDeleteById(req:Request,id):
    try:
        if(bool(req.cookies)):
            tok = t.auth_token(req.cookies['Token'])
            if tok['Value'] and tok['role']==1:
                table = await req.json()
                result = await db.deleteById(await db.db_connect(),table,id)
                if table.lower()=='user' and str(tok['id'])==str(id):
                    resp = JSONResponse(content = {'Value':401,'Message': "Unauthorized"})
                    resp.delete_cookie('Token')
                    return resp
                else:
                    return result
        return {'Value':401,'Message': "Unauthorized"}
    except:
            return {'Value':False,'Meassage':"Error"}

