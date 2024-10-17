import requests
import os
import json
from prettytable import PrettyTable

# Fungsi untuk menampilkan ASCII art judul "Sercing"
def print_title():
    title = """
    ███████╗███████╗██████╗  ██████╗██╗███╗   ██╗ ██████╗ 
    ██╔════╝██╔════╝██╔══██╗██╔════╝██║████╗  ██║██╔════╝ 
    ███████╗█████╗  ██████╔╝██║     ██║██╔██╗ ██║██║  ███╗
    ╚════██║██╔══╝  ██╔═══╝ ██║     ██║██║╚██╗██║██║   ██║
    ███████║███████╗██║     ╚██████╗██║██║ ╚████║╚██████╔╝
    ╚══════╝╚══════╝╚═╝      ╚═════╝╚═╝╚═╝  ╚═══╝ ╚═════╝ 
                                                         
    """
    print(title)

# Fungsi untuk menyimpan API key agar hanya perlu input satu kali
def get_api_key():
    api_key_file = "api_key.json"
    
    if os.path.exists(api_key_file):
        with open(api_key_file, 'r') as f:
            data = json.load(f)
            return data.get("api_key", None)
    
    print("\n🚀 First time setup: Let's get your SerpApi key.")
    api_key = input("🔐 Enter your SerpApi API Key: ")
    
    with open(api_key_file, 'w') as f:
        json.dump({"api_key": api_key}, f)
    
    print("✅ API Key saved for future use!")
    return api_key

# Fungsi untuk menentukan ikon berdasarkan ekstensi file
def get_file_icon(file_name):
    if file_name.endswith(".pdf"):
        return "📕"  # PDF file
    elif file_name.endswith(".doc") or file_name.endswith(".docx"):
        return "📄"  # Word document
    elif file_name.endswith(".xls") or file_name.endswith(".xlsx"):
        return "📊"  # Excel file
    elif file_name.endswith(".ppt") or file_name.endswith(".pptx"):
        return "📑"  # PowerPoint file
    elif file_name.endswith(".png") or file_name.endswith(".jpg") or file_name.endswith(".jpeg"):
        return "🖼️"  # Image file
    elif file_name.endswith(".txt"):
        return "📝"  # Text file
    else:
        return "📁"  # Default for other files

# Fungsi untuk menangani pencarian file dengan paginasi dan menampilkan hanya nama file dan ekstensinya
def search_files(api_key, domain, file_extension, file_name=None, max_results=50):
    print(f"\n🔎 Searching for files on {domain} with extension: {file_extension if file_extension else 'All'}...")
    
    query = f"site:{domain} "
    
    if file_name:
        query += f'"{file_name}" '  # Mencari nama file spesifik jika diberikan
    
    if file_extension:
        query += f"ext:{file_extension}"
    else:
        query += "ext:pdf OR ext:docx OR ext:xlsx OR ext:pptx OR ext:png OR ext:jpg OR ext:jpeg"

    all_results = []
    start = 0  # Paginate from result 0
    
    while True:
        params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
            "start": start  # Untuk mengambil halaman berikutnya
        }

        response = requests.get("https://serpapi.com/search", params=params)
        data = response.json()

        # Penanganan jika API limit sudah habis
        if "error" in data and "API limit" in data["error"]:
            print("⚠️ API limit reached. Please upgrade or wait for quota reset.")
            return []

        if 'organic_results' not in data or not data['organic_results']:
            break  # Keluar jika tidak ada hasil lagi

        # Mendapatkan nama file dan ekstensi dari URL
        search_results = [result['link'].split('/')[-1] for result in data['organic_results']]
        all_results.extend(search_results)
        start += 10  # Menambah indeks untuk mengambil halaman berikutnya
        print(f"📄 Fetching more results... Total files found so far: {len(all_results)}")

        if len(all_results) >= max_results:  # Batas hasil yang ingin diambil
            break

    if not all_results:
        print("🚫 No files found.")
        return []

    # Membuat tabel hasil pencarian
    table = PrettyTable()
    table.field_names = ["#", "Icon", "File Name", "Extension"]
    
    for idx, result in enumerate(all_results, 1):
        icon = get_file_icon(result)
        file_name, file_ext = os.path.splitext(result)
        table.add_row([idx, icon, file_name, file_ext])

    print("\n🔗 List of found files (in table format):")
    print(table)

    return all_results

# Fungsi untuk membuat folder spesifik untuk pencarian
def create_search_folder(domain):
    # Nama folder berdasarkan domain
    folder_name = f"search_results_{domain}"
    
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"📁 Created folder: {folder_name}")
    else:
        print(f"📁 Using existing folder: {folder_name}")
    
    return folder_name

# Fungsi untuk mendownload file yang dipilih user
def download_file(domain, file_name, save_path):
    try:
        url = f"https://{domain}/{file_name}"
        response = requests.get(url, stream=True)
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        print(f"✅ File downloaded and saved at {save_path}")
    except Exception as e:
        print(f"⚠️ Error while downloading file: {e}")

# Fungsi untuk mendownload semua file yang ditemukan
def download_all_files(domain, file_list, folder_name):
    print("\n📥 Starting download of all files...")
    
    for file_name in file_list:
        save_path = os.path.join(folder_name, file_name)
        print(f"⏳ Downloading {file_name}...")
        download_file(domain, file_name, save_path)

    print("\n🎉 All files downloaded successfully!")

# Fungsi utama untuk menjalankan program
def main():
    print_title()
    
    # Mendapatkan API key (disimpan untuk penggunaan berikutnya)
    api_key = get_api_key()
    
    domain = input("\n🌐 Enter the website domain (example: example.com): ")
    file_name = input("📄 Enter a specific file name to search (leave blank if none): ")
    file_extension = input("📝 Enter file extension to search (e.g., pdf, docx, xlsx, leave blank for all): ")
    max_results = int(input("🔢 How many results to fetch (example: 50): "))
    
    # Mencari file di domain yang diinput user dengan batas hasil tertentu
    search_results = search_files(api_key, domain, file_extension, file_name, max_results)
    
    if not search_results:
        return
    
    # Membuat folder spesifik untuk setiap pencarian
    search_folder = create_search_folder(domain)

    print("\n🎯 What would you like to do next?")
    print("  1. Download a specific file")
    print("  2. Download all files")
    user_choice = input("➡️  Enter your choice (1/2): ")

    if user_choice == "1":
        # Memilih file untuk didownload satu per satu
        try:
            file_index = int(input("\n📂 Enter the file index to download: ")) - 1
            if 0 <= file_index < len(search_results):
                file_name = search_results[file_index]
                
                # Menentukan path penyimpanan di folder spesifik
                save_path = os.path.join(search_folder, file_name)
                
                # Mendownload file
                download_file(domain, file_name, save_path)
            else:
                print("❌ Invalid index selected.")
        except ValueError:
            print("❌ Please enter a valid number.")

    elif user_choice == "2":
        # Mendownload semua file ke folder pencarian
        download_all_files(domain, search_results, search_folder)
    else:
        print("❌ Invalid choice. Exiting.")

# Memulai program
if __name__ == "__main__":
    main()
