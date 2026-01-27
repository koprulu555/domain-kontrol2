#!/usr/bin/env python3
"""
BaseURL Çekici - Kök dizinde çalışır
domain.txt'den domaini alır, channel.html'den baseUrl'i çeker
"""

import requests
import re
import sys

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
PROXY = 'https://api.codetabs.com/v1/proxy/?quest='

def main():
    print("="*50)
    print("BASEURL ÇEKİCİ BAŞLADI")
    print("="*50)
    
    # 1. domain.txt dosyasını oku
    try:
        with open('domain.txt', 'r') as f:
            content = f.read()
        match = re.search(r'guncel_domain=(https?://[^\s]+)', content)
        if not match:
            print("❌ domain.txt'de guncel_domain= bulunamadı")
            sys.exit(1)
        domain = match.group(1).strip().rstrip('/')
        print(f"✅ Domain: {domain}")
    except FileNotFoundError:
        print("❌ domain.txt dosyası bulunamadı")
        sys.exit(1)
    
    # 2. channel.html URL'si
    url = f"{domain}/channel.html"
    print(f"🔗 Hedef: {url}")
    
    # 3. HTML'i getir (önce normal, sonra proxy)
    headers = {'User-Agent': USER_AGENT}
    html = None
    
    try:
        print("🔄 Normal istek deneniyor...")
        r = requests.get(url, headers=headers, timeout=8)
        r.raise_for_status()
        html = r.text
        print("✅ Normal başarılı")
    except:
        print("⚠️  Normal başarısız, proxy deneniyor...")
        try:
            proxy_url = f"{PROXY}{url}"
            r = requests.get(proxy_url, headers=headers, timeout=12)
            r.raise_for_status()
            html = r.text
            print("✅ Proxy başarılı")
        except Exception as e:
            print(f"❌ Proxy de başarısız: {e}")
            sys.exit(1)
    
    if not html:
        print("❌ HTML alınamadı")
        sys.exit(1)
    
    print(f"📄 HTML alındı ({len(html)} karakter)")
    
    # 4. BASEURL'i 3 FARKLI REGEX İLE ARA
    print("\n🔍 BaseURL aranıyor...")
    baseurl = None
    
    # Regex 1: Tam senin gösterdiğin
    pattern1 = r"<script>\(function\(\)\{const CONFIG=\{baseUrl:'(https?://[^']+\.sbs)/'"
    match1 = re.search(pattern1, html, re.IGNORECASE)
    if match1:
        baseurl = match1.group(1).rstrip('/')
        print(f"✅ Regex 1 ile bulundu: {baseurl}")
    
    # Regex 2: Genel CONFIG
    if not baseurl:
        pattern2 = r"CONFIG\s*=\s*\{[^}]*baseUrl\s*:\s*['\"](https?://[^'\"]+\.sbs)"
        match2 = re.search(pattern2, html, re.IGNORECASE | re.DOTALL)
        if match2:
            baseurl = match2.group(1).rstrip('/')
            print(f"✅ Regex 2 ile bulundu: {baseurl}")
    
    # Regex 3: Herhangi .sbs URL
    if not baseurl:
        pattern3 = r'(https?://[^\s<>"\']+\.sbs)'
        match3 = re.search(pattern3, html, re.IGNORECASE)
        if match3:
            baseurl = match3.group(1).rstrip('/')
            print(f"✅ Regex 3 ile bulundu: {baseurl}")
    
    if not baseurl:
        print("❌ BaseURL bulunamadı")
        sys.exit(1)
    
    # 5. DOSYAYA YAZ
    with open('guncel_baseurl.txt', 'w') as f:
        f.write(f'guncel_baseurl={baseurl}')
    print(f"\n💾 guncel_baseurl.txt'ye yazıldı")
    print(f"📋 İçerik: guncel_baseurl={baseurl}")
    
    print("\n" + "="*50)
    print("✅ İŞLEM TAMAMLANDI")
    print("="*50)

if __name__ == '__main__':
    main()
