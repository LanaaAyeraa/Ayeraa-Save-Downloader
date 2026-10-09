"""Server Web mandiri Ayeraa Save Downloader untuk Android & Jaringan Lokal."""
from __future__ import annotations

import sys
import webbrowser

from allsave import web
from allsave.branding import make_logo

PORT = 8080

if __name__ == "__main__":
    ip = web.get_local_ip()
    url = f"http://{ip}:{PORT}"
    print("=" * 60)
    print("      Ayeraa Save Downloader - Mobile & Web Server")
    print("=" * 60)
    print(f"\n[+] Server berjalan di jaringan lokal:")
    print(f"    --> Buka di HP Android:  {url}")
    print(f"    --> Buka di Laptop:      http://localhost:{PORT}")
    print("\nPetunjuk:")
    print("1. Pastikan HP Android dan Laptop terhubung ke Wi-Fi yang sama.")
    print(f"2. Buka browser di HP (Chrome/Samsung/Firefox), ketik: {url}")
    print("3. Tempel link video apa saja, lalu klik 'Download ke HP'.")
    print("\nTekan Ctrl+C di jendela ini untuk mematikan server.\n")

    server = web.start_server(PORT)
    try:
        # Buka browser lokal secara otomatis jika dijalankan langsung
        if len(sys.argv) > 1 and sys.argv[1] == "--open":
            webbrowser.open(f"http://localhost:{PORT}")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer dimatikan.")
        server.server_close()
