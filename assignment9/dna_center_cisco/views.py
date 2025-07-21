# dna_center_cisco/views.py

import requests, urllib3, datetime
from requests.auth import HTTPBasicAuth
from django.shortcuts import render
from .dnac_config import DNAC
from pymongo import MongoClient

urllib3.disable_warnings()

MONGO_URI = "mongodb://34.224.75.144:27017"
client = MongoClient(MONGO_URI)
log_collection = client.assignment9.logs

class DNAC_Manager:
    def __init__(self):
        self.token = None

    def get_auth_token(self):
        try:
            url = f"https://{DNAC['host']}:{DNAC['port']}/dna/system/api/v1/auth/token"
            response = requests.post(url, auth=HTTPBasicAuth(DNAC['username'], DNAC['password']), verify=False)
            response.raise_for_status()
            self.token = response.json()['Token']
            self.log("Auth", "Success")
            return self.token
        except Exception as e:
            self.log("Auth", f"Failed: {e}")
            return None

    def get_network_devices(self):
        try:
            url = f"https://{DNAC['host']}:{DNAC['port']}/api/v1/network-device"
            headers = {"X-Auth-Token": self.token}
            response = requests.get(url, headers=headers, verify=False)
            response.raise_for_status()
            return response.json().get('response', [])
        except Exception as e:
            self.log("Devices", f"Failed: {e}")
            return []

    def get_device_interfaces(self, ip):
        try:
            devices = self.get_network_devices()
            device = next((d for d in devices if d.get('managementIpAddress') == ip), None)
            if not device: return []
            url = f"https://{DNAC['host']}:{DNAC['port']}/api/v1/interface"
            headers = {"X-Auth-Token": self.token}
            params = {"deviceId": device['id']}
            response = requests.get(url, headers=headers, params=params, verify=False)
            response.raise_for_status()
            self.log(ip, "Interfaces Success")
            return response.json().get('response', [])
        except Exception as e:
            self.log(ip, f"Interfaces Failed: {e}")
            return []

    def log(self, ip_or_action, result):
        log_collection.insert_one({
            "timestamp": datetime.datetime.utcnow(),
            "target": ip_or_action,
            "result": result
        })

def show_token(request):
    dnac = DNAC_Manager()
    token = dnac.get_auth_token()
    return render(request, "token.html", {"token": token})

def list_devices(request):
    dnac = DNAC_Manager()
    dnac.get_auth_token()
    devices = dnac.get_network_devices()
    return render(request, "devices.html", {"devices": devices})

def device_interfaces(request):
    ip = request.GET.get("ip")
    dnac = DNAC_Manager()
    dnac.get_auth_token()
    interfaces = dnac.get_device_interfaces(ip)
    return render(request, "interfaces.html", {"interfaces": interfaces, "ip": ip})

def home(request):
    return render(request, "home.html")
