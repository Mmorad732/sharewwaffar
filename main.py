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
async def login(req:Request):
    if not bool(req.cookies) or bool(await req.body()):
        user = await req.json()
        auth = db.authUser(db.db_connect(),user)
        if (auth['Value'] and auth['auth']==2): 
            resp = JSONResponse(content = {"Value":True,"Message": "Authorized"})
            resp.set_cookie(key="Token",value=t.create_access_token({"id":auth['id']},5),secure=True,httponly=True)
            return resp
    else:
        tok = t.auth_token(req.cookies['Token'])
        if tok['Value']:
            auth = await db.getIdFromdb(db.db_connect(),'user',tok['id'],'authorization')
            if auth['Value'] and auth['Result']['authorization']==2:
                resp = JSONResponse(content = {"Value":True,"Message": "Authorized token"}) 
                return resp
    resp = JSONResponse(content = {"Value":False,"Message": "UnAuthorized"})
    return resp

# Admin
@app.get('/admin')
async def index(req:Request):
    if(bool(req.cookies)):
        tok = t.auth_token(req.cookies['Token'])
        if tok['Value']:
            adminAuth = await db.getIdFromdb(db.db_connect(),'user',tok['id'],'authorization')
            if adminAuth['Value'] and adminAuth['Result']['authorization']==1:    
                return HTMLResponse(pkg_resources.resource_string(__name__, 'Admin_pages/index.html'))
            else:
                resp = HTMLResponse(pkg_resources.resource_string(__name__, 'Admin_pages/login.html'))
                resp.delete_cookie('Token')
                return resp
            
    return HTMLResponse(pkg_resources.resource_string(__name__, 'Admin_pages/login.html')) 
   
@app.post('/adminLogout')
async def logout(req:Request):
    respo = RedirectResponse('/admin', status_code=status.HTTP_302_FOUND)
    if(bool(req.cookies)):
        respo.delete_cookie('Token')
    return respo

@app.post('/adminauth')
async def adminAuth(req:Request):
    user = await req.form()
    user_dict = {}
    for i in user:
        user_dict[i] = user[i]
    resp = RedirectResponse('/admin',status_code=status.HTTP_302_FOUND)
    auth = db.authUser(db.db_connect(),user_dict)
    if (auth['Value'] and auth['auth']==1): 
        resp.set_cookie(key="Token",value=t.create_access_token({"id":auth['id']},30),secure=True,httponly=True)
    return resp

@app.post('/tokenauth')
async def index(req:Request):
    if bool(req.cookies):
        tok = t.auth_token(req.cookies['Token'])
        if(tok['Value']):
            if tok['Value']:    
                return {'Value':True , 'Message':"Authorized token"}
            else:
                return {'Value':False , 'Message':"UnAuthorized"}
    return {"Value":False , "Message":"UnAuthorized"}

@app.post('/form')
async def form(req:Request):
    if(bool(req.cookies)):
        tok = t.auth_token(req.cookies['Token'])
        if tok['Value']:
            adminAuth = await db.getIdFromdb(db.db_connect(),'user',tok['id'],'authorization')
            if adminAuth['Value'] and adminAuth['Result']['authorization']==1:
                type = await req.json()
                form = type+"_form.html"
                return {'Value':True,'Result':HTMLResponse(pkg_resources.resource_string(__name__, 'Admin_pages/'+form))}
    return {'Value':401,'Message': "UnAuthorized"}
    
@app.post('/dbfetch')
async def fetchdb(req:Request):
    if(bool(req.cookies)):
        tok = t.auth_token(req.cookies['Token'])
        if tok['Value']:
            adminAuth = await db.getIdFromdb(db.db_connect(),'user',tok['id'],'authorization')
            if adminAuth['Value'] and adminAuth['Result']['authorization']==1:
                table = await req.json()
                result = db.getFromdb(db.db_connect(),table)
                return result
    return {'Value':401,'Message': "Unauthorized"}

@app.post('/dbfetch/{id}')
async def fetchdbById(req:Request,id:int):
    if(bool(req.cookies)):
        tok = t.auth_token(req.cookies['Token'])
        if tok['Value']:
            adminAuth = await db.getIdFromdb(db.db_connect(),'user',tok['id'],'authorization')
            if adminAuth['Value'] and adminAuth['Result']['authorization']==1:
                table = await req.json()
                result = await db.getIdFromdb(db.db_connect(),table,id)
                return result
    return {'Value':401,'Message': "Unauthorized"}

@app.post('/dbinsert')
async def dbInsert(req:Request):
    if(bool(req.cookies)):
        tok = t.auth_token(req.cookies['Token'])
        if tok['Value']:
            adminAuth = await db.getIdFromdb(db.db_connect(),'user',tok['id'],'authorization')
            if adminAuth['Value'] and adminAuth['Result']['authorization']==1:
                content = await req.form()
                content_dict = {}
                for i in content:
                    content_dict[i] = content[i]
                result = await db.insertIntoTable(db.db_connect(),content_dict)
                return result
    return {'Value':401,'Message': "Unauthorized"}

@app.post('/dbinsert/{id}')
async def dbInsertById(req:Request,id):
    if(bool(req.cookies)):
        tok = t.auth_token(req.cookies['Token'])
        if tok['Value']:
            adminAuth = await db.getIdFromdb(db.db_connect(),'user',tok['id'],'authorization')
            if adminAuth['Value'] and adminAuth['Result']['authorization']==1:
                content = await req.form()
                content_dict = {}
                for i in content:
                    content_dict[i] = content[i]
                result = await db.updateItem(db.db_connect(),content_dict,id)
                return result
    return {'Value':401,'Message': "Unauthorized"}

@app.post('/dbdelete/{id}')
async def list(req:Request,id):
    if(bool(req.cookies)):
        tok = t.auth_token(req.cookies['Token'])
        if tok['Value']:
            adminAuth = await db.getIdFromdb(db.db_connect(),'user',tok['id'],'authorization')
            if adminAuth['Value'] and adminAuth['Result']['authorization']==1:
                table = await req.json()
                result = await db.deleteById(db.db_connect(),table,id)
                return result
    return {'Value':401,'Message': "Unauthorized"}

