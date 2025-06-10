# Employee Salary Calculator

A comprehensive web application for calculating employee salaries with automatic deductions and PDF pay slip generation.

## Features

- **Complete Salary Calculation**: Handles basic salary, overtime, absent days, and late entries
- **Automatic Deductions**: Calculates PF, ESI, and Professional Tax based on current regulations
- **PDF Pay Slip Generation**: Creates professional pay slips in PDF format
- **Modern UI**: Responsive design with client-side validation
- **Error Handling**: Comprehensive validation and error handling

## Calculation Rules

### Attendance-Based Calculations
- **Absent Days**: Full day salary deduction for each absent day
- **Late Entry Days**: First 3 days are free, then half day salary deduction for each additional late day
- **Overtime Days**: Half day salary addition for each overtime day

### Statutory Deductions
- **PF (Provident Fund)**: 12% of basic salary (calculated on maximum of ₹15,000, so maximum PF = ₹1,800)
- **ESI (Employee State Insurance)**: 0.75% of basic salary (only applicable if basic salary ≤ ₹21,000)
- **Professional Tax**: Based on salary slabs:
  - ₹0 to ₹10,000: ₹0
  - ₹10,001 to ₹15,000: ₹110
  - ₹15,001 to ₹25,000: ₹130
  - ₹25,001 to ₹40,000: ₹150
  - ₹40,001 and above: ₹200

### Formula
```
Daily Salary = Basic Salary / Days in Month
Gross Earnings = Basic Salary + Overtime Addition
Total Deductions = Absent Deduction + Late Entry Deduction + PF + ESI + Professional Tax
Net Salary = Gross Earnings - Total Deductions
```

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Local Development Setup

1. **Clone or download the project files**
   ```bash
   # If using git
   git clone <repository-url>
   cd employee-salary-calculator
   
   # Or create directory and copy files
   mkdir employee-salary-calculator
   cd employee-salary-calculator
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   Open your browser and go to `http://localhost:5000`

## Project Structure

```
employee-salary-calculator/
│
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
│
└── templates/
    ├── index.html        # Input form page
    └── result.html       # Results display page
```

## Usage

1. **Input Employee Details**
   - Enter employee name (required)
   - Enter basic salary (required, must be > 0)
   - Enter attendance details (optional, defaults to 0)

2. **View Results**
   - Review detailed salary breakdown
   - See all calculations and deductions
   - View net salary

3. **Generate PDF Pay Slip**
   - Click "Download Pay Slip PDF" button
   - PDF will be automatically downloaded
   - Contains all salary details in professional format

## API Endpoints

- `GET /` - Main input form
- `POST /calculate` - Calculate salary and show results
- `POST /generate_pdf` - Generate and download PDF pay slip

## Deployment Options

### 1. Heroku Deployment

Create additional files for Heroku:

**Procfile:**
```
web: python app.py
```

**runtime.txt:**
```
python-3.11.0
```

Deploy steps:
```bash
heroku create your-app-name
git add .
git commit -m "Initial commit"
git push heroku main
```

### 2. Railway Deployment

1. Connect your GitHub repository to Railway
2. Railway will automatically detect Flask app
3. Set environment variables if needed
4. Deploy

### 3. PythonAnywhere Deployment

1. Upload files to PythonAnywhere
2. Create a web app with manual configuration
3. Set up WSGI file:
   ```python
   import sys
   sys.path.insert(0, '/home/yourusername/mysite')
   from app import app as application
   ```

### 4. DigitalOcean App Platform

1. Connect GitHub repository
2. Configure build settings:
   - Build Command: `pip install -r requirements.txt`
   - Run Command: `python app.py`

## Testing

### Test Cases to Verify

1. **Basic Functionality**
   - Employee with only basic salary
   - Employee with all types of attendance (absent, late, overtime)
   - Different salary ranges for professional tax calculation

2. **Edge Cases**
   - Zero absent/late/overtime days
   - Maximum days in each category
   - Very high and very low salaries

3. **Validation**
   - Empty required fields
   - Negative values
   - Invalid data types

### Sample Test Data

**Test Case 1: Regular Employee**
- Name: John Doe
- Basic Salary: ₹25,000
- Absent Days: 2
- Late Entry Days: 5
- Overtime Days: 3

**Expected Results:**
- Daily Salary: ₹806.45 (for 31-day month)
- Absent Deduction: ₹1,612.90
- Late Entry Deduction: ₹806.45 (2 days after 3 free days)
- Overtime Addition: ₹1,209.68
- PF: ₹1,800.00 (12% of ₹15,000 max)
- ESI: ₹0.00 (not applicable since ₹25,000 > ₹21,000)
- Professional Tax: ₹130
- Net Salary: ₹20,952.83

## Error Handling

The application includes comprehensive error handling for:
- Invalid input data
- Server errors
- PDF generation issues
- Form validation errors

## Security Considerations

- Input validation on both client and server side
- Secure form handling
- Protection against common web vulnerabilities
- Safe PDF generation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

For issues and questions:
1. Check the error messages in the application
2. Review this README for common solutions
3. Check server logs for detailed error information

## Version History

- **v1.0.0**: Initial release with basic functionality
  - Salary calculation with all deductions
  - PDF pay slip generation
  - Modern responsive UI
  - Complete validation and error handling 