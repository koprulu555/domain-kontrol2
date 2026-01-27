#!/usr/bin/env python3
"""
BaseURL Çekici Scripti
domain.txt dosyasından domaini alır, channel.html'e istek atar,
baseUrl'i bulur ve guncel_baseurl.txt dosyasına yazar.
"""

import requests
import re
import os
import sys
from urllib.parse import urljoin

# ===== AYARLAR =====
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
TIMEOUT = 10
PROXY_URL = 'https://api.codetabs.com/v1/proxy/?quest='

# ===== FONKSİYONLAR =====
def read_domain_from_file(filepath='domain.txt'):
    """domain.txt dosyasından guncel_domain değerini okur."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('guncel_domain='):
                    domain = line.split('=', 1)[1].strip()
                    if domain:
                        # URL'nin sonundaki '/' temizle
                        return domain.rstrip('/')
        print(f"❌ HATA: {filepath} dosyasında 'guncel_domain=' bulunamadı.")
        return None
    except FileNotFoundError:
        print(f"❌ HATA: {filepath} dosyası bulunamadı.")
        return None
    except Exception as e:
        print(f"❌ HATA: Dosya okunurken hata: {e}")
        return None

def fetch_html(url):
    """
    Bir URL'den HTML içeriğini getir.
    Önce direkt dener, başarısız olursa proxy kullanır.
    """
    headers = {'User-Agent': USER_AGENT}
    
    # 1. Direkt istek
    try:
        print(f"🌐 Direkt istek deneniyor: {url}")
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        print("✅ Direkt istek başarılı.")
        return response.text
    except requests.RequestException as e:
        print(f"⚠️  Direkt istek başarısız: {e}")
    
    # 2. Proxy ile istek
    try:
        proxy_full_url = PROXY_URL + url
        print(f"🔁 Proxy ile deneniyor: {proxy_full_url}")
        response = requests.get(proxy_full_url, headers=headers, timeout=TIMEOUT+5)
        response.raise_for_status()
        print("✅ Proxy isteği başarılı.")
        return response.text
    except requests.RequestException as e:
        print(f"❌ Proxy isteği de başarısız: {e}")
    
    return None

def extract_baseurl(html):
    """
    HTML içeriğinden baseUrl'i çıkarmak için 3 farklı regex dener.
    """
    if not html:
        return None
    
    # REGEX 1: Tam senin gösterdiğin format
    # <script>(function(){const CONFIG={baseUrl:'https://...'
    patterns = [
        # Pattern 1: TAM FORMAT
        r"<script>\(function\(\)\{const CONFIG=\{baseUrl:'(https?://[^']+\.sbs)/'",
        # Pattern 2: Genel CONFIG={baseUrl:'...'
        r"CONFIG\s*=\s*\{[^}]*baseUrl\s*:\s*['\"](https?://[^'\"]+\.sbs)",
        # Pattern 3: Herhangi bir yerde .sbs ile biten URL
        r'(https?://[^\s<>"\']+\.sbs)'
    ]
    
    for i, pattern in enumerate(patterns, 1):
        try:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                baseurl = match.group(1).rstrip('/')
                print(f"✅ Regex {i} ile bulundu: {baseurl}")
                return baseurl
        except Exception as e:
            print(f"⚠️  Regex {i} hatası: {e}")
            continue
    
    print("❌ Hiçbir regex ile baseUrl bulunamadı.")
    return None

def write_baseurl_to_file(baseurl, filepath='guncel_baseurl.txt'):
    """BaseURL'i dosyaya yazar."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f'guncel_baseurl={baseurl}')
        print(f"💾 {filepath} dosyasına yazıldı: {baseurl}")
        return True
    except Exception as e:
        print(f"❌ Dosya yazma hatası: {e}")
        return False

# ===== ANA PROGRAM =====
def main():
    print("="*60)
    print("🚀 BaseURL Çekici Başlatılıyor")
    print("="*60)
    
    # 1. Domain'i dosyadan oku
    print("\n1️⃣  Domain okunuyor...")
    domain = read_domain_from_file()
    if not domain:
        sys.exit(1)
    
    print(f"   ✅ Domain: {domain}")
    
    # 2. channel.html URL'sini oluştur
    channel_url = urljoin(domain + '/', 'channel.html')
    print(f"\n2️⃣  Channel.html URL'si: {channel_url}")
    
    # 3. HTML'i getir
    print("\n3️⃣  HTML içeriği alınıyor...")
    html = fetch_html(channel_url)
    if not html:
        print("❌ HTML alınamadı. İşlem sonlandırılıyor.")
        sys.exit(1)
    
    print(f"   ✅ HTML alındı ({len(html)} karakter)")
    
    # 4. BaseURL'i çıkar
    print("\n4️⃣  BaseURL aranıyor...")
    baseurl = extract_baseurl(html)
    if not baseurl:
        sys.exit(1)
    
    # 5. Dosyaya yaz
    print("\n5️⃣  Dosyaya yazılıyor...")
    if write_baseurl_to_file(baseurl):
        print("\n" + "="*60)
        print("✨ İŞLEM BAŞARIYLA TAMAMLANDI")
        print("="*60)
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
