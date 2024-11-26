import json
import requests
base_url = "http://ohocake.finliftconsulting.com.np"
database_name = "test"
username = "api@ohocakes.com"
password = "123"
url1 = "/api/auth/token/"
url = "/web/session/authenticate/"
from .models import OdooTokenStore
def post_authenticate():
    headers = {"content-type": "application/json"}
    data = {
        "jsonrpc": "2.0",
        "params": {
        "db": database_name,
        "login": username,
        "password": password}
        }
    res = requests.post("{0}{1}".format(base_url, url),headers=headers,data=json.dumps(data,indent=4))
    print(res.json())
    if res.status_code == 200:
        session_id = res.cookies
        s_id = session_id['session_id']
        ses_id = f"session_id={s_id}"
        header = {
            "login": username,
            "password": password,
            "db": database_name,
            "content-type": "application/jsonp",
            "Cookie":ses_id
        }
        get_tokens = requests.get("{0}{1}".format(base_url, url1), headers=header)
        new_session_id = get_tokens.cookies
        n_s_id = new_session_id['session_id']
        n_ses_id = f"session_id={n_s_id}"
        if get_tokens.status_code == 200:
            ds = get_tokens.json()
            tokens = ds.get('access_token')
            partner_id = ds.get('partner_id')
            if OdooTokenStore.objects.first():
                obj = OdooTokenStore.objects.first()
                obj.access_key = tokens
                obj.partner_id = partner_id
                obj.session_key = n_ses_id
                obj.save()
            else:
                OdooTokenStore.objects.create(access_key=tokens,session_key =n_ses_id, partner_id=partner_id)
            return n_ses_id, tokens, partner_id
        else:
           return "error"
    else:
        return "error"


