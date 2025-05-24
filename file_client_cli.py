import socket
import json
import base64
import logging
import os

server_address = ('0.0.0.0', 7777)

def send_command(command_str=""):
    global server_address
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    logging.warning(f"connecting to {server_address}")
    try:
        logging.warning(f"sending message ")
        sock.sendall(command_str.encode())
        data_received = ""  # empty string
        while True:
            data = sock.recv(16)
            if data:
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                break
        hasil = json.loads(data_received)
        logging.warning("data received from server:")
        return hasil
    except:
        logging.warning("error during data receiving")
        return False

def remote_list():
    command_str = f"LIST"
    hasil = send_command(command_str)
    if hasil['status'] == 'OK':
        print("Daftar file di server:")
        for nmfile in hasil['data']:
            print(f"- {nmfile}")
        return True
    else:
        print("Gagal mendapatkan daftar file")
        return False

def remote_get(filename=""):
    command_str = f"GET {filename}"
    hasil = send_command(command_str)
    if hasil['status'] == 'OK':
        namafile = hasil['data_namafile']
        isifile = base64.b64decode(hasil['data_file'])
        # Simpan file di folder downloads
        os.makedirs('downloads', exist_ok=True)
        save_path = os.path.join('downloads', namafile)
        with open(save_path, 'wb+') as fp:
            fp.write(isifile)
        print(f"File {namafile} berhasil didownload ke folder downloads")
        return True
    else:
        print("Gagal mengunduh file:", hasil.get('data', 'Unknown error'))
        return False

def remote_upload(filename):
    try:
        # Cari file di beberapa lokasi yang mungkin
        possible_locations = [
            filename,  # Direktori saat ini
            os.path.join('files', filename),  # Subfolder files
            os.path.join('../files', filename),  # Folder files di parent directory
            os.path.join(os.path.dirname(__file__), 'files', filename)  # Absolute path
        ]
        
        file_path = None
        for location in possible_locations:
            if os.path.exists(location):
                file_path = location
                break
                
        if not file_path:
            print("File tidak ditemukan. Mencari di lokasi berikut:")
            for loc in possible_locations:
                print(f"- {loc}")
            return False
            
        with open(file_path, 'rb') as fp:
            filedata = fp.read()
            
        encoded_data = base64.b64encode(filedata).decode()
        command_str = f"UPLOAD {os.path.basename(filename)} {encoded_data}"
        hasil = send_command(command_str)
        
        if hasil['status'] == 'OK':
            print(f"File {filename} berhasil diupload ke server")
            return True
        else:
            print("Gagal upload:", hasil.get('data', 'Unknown error'))
            return False
    except Exception as e:
        print(f"Error saat upload: {str(e)}")
        return False

def remote_delete(filename):
    command_str = f"DELETE {filename}"
    hasil = send_command(command_str)
    if hasil['status'] == 'OK':
        print(f"File {filename} berhasil dihapus dari server")
        return True
    else:
        print("Gagal menghapus:", hasil.get('data', 'Unknown error'))
        return False

if __name__ == '__main__':
    server_address = ('172.16.16.101', 2727)  # Ganti dengan IP server
    
    while True:
        print("\nMenu:")
        print("1. List file di server")
        print("2. Download file")
        print("3. Upload file")
        print("4. Delete file")
        print("5. Keluar")
        
        choice = input("Pilih menu (1-5): ")
        
        if choice == '1':
            remote_list()
        elif choice == '2':
            filename = input("Nama file yang akan didownload: ")
            remote_get(filename)
        elif choice == '3':
            filename = input("Nama file yang akan diupload: ")
            remote_upload(filename)
        elif choice == '4':
            filename = input("Nama file yang akan dihapus: ")
            remote_delete(filename)
        elif choice == '5':
            break
        else:
            print("Pilihan tidak valid")