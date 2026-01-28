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
    
    # Regex 1: Tam senin gösterdiğin - <script>(function(){const CONFIG={baseUrl:'https://...
    pattern1 = r"<script>\(function\(\)\{const CONFIG=\{baseUrl:'(https?://[^']+\.sbs)/'"
    match1 = re.search(pattern1, html, re.IGNORECASE)
    if match1:
        baseurl = match1.group(1).rstrip('/')
        print(f"✅ Regex 1 ile bulundu: {baseurl}")
    
    # Regex 2: "const" kelimesinden SONRA gelen ilk https://...sbs URL'si
    if not baseurl:
        # const'tan sonraki ilk https://...sbs'yi ara
        const_index = html.lower().find('const')
        if const_index != -1:
            # const'tan sonraki kısmı al
            after_const = html[const_index:]
            pattern2 = r'https?://[^\s<>"\']+\.sbs'
            match2 = re.search(pattern2, after_const, re.IGNORECASE)
            if match2:
                baseurl = match2.group(0).rstrip('/')
                print(f"✅ Regex 2 ile bulundu (const'tan sonra): {baseurl}")
    
    # Regex 3: Tüm HTML sayfasında başı https ile başlayan, .sbs ile biten İLK URL
    if not baseurl:
        pattern3 = r'https?://[^\s<>"\']+\.sbs'
        # Tüm eşleşmeleri bul
        matches3 = re.findall(pattern3, html, re.IGNORECASE)
        if matches3:
            # İlk eşleşmeyi al
            baseurl = matches3[0].rstrip('/')
            print(f"✅ Regex 3 ile bulundu (tüm HTML'de ilk .sbs URL): {baseurl}")
    
    if not baseurl:
        print("❌ BaseURL bulunamadı")
        print("   HTML'de .sbs içeren URL'ler:")
        all_sbs = re.findall(r'https?://[^\s<>"\']*\.sbs[^\s<>"\']*', html, re.IGNORECASE)
        for url in all_sbs[:5]:  # İlk 5'ini göster
            print(f"   - {url}")
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
