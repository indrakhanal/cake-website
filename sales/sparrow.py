from .models import *
from django.shortcuts import render, redirect
from django.http.response import Http404
from django.http import JsonResponse

from .models import *
import requests
import uuid
import base64
import json

def send_order_sms(vendor,to_mobile,message):
   url = "http://api.sparrowsms.com/v2/sms/"
   headers= {
         "Content-Type": "application/json"
   }
   payload = {
      "token": "F6SQ2Mn444daU8Q8uDcU",
      "from": vendor,
      "to": str(to_mobile),
      "text": message
   }

   response = requests.post(url, data = json.dumps(payload),headers= headers)
   return response
   
   
   
  
