import os
import shutil
import sys
import time
import json
from tkinter import Tk, filedialog

# Kısayol modülü kontrolü
try:
    import win32com.client
except ImportError:
    pass

# Renklendirme kontrolü
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    class Fore: GREEN = ""; RED = ""; CYAN = ""; YELLOW = ""; RESET = ""
    class Style: BRIGHT = ""; RESET_ALL = ""

# --- YAPILANDIRMA VE DOSYA YOLLARI ---
BASE_PATH = r"C:\EasyInstalled"
MEM_PATH = os.path.join(BASE_PATH, "mem")
SETTINGS_FILE = os.path.join(MEM_PATH, "settings.json")

# --- GENİŞLETİLMİŞ DİL SÖZLÜĞÜ ---
LANGUAGES = {
    "tr": {
        "title": "      EASY PORTABLE INSTALLER v1.0     ",
        "menu_1": "1. Yeni Portable Program Kur",
        "menu_2": "2. Ayarlar (Dil Değiştir)",
        "menu_3": "3. Hakkında",
        "menu_4": "4. Çıkış",
        "select_exe": "[*] Lütfen kurulacak .exe dosyasını seçin...",
        "no_file": "[!] Dosya seçilmedi. Ana menüye dönülüyor.",
        "selected": "Seçilen Dosya:",
        "target": "Hedef Konum:",
        "ask_install": "Kurulumu başlatmak istiyor musunuz? (e/h): ",
        "creating_folders": "[+] Hedef klasörler oluşturuldu.",
        "copying": "[*] Dosya kopyalanıyor...",
        "success": "[V] BAŞARILI! Kurulum tamamlandı.",
        "ask_shortcut": "Masaüstüne kısayol oluşturulsun mu? (e/h): ",
        "shortcut_done": "[+] Masaüstüne kısayol oluşturuldu: ",
        "error_perm": "[!] HATA: Erişim reddedildi. Yönetici olarak çalıştırın.",
        "about": "Bu program taşınabilir dosyaları C: dizininde düzenler.",
        "exit": "Güle güle! 👋",
        "press_enter": "\nDevam etmek için Enter'a basın...",
        "lang_changed": "[+] Dil başarıyla değiştirildi!"
    },
    "en": {
        "title": "      EASY PORTABLE INSTALLER v1.0      ",
        "menu_1": "1. Install New Portable Program",
        "menu_2": "2. Settings (Change Language)",
        "menu_3": "3. About",
        "menu_4": "4. Exit",
        "select_exe": "[*] Please select the .exe file to install...",
        "no_file": "[!] No file selected. Returning to menu.",
        "selected": "Selected File:",
        "target": "Target Path:",
        "ask_install": "Do you want to start the installation? (y/n): ",
        "creating_folders": "[+] Target folders created.",
        "copying": "[*] Copying file...",
        "success": "[V] SUCCESS! Installation completed.",
        "ask_shortcut": "Create desktop shortcut? (y/n): ",
        "shortcut_done": "[+] Desktop shortcut created: ",
        "error_perm": "[!] ERROR: Permission denied. Run as Administrator.",
        "about": "This program organizes portable files in C: directory.",
        "exit": "Goodbye! 👋",
        "press_enter": "\nPress Enter to continue...",
        "lang_changed": "[+] Language changed successfully!"
    },
    "de": {
        "title": "      EASY PORTABLE INSTALLER v1.0     ",
        "menu_1": "1. Yeni Portable Programm installieren",
        "menu_2": "2. Einstellungen (Sprache ändern)",
        "menu_3": "3. Über",
        "menu_4": "4. Beenden",
        "select_exe": "[*] Bitte wählen Sie die zu installierende .exe-Datei...",
        "no_file": "[!] Keine Datei ausgewählt. Zurück zum Menü.",
        "selected": "Ausgewählte Datei:",
        "target": "Zielpfad:",
        "ask_install": "Installation starten? (j/n): ",
        "creating_folders": "[+] Zielordner erstellt.",
        "copying": "[*] Datei wird kopiert...",
        "success": "[V] ERFOLG! Installation abgeschlossen.",
        "ask_shortcut": "Desktop-Verknüpfung erstellen? (j/n): ",
        "shortcut_done": "[+] Desktop-Verknüpfung erstellt: ",
        "error_perm": "[!] FEHLER: Zugriff verweigert. Als Administrator ausführen.",
        "about": "Dieses Programm organisiert portable Dateien im Verzeichnis C:.",
        "exit": "Auf Wiedersehen! 👋",
        "press_enter": "\nDrücken Sie die Eingabetaste, um fortzufahren...",
        "lang_changed": "[+] Sprache erfolgreich geändert!"
    },
    "ru": {
        "title": "      EASY PORTABLE INSTALLER v1.0      ",
        "menu_1": "1. Установить новую портативную программу",
        "menu_2": "2. Настройки (Сменить язык)",
        "menu_3": "3. О программе",
        "menu_4": "4. Выход",
        "select_exe": "[*] Пожалуйста, выберите файл .exe для установки...",
        "no_file": "[!] Файл не выбран. Возврат в меню.",
        "selected": "Выбранный файл:",
        "target": "Целевой путь:",
        "ask_install": "Начать установку? (д/н): ",
        "creating_folders": "[+] Целевые папки созданы.",
        "copying": "[*] Копирование файла...",
        "success": "[V] УСПЕХ! Установка завершена.",
        "ask_shortcut": "Создать ярлык на рабочем столе? (д/н): ",
        "shortcut_done": "[+] Ярлык на рабочем столе создан: ",
        "error_perm": "[!] ОШИБКА: Доступ запрещен. Запустите от имени администратора.",
        "about": "Эта программа организует портативные файлы в каталоге C:.",
        "exit": "До свидания! 👋",
        "press_enter": "\nНажмите Enter, чтобы продолжить...",
        "lang_changed": "[+] Язык успешно изменен!"
    }
}

L = LANGUAGES["tr"]

def ayarları_yukle():
    if not os.path.exists(MEM_PATH):
        os.makedirs(MEM_PATH)
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("lang", "tr")
        except:
            return "tr"
    return None

def ayarları_kaydet(lang_code):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump({"lang": lang_code}, f)

def dil_secme_ekrani():
    ekrani_temizle()
    print(Fore.YELLOW + "Select Language / Dil Seçin / Sprache wählen / Выберите язык:")
    print("1. Türkçe")
    print("2. English")
    print("3. Deutsch")
    print("4. Русский")
    choice = input("\n>>> ")
    
    mapping = {"1": "tr", "2": "en", "3": "de", "4": "ru"}
    lang = mapping.get(choice, "tr")
    
    ayarları_kaydet(lang)
    return lang

def ekrani_temizle():
    os.system('cls' if os.name == 'nt' else 'clear')

def baslik_yazdir():
    ekrani_temizle()
    print(Fore.CYAN + Style.BRIGHT + "="*50)
    print(Fore.CYAN + Style.BRIGHT + L["title"])
    print(Fore.CYAN + Style.BRIGHT + "="*50 + "\n")

def kisayol_olustur(hedef_exe, uygulama_adi):
    try:
        masaustu = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        kisayol_yolu = os.path.join(masaustu, f"{uygulama_adi}.lnk")
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(kisayol_yolu)
        shortcut.TargetPath = hedef_exe
        shortcut.WorkingDirectory = os.path.dirname(hedef_exe)
        shortcut.IconLocation = hedef_exe
        shortcut.save()
        print(Fore.GREEN + L["shortcut_done"] + uygulama_adi)
    except:
        pass

def kurulum_yap():
    baslik_yazdir()
    print(Fore.YELLOW + L["select_exe"])
    
    root = Tk(); root.withdraw(); root.attributes('-topmost', True)
    kaynak_dosya = filedialog.askopenfilename(filetypes=[("Executable Files", "*.exe")])
    root.destroy()

    if not kaynak_dosya:
        print(Fore.RED + L["no_file"])
        time.sleep(2); return

    dosya_adi = os.path.basename(kaynak_dosya)
    uygulama_adi = os.path.splitext(dosya_adi)[0]
    hedef_klasor = os.path.join(BASE_PATH, uygulama_adi, "portable")
    hedef_dosya_yolu = os.path.join(hedef_klasor, dosya_adi)

    print(f"\n{Fore.GREEN}{L['selected']} {Style.RESET_ALL}{dosya_adi}")
    print(f"{Fore.GREEN}{L['target']}   {Style.RESET_ALL}{hedef_klasor}\n")
    
    # Almanca (j) ve Rusça (д) karakterlerini de onay listesine ekleyelim
    onay = input(Fore.YELLOW + L["ask_install"]).lower()
    if onay in ['e', 'y', 'j', 'д']:
        try:
            if not os.path.exists(hedef_klasor):
                os.makedirs(hedef_klasor)
                print(Fore.CYAN + L["creating_folders"])

            print(Fore.CYAN + L["copying"])
            shutil.copy2(kaynak_dosya, hedef_dosya_yolu)
            print(Fore.GREEN + Style.BRIGHT + f"\n{L['success']}")
            
            ks_onay = input(Fore.CYAN + L["ask_shortcut"]).lower()
            if ks_onay in ['e', 'y', 'j', 'д']:
                kisayol_olustur(hedef_dosya_yolu, uygulama_adi)
        except PermissionError:
            print(Fore.RED + L["error_perm"])
        except Exception as e:
            print(Fore.RED + f"Error: {e}")
    
    input(Fore.YELLOW + L["press_enter"])

def main():
    global L
    kayitli_dil = ayarları_yukle()
    if not kayitli_dil:
        kayitli_dil = dil_secme_ekrani()
    
    L = LANGUAGES.get(kayitli_dil, LANGUAGES["tr"])

    while True:
        baslik_yazdir()
        print(L["menu_1"])
        print(L["menu_2"])
        print(L["menu_3"])
        print(L["menu_4"])
        
        secim = input(Fore.CYAN + "\n>>> ")
        
        if secim == '1':
            kurulum_yap()
        elif secim == '2':
            yeni_dil = dil_secme_ekrani()
            L = LANGUAGES[yeni_dil]
            print(Fore.GREEN + L["lang_changed"])
            time.sleep(1)
        elif secim == '3':
            baslik_yazdir()
            print(L["about"])
            input(L["press_enter"])
        elif secim == '4':
            print(Fore.GREEN + L["exit"])
            break

if __name__ == "__main__":
    main()
