import win32print
import win32ui
def is_printer_connected():
    try:
        printer_name = "HPRT HT300"
        hprinter = win32print.OpenPrinter(printer_name)
        printer_status = win32print.GetPrinter(hprinter, 2)  # Get detailed printer info
        win32print.ClosePrinter(hprinter)

        status = printer_status["Status"]
        attributes = printer_status["Attributes"]

        # Check if printer is offline, error state, or paused
        if status & win32print.PRINTER_STATUS_OFFLINE:
            return False
        if status & win32print.PRINTER_STATUS_ERROR:
            return False
        if status & win32print.PRINTER_STATUS_PAUSED:
            return False
        if attributes & win32print.PRINTER_ATTRIBUTE_WORK_OFFLINE:
            return False


        return True
    except:
        return False
def printvalue(barcode_data, order_number,howmany):
    PRINTER_NAME = "HPRT HT300"
    OUTPUT_PRN_FILE = "barcode_label.prn"
    ORDER_FILE_PATH = "assets/order.txt"

    def generate_prn(barcode_data, order_number, output_file=OUTPUT_PRN_FILE):
        order_key = f"[order_{order_number}]"
        order_lines = []
        capture = False
        
        # Read order file
        with open(ORDER_FILE_PATH, "r", encoding="utf-8") as file:
            for line in file:
                if line.strip() == order_key:
                    capture = True
                    continue
                if capture:
                    if line.strip().startswith("[order_"):  # Stop at next order
                        break
                    order_lines.append(line.strip())

        if not order_lines:
            print(f"Error: Order {order_number} not found.")
            return None

        # Replace placeholders
        prn_content = "\n".join(order_lines)
        prn_content = prn_content.replace("ffff", barcode_data)
        prn_content = prn_content.replace("counttt", str(howmany))
        # Save to PRN file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(prn_content)

        print(f"PRN file generated: {output_file}")
        return output_file

    def print_prn_file(prn_file):
        try:
            hprinter = win32print.OpenPrinter(PRINTER_NAME)
            hprinter_job = win32print.StartDocPrinter(hprinter, 1, ("Barcode Print", None, "RAW"))
            win32print.StartPagePrinter(hprinter)

            with open(prn_file, "rb") as f:
                data = f.read()
                win32print.WritePrinter(hprinter, data)

            win32print.EndPagePrinter(hprinter)
            win32print.EndDocPrinter(hprinter)
            win32print.ClosePrinter(hprinter)
            print("Print job sent to printer.")
        except Exception as e:
            print(f"Error while printing: {e}")

    # Generate PRN and print
    prn_file = generate_prn(barcode_data, order_number)
    if prn_file:
        print_prn_file(prn_file)

# Example usage
#printvalue("1234567890254810", 3)
