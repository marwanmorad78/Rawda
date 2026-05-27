# Local invoice printing

Django cannot silently print from the browser, so accepted orders are sent to a small local service on the laptop connected to the receipt printer.

## Django settings

Set these environment variables for the Django process:

```env
INVOICE_PRINT_ENABLED=True
INVOICE_PRINT_SERVICE_URL=http://127.0.0.1:5050/print-order
INVOICE_PRINT_SERVICE_TOKEN=use-a-long-random-shared-token
INVOICE_PRINT_TIMEOUT_SECONDS=3
```

Keep `INVOICE_PRINT_ENABLED=False` on hosted/public deployments unless they can reach your trusted local print service.

## Windows print service

Install `pywin32` in the Python environment that will run the local service:

```powershell
python -m pip install pywin32
```

Start the service on the printer laptop:

```powershell
$env:PRINT_SERVICE_TOKEN="use-a-long-random-shared-token"
$env:PRINT_SERVICE_HOST="127.0.0.1"
$env:PRINT_SERVICE_PORT="5050"
$env:PRINT_SERVICE_PRINTER=""
python scripts\local_print_service.py
```

Leave `PRINT_SERVICE_PRINTER` empty to use the Windows default printer, or set it to the exact printer name shown in Windows Printers & scanners.

## Security notes

- Bind to `127.0.0.1` unless the Django server is on another trusted machine.
- Use the same long secret token in Django and the print service.
- Do not expose `/print-order` to the public internet.
- Printing failures are stored on the order as `print_status=failed` and do not block checkout.

## Automatic acceptance cleanup

The app auto-accepts busy-center orders when customer or dashboard order pages load. For production, run this command every minute using your scheduler:

```powershell
uv run python src\manage.py auto_accept_busy_orders
```
