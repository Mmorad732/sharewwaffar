from urllib import request
from fastapi import FastAPI , Request
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
import tokenfns as t
import db_funcs as db
from fastapi.staticfiles import StaticFiles
import pkg_resources
import starlette.status as status
from fastapi.templating import Jinja2Templates

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
            if (auth['Value'] and auth['auth']==2): 
                resp = JSONResponse(content = {"Value":auth['Value'],"Message": auth['Message']})
                resp.set_cookie(key="Token",value=t.create_access_token({"id":auth['id'],"role":auth['auth']},60),secure=True,httponly=True)
                return resp
            else:
                resp = JSONResponse(content = {"Value":auth['Value'],"Message": auth['Message']})
                return resp
        elif bool(req.cookies):
            tok = t.auth_token(req.cookies['Token'])
            if tok['Value']:
                auth = await db.getIdFromdb(await db.db_connect(),'user',tok['id'],'authorization')
                if auth['Value'] and tok['role']==1:
                    resp = JSONResponse(content = {"Value":auth['Value'],"Message": "Authorized User"}) 
                    return resp
        resp = JSONResponse(content = {"Value":True,"Message": "Guest"})
        return resp
    except:
        return {'Value':False,'Meassage':"Error"}

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
            return resp
        return {'Value':False,'Message':"Empty fields"}
    except:
            return {'Value':False,'Meassage':"Error"}



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

