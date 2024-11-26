
url = "https://ohocakes.10orbits-erp.com"
db = "ohocakes_trial"
username = "api@10orbits.com"
password = "api@10orbits.com"
import xmlrpc.client
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
ids = models.execute_kw(db, uid, password, 'account.move', 'search_read', [[['source_document', '=', '2022-08-04-35']]], {'fields': ['partner_id', 'id']})
print(ids)
# ids = models.execute_kw(db, uid, password, 'account.move', 'search', [[['source_document', '=', '2022-08-04-35']]])