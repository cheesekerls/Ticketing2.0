from escpos.printer import Serial
from PIL import Image
import qrcode
import time
import traceback


def print_ticket_to_pos(request, service_id=None):
    print("🟢 print_ticket_to_pos CALLED")  # confirm view is hit
    print("Method:", request.method)
    print("POST data:", request.POST)
    message = None


def print_ticket_to_pos(ticket_text, qr_data=None):
    """
    Prints ticket text and an optional QR code, centered.
    qr_data: The text or URL to encode in the QR (e.g., ticket number)
    """
    try:
        print("🖨️ Connecting to printer...")
        printer = Serial(devfile="COM3", baudrate=9600, timeout=1)
        time.sleep(1)
        printer.hw("INIT")
        printer.set(align='center', font='a', width=3, height=3)

        print("✅ Printer connected successfully.")

        # --- Print text centered ---
        for line in ticket_text.strip().split("\n"):
            printer.text(line.strip() + "\n")

        # --- Print QR code ---
        if qr_data:
            print(f"Generating QR for: {qr_data}")

            qr = qrcode.QRCode(box_size=11, border=5)  # smaller QR to reduce space
            qr.add_data(qr_data)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_bw = qr_img.convert('1')

            printer.set(align='center')
            printer.image(qr_bw)

        # --- Minimal footer ---
        printer.set(align='center', width=1, height=1)
        printer.text("\nThank you!\n")  # only one line break

        try:
            printer.cut()
        except Exception:
            printer.text("\n")

        printer.close()
        print("✅ Printing complete.")

    except Exception as e:
        print("❌ Printer error:")
        print(traceback.format_exc())