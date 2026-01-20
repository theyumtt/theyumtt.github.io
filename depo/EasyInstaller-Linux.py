import os
import shutil
import sys
import time
import json
from tkinter import Tk, filedialog

# --- YAPILANDIRMA ---
HOME_DIR = os.path.expanduser("~")
BASE_PATH = os.path.join(HOME_DIR, "EasyInstalled")
MEM_PATH = os.path.join(BASE_PATH, "mem")
LANG_PATH = os.path.join(MEM_PATH, "lang")
SETTINGS_FILE = os.path.join(MEM_PATH, "settings.json")

# --- VARSAYILAN DİLLER (Dosya yoksa bunlar oluşturulur) ---
DEFAULT_LANGS = {
    "tr": {
        "title": "      EASY PORTABLE INSTALLER LINUX v1.0      ",
        "menu_1": "1. Yeni AppImage/Portable Kur",
        "menu_2": "2. Ayarlar (Dil Değiştir)",
        "menu_3": "3. Hakkında",
        "menu_4": "4. Çıkış",
        "select_file": "[*] Lütfen kurulacak AppImage dosyasını seçin...",
        "no_file": "[!] Dosya seçilmedi. Ana menüye dönülüyor.",
        "selected": "Seçilen Dosya:",
        "target": "Hedef Konum:",
        "ask_install": "Kurulumu başlatmak istiyor musunuz? (e/h): ",
        "creating_folders": "[+] Hedef klasörler oluşturuldu.",
        "copying": "[*] Dosya kopyalanıyor ve izinler ayarlanıyor...",
        "success": "[V] BAŞARILI! Kurulum tamamlandı.",
        "ask_shortcut": "Uygulama menüsüne (Launcher) eklensin mi? (e/h): ",
        "shortcut_done": "[+] Uygulama menüsüne eklendi: ",
        "error_perm": "[!] HATA: Erişim reddedildi.",
        "about": "Bu program AppImage dosyalarını ~/EasyInstalled dizininde düzenler.",
        "exit": "Güle güle! 👋",
        "press_enter": "\nDevam etmek için Enter'a basın...",
        "lang_changed": "[+] Dil başarıyla değiştirildi!"
    },
    "en": {
        "title": "      EASY PORTABLE INSTALLER LINUX v1.0      ",
        "menu_1": "1. Install New AppImage/Portable",
        "menu_2": "2. Settings (Change Language)",
        "menu_3": "3. About",
        "menu_4": "4. Exit",
        "select_file": "[*] Please select the AppImage file to install...",
        "no_file": "[!] No file selected. Returning to menu.",
        "selected": "Selected File:",
        "target": "Target Path:",
        "ask_install": "Do you want to start the installation? (y/n): ",
        "creating_folders": "[+] Target folders created.",
        "copying": "[*] Copying file and setting permissions...",
        "success": "[V] SUCCESS! Installation completed.",
        "ask_shortcut": "Add to application menu (Launcher)? (y/n): ",
        "shortcut_done": "[+] Added to application menu: ",
        "error_perm": "[!] ERROR: Permission denied.",
        "about": "This program organizes AppImage files in ~/EasyInstalled directory.",
        "exit": "Goodbye! 👋",
        "press_enter": "\nPress Enter to continue...",
        "lang_changed": "[+] Language changed successfully!"
    }
}

L = {}

# --- FONKSİYONLAR ---

def sistem_hazirla():
    """Gerekli klasörleri ve dil dosyalarını oluşturur."""
    os.makedirs(LANG_PATH, exist_ok=True)
    for lang_code, content in DEFAULT_LANGS.items():
        file_path = os.path.join(LANG_PATH, f"{lang_code}.json")
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(content, f, ensure_ascii=False, indent=4)

def dil_yukle(lang_code):
    file_path = os.path.join(LANG_PATH, f"{lang_code}.json")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return DEFAULT_LANGS.get(lang_code, DEFAULT_LANGS["tr"])

def ayarları_oku():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get("lang", "tr")
        except:
            pass
    return "tr"

def ayarları_kaydet(lang_code):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump({"lang": lang_code}, f)

def ekrani_temizle():
    os.system('clear')

def baslik_yazdir():
    ekrani_temizle()
    print("\033[96m" + "="*50)
    print("\033[96m" + L.get("title", "Easy Installer"))
    print("\033[96m" + "="*50 + "\n\033[0m")

def kisayol_olustur(hedef_exe, uygulama_adi):
    try:
        apps_path = os.path.join(HOME_DIR, ".local/share/applications")
        os.makedirs(apps_path, exist_ok=True)
        desktop_file = os.path.join(apps_path, f"{uygulama_adi.lower()}.desktop")

        content = f"[Desktop Entry]\nType=Application\nName={uygulama_adi}\nExec=\"{hedef_exe}\"\nIcon=system-run\nTerminal=false\nCategories=Utility;"

        with open(desktop_file, "w") as f:
            f.write(content)
        os.chmod(desktop_file, 0o755)
        print("\033[92m" + L["shortcut_done"] + uygulama_adi + "\033[0m")
    except Exception as e:
        print(f"\033[91m[!] Hata: {e}\033[0m")

def kurulum_yap():
    baslik_yazdir()
    print("\033[93m" + L["select_file"] + "\033[0m")

    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    kaynak = filedialog.askopenfilename(filetypes=[("AppImage", "*.AppImage"), ("All", "*")])
    root.destroy()

    if not kaynak:
        print("\033[91m" + L["no_file"] + "\033[0m")
        input(L["press_enter"])
        return

    uygulama_adi = os.path.splitext(os.path.basename(kaynak))[0]
    hedef_klasor = os.path.join(BASE_PATH, uygulama_adi)
    hedef_dosya = os.path.join(hedef_klasor, os.path.basename(kaynak))

    print(f"\n\033[92m{L['selected']} \033[0m{uygulama_adi}")
    print(f"\033[92m{L['target']} \033[0m{hedef_klasor}")

    if input("\n\033[93m" + L["ask_install"] + "\033[0m").lower() in ['e', 'y']:
        try:
            print("\033[93m" + L["copying"] + "\033[0m")
            os.makedirs(hedef_klasor, exist_ok=True)
            shutil.copy2(kaynak, hedef_dosya)
            os.chmod(hedef_dosya, 0o755)
            print("\033[92m" + L["success"] + "\033[0m")

            if input("\n\033[96m" + L["ask_shortcut"] + "\033[0m").lower() in ['e', 'y']:
                kisayol_olustur(hedef_dosya, uygulama_adi)
        except PermissionError:
            print("\033[91m" + L["error_perm"] + "\033[0m")
        except Exception as e:
            print(f"\033[91m[!] Hata: {e}\033[0m")

    input(L["press_enter"])

def main():
    global L
    sistem_hazirla()
    dil_kodu = ayarları_oku()
    L = dil_yukle(dil_kodu)

    while True:
        baslik_yazdir()
        print(L["menu_1"])
        print(L["menu_2"])
        print(L["menu_3"])
        print(L["menu_4"])

        secim = input("\n\033[93m>>> \033[0m")

        if secim == '1':
            kurulum_yap()
        elif secim == '2':
            yeni = "en" if dil_kodu == "tr" else "tr"
            ayarları_kaydet(yeni)
            dil_kodu = yeni
            L = dil_yukle(yeni)
            print("\033[92m" + L["lang_changed"] + "\033[0m")
            time.sleep(1)
        elif secim == '3':
            baslik_yazdir()
            print("\033[96m" + L["about"] + "\033[0m")
            input(L["press_enter"])
        elif secim == '4':
            baslik_yazdir()
            print("\033[92m" + L["exit"] + "\033[0m")
            time.sleep(1)
            break

if __name__ == "__main__":
    main()
