import socketserver
import http.server
import urllib.request

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        req = urllib.request.Request(
            'http://127.0.0.1:1235' + self.path,
            data=body,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        try:
            response = urllib.request.urlopen(req, timeout=120)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(response.read())
        except Exception as e:
            self.send_response(502)
            self.end_headers()
            self.wfile.write(str(e).encode())
    
    def do_GET(self):
        req = urllib.request.Request('http://127.0.0.1:1235' + self.path)
        try:
            response = urllib.request.urlopen(req, timeout=10)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(response.read())
        except Exception as e:
            self.send_response(502)
            self.end_headers()
            self.wfile.write(str(e).encode())
    
    def log_message(self, format, *args):
        pass  # Silenzioso

if __name__ == '__main__':
    with socketserver.TCPServer(('0.0.0.0', 1234), ProxyHandler) as httpd:
        print('🔄 PROXY ATTIVO: 0.0.0.0:1234 -> 127.0.0.1:1235')
        print('📡 Themis puo connettersi su http://192.168.8.129:1234')
        httpd.serve_forever()
