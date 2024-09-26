from flask import Flask, render_template, request, send_file
import qrcode
from fpdf import FPDF
import csv
import io
import time
from selenium import webdriver
from faker import Faker

app = Flask(__name__)
fake = Faker()

# Service 1: Website Screenshot Service
@app.route('/screenshot', methods=['GET', 'POST'])
def screenshot():
    if request.method == 'POST':
        url = request.form['url']
        options = webdriver.ChromeOptions()
        options.headless = True
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        screenshot_path = f"static/screenshot_{time.time()}.png"
        driver.save_screenshot(screenshot_path)
        driver.quit()
        return send_file(screenshot_path, as_attachment=True)
    return render_template('screenshot.html')


# Service 2: Random User Data Generator (CSV)
@app.route('/random_user', methods=['GET', 'POST'])
def random_user():
    if request.method == 'POST':
        num_users = int(request.form['num_users'])
        with open('generated.csv', 'w', newline='') as csvfile:
            fieldnames = ['Name', 'Address', 'Email', 'Phone Number']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for _ in range(num_users):
                writer.writerow({
                    'Name': fake.name(),
                    'Address': fake.address(),
                    'Email': fake.email(),
                    'Phone Number': fake.phone_number()
                })
        return send_file('generated.csv', as_attachment=True)
    return render_template('random_user.html')


# Service 3: PDF with QR Code Generator
@app.route('/qr_code', methods=['GET', 'POST'])
def qr_code():
    if request.method == 'POST':
        data = request.form['info']
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        img.save("static/qrcode.png")
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Add input data text
        pdf.cell(200, 10, txt="Input Data:", ln=True, align='C')
        pdf.multi_cell(0, 10, txt=data, align='L')
        
        # Add QR code at the bottom of the page
        page_height = pdf.h  
        qr_code_height = 50  
        qr_code_y_position = page_height - qr_code_height - 20 
        
        pdf.image("static/qrcode.png", x=85, y=qr_code_y_position, w=50, h=qr_code_height)
        
        # Output PDF
        pdf_file = "generated.pdf"
        pdf.output(pdf_file)
        
        return send_file(pdf_file, as_attachment=True)
    
    return render_template('qr_code.html')



# Home Page with Links to All Services
@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
