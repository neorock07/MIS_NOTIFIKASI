"""
===========================NOTE===============================
Sesuaikan find /tmp/ -type f -name 'xauth_*' 2>/dev/null | head -n 1 dengan lokasi root file xauth_*
lihat dahulu dengan echo $XAUTHORITY, lalu ambil direktori root nya.

misal :
/tmp/xauth_hasduh
maka ambil /tmp/ lalau isikan di kode find /tmp/ -type f -name 'xauth_*' 2>/dev/null | head -n 1

"""




import asyncio
import signal
import webbrowser
from desktop_notifier import DesktopNotifier, Urgency, Button, ReplyField, DEFAULT_SOUND
import requests
import os
import subprocess
import tkinter as tk
from tkinter import ttk
import tkinter as tk
from tkinter import messagebox
from bs4 import BeautifulSoup
from datetime import datetime
import logging

def set_crontab_variable():
    """
        kode untuk set variabel pengaturan untuk xscreensaver pada Crontab
        untuk memberikan permission pada crontab untuk dapat mengakses display.
    """
    
    #mengatur agar menggunakan display ke-0
    os.environ["DISPLAY"] = ":0"
    #mencari key session untuk authority dengan pola (xauth_...)
    #SESUAIKAN DENGEN PATH PADA PC MASING-MASING.
    cm_find = "find /tmp/ -type f -name 'xauth_*' 2>/dev/null | head -n 1"
    path_xauth = ""
    try:
        path_xauth = subprocess.check_output(
                cm_find,
                shell=True,
                text=True
            ).strip()
        if path_xauth:
            os.environ["XAUTHORITY"] = path_xauth
            print(f"PATH XAUTHORITY : {path_xauth}")
        else:
            print("XAUTHORITY NOT FOUND")
    except subprocess.CalledProcessError as e:
        print("Error when find XAUTHORITY")
    return path_xauth



def get_ess_data(nik_mis:str)->dict:
    """
    Mendapatkan data ESS
    
    :param nik_mis (str): nik anggota
    :return response: json response
    """
    
    URL = "https://konimex.com:447/mis/api_ess/getEss"
    response = requests.post(URL, json={'nik_mis' : nik_mis})
    if response.status_code != 200:
        logging.debug(f'Error {response.json()}')
    return response.json()



def clear_html(html:str)->str:
    """
    Membersihkan HTML format
    
    :param html (str): string mengandung html format.
    :return soup (str): string hasil remove html tag.
    
    """
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()


def on_row_selected(event):
    """
    Menangani ketika baris diklik 2 kali, akan menampilkan pop dialog berisi judul dan deskripsi konten.
    """
    
    selected_item = tree.focus()
    if not selected_item:
        return 
    
    item_data = tree.item(selected_item)
    values = item_data["values"]
    popup = tk.Toplevel(root)
    popup.title("Row Details")
    popup.geometry("600x500")
    title_label = tk.Label(
        popup, 
        text="Judul : ",
        font=("Arial", 14, "bold"),
        anchor="w"
        )
    title_label.pack(fill="x", padx=10, pady=5)
    title_content = tk.Label(
        popup, 
        text=values[0],
        font=("Arial", 12),
        wraplength=380, 
        justify="left"
        )
    title_content.pack(fill="x", padx=10)
    desc_label = tk.Label(
        popup, 
        text="Deskripsi : ",
        font=("Arial", 14, "bold"),
        anchor="w"
        )
    desc_label.pack(fill="x", padx=10, pady=5)
    desc_content = tk.Label(
        popup, 
        text=values[1],
        font=("Arial", 12),
        wraplength=380, 
        justify="left"
        )
    desc_content.pack(fill="x", padx=10)
    close_button= ttk.Button(popup, text="Close", command=popup.destroy)
    close_button.pack(pady=10)
    

def show_table(data):
    """
    Membuat tabel untuk menampilkan data ESS.
    
    :param data (dict): data hasil get dari API.
    
    """
    
    #membuat header tabel
    heading_ar = [
        "Judul", 
        "Deskripsi (klik 2x)", 
        "Masalah", 
        "Bagian", 
        "PIC", 
        "No.Telp",
        "Waktu SS Masuk",
        "Status"
        ]
    tree.pack(padx=10, pady=10)
    sty = ttk.Style()
    sty.theme_use('clam')
    sty.configure('Treeview', rowheight=80, font=("Arial", 12))
    
    for i in range(len(heading_ar)):
        index = i+1
        tree.heading(index, text=heading_ar[i])
    
    # memasukkan data ke baris    
    for row in data:
        tree.insert("", "end", values=row)
    
    # membuat horizontal scrollbar
    h_scroll = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(xscrollcommand=h_scroll.set)
    
    # membuat vertical scrollbar
    v_scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=v_scroll.set)
    
    tree.grid(row=0, column=0, sticky="nsew")
    h_scroll.grid(row=1, column=0, sticky="ew")
    v_scroll.grid(row=0, column=1, sticky="ns")
    
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    tree.bind("<Double-1>", on_row_selected)
    
    # tombol untuk close
    close_button = tk.Button(dialog, text="Tutup", command=dialog.destroy)
    close_button.pack(pady=10)
    
    #setting ukuran dialog table pop up
    dialog.update_idletasks()
    dialog.geometry(f"+{root.winfo_screenwidth()//2-dialog.winfo_width()//2}+{root.winfo_screenheight()//2-dialog.winfo_height()//2}")
    # jalankan di main thread.
    root.mainloop()
    

def create_dialog(data):
    """
    Implementasi pembuatan tabel dan assign data    
    
    :param data (dict): data dari API.
    
    """
    
    set_crontab_variable()
    list_ess = data['data']['ess']
    print(list_ess)
    data_arr = []
    for i in list_ess:
        data_arr.append([
            i['judul'],
            clear_html(i['deskripsi']),
            i['masalah'],
            i['bagian'],
            i['pic'],
            i['no_telp'],
            i['waktu_ss_masuk'],
            i['status']
            ])
        
    show_table(data_arr)    



async def main(data) -> None:
    """
    Fungsi utama yang mengintegrasikan setiap fungsi dan menampilkan notifikasi.
    Harus asynchronus;
    
    :param data (dict): data dari API.
    """
    #buat objek untuk menampilkan widget notification 
    notifier = DesktopNotifier(
        app_name=f"EES Notifikasi",
        notification_limit=10,
    )
    
    # tampilkan widget notification
    await notifier.send(
        title=data['message'],
        message=f"Jumlah : {data['jumlah']}",
        urgency=Urgency.Critical,
        buttons=[
            #button untuk mengarahkan ke web ESS;
            Button(
                title="Open Site",
                on_pressed=lambda: webbrowser.open("https://konimex.com:447/mis/surat_servis_mis"),
            ),
            #button untuk menampilkan detail di pop up dialog
            Button(
                title="Detail",
                on_pressed=lambda: create_dialog(data),
            ),
        ],
        
        on_clicked=lambda: print("Notification clicked"),
        on_dismissed=lambda: print("Notification dismissed"),
        sound=DEFAULT_SOUND,
    )

    # Run the event loop forever to respond to user interactions with the notification.
    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()

    loop.add_signal_handler(signal.SIGINT, stop_event.set)
    loop.add_signal_handler(signal.SIGTERM, stop_event.set)

    await stop_event.wait()

if __name__=="__main__":
    
    #inisiasi variabel yang diperlukan di Crontab.
    perkasa = set_crontab_variable()
    #inisiasi pembuatan widget tkinter
    root = tk.Tk()
    root.withdraw()

    dialog = tk.Toplevel(root)
    dialog.title("Detail Task")
    frame = tk.Frame(dialog)
    frame.pack(fill="both", expand=True, padx=10, pady=10)
    tree = ttk.Treeview(frame, columns=(1, 2, 3, 4, 5, 6, 7, 8), show="headings", height=2)

    print(datetime.today())
    
    data = get_ess_data("02348")
    #jalankan jika terdapat pesan ESS masuk.
    if data['jumlah'] > 0:
        asyncio.run(main(data))

