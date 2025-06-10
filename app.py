from flask import Flask, render_template, request, send_file, jsonify
from datetime import datetime, date
import calendar
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import io
import os

app = Flask(__name__)

class SalaryCalculator:
    def __init__(self, basic_salary, absent_days, late_entry_days, overtime_days, month=None, year=None):
        self.basic_salary = float(basic_salary)
        self.absent_days = int(absent_days)
        self.late_entry_days = int(late_entry_days)
        self.overtime_days = int(overtime_days)
        
        # Get current month and year if not provided
        if month is None or year is None:
            today = date.today()
            self.month = today.month
            self.year = today.year
        else:
            self.month = int(month)
            self.year = int(year)
        
        # Calculate days in month
        self.days_in_month = calendar.monthrange(self.year, self.month)[1]
        self.daily_salary = self.basic_salary / self.days_in_month
    
    def calculate_absent_deduction(self):
        """Calculate deduction for absent days (full day salary per absent day)"""
        return self.absent_days * self.daily_salary
    
    def calculate_late_entry_deduction(self):
        """Calculate deduction for late entry days (half day after 3 free days)"""
        if self.late_entry_days <= 3:
            return 0
        else:
            deductible_late_days = self.late_entry_days - 3
            return deductible_late_days * (self.daily_salary / 2)
    
    def calculate_overtime_addition(self):
        """Calculate addition for overtime days (half day salary per overtime day)"""
        return self.overtime_days * (self.daily_salary / 2)
    
    def calculate_pf(self):
        """Calculate Provident Fund (12% of basic salary, maximum on ₹15,000)"""
        # PF is calculated on maximum of ₹15,000 basic salary
        pf_eligible_salary = min(self.basic_salary, 15000)
        return pf_eligible_salary * 0.12
    
    def calculate_esi(self):
        """Calculate Employee State Insurance (0.75% of basic salary, only if basic ≤ ₹21,000)"""
        # ESI is only applicable if basic salary is ≤ ₹21,000
        if self.basic_salary > 21000:
            return 0
        else:
            return self.basic_salary * 0.0075
    
    def calculate_professional_tax(self, gross_salary):
        """Calculate Professional Tax based on salary slabs"""
        if gross_salary <= 10000:
            return 0
        elif gross_salary <= 15000:
            return 110
        elif gross_salary <= 25000:
            return 130
        elif gross_salary <= 40000:
            return 150
        else:
            return 200
    
    def calculate_total_salary(self):
        """Calculate the complete salary breakdown"""
        # Base calculations
        absent_deduction = self.calculate_absent_deduction()
        late_entry_deduction = self.calculate_late_entry_deduction()
        overtime_addition = self.calculate_overtime_addition()
        
        # Gross earnings calculation
        gross_earnings = self.basic_salary + overtime_addition
        
        # Attendance adjusted salary (after attendance deductions)
        attendance_adjusted_salary = gross_earnings - absent_deduction - late_entry_deduction
        
        # Statutory deductions (calculated on basic salary, not adjusted salary)
        pf_deduction = self.calculate_pf()
        esi_deduction = self.calculate_esi()
        professional_tax = self.calculate_professional_tax(attendance_adjusted_salary)
        
        # Total deductions calculation
        total_statutory_deductions = pf_deduction + esi_deduction + professional_tax
        total_all_deductions = absent_deduction + late_entry_deduction + total_statutory_deductions
        
        # Net salary calculation
        net_salary = gross_earnings - total_all_deductions
        
        return {
            'basic_salary': round(self.basic_salary, 2),
            'days_in_month': self.days_in_month,
            'daily_salary': round(self.daily_salary, 2),
            'absent_days': self.absent_days,
            'absent_deduction': round(absent_deduction, 2),
            'late_entry_days': self.late_entry_days,
            'late_entry_deduction': round(late_entry_deduction, 2),
            'overtime_days': self.overtime_days,
            'overtime_addition': round(overtime_addition, 2),
            'gross_earnings': round(gross_earnings, 2),
            'attendance_adjusted_salary': round(attendance_adjusted_salary, 2),
            'pf_deduction': round(pf_deduction, 2),
            'esi_deduction': round(esi_deduction, 2),
            'professional_tax': round(professional_tax, 2),
            'total_statutory_deductions': round(total_statutory_deductions, 2),
            'total_all_deductions': round(total_all_deductions, 2),
            'net_salary': round(net_salary),
            'month': calendar.month_name[self.month],
            'month_number': self.month,
            'year': self.year
        }

def generate_payslip_pdf(employee_name, salary_data):
    """Generate PDF payslip"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1,  # Center alignment
    )
    
    # Title
    title = Paragraph("EMPLOYEE PAY SLIP", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Employee details table
    employee_data = [
        ['Employee Name:', employee_name],
        ['Month/Year:', f"{salary_data['month']} {salary_data['year']}"],
        ['Days in Month:', str(salary_data['days_in_month'])],
        ['Daily Salary:', f"₹ {salary_data['daily_salary']:.2f}"]
    ]
    
    employee_table = Table(employee_data, colWidths=[2*inch, 3*inch])
    employee_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (0, 0), (0, -1), colors.grey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(employee_table)
    elements.append(Spacer(1, 20))
    
    # Salary breakdown table
    salary_breakdown = [
        ['EARNINGS', 'AMOUNT (₹)', 'DEDUCTIONS', 'AMOUNT (₹)'],
        ['Basic Salary', f"{salary_data['basic_salary']:.2f}", 'Absent Days Deduction', f"{salary_data['absent_deduction']:.2f}"],
        ['Overtime Addition', f"{salary_data['overtime_addition']:.2f}", 'Late Entry Deduction', f"{salary_data['late_entry_deduction']:.2f}"],
        ['', '', 'PF (12% on max ₹15K)', f"{salary_data['pf_deduction']:.2f}"],
        ['', '', f"ESI (0.75%{' - N/A' if salary_data['basic_salary'] > 21000 else ''})", f"{salary_data['esi_deduction']:.2f}"],
        ['', '', 'Professional Tax', f"{salary_data['professional_tax']:.2f}"],
        ['GROSS EARNINGS', f"{salary_data['gross_earnings']:.2f}", 'TOTAL DEDUCTIONS', f"{salary_data['total_all_deductions']:.2f}"],
        ['', '', 'NET SALARY', f"{salary_data['net_salary']:.0f}"]
    ]
    
    salary_table = Table(salary_breakdown, colWidths=[2*inch, 1.5*inch, 2*inch, 1.5*inch])
    salary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -3), colors.beige),
        ('BACKGROUND', (0, -2), (-1, -1), colors.lightblue),
        ('FONTNAME', (0, -2), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(salary_table)
    elements.append(Spacer(1, 20))
    
    # Attendance details
    attendance_details = [
        ['ATTENDANCE DETAILS', '', '', ''],
        ['Absent Days', str(salary_data['absent_days']), 'Late Entry Days', str(salary_data['late_entry_days'])],
        ['Overtime Days', str(salary_data['overtime_days']), '', '']
    ]
    
    attendance_table = Table(attendance_details, colWidths=[2*inch, 1.5*inch, 2*inch, 1.5*inch])
    attendance_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('SPAN', (0, 0), (-1, 0)),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(attendance_table)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate_salary():
    try:
        # Get form data
        employee_name = request.form['employee_name']
        basic_salary = float(request.form['basic_salary'])
        salary_month = int(request.form['salary_month'])
        salary_year = int(request.form['salary_year'])
        absent_days = int(request.form['absent_days'])
        late_entry_days = int(request.form['late_entry_days'])
        overtime_days = int(request.form['overtime_days'])
        
        # Validation
        if basic_salary <= 0:
            return jsonify({'error': 'Basic salary must be greater than 0'}), 400
        if absent_days < 0 or late_entry_days < 0 or overtime_days < 0:
            return jsonify({'error': 'Days cannot be negative'}), 400
        if salary_month < 1 or salary_month > 12:
            return jsonify({'error': 'Invalid month'}), 400
        if salary_year < 2020 or salary_year > date.today().year + 3:
            return jsonify({'error': 'Invalid year'}), 400
        
        # Calculate salary
        calculator = SalaryCalculator(basic_salary, absent_days, late_entry_days, overtime_days, salary_month, salary_year)
        salary_data = calculator.calculate_total_salary()
        
        # Store in session or pass to template
        return render_template('result.html', 
                             employee_name=employee_name, 
                             salary_data=salary_data)
    
    except ValueError as e:
        return jsonify({'error': 'Invalid input values'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    try:
        # Get data from form
        employee_name = request.form['employee_name']
        basic_salary = float(request.form['basic_salary'])
        salary_month = int(request.form['salary_month'])
        salary_year = int(request.form['salary_year'])
        absent_days = int(request.form['absent_days'])
        late_entry_days = int(request.form['late_entry_days'])
        overtime_days = int(request.form['overtime_days'])
        
        # Calculate salary
        calculator = SalaryCalculator(basic_salary, absent_days, late_entry_days, overtime_days, salary_month, salary_year)
        salary_data = calculator.calculate_total_salary()
        
        # Generate PDF
        pdf_buffer = generate_payslip_pdf(employee_name, salary_data)
        
        # Create a temporary file name
        filename = f"payslip_{employee_name.replace(' ', '_')}_{salary_data['month']}_{salary_data['year']}.pdf"
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 