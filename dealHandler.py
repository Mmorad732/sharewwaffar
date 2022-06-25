from email import message
import db_funcs as db
import datetime
async def dealShoutOut(product,date):
    interestedUsers = await db.getHist(await db.db_connect(),product,'interested')
    product_query = await db.getProduct(await db.db_connect(),product)
    offer = str(product_query['Result']['offer']).split('-')
    message = 'Buy '+str(offer[0]) +' '+product_query['Result']['name'] +' before '+str(date+datetime.timedelta(days=1))+' to get '+str(offer[1])+' off or buy it with friends and get it as cashback'
    notificiationList = []
    if interestedUsers['Value']:
        for users in interestedUsers['Result']:
            notificiationList.append({'user':users['user'],'product':product_query['Result']['id'],'message':message,'end_date':str(date)})
    res = await db.addNotifications(await db.db_connect(),notificiationList)
    return res
