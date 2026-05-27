import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


HOST = os.getenv("PRINT_SERVICE_HOST", "127.0.0.1")
PORT = int(os.getenv("PRINT_SERVICE_PORT", "5050"))
TOKEN = os.getenv("PRINT_SERVICE_TOKEN", "")
PRINTER_NAME = os.getenv("PRINT_SERVICE_PRINTER", "")


def send_to_windows_printer(text):
    try:
        import win32print
    except ImportError as exc:
        raise RuntimeError("Install pywin32 first: python -m pip install pywin32") from exc

    printer_name = PRINTER_NAME or win32print.GetDefaultPrinter()
    handle = win32print.OpenPrinter(printer_name)
    try:
        job = win32print.StartDocPrinter(handle, 1, ("Rawda invoice", None, "RAW"))
        try:
            win32print.StartPagePrinter(handle)
            win32print.WritePrinter(handle, text.encode("utf-8", errors="replace"))
            win32print.EndPagePrinter(handle)
        finally:
            win32print.EndDocPrinter(handle)
    finally:
        win32print.ClosePrinter(handle)


class PrintRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/print-order":
            self.send_json(404, {"ok": False, "error": "Not found"})
            return

        if not TOKEN or self.headers.get("X-Print-Token") != TOKEN:
            self.send_json(403, {"ok": False, "error": "Invalid print token"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            invoice_text = payload.get("invoice_text") or json.dumps(payload, indent=2, ensure_ascii=False)
            send_to_windows_printer(invoice_text + "\n\n\n")
        except Exception as exc:
            self.send_json(500, {"ok": False, "error": str(exc)})
            return

        self.send_json(200, {"ok": True})

    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format % args}")

    def send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    if HOST not in {"127.0.0.1", "localhost"}:
        print("Warning: bind only to a trusted local network.")
    if not TOKEN:
        raise SystemExit("Set PRINT_SERVICE_TOKEN before starting the print service.")

    server = ThreadingHTTPServer((HOST, PORT), PrintRequestHandler)
    print(f"Listening on http://{HOST}:{PORT}/print-order")
    print(f"Printer: {PRINTER_NAME or 'Windows default printer'}")
    server.serve_forever()


if __name__ == "__main__":
    main()
