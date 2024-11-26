from win11toast import toast, notify
from pathlib import Path
import requests
import logging

def get_ess_data(nik_mis:str)->dict:
    """
    Function untuk mendapatkan data dari API.
    
    :param nik_mis (str): nik setiap anggota MIS.
    :return (dict): data dari API.
    """
    
    URL = "https://konimex.com:447/mis/api_ess/getEss"
    response = requests.post(URL, json={'nik_mis':nik_mis})
    if response.status_code != 200:
        logging.debug(f"Error : {response.json()}")
    return response.json()   

def run(nik_mis:str):
    """
    Menampilkan push-notifications pada windows.
    
    :param nik_mis (str): nik mis setiap anggota.
    
    """
    
    BASE_DIR = Path(__file__).resolve(strict=True).parent
    data = get_ess_data(nik_mis=nik_mis)
    
    buttons = [
        {'activationType': 'protocol', 'arguments': 'https://konimex.com:447/mis/surat_servis_mis', 'content': 'Open Site'},
        {'activationType': 'protocol', 'arguments': f'{BASE_DIR}\dialog.pyw', 'content': 'Detail'}
    ]
    if data['jumlah'] > 0:
        notify(data['message'], f"Jumlah : {data['jumlah']}", buttons=buttons, scenario='incomingCall')

if __name__=="__main__":
    run("02348")