#!/usr/bin/env python3
"""
E-Stamp PDF Generator - Standalone Application
Generates 8.5 x 14 inch e-stamp PDF documents with barcode and QR code
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from reportlab.lib.pagesizes import legal
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import barcode
from barcode.writer import ImageWriter
import qrcode
from PIL import Image
import io
from datetime import datetime
import os

class EStampGenerator:
    """Main PDF Generator Class"""

    def __init__(self):
        self.width, self.height = legal  # 8.5 x 14 inches

    def generate_barcode(self, data):
        """Generate barcode image"""
        try:
            code128 = barcode.get('code128', data, writer=ImageWriter())
            buffer = io.BytesIO()
            code128.write(buffer)
            buffer.seek(0)
            return Image.open(buffer)
        except Exception as e:
            print(f"Barcode generation error: {e}")
            return None

    def generate_qr_code(self, data):
        """Generate QR code image"""
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=2)
            qr.add_data(data)
            qr.make(fit=True)
            return qr.make_image(fill_color="black", back_color="white")
        except Exception as e:
            print(f"QR code generation error: {e}")
            return None

    def create_estamp(self, output_filename, data):
        """Create e-stamp PDF with all details"""
        c = canvas.Canvas(output_filename, pagesize=legal)

        # Title
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(self.width/2, self.height - 80, "E-STAMP")
        c.line(self.width/2 - 50, self.height - 85, self.width/2 + 50, self.height - 85)

        # Generate and draw barcode
        barcode_img = self.generate_barcode(data.get('id', 'PB-LHR-85E0A9D44A96E019'))
        if barcode_img:
            barcode_path = 'temp_barcode.png'
            barcode_img.save(barcode_path)
            c.drawImage(barcode_path, 60, self.height - 180, width=2.5*inch, height=0.8*inch)
            # Clean up temp file
            try:
                os.remove(barcode_path)
            except:
                pass

        # Generate and draw QR code
        qr_img = self.generate_qr_code(data.get('id', 'PB-LHR-85E0A9D44A96E019'))
        if qr_img:
            qr_path = 'temp_qr.png'
            qr_img.save(qr_path)
            c.drawImage(qr_path, self.width - 140, self.height - 180, width=80, height=80)
            # Add text under QR
            c.setFont("Helvetica", 7)
            c.drawString(self.width - 140, self.height - 190, "Scan for online verification")
            # Clean up temp file
            try:
                os.remove(qr_path)
            except:
                pass

        # Main content section
        y_position = self.height - 200
        left_margin = 60
        label_width = 140

        # Define all fields
        fields = [
            ('ID:', data.get('id', '')),
            ('Type:', data.get('type', '')),
            ('Amount:', data.get('amount', '')),
            ('', ''),  # Empty line for spacing
            ('Description:', data.get('description', '')),
            ('Applicant:', data.get('applicant', '')),
            ('W/O:', data.get('wo', '')),
            ('Address:', data.get('address', '')),
            ('Issue Date:', data.get('issue_date', '')),
            ('Delisted On/Validity:', data.get('validity', '')),
            ('Amount in Words:', data.get('amount_words', '')),
            ('Reason:', data.get('reason', '')),
            ('Vendor Information:', data.get('vendor', ''))
        ]

        # Draw fields
        for label, value in fields:
            if label:
                c.setFont("Helvetica-Bold", 9)
                c.drawString(left_margin, y_position, label)
                c.setFont("Helvetica", 9)
                c.drawString(left_margin + label_width, y_position, value)
            y_position -= 18

        # Bottom instruction box
        box_y = y_position - 30
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        c.rect(60, box_y - 30, self.width - 120, 40)

        # Instruction text
        c.setFont("Helvetica", 8)
        instruction = data.get('instruction_english', 'Type "eStamp <16 digit eStamp Number>" send to 8100')
        c.drawCentredString(self.width/2, box_y - 15, instruction)

        # Save PDF
        c.save()
        return True


class EStampGUI:
    """GUI Application for E-Stamp Generator"""

    def __init__(self, root):
        self.root = root
        self.root.title("E-Stamp PDF Generator - Pakistan")
        self.root.geometry("750x850")
        self.root.resizable(False, False)

        # Set icon color scheme
        self.root.configure(bg='#f0f0f0')

        # Create generator instance
        self.generator = EStampGenerator()

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        # Header Frame
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        # Title
        title_label = tk.Label(header_frame, text="E-STAMP PDF GENERATOR", 
                               font=("Arial", 20, "bold"), 
                               fg="white", bg='#2c3e50')
        title_label.pack(pady=15)

        subtitle = tk.Label(header_frame, text="Generate 8.5 x 14 inch Legal Size Documents", 
                           font=("Arial", 10), 
                           fg="#ecf0f1", bg='#2c3e50')
        subtitle.pack()

        # Main content frame with canvas and scrollbar
        content_frame = tk.Frame(self.root, bg='#f0f0f0')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Create canvas for scrolling
        canvas = tk.Canvas(content_frame, bg='#f0f0f0', highlightthickness=0)
        scrollbar = tk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f0f0f0')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Form fields
        self.entries = {}
        fields = [
            ('ID Number:', 'id', 'PB-LHR-85E0A9D44A96E019'),
            ('Type:', 'type', 'Low Denomination'),
            ('Amount:', 'amount', 'Rs.100/-'),
            ('Description:', 'description', 'AFFIDAVIT-4'),
            ('Applicant:', 'applicant', 'RIFAT FARHAN 35201-1498228-4'),
            ('W/O:', 'wo', 'MUHAMMAD FARHAN'),
            ('Address:', 'address', 'LAHORE'),
            ('Issue Date:', 'issue_date', datetime.now().strftime("%d-%b-%Y %I:%M:%S %p").upper()),
            ('Validity Date:', 'validity', '14-JAN-2025'),
            ('Amount in Words:', 'amount_words', 'One Hundred Rupees Only'),
            ('Reason:', 'reason', 'AFFIDAVIT'),
            ('Vendor Information:', 'vendor', 'Nadeem Ahmad Stamp Vendor | PB-LHR-981 | Mustafabad, Lahore'),
        ]

        for i, (label_text, field_name, default_value) in enumerate(fields):
            # Label
            label = tk.Label(scrollable_frame, text=label_text, 
                           font=("Arial", 10, "bold"), 
                           anchor='w', bg='#f0f0f0')
            label.grid(row=i, column=0, sticky='w', pady=10, padx=(5, 15))

            # Entry
            entry = tk.Entry(scrollable_frame, width=55, 
                           font=("Arial", 10), 
                           relief=tk.SOLID, 
                           borderwidth=1)
            entry.insert(0, default_value)
            entry.grid(row=i, column=1, sticky='ew', pady=10, padx=(0, 5))
            self.entries[field_name] = entry

        # Instruction text
        instr_label = tk.Label(scrollable_frame, text="Instruction Text:", 
                              font=("Arial", 10, "bold"), 
                              anchor='w', bg='#f0f0f0')
        instr_label.grid(row=len(fields), column=0, sticky='w', pady=10, padx=(5, 15))

        self.instruction_entry = tk.Entry(scrollable_frame, width=55, 
                                         font=("Arial", 10), 
                                         relief=tk.SOLID, 
                                         borderwidth=1)
        self.instruction_entry.insert(0, 'Type "eStamp <16 digit eStamp Number>" send to 8100')
        self.instruction_entry.grid(row=len(fields), column=1, sticky='ew', pady=10, padx=(0, 5))

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Buttons frame
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(pady=20)

        # Generate button
        generate_btn = tk.Button(button_frame, text="📄 Generate PDF", 
                                command=self.generate_pdf,
                                bg="#27ae60", fg="white", 
                                font=("Arial", 13, "bold"),
                                padx=40, pady=12,
                                cursor="hand2",
                                relief=tk.FLAT,
                                activebackground="#229954")
        generate_btn.pack(side=tk.LEFT, padx=10)

        # Clear button
        clear_btn = tk.Button(button_frame, text="🗑️ Clear All", 
                             command=self.clear_fields,
                             bg="#e74c3c", fg="white", 
                             font=("Arial", 13, "bold"),
                             padx=40, pady=12,
                             cursor="hand2",
                             relief=tk.FLAT,
                             activebackground="#c0392b")
        clear_btn.pack(side=tk.LEFT, padx=10)

        # Footer
        footer = tk.Label(self.root, text="© 2026 E-Stamp Generator | Made with Python", 
                         font=("Arial", 8), 
                         fg="#7f8c8d", bg='#f0f0f0')
        footer.pack(pady=(0, 10))

    def generate_pdf(self):
        """Generate PDF from form data"""
        try:
            # Get data from entries
            data = {key: entry.get().strip() for key, entry in self.entries.items()}
            data['instruction_english'] = self.instruction_entry.get().strip()

            # Validate required fields
            if not data.get('id'):
                messagebox.showwarning("Missing Data", "Please enter ID Number!")
                return

            # Ask for save location
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile=f"estamp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )

            if filename:
                # Generate PDF
                success = self.generator.create_estamp(filename, data)

                if success:
                    messagebox.showinfo("✅ Success", 
                                      f"E-Stamp PDF generated successfully!\n\nSaved as:\n{filename}")
                else:
                    messagebox.showerror("❌ Error", "Failed to generate PDF!")

        except Exception as e:
            messagebox.showerror("❌ Error", f"Failed to generate PDF:\n\n{str(e)}")

    def clear_fields(self):
        """Clear all form fields"""
        response = messagebox.askyesno("Clear All", "Are you sure you want to clear all fields?")
        if response:
            for entry in self.entries.values():
                entry.delete(0, tk.END)
            self.instruction_entry.delete(0, tk.END)
            messagebox.showinfo("Cleared", "All fields have been cleared!")


def main():
    """Main application entry point"""
    root = tk.Tk()
    app = EStampGUI(root)
    root.mainloop()


if __name__ == "__main__":
    # Check dependencies
    try:
        import reportlab
        import barcode
        import qrcode
        from PIL import Image
        print("✅ All dependencies found!")
        print("🚀 Starting E-Stamp Generator...")
        main()
    except ImportError as e:
        print("❌ Missing dependency!")
        print(f"\nError: {e}")
        print("\n📦 Please install required packages:")
        print("pip install reportlab python-barcode qrcode Pillow")
        input("\nPress Enter to exit...")
