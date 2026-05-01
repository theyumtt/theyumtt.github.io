import requests
import os
import tarfile
import shutil
import subprocess
import glob
import re

wdir = os.getcwd()
target = os.path.join(wdir, "downloaded_packages")
url = "https://github.com/obsproject/obs-studio/releases/download/32.1.2/OBS-Studio-32.1.2-Ubuntu-24.04-x86_64.deb"

if not os.path.exists(target):
    os.makedirs(target)

file_path        = os.path.join(target, "obs.deb")
file_path_data   = os.path.join(target, "data.tar.gz")
file_path_ctrl   = os.path.join(target, "control.tar.gz")

# ─── Ubuntu .deb bağımlılık adı → Arch paket adı eşlemesi ──────────────────
DEB_TO_ARCH = {
    "libasound2t64":        "alsa-lib",
    "libatk-bridge2.0-0t64":"at-spi2-core",
    "libatk1.0-0t64":       "at-spi2-core",
    "libatspi2.0-0t64":     "at-spi2-core",
    "libavcodec60":         "ffmpeg",
    "libavdevice60":        "ffmpeg",
    "libavformat60":        "ffmpeg",
    "libavutil58":          "ffmpeg",
    "libswresample4":       "ffmpeg",
    "libswscale7":          "ffmpeg",
    "libc6":                "glibc",
    "libcups2t64":          "libcups",
    "libcurl4t64":          "curl",
    "libdbus-1-3":          "dbus",
    "libdrm2":              "libdrm",
    "libegl1":              "libglvnd",
    "libexpat1":            "expat",
    "libfontconfig1":       "fontconfig",
    "libfreetype6":         "freetype2",
    "libgbm1":              "mesa",
    "libgcc-s1":            "gcc-libs",
    "libglib2.0-0t64":      "glib2",
    "libglx0":              "libglvnd",
    "libjansson4":          "jansson",
    "libluajit-5.1-2":      "luajit",
    "libluajit2-5.1-2":     "luajit",
    "libmbedcrypto7t64":    "mbedtls",
    "libmbedtls14t64":      "mbedtls",
    "libmbedx509-1t64":     "mbedtls",
    "libnspr4":             "nspr",
    "libnss3":              "nss",
    "libopengl0":           "libglvnd",
    "libpci3":              "pciutils",
    "libpipewire-0.3-0t64": "pipewire",
    "libpulse0":            "libpulse",
    "libpython3.12t64":     "python",
    "libqrcodegencpp1":     None,  # AUR'da: qr-code-generator-cpp (yay/paru ile kur)
    "libqt6core6t64":       "qt6-base",
    "libqt6dbus6t64":       "qt6-base",
    "libqt6gui6t64":        "qt6-base",
    "libqt6network6t64":    "qt6-base",
    "libqt6svg6":           "qt6-svg",
    "libqt6widgets6t64":    "qt6-base",
    "libqt6xml6t64":        "qt6-base",
    "librist4":             "librist",
    "libspeexdsp1":         "speexdsp",
    "libsrt1.5-openssl":    "srt",
    "libstdc++6":           "gcc-libs",
    "libudev1":             "systemd-libs",
    "libuuid1":             "util-linux-libs",
    "libv4l-0t64":          "v4l-utils",
    "libva-drm2":           "libva",
    "libva2":               "libva",
    "libvpl2":              "onevpl",
    "libwayland-client0":   "wayland",
    "libwayland-egl1":      "wayland",
    "libx11-6":             "libx11",
    "libx11-xcb1":          "libx11",
    "libx264-164":          "x264",
    "libxcb-composite0":    "libxcb",
    "libxcb-randr0":        "libxcb",
    "libxcb-shm0":          "libxcb",
    "libxcb-xfixes0":       "libxcb",
    "libxcb-xinerama0":     "libxcb",
    "libxcb1":              "libxcb",
    "libxcomposite1":       "libxcomposite",
    "libxdamage1":          "libxdamage",
    "libxext6":             "libxext",
    "libxfixes3":           "libxfixes",
    "libxkbcommon0":        "libxkbcommon",
    "libxrandr2":           "libxrandr",
    "zlib1g":               "zlib",
}

def parse_depends(control_file):
    """control dosyasından Depends satırını okur, paket adlarını döner."""
    depends = []
    with open(control_file, "r") as f:
        for line in f:
            if line.startswith("Depends:"):
                raw = line[len("Depends:"):].strip()
                entries = raw.split(",")
                for entry in entries:
                    # | ile ayrılmış alternatiflerin ilkini al
                    first = entry.split("|")[0].strip()
                    # Parantez içini sil: libfoo (>= 1.2) → libfoo
                    name = re.sub(r"\s*\(.*?\)", "", first).strip()
                    if name:
                        depends.append(name)
    return depends

def install_dependencies(depends):
    """Debian bağımlılık listesini Arch paketlerine çevirir ve kurar."""
    arch_pkgs = set()
    bilinmeyen = []

    for deb_pkg in depends:
        arch = DEB_TO_ARCH.get(deb_pkg)
        if arch:
            arch_pkgs.add(arch)
        else:
            bilinmeyen.append(deb_pkg)

    if bilinmeyen:
        print(f"[!] Eşlemesi bulunamayan paketler: {', '.join(bilinmeyen)}")

    if arch_pkgs:
        print(f"[*] Kurulacak Arch paketleri: {', '.join(sorted(arch_pkgs))}")
        basarisiz = []
        for pkg in sorted(arch_pkgs):
            result = subprocess.run(["pacman", "-S", "--needed", "--noconfirm", pkg])
            if result.returncode != 0:
                basarisiz.append(pkg)
                print(f"[!] Kurulamadı (atlanıyor): {pkg}")
        if basarisiz:
            print(f"[!] Kurulamayan paketler: {', '.join(basarisiz)}")
            print("[!] Bunları AUR'dan dene: yay -S " + " ".join(basarisiz))
        else:
            print("[+] Tüm bağımlılıklar kuruldu.")

# ─── 1. PAKETİ İNDİR ────────────────────────────────────────────────────────
print("[*] Paket indiriliyor...")
req = requests.get(url, stream=True)
req.raise_for_status()
with open(file_path, "wb") as f:
    for chunk in req.iter_content(chunk_size=8192):
        f.write(chunk)
print("[*] Paket indirildi.")

# ─── 2. .DEB DOSYASINI AÇ ───────────────────────────────────────────────────
os.chdir(target)
print("[*] .deb açılıyor...")
subprocess.run(["ar", "x", "obs.deb"], check=True)
print("[*] .deb açıldı.")

# ─── 3. CONTROL DOSYASINI OKU, BAĞIMLILIKLARI KUR ──────────────────────────
print("[*] Bağımlılıklar okunuyor...")
ctrl_extract = os.path.join(target, "ctrl_files")
os.makedirs(ctrl_extract, exist_ok=True)

with tarfile.open(file_path_ctrl, "r:gz") as ctrl:
    ctrl.extractall(path=ctrl_extract)

control_file = os.path.join(ctrl_extract, "control")
if not os.path.exists(control_file):
    print("[-] control dosyası bulunamadı!")
    exit(1)

depends = parse_depends(control_file)
print(f"[*] Toplam {len(depends)} bağımlılık bulundu.")
install_dependencies(depends)

# ─── 4. data.tar.gz DOSYASINI AÇ ────────────────────────────────────────────
print("[*] Paket içeriği çıkartılıyor...")
if not os.path.exists(file_path_data):
    print("[-] data.tar.gz bulunamadı!")
    subprocess.run(["ls", "-la", target])
    exit(1)

with tarfile.open(file_path_data, "r:gz") as software:
    software.extractall(path="obs_files")
print("[*] Paket içeriği çıkartıldı.")

# ─── 5. /USR ALTINA KOPYALA ─────────────────────────────────────────────────
print("[*] Sisteme kopyalanıyor...")
kaynak_usr = os.path.join("obs_files", "usr")

if not os.path.exists(kaynak_usr):
    print("[-] obs_files/usr bulunamadı!")
    exit(1)

try:
    shutil.copytree(kaynak_usr, "/usr", dirs_exist_ok=True)
    print("[+] Dosyalar kopyalandı!")
except PermissionError:
    print("[-] Yetki hatası! sudo ile çalıştır.")
    exit(1)

# ─── 6. KÜTÜPHANELERİ BAĞLA (DİNAMİK SÜRÜM) ────────────────────────────────
print("[*] Kütüphane linkleri kuruluyor...")

lib_list = [
    "libavcodec.so",
    "libavdevice.so",
    "libavformat.so",
    "libavutil.so",
    "libswresample.so",
    "libswscale.so",
]

for base in lib_list:
    pattern = f"/usr/lib/{base}.*"
    found = sorted(glob.glob(pattern))

    # libavcodec.so.61 → 2 nokta
    versioned = [f for f in found if f.count(".") == 2]

    if not versioned:
        print(f"[!] {base} bulunamadı, ffmpeg kurulumu eksik olabilir.")
        continue

    newest    = versioned[-1]
    major     = newest.split(".so.")[-1]
    link_path = f"/usr/lib/{base}.{major}"

    if not os.path.exists(link_path):
        try:
            subprocess.run(["ln", "-s", newest, link_path], check=True)
            print(f"[+] Link: {link_path} -> {newest}")
        except Exception as e:
            print(f"[-] Link kurulamadı ({base}): {e}")
    else:
        print(f"[~] Zaten mevcut: {link_path}")

# ─── 7. ldconfig GÜNCELLE ────────────────────────────────────────────────────
print("[*] Kütüphane önbelleği güncelleniyor...")
try:
    subprocess.run(["ldconfig"], check=True)
    print("[+] ldconfig tamam.")
except Exception as e:
    print(f"[-] ldconfig hatası: {e}")

# ─── 8. TEMİZLİK ─────────────────────────────────────────────────────────────
os.chdir(wdir)
print("[*] Geçici dosyalar temizleniyor...")
try:
    shutil.rmtree(target)
    print("[+] Temizlik tamam.")
except Exception as e:
    print(f"[-] Temizlik hatası: {e}")

print("\n[!] KURULUM TAMAMLANDI.")
print("[?] Terminale 'obs' yaz ve dene!")
