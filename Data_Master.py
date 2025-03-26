import tkinter as tk
from tkinter import ttk
import threading
import serial
import serial.tools.list_ports
from PIL import Image, ImageTk  # Import Pillow for image handling
import printbarcode
from tkinter import messagebox
from datetime import datetime
global numberofprder,printnumcount,printerhere,app
numberofprder="none"
printnumcount=1
printerhere="no"
def get_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def detect_scanner_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "USB Serial Device" in port.description:
            return port.device
    return ""

def save_scanned_data(data):
    now = datetime.now()
    formatted_datetime = now.strftime("%d-%m-%Y %H:%M")  # Example: 28-02-2025 14:30
    with open("scanned_qr_codes.txt", "a") as file:
        file.write(formatted_datetime+"  |"+data+"|" + "\n")

class QRScannerApp:
    def __init__(self, root):
        global bgup,fgup,trecl,bgupb,bgupd,is_on
        fgup="black"
        is_on = False
        bgup="white"
        bgupb="gray"
        trecl="#f1ecec"
        bgupd="gray"
        self.last_scanned2=""
        self.root = root
        self.root.title("QR Code Scanner")
        self.root.geometry("800x400")
        self.root.configure(bg=bgup)
        icon =  tk.PhotoImage(file="assets/logo.png")
        self.root.iconphoto(True, icon)
        
        self.serial_port = serial.Serial()
        self.last_scanned = ""
        self.print_counts = {}
        self.scan_history = []
        
        self.create_widgets()
        self.auto_detect_port()
        self.root.bind("<KeyRelease-Return>", self.on_enter_pressed)


    def destroyhall(self):
        self.running = False  # Flag to stop the thread loop
        if self.serial_port.is_open:
            self.serial_port.close()  # Close the serial port
        if hasattr(self, 'serial_thread') and self.serial_thread.is_alive():
            self.serial_thread.join(timeout=1)  # Ensure it stops safely
        self.root.quit()
        self.root.destroy()

    def open_new_window(self):
        global printnumcount
        def load_button_image(image_path, size,self):  # Resize as needed
            self.image = Image.open(image_path)
            self.image = self.image.resize(size, Image.LANCZOS)  # Resize image
            return ImageTk.PhotoImage(self.image)
        self.new_window = tk.Toplevel(self.root)
        self.new_window.title("SIZE CHANGER")
        self.new_window.geometry("550x400")
        self.new_window.configure(bg=bgup)
        self.canvas = tk.Canvas(self.new_window, width=560, height=50, bg="#0aa5c4", highlightthickness=0)#1c1c1c
        self.canvas.place(x=0, y=0)  # Adjust y position to align with text
        self.label = tk.Label(self.new_window, text="Settings", fg="#f4f4f4", bg="#0aa5c4", font=("Arial", 16,"bold"))
        self.label.place(x=210,y=10)
        ff=open("assets/sizecheck.txt","r")
        number=ff.read()
        ff.close()
        self.label2 = tk.Label(self.new_window, text=f"Choosen Style_{number}", fg="black", bg=bgup, font=("Arial", 16,"bold"))
        self.label2.place(x=200,y=60)

        self.label4 = tk.Label(self.new_window, text="Style_1", fg="black", bg=bgup, font=("Arial", 16,"bold"))
        self.label4.place(x=50,y=180)

        self.label5 = tk.Label(self.new_window, text="Style_2", fg="black", bg=bgup, font=("Arial", 16,"bold"))
        self.label5.place(x=220,y=180)

        self.label6 = tk.Label(self.new_window, text="Style_3", fg="black", bg=bgup, font=("Arial", 16,"bold"))
        self.label6.place(x=390,y=180)

        self.label42 = tk.Label(self.new_window, text="Powered by MoonSide", fg="black", bg=bgup, font=("Arial", 10,"bold"))
        self.label42.place(x=20,y=370)
        def choose(number):
            global numberofprder
            self.label2.config(text=f"Choosen Style_{number}")
            numberofprder=number
            self.size_status_label.config(text=f"Style : style_{numberofprder}")
            ff=open("assets/sizecheck.txt","w")
            ff.write(str(numberofprder))
            ff.close()
        def destroy():
                self.new_window.destroy()
        def changelang():
                global app
                file=open("assets/language.txt","w")
                file.write("ru")
                file.close()
                self.running = False  # Flag to stop the thread loop
                if self.serial_port.is_open:
                    self.serial_port.close()  # Close the serial port
                if hasattr(self, 'serial_thread') and self.serial_thread.is_alive():
                    self.serial_thread.join(timeout=1)  # Ensure it stops safely
                self.new_window.destroy()
                self.root.destroy() 
                new_root = tk.Tk()   # Create a new Tkinter root window
                app = QRScannerAppRU(new_root)  # Start the Russian version of the app
                new_root.mainloop()  # Run the main loop
               
        self.gallery_image1 = load_button_image("assets/size2.png", (140, 70),self)  # Adjust path & size
        self.close_button1 = ttk.Button(self.new_window,image=self.gallery_image1, padding=0,command=lambda:choose(1))
        self.close_button1.place(x=30,y=100,width=150,height=80)
        self.gallery_image2 = load_button_image("assets/size1.png", (140, 70),self)  
        self.close_button2 = ttk.Button(self.new_window, image=self.gallery_image2, padding=0,   command=lambda:choose(2))
        self.close_button2.place(x=200,y=100,width=150,height=80)
        self.gallery_image3 = load_button_image("assets/size3.png", (140, 70),self)  
        self.close_button3 = ttk.Button(self.new_window, image=self.gallery_image3,  padding=0,  command=lambda:choose(3))
        self.close_button3.place(x=370,y=100,width=150,height=80)

        def increase():
            global printnumcount
            printnumcount += 1
            fin=open("assets/printcount.txt","w")
            fin.write(str(printnumcount))
            fin.close()
            self.label.config(text=str(printnumcount))
            self.countprint_label.config(text=f"Copy : {printnumcount}")

        def decrease():
            global printnumcount
            if printnumcount!=1:
                printnumcount -= 1
                fin=open("assets/printcount.txt","w")
                fin.write(str(printnumcount))
                fin.close()
                self.label.config(text=str(printnumcount))
                self.countprint_label.config(text=f"Copy : {printnumcount}")
        fin=open("assets/printcount.txt","r")
        printnumcount=int(fin.read())
        #print(printnumcount)
        fin.close()
        
        # Decrease Button
        self.minus_button = tk.Button(self.new_window, text="-", font=("Arial", 16), width=5, command=decrease)
        self.minus_button.place(x=460,y=230,width=50,height=50)

        # Label to display number
        self.labelNMAE = tk.Label(self.new_window, text="Printed copies count:", font=("Arial", 18,"bold"),bg=bgup)
        self.labelNMAE.place(x=20,y=235)

        self.label = tk.Label(self.new_window, text=str(printnumcount), font=("Arial", 16))
        self.label.place(x=400,y=230,width=50,height=50)

        # Increase Button
        self.plus_button = tk.Button(self.new_window, text="+", font=("Arial", 16), width=5, command=increase)
        self.plus_button.place(x=340,y=230,width=50,height=50)
        
        self.close_button = ttk.Button(self.new_window, text="Close", command=destroy)
        self.close_button.place(x=450,y=360)
        self.labelNMAE1 = tk.Label(self.new_window, text="Change language to --> ", font=("Arial", 18,"bold"),bg=bgup)
        self.labelNMAE1.place(x=20,y=300)
        self.langcha = tk.Button(self.new_window, text="Russian", font=("Arial", 16), command=changelang)
        self.langcha.place(x=350,y=300,width=150,height=40)
    def toggle(self):
        global is_on
        is_on = not is_on
        self.is_scan.config(text="ON" if is_on else "OFF", bg="green" if is_on else "red")
    def get_entry_value(self):
            data = self.entry_value.get()
            
            if (data and data != self.last_scanned2):
                if data in self.scan_history:
                    self.last_scanned2 = data
                    self.last_scanned=self.last_scanned2
                    self.last_scanned_label.config(text=data)
                    save_scanned_data(data)
                     # Initialize print count for new scan
                    self.scan_history.append(data)
                    self.update_history_table()
                else:
                    self.last_scanned2 = data
                    self.last_scanned=self.last_scanned2
                    self.last_scanned_label.config(text=data)
                    save_scanned_data(data)  
                    self.print_counts[data] = 0 # Initialize print count for new scan
                    self.scan_history.append(data)
                    self.update_history_table()
    def create_widgets(self):
        class PlaceholderEntry(tk.Entry):
            def __init__(self, master=None, placeholder="Enter text...", color="gray", *args, **kwargs):
                super().__init__(master, *args, **kwargs)

                self.placeholder = placeholder
                self.placeholder_color = color
                self.default_fg_color = self["fg"]

                self.put_placeholder()

                self.bind("<FocusIn>", self.on_focus_in)
                self.bind("<FocusOut>", self.on_focus_out)

            def put_placeholder(self):
                """Put the placeholder text in the entry."""
                self.insert(0, self.placeholder)
                self["fg"] = self.placeholder_color

            def on_focus_in(self, event):
                """Remove placeholder text when clicked."""
                if self.get() == self.placeholder:
                    self.delete(0, tk.END)
                    self["fg"] = self.default_fg_color

            def on_focus_out(self, event):
                """Restore placeholder text if the entry is empty."""
                if not self.get():
                    self.put_placeholder()
        def load_button_image(image_path, size=(50, 50)):  # Resize as needed
            image = Image.open(image_path)
            image = image.resize(size, Image.LANCZOS)  # Resize image
            return ImageTk.PhotoImage(image)
        
        self.entry_value = PlaceholderEntry(self.root, font=("Arial", 12,"bold"),fg="black",bg="#d8dad8")
        self.entry_value.place(x=70, y=170,width=200,height=40)    
        self.name = tk.Label(self.root, text="Data Master", fg=fgup, bg=bgup, font=("Arial", 18, "bold"))
        self.name.place(x=70, y=0)

        self.data_label = tk.Label(self.root, text="Last Scanned:", fg=fgup, bg=bgup, font=("Arial", 13))
        self.data_label.place(x=10, y=40)

        # Add red underline using Canvas
        self.canvas = tk.Canvas(self.root, width=300, height=3, bg=fgup, highlightthickness=0)#1c1c1c
        self.canvas.place(x=0, y=35)  # Adjust y position to align with text

        self.canvasd = tk.Canvas(self.root, width=850, height=70, bg=bgupd, highlightthickness=1)#1c1c1c
        self.canvasd.place(x=-8, y=339)
        self.canvasd2 = tk.Canvas(self.root, width=1, height=70, bg="black", highlightthickness=0)#1c1c1c
        self.canvasd2.place(x=300, y=339)
        self.last_scanned_label = tk.Label(self.root, text="None", font=("Arial", 15, "bold"), fg=fgup, bg=bgup)
        self.last_scanned_label.place(x=10, y=70)

        try:
            image_path = "assets/mslogo.png"
            self.logo_image = Image.open(image_path)

            self.logo_image = self.logo_image.resize((80, 50))  # Resize as needed
            self.logo_photo = ImageTk.PhotoImage(self.logo_image)  # Store reference

            self.logo_label = tk.Label(self.root, image=self.logo_photo, bg=bgupd)
            self.logo_label.place(x=10, y=340)  # Adjust position as needed
            self.data_labels = tk.Label(self.root, text="MoonSide", fg=bgup, bg=bgupd, font=("Arial", 9))
            self.data_labels.place(x=20, y=380)
        except Exception as e:
            print(f"Error loading image: {e}")
        style=ttk.Style()
        style.theme_use("clam")
        # ttk Button style for Button 1
        style.configure('buttondesign1.TButton', font="georgia 20 bold",width=20,bordercolor="lightgreen")
        style.map('buttondesign1.TButton',background=[('active',"lightgreen"),('!disabled',bgupb)],foreground=[('active','black'),('!disabled',bgup)])
        style.configure('buttondesign2.TButton', font="georgia 8 ",width=20,bordercolor="lightgreen")
        style.map('buttondesign2.TButton',background=[('active','white'),('!disabled',"#899292")],foreground=[('active','black'),('!disabled',fgup)])
        self.gallery_image = load_button_image("assets/set.png", (25, 25))  # Adjust path & size
        self.slider_button = ttk.Button(self.root, text="Settings",command=self.open_new_window, style='buttondesign2.TButton', image=self.gallery_image, compound="top")
        self.slider_button.place(x=540, y=345, width=80, height=50)
        self.slider_button.image = self.gallery_image
        self.gallery_image22 = load_button_image("assets/quit.png", (25, 25))  # Adjust path & size
        self.quit_button = ttk.Button(self.root,text="Quit", command=self.destroyhall, style='buttondesign2.TButton', image=self.gallery_image22, compound="top")
        self.quit_button.place(x=720, y=345, width=80, height=50)
        self.quit_button.image = self.gallery_image22
        self.gallery_image2w2 = load_button_image("assets/rester.png", (25, 25))  # Adjust path & size
        self.res_button = ttk.Button(self.root,text="refresh", command=self.auto_detect_port, style='buttondesign2.TButton', image=self.gallery_image2w2, compound="top")
        self.res_button.place(x=630, y=345, width=80, height=50)
        self.res_button.image = self.gallery_image2w2
         
        self.check_entry = tk.Button(self.root,text="ADD",bg="blue" ,fg="white",command=self.get_entry_value, font=("Arial", 10,"bold"))
        self.check_entry.place(x=10, y=170, width=50, height=40)

        self.is_scan = tk.Button(self.root,text="OFF",bg="red",fg="white" ,command=self.toggle, font=("Arial", 10,"bold"))
        self.is_scan.place(x=10, y=115, width=50, height=40)
        self.data_label22 = tk.Label(self.root, text="""  <-- Scan to Print""", fg=fgup, bg=bgup, font=("Arial", 13,"bold"))
        self.data_label22.place(x=60, y=120)

        self.print_button = ttk.Button(self.root, text="Print", command=self.print_data, style='buttondesign1.TButton')
        self.print_button.place(x=25, y=220, width=250, height=70)
        self.data_label2 = tk.Label(self.root, text="""(or press enter to print)""", fg=fgup, bg=bgup, font=("Arial", 10))
        self.data_label2.place(x=80, y=290)

        self.size_status_label = tk.Label(self.root, text="Style : Not Connected", fg=bgup, bg=bgupd, font=("Arial", 12, "bold"))
        self.size_status_label.place(x=305, y=345)
        self.countprint_label = tk.Label(self.root, text="Copy : Not Connected", fg=bgup, bg=bgupd, font=("Arial", 12, "bold"))
        self.countprint_label.place(x=305, y=375)

        self.port_status_label = tk.Label(self.root, text="Scanner : Not Connected", fg="#f0ad45", bg=bgupd, font=("Arial", 11, "bold"))
        self.port_status_label.place(x=95, y=345)
        self.printer_label = tk.Label(self.root, text="Printer : Not Connected", fg="#f0ad45", bg=bgupd, font=("Arial", 11, "bold"))
        self.printer_label.place(x=95, y=375)


        self.history_table = ttk.Treeview(self.root, columns=("#", "Data", "Printed"), show="headings")
        self.history_table.heading("#", text="No.")
        self.history_table.heading("Data", text="Scanned Data")
        self.history_table.heading("Printed", text="Printed")

        self.history_table.column("#", width=40, anchor="center")
        self.history_table.column("Data", width=250, anchor="center")
        self.history_table.column("Printed", width=100, anchor="center")

        self.history_table.place(x=300, y=0, width=500, height=340)

        self.style = ttk.Style()
        self.style.theme_use("clam")  # Use clam theme to enable background color changes
        self.style.configure("Treeview", rowheight=25, background=trecl, foreground=fgup, fieldbackground=trecl)
        self.style.map("Treeview", background=[["selected", "#505050"]])

        # Set Treeview heading style
        self.style.configure("Treeview.Heading", font=("Arial", 15, "bold"), background=bgup, foreground=fgup)

    
    def auto_detect_port(self):
        global printerhere
        
        fin=open("assets/printcount.txt","r")
        printnumcount=int(fin.read())
        fin.close()
        self.countprint_label.config(text=f"Copy : {printnumcount}")
        ff=open("assets/sizecheck.txt","r")
        order=int(ff.readline())
        ff.close()       
        self.size_status_label.config(text=f"Style : style_{order}")
        detected_port = detect_scanner_port()
        printer = printbarcode.is_printer_connected()
        if detected_port:
            self.serial_port.port = detected_port
            self.serial_port.baudrate = 9600
            self.serial_port.timeout = 1
            try:
                self.serial_port.open()
                self.start_serial_thread()  # Start the thread here
                self.port_status_label.config(text=f"Scanner : Connected ●", fg="#3fd61a")
            except serial.SerialException:
                self.port_status_label.config(text="Scanner : Not Connected", fg="#f0ad45")
        else:
            self.port_status_label.config(text="Scanner : Not Connected", fg="#f0ad45")
        if printer==True:
            self.printer_label.config(text=f"Printer : Connected ●", fg="#3fd61a")
            printerhere="yes"
        else:
            self.printer_label.config(text=f"Printer : Not Connected ", fg="#f0ad45")
            printerhere="no"

    def start_serial_thread(self):
        """Start a background thread for reading serial data."""
        self.running = True
        self.serial_thread = threading.Thread(target=self.read_serial_data, daemon=True)
        self.serial_thread.start()
    def read_serial_data(self):
        """Read data from the serial port in a separate thread and update GUI safely."""
        while self.running and self.serial_port.is_open:
            try:
                data = self.serial_port.readline().decode('utf-8').strip()
                if (data and data != self.last_scanned):
                        self.last_scanned = data
                        self.last_scanned_label.config(text=data)
                        save_scanned_data(data)
                        self.print_counts[data] = 0  # Initialize print count for new scan
                        self.scan_history.append(data)
                        self.update_history_table()
                if (is_on and data!=""):
                        self.print_data()
            except serial.SerialException:
                break  # Stop reading if there's an error
    
    def update_history_table(self):
        self.history_table.delete(*self.history_table.get_children())
        for i, data in enumerate(self.scan_history, 1):
            self.history_table.insert("", "0", values=(i, data, self.print_counts.get(data, 0)))
    
    def print_data(self):
        global printerhere
        if printerhere=="yes":
            if self.last_scanned:
                print("Printing:", self.last_scanned)
                if self.last_scanned in self.print_counts:
                    self.print_counts[self.last_scanned] += 1
                    ff=open("assets/sizecheck.txt","r")
                    order=int(ff.readline())
                    ff.close()
                    try:
                        fin=open("assets/printcount.txt","r")
                        howmany=int(fin.read())
                        fin.close()
                    except:
                        howmany=1
                    printbarcode.printvalue(self.last_scanned,order,howmany)
                self.update_history_table()
        else:
            messagebox.showerror("Error", "Printer is not connected !!!")

    
    def on_enter_pressed(self, event):
        self.print_data()

#######################################################################
#russian##########################################
class QRScannerAppRU:
    def __init__(self, new_root):
        global bgup,fgup,trecl,bgupb,bgupd,is_on
        fgup="black"
        is_on = False
        bgup="white"
        bgupb="gray"
        trecl="#f1ecec"
        bgupd="gray"
        self.last_scanned2=""
        self.new_root = new_root
        self.new_root.title("Data Master")
        self.new_root.geometry("800x400")
        self.new_root.configure(bg=bgup)
        icon =  tk.PhotoImage(file="assets/logo.png")
        self.new_root.iconphoto(True, icon)
        
        self.serial_port = serial.Serial()
        self.last_scanned = ""
        self.print_counts = {}
        self.scan_history = []
        
        self.create_widgets()
        self.auto_detect_port()
        self.new_root.bind("<KeyRelease-Return>", self.on_enter_pressed)

    def destroyhall(self):
        self.running = False  # Flag to stop the thread loop
        if self.serial_port.is_open:
            self.serial_port.close()  # Close the serial port
        if hasattr(self, 'serial_thread') and self.serial_thread.is_alive():
            self.serial_thread.join(timeout=1)  # Ensure it stops safely
        self.new_root.quit()
        self.new_root.destroy()

    def open_new_window(self):
        global printnumcount
        def load_button_image(image_path, size,self):  # Resize as needed
            self.image = Image.open(image_path)
            self.image = self.image.resize(size, Image.LANCZOS)  # Resize image
            return ImageTk.PhotoImage(self.image)
        self.new_window = tk.Toplevel(self.new_root)
        self.new_window.title("Data Master --- настройки")
        self.new_window.geometry("550x400")
        self.new_window.configure(bg=bgup)
        self.canvas = tk.Canvas(self.new_window, width=560, height=50, bg="#0aa5c4", highlightthickness=0)#1c1c1c
        self.canvas.place(x=0, y=0)  # Adjust y position to align with text
        self.label = tk.Label(self.new_window, text="настройки", fg="#f4f4f4", bg="#0aa5c4", font=("Arial", 16,"bold"))
        self.label.place(x=210,y=10)
        ff=open("assets/sizecheck.txt","r")
        number=ff.read()
        ff.close()
        self.label2 = tk.Label(self.new_window, text=f"Выбранный стиль_{number}", fg="black", bg=bgup, font=("Arial", 16,"bold"))
        self.label2.place(x=150,y=60)

        self.label4 = tk.Label(self.new_window, text="стиль_1", fg="black", bg=bgup, font=("Arial", 16,"bold"))
        self.label4.place(x=50,y=180)

        self.label5 = tk.Label(self.new_window, text="стиль_2", fg="black", bg=bgup, font=("Arial", 16,"bold"))
        self.label5.place(x=220,y=180)

        self.label6 = tk.Label(self.new_window, text="стиль_3", fg="black", bg=bgup, font=("Arial", 16,"bold"))
        self.label6.place(x=390,y=180)

        self.label42 = tk.Label(self.new_window, text="Разработано MoonSide", fg="black", bg=bgup, font=("Arial", 10,"bold"))
        self.label42.place(x=20,y=370)
        def choose(number):
            global numberofprder
            self.label2.config(text=f"Выбранный стиль_{number}")
            numberofprder=number
            self.size_status_label.config(text=f"Cтиль : стиль_{numberofprder}")
            ff=open("assets/sizecheck.txt","w")
            ff.write(str(numberofprder))
            ff.close()
        def destroy():
                self.new_window.destroy()
        def changelang():
                global app
                file=open("assets/language.txt","w")
                file.write("en")
                file.close()
                self.running = False  # Flag to stop the thread loop
                if self.serial_port.is_open:
                    self.serial_port.close()  # Close the serial port
                if hasattr(self, 'serial_thread') and self.serial_thread.is_alive():
                    self.serial_thread.join(timeout=1)  # Ensure it stops safely
                self.new_window.destroy()
                self.new_root.destroy() 
                new_root = tk.Tk()   # Create a new Tkinter new_root window
                app = QRScannerApp(new_root)  # Start the Russian version of the app
                new_root.mainloop()  # Run the main loop
        self.gallery_image1 = load_button_image("assets/size2.png", (140, 70),self)  # Adjust path & size
        self.close_button1 = ttk.Button(self.new_window,image=self.gallery_image1, padding=0,command=lambda:choose(1))
        self.close_button1.place(x=30,y=100,width=150,height=80)
        self.gallery_image2 = load_button_image("assets/size1.png", (140, 70),self)  
        self.close_button2 = ttk.Button(self.new_window, image=self.gallery_image2, padding=0,   command=lambda:choose(2))
        self.close_button2.place(x=200,y=100,width=150,height=80)
        self.gallery_image3 = load_button_image("assets/size3.png", (140, 70),self)  
        self.close_button3 = ttk.Button(self.new_window, image=self.gallery_image3,  padding=0,  command=lambda:choose(3))
        self.close_button3.place(x=370,y=100,width=150,height=80)

        def increase():
            global printnumcount
            printnumcount += 1
            fin=open("assets/printcount.txt","w")
            fin.write(str(printnumcount))
            fin.close()
            self.label.config(text=str(printnumcount))
            self.countprint_label.config(text=f"Копии : {printnumcount}")

        def decrease():
            global printnumcount
            if printnumcount!=1:
                printnumcount -= 1
                fin=open("assets/printcount.txt","w")
                fin.write(str(printnumcount))
                fin.close()
                self.label.config(text=str(printnumcount))
                self.countprint_label.config(text=f"Копии : {printnumcount}")
        fin=open("assets/printcount.txt","r")
        printnumcount=int(fin.read())
        #print(printnumcount)
        fin.close()
        
        # Decrease Button
        self.minus_button = tk.Button(self.new_window, text="-", font=("Arial", 16), width=5, command=decrease)
        self.minus_button.place(x=460,y=230,width=50,height=50)

        # Label to display number
        self.labelNMAE = tk.Label(self.new_window, text="Количество копий печати:", font=("Arial", 16,"bold"),bg=bgup)
        self.labelNMAE.place(x=20,y=235)
        self.label = tk.Label(self.new_window, text=str(printnumcount), font=("Arial", 16))
        self.label.place(x=400,y=230,width=50,height=50)

        # Increase Button
        self.plus_button = tk.Button(self.new_window, text="+", font=("Arial", 16), width=5, command=increase)
        self.plus_button.place(x=340,y=230,width=50,height=50)
        
        self.close_button = ttk.Button(self.new_window, text="Закрывать", command=destroy)
        self.close_button.place(x=450,y=360)
        self.labelNMAE1 = tk.Label(self.new_window, text="Изменить язык на --> ", font=("Arial", 16,"bold"),bg=bgup)
        self.labelNMAE1.place(x=20,y=305)
        self.langcha = tk.Button(self.new_window, text="Английский", font=("Arial", 16), command=changelang)
        self.langcha.place(x=350,y=300,width=150,height=40)
    def toggle(self):
        global is_on
        is_on = not is_on
        self.is_scan.config(text="ON" if is_on else "OFF", bg="green" if is_on else "red")
    def get_entry_value(self):
            data = self.entry_value.get()
            if (data and data != self.last_scanned2):
                if data in self.scan_history:
                    self.last_scanned2 = data
                    self.last_scanned=self.last_scanned2
                    self.last_scanned_label.config(text=data)
                    save_scanned_data(data)
                     # Initialize print count for new scan
                    self.scan_history.append(data)
                    self.update_history_table()
                else:
                    self.last_scanned2 = data
                    self.last_scanned=self.last_scanned2
                    self.last_scanned_label.config(text=data)
                    save_scanned_data(data)  
                    self.print_counts[data] = 0 # Initialize print count for new scan
                    self.scan_history.append(data)
                    self.update_history_table()
    def create_widgets(self):
        class PlaceholderEntry(tk.Entry):
            def __init__(self, master=None, placeholder="Введите текст...", color="gray", *args, **kwargs):
                super().__init__(master, *args, **kwargs)

                self.placeholder = placeholder
                self.placeholder_color = color
                self.default_fg_color = self["fg"]

                self.put_placeholder()

                self.bind("<FocusIn>", self.on_focus_in)
                self.bind("<FocusOut>", self.on_focus_out)

            def put_placeholder(self):
                """Put the placeholder text in the entry."""
                self.insert(0, self.placeholder)
                self["fg"] = self.placeholder_color

            def on_focus_in(self, event):
                """Remove placeholder text when clicked."""
                if self.get() == self.placeholder:
                    self.delete(0, tk.END)
                    self["fg"] = self.default_fg_color

            def on_focus_out(self, event):
                """Restore placeholder text if the entry is empty."""
                if not self.get():
                    self.put_placeholder()
        def load_button_image(image_path, size, self):  # Resize as needed
            self.image = Image.open(image_path)
            self.image = self.image.resize(size, Image.LANCZOS)  # Resize image
            return ImageTk.PhotoImage(self.image)
        
        self.entry_value = PlaceholderEntry(self.new_root, font=("Arial", 12,"bold"),fg="black",bg="#d8dad8")
        self.entry_value.place(x=70, y=170,width=200,height=40)    
        self.name = tk.Label(self.new_root, text="Data Master", fg=fgup, bg=bgup, font=("Arial", 18, "bold"))
        self.name.place(x=70, y=0)

        self.data_label = tk.Label(self.new_root, text="Последнее сканирование:", fg=fgup, bg=bgup, font=("Arial", 13))
        self.data_label.place(x=10, y=40)

        # Add red underline using Canvas
        self.canvas = tk.Canvas(self.new_root, width=300, height=3, bg=fgup, highlightthickness=0)#1c1c1c
        self.canvas.place(x=0, y=35)  # Adjust y position to align with text

        self.canvasd = tk.Canvas(self.new_root, width=850, height=70, bg=bgupd, highlightthickness=1)#1c1c1c
        self.canvasd.place(x=-8, y=339)
        self.canvasd2 = tk.Canvas(self.new_root, width=1, height=70, bg="black", highlightthickness=0)#1c1c1c
        self.canvasd2.place(x=300, y=339)
        self.last_scanned_label = tk.Label(self.new_root, text="пустой", font=("Arial", 15, "bold"), fg=fgup, bg=bgup)
        self.last_scanned_label.place(x=10, y=70)

        try:
            image_path = "assets/mslogo.png"
            self.logo_image = Image.open(image_path)

            self.logo_image = self.logo_image.resize((80, 50))  # Resize as needed
            self.logo_photo = ImageTk.PhotoImage(self.logo_image)  # Store reference

            self.logo_label = tk.Label(self.new_root, image=self.logo_photo, bg=bgupd)
            self.logo_label.place(x=10, y=340)  # Adjust position as needed
            self.data_labels = tk.Label(self.new_root, text="MoonSide", fg=bgup, bg=bgupd, font=("Arial", 9))
            self.data_labels.place(x=20, y=380)
        except Exception as e:
            print(f"Error loading image: {e}")
        style=ttk.Style()
        style.theme_use("clam")
        # ttk Button style for Button 1
        style.configure('buttondesign1.TButton', font="georgia 20 bold",width=20,bordercolor="lightgreen")
        style.map('buttondesign1.TButton',background=[('active',"lightgreen"),('!disabled',bgupb)],foreground=[('active','black'),('!disabled',bgup)])
        style.configure('buttondesign2.TButton', font="georgia 7 ",width=20,bordercolor="lightgreen")
        style.map('buttondesign2.TButton',background=[('active','white'),('!disabled',"#899292")],foreground=[('active','black'),('!disabled',fgup)])
        self.gallery_image = load_button_image("assets/set.png", (25, 25),self)  # Adjust path & size
        self.slider_button = ttk.Button(self.new_root, text="Настройки",command=self.open_new_window, style='buttondesign2.TButton', image=self.gallery_image, compound="top")
        self.slider_button.place(x=540, y=345, width=80, height=50)
    
        self.gallery_image22 = load_button_image("assets/quit.png", (25, 25),self)  # Adjust path & size
        self.quit_button = ttk.Button(self.new_root,text="закрывать", command=self.destroyhall, style='buttondesign2.TButton', image=self.gallery_image22, compound="top")
        self.quit_button.place(x=720, y=345, width=80, height=50)

        self.gallery_image2w2 = load_button_image("assets/rester.png", (25, 25),self)  # Adjust path & size
        self.res_button = ttk.Button(self.new_root,text="обновить", command=self.auto_detect_port, style='buttondesign2.TButton', image=self.gallery_image2w2, compound="top")
        self.res_button.place(x=630, y=345, width=80, height=50)
         
        self.check_entry = tk.Button(self.new_root,text="доб",bg="blue" ,fg="white",command=self.get_entry_value, font=("Arial", 10,"bold"))
        self.check_entry.place(x=10, y=170, width=50, height=40)

        self.is_scan = tk.Button(self.new_root,text="OFF",bg="red",fg="white" ,command=self.toggle, font=("Arial", 10,"bold"))
        self.is_scan.place(x=10, y=115, width=50, height=40)
        self.data_label22 = tk.Label(self.new_root, text="""  <-- Сканировать для печати""", fg=fgup, bg=bgup, font=("Arial", 10,"bold"))
        self.data_label22.place(x=60, y=120)

        self.print_button = ttk.Button(self.new_root, text="Печать", command=self.print_data, style='buttondesign1.TButton')
        self.print_button.place(x=25, y=220, width=250, height=70)
        self.data_label2 = tk.Label(self.new_root, text="""(или нажмите Enter, чтобы распечатать)""", fg=fgup, bg=bgup, font=("Arial", 10))
        self.data_label2.place(x=30, y=290)

        self.size_status_label = tk.Label(self.new_root, text="Стиль : Не подключено", fg=bgup, bg=bgupd, font=("Arial", 12, "bold"))
        self.size_status_label.place(x=305, y=345)
        self.countprint_label = tk.Label(self.new_root, text="Копии : Не подключено", fg=bgup, bg=bgupd, font=("Arial", 12, "bold"))
        self.countprint_label.place(x=305, y=375)

        self.port_status_label = tk.Label(self.new_root, text="Сканер : Не подключено", fg="#f0ad45", bg=bgupd, font=("Arial", 11, "bold"))
        self.port_status_label.place(x=95, y=345)
        self.printer_label = tk.Label(self.new_root, text="Принтер : Не подключено", fg="#f0ad45", bg=bgupd, font=("Arial", 11, "bold"))
        self.printer_label.place(x=95, y=375)


        self.history_table = ttk.Treeview(self.new_root, columns=("#", "Data", "Printed"), show="headings")
        self.history_table.heading("#", text="No.")
        self.history_table.heading("Data", text="Сканированные данные")
        self.history_table.heading("Printed", text="Печатный")

        self.history_table.column("#", width=40, anchor="center")
        self.history_table.column("Data", width=250, anchor="center")
        self.history_table.column("Printed", width=100, anchor="center")

        self.history_table.place(x=300, y=0, width=500, height=340)

        self.style = ttk.Style()
        self.style.theme_use("clam")  # Use clam theme to enable background color changes
        self.style.configure("Treeview", rowheight=25, background=trecl, foreground=fgup, fieldbackground=trecl)
        self.style.map("Treeview", background=[["selected", "#505050"]])

        # Set Treeview heading style
        self.style.configure("Treeview.Heading", font=("Arial", 15, "bold"), background=bgup, foreground=fgup)

    
    def auto_detect_port(self):
        global printerhere
        
        fin=open("assets/printcount.txt","r")
        printnumcount=int(fin.read())
        fin.close()
        self.countprint_label.config(text=f"Копии : {printnumcount}")
        ff=open("assets/sizecheck.txt","r")
        order=int(ff.readline())
        ff.close()       
        self.size_status_label.config(text=f"Стиль : стиль_{order}")
        detected_port = detect_scanner_port()
        printer = printbarcode.is_printer_connected()
        if detected_port:
            self.serial_port.port = detected_port
            self.serial_port.baudrate = 9600
            self.serial_port.timeout = 1
            try:
                self.serial_port.open()
                self.start_serial_thread()  # Start the thread here
                self.port_status_label.config(text=f"Сканер : Подключен ●", fg="#3fd61a")
            except serial.SerialException:
                self.port_status_label.config(text="Сканер : Не подключено", fg="#f0ad45")
        else:
            self.port_status_label.config(text="Сканер :Не подключено", fg="#f0ad45")
        if printer==True:
            self.printer_label.config(text=f"Принтер : Подключен ●", fg="#3fd61a")
            printerhere="yes"
        else:
            self.printer_label.config(text=f"Принтер : Не подключено", fg="#f0ad45")
            printerhere="no"

    def start_serial_thread(self):
        """Start a background thread for reading serial data."""
        self.running = True
        self.serial_thread = threading.Thread(target=self.read_serial_data, daemon=True)
        self.serial_thread.start()
    def read_serial_data(self):
        """Read data from the serial port in a separate thread and update GUI safely."""
        while self.running and self.serial_port.is_open:
            try:
                data = self.serial_port.readline().decode('utf-8').strip()
                if (data and data != self.last_scanned):
                        self.last_scanned = data
                        self.last_scanned_label.config(text=data)
                        save_scanned_data(data)
                        self.print_counts[data] = 0  # Initialize print count for new scan
                        self.scan_history.append(data)
                        self.update_history_table()
                if (is_on and data!=""):
                        self.print_data()
            except serial.SerialException:
                break  # Stop reading if there's an error
    
    def update_history_table(self):
        self.history_table.delete(*self.history_table.get_children())
        for i, data in enumerate(self.scan_history, 1):
            self.history_table.insert("", "0", values=(i, data, self.print_counts.get(data, 0)))
    
    def print_data(self):
        global printerhere
        if printerhere=="yes":
            if self.last_scanned:
                print("Printing:", self.last_scanned)
                if self.last_scanned in self.print_counts:
                    self.print_counts[self.last_scanned] += 1
                    ff=open("assets/sizecheck.txt","r")
                    order=int(ff.readline())
                    ff.close()
                    try:
                        fin=open("assets/printcount.txt","r")
                        howmany=int(fin.read())
                        fin.close()
                    except:
                        howmany=1
                    printbarcode.printvalue(self.last_scanned,order,howmany)
                self.update_history_table()
        else:
            messagebox.showerror("Error", "Принтер не подключен !!!")

    
    def on_enter_pressed(self, event):
            self.print_data()



file=open("assets/language.txt","r")
lang=file.read()
file.close()
if lang=="en":
        root = tk.Tk()
        app = QRScannerApp(root)
        root.mainloop()
elif lang=="ru":
        new_root = tk.Tk()
        app = QRScannerAppRU(new_root)
        new_root.mainloop()