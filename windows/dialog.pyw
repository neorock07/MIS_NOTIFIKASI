import requests
import logging
import tkinter as tk
from tkinter import ttk
from bs4 import BeautifulSoup
from tkinter import messagebox

root = tk.Tk()
root.withdraw()

dialog = tk.Toplevel(root)
dialog.title("Detail Task")
frame = tk.Frame(dialog)
frame.pack(fill="both", expand=True, padx=10, pady=10)    
tree = ttk.Treeview(frame, columns=(1, 2, 3,4, 5, 6, 7, 8), show="headings", height=2, )

def extract_html(html:str)->str:
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()

def sort_column(tree, col, reverse):
    """
    Fungsi untuk mengurutkan data di kolom Treeview.
    """
    data_list = [(tree.set(item, col), item) for item in tree.get_children("")]

    data_list.sort(key=lambda t: t[0], reverse=reverse)

    for index, (val, item) in enumerate(data_list):
        tree.move(item, "", index)

    tree.heading(col, command=lambda: sort_column(tree, col, not reverse))


def on_row_select(event):
    selected_item = tree.focus()
    if not selected_item:
        return
    
    item_data = tree.item(selected_item)  
    values = item_data["values"]  

    popup = tk.Toplevel(root)
    popup.title("Row Details")
    popup.geometry("600x500")

    title_label = tk.Label(
        popup, text="Judul:", font=("Arial", 14, "bold"), anchor="w"
    )
    title_label.pack(fill="x", padx=10, pady=5)
    title_content = tk.Label(
        popup, text=values[0], font=("Arial", 12), wraplength=380, justify="left"
    )
    title_content.pack(fill="x", padx=10)

    desc_label = tk.Label(
        popup, text="Deskripsi:", font=("Arial", 14, "bold"), anchor="w"
    )
    desc_label.pack(fill="x", padx=10, pady=5)
    desc_content = tk.Label(
        popup, text=values[1], font=("Arial", 12), wraplength=380, justify="left"
    )
    desc_content.pack(fill="x", padx=10)

    close_button = ttk.Button(popup, text="Close", command=popup.destroy)
    close_button.pack(pady=10)

def show_table_dialog(data):
    """
    Function untuk membuat dialog untuk detail task dalam bentuk 
    tabel.
    
    :param data (list): data dari API.
    
    """
    headings_ar = ["Judul", "Deskripsi (klik 2x)", "Masalah", "Bagian", "PIC", "No.Telp", "Waktu SS Masuk", "Status"]
    
    tree.pack(padx=10, pady=10)
    sty  = ttk.Style()
    sty.theme_use('clam')
    sty.configure('Treeview', rowheight=80, font=("Arial", 12))
    
    for i in range(len(headings_ar)):
        index = i+1
        tree.heading(index, text=headings_ar[i])

    for row in data:
        tree.insert("", "end", values=row)

    # Scrollbar Horizontal
    h_scroll = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(xscrollcommand=h_scroll.set)

    # Scrollbar Vertical
    v_scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=v_scroll.set)

    tree.grid(row=0, column=0, sticky="nsew")
    h_scroll.grid(row=1, column=0, sticky="ew")
    v_scroll.grid(row=0, column=1, sticky="ns")

    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    tree.bind("<Double-1>", on_row_select)
    
    close_button = tk.Button(dialog, text="Tutup", command=dialog.destroy)
    close_button.pack(pady=10)

    dialog.update_idletasks()
    dialog.geometry(f"+{root.winfo_screenwidth()//2-dialog.winfo_width()//2}+{root.winfo_screenheight()//2-dialog.winfo_height()//2}")

    root.mainloop()


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

def create_dialog(nik_mis:str):
    """
    menampilkan dialog pop up untuk detail task.
    
    :param nik_mis (str): nik tiap anggota mis.
    
    """
    
    data = get_ess_data(nik_mis)
    list_ess = data['data']['ess']
    data_arr = []
    
    for i in list_ess:
        data_arr.append(
            [
            i["judul"],
            extract_html(i["deskripsi"]),
            i["masalah"],
            i["bagian"],
            i["pic"],
            i["no_telp"],
            i["waktu_ss_masuk"],
            i["status"]
            ])
        
    show_table_dialog(data_arr)

    
if __name__=='__main__':
    create_dialog("02348")    