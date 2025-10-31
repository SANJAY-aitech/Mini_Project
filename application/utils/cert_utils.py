from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics import renderPDF
import pdfplumber
import os
from datetime import datetime
import re

def generate_certificate(output_path, uid, candidate_name, course_name, org_name, institute_logo_path=None, format_type="PDF"):
    """
    Generate a professional certificate with enhanced design
    """

    doc = SimpleDocTemplate(output_path, pagesize=A4, 
                          topMargin=1*inch, bottomMargin=1*inch,
                          leftMargin=1*inch, rightMargin=1*inch)
    
    elements = []
    
    
    if institute_logo_path and os.path.exists(institute_logo_path):
        try:
            logo = Image(institute_logo_path, width=120, height=120)
            elements.append(logo)
            elements.append(Spacer(1, 0.2*inch))
        except:
            pass  # Skip logo if there's an error
    
    # Institute name with enhanced styling
    institute_style = ParagraphStyle(
        "InstituteStyle",
        parent=getSampleStyleSheet()["Title"],
        fontName="Helvetica-Bold",
        fontSize=16,
        textColor=colors.darkblue,
        spaceAfter=0.15*inch,
        alignment=1  # Center alignment
    )
    institute = Paragraph(f"<b>{org_name}</b>", institute_style)
    elements.extend([institute, Spacer(1, 0.2*inch)])
    
    # Certificate title with decorative styling
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=getSampleStyleSheet()["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        textColor=colors.darkred,
        spaceAfter=0.2*inch,
        alignment=1
    )
    title = Paragraph("CERTIFICATE OF COMPLETION", title_style)
    elements.extend([title, Spacer(1, 0.3*inch)])
    
    # Certificate body with professional formatting
    body_style = ParagraphStyle(
        "BodyStyle",
        parent=getSampleStyleSheet()["BodyText"],
        fontSize=13,
        leading=18,
        alignment=1,
        spaceAfter=0.1*inch
    )
    
    body_text = f"""
    This is to certify that<br/><br/>
    <font color='darkblue' size='20'><b>{candidate_name}</b></font><br/><br/>
    Student ID: <font color='darkred'><b>{uid}</b></font><br/><br/>
    has successfully completed the course<br/><br/>
    <font color='darkgreen' size='18'><b>"{course_name}"</b></font><br/><br/>
    and is hereby awarded this certificate of completion.
    """
    
    body = Paragraph(body_text, body_style)
    elements.extend([body, Spacer(1, 0.15*inch)])
    
    # Add date and signature section
    date_style = ParagraphStyle(
        "DateStyle",
        parent=getSampleStyleSheet()["BodyText"],
        fontSize=10,
        alignment=1
    )
    
    current_date = datetime.now().strftime("%B %d, %Y")
    date_text = f"Date of Issue: {current_date}"
    date_para = Paragraph(date_text, date_style)
    elements.extend([date_para, Spacer(1, 0.08*inch)])
    
    # Signature section
    signature_table_data = [
        ["", "", ""],
        ["_________________", "", "_________________"],
        ["Registrar Signature", "", "Dean Signature"]
    ]
    
    signature_table = Table(signature_table_data, colWidths=[2*inch, 1*inch, 2*inch])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, 1), 12),
    ]))
    
    elements.append(signature_table)
    elements.append(Spacer(1, 0.08*inch))
    
    # Add certificate ID at the bottom
    cert_id_style = ParagraphStyle(
        "CertIdStyle",
        parent=getSampleStyleSheet()["BodyText"],
        fontSize=8,
        textColor=colors.grey,
        alignment=1
    )
    
    cert_id_text = f"Certificate ID: {uid}_{candidate_name.replace(' ', '_')}_{current_date.replace(' ', '_')}"
    cert_id_para = Paragraph(cert_id_text, cert_id_style)
    elements.append(cert_id_para)
    
    # Build the PDF document
    doc.build(elements)
    print(f"Certificate generated and saved at: {output_path}")


def generate_bulk_certificates(certificates_data, output_dir, org_name, institute_logo_path=None):
    """
    Generate multiple certificates from a list of student data
    certificates_data: List of dictionaries with keys: uid, candidate_name, course_name
    """
    generated_certificates = []
    
    for i, cert_data in enumerate(certificates_data):
        try:
            uid = cert_data.get('uid', f'STU{i+1:03d}')
            candidate_name = cert_data.get('candidate_name', 'Unknown Student')
            course_name = cert_data.get('course_name', 'General Course')
            
            output_path = os.path.join(output_dir, f"certificate_{uid}_{candidate_name.replace(' ', '_')}.pdf")
            
            generate_certificate(output_path, uid, candidate_name, course_name, org_name, institute_logo_path)
            
            generated_certificates.append({
                'uid': uid,
                'candidate_name': candidate_name,
                'course_name': course_name,
                'file_path': output_path,
                'status': 'success'
            })
            
        except Exception as e:
            generated_certificates.append({
                'uid': cert_data.get('uid', f'STU{i+1:03d}'),
                'candidate_name': cert_data.get('candidate_name', 'Unknown Student'),
                'course_name': cert_data.get('course_name', 'General Course'),
                'file_path': None,
                'status': 'error',
                'error': str(e)
            })
    
    return generated_certificates


def validate_certificate_data(uid, candidate_name, course_name, org_name):
    """
    Validate certificate input data
    """
    errors = []
    
    if not uid or len(uid.strip()) == 0:
        errors.append("UID is required")
    
    if not candidate_name or len(candidate_name.strip()) == 0:
        errors.append("Candidate name is required")
    
    if not course_name or len(course_name.strip()) == 0:
        errors.append("Course name is required")
    
    if not org_name or len(org_name.strip()) == 0:
        errors.append("Organization name is required")
    
    # Additional validations
    if len(uid) > 50:
        errors.append("UID is too long (max 50 characters)")
    
    if len(candidate_name) > 100:
        errors.append("Candidate name is too long (max 100 characters)")
    
    if len(course_name) > 200:
        errors.append("Course name is too long (max 200 characters)")
    
    return errors


def extract_certificate(pdf_path):
    """
    Extract certificate data from PDF file
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Extract text from each page
            text = ""
            for page in pdf.pages:
                text += page.extract_text()
            
            if not text:
                return None, None, None, None, None
            
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            
            if len(lines) < 4:
                return None, None, None, None, None
                
            # Initialize defaults
            org_name = lines[0] if lines else "Unknown Organization"
            candidate_name = None
            uid = None
            course_name = None

            # helper to get next non-empty line
            def next_nonempty(idx):
                for j in range(idx + 1, len(lines)):
                    if lines[j].strip():
                        return lines[j].strip()
                return ""

            # Search lines for UID, candidate name, and course
            for idx, line in enumerate(lines):
                l = line
                if "Student ID:" in l:
                    uid = l.split("Student ID:")[-1].strip()

                if "This is to certify that" in l and idx + 1 < len(lines):
                    candidate_name = next_nonempty(idx)

                if "has successfully completed" in l or "completed the course" in l:
                    # Try to capture quoted course on same line
                    m = re.search(r'"([^"]+)"', l)
                    if m:
                        course_name = m.group(1).strip()
                    else:
                        # fallback to next non-empty line
                        nxt = next_nonempty(idx)
                        if nxt:
                            course_name = nxt.strip().strip('"')

            # Final fallbacks
            if not candidate_name:
                candidate_name = "Unknown Student"
            if not uid:
                uid = "Unknown UID"
            if not course_name:
                # try to find any quoted substring in full text
                mq = re.search(r'"([^"]{2,200})"', text)
                if mq:
                    course_name = mq.group(1).strip()
                else:
                    course_name = ""

            # Try to detect printed certificate hash (SHA256) in the text
            certificate_hash = None
            # Search for a labeled hash first
            for line in lines:
                if "Certificate Hash ID:" in line or "Certificate ID:" in line:
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        possible = parts[1].strip()
                        m = re.search(r"[a-fA-F0-9]{64}", possible)
                        if m:
                            certificate_hash = m.group(0)
                            break
            # If not found, search any 64-hex substring in the document
            if not certificate_hash:
                joined = " ".join(lines)
                m = re.search(r"\b[a-fA-F0-9]{64}\b", joined)
                if m:
                    certificate_hash = m.group(0)

            return uid, candidate_name, course_name, org_name, certificate_hash
            
    except Exception as e:
        print(f"Error extracting certificate data: {str(e)}")
        return None, None, None, None, None


def get_certificate_template_info():
    """
    Get information about certificate templates
    """
    return {
        "default_template": {
            "name": "Standard Certificate",
            "description": "Professional certificate with decorative border",
            "features": ["Logo support", "Decorative border", "Signature section", "Date stamp"]
        },
        "available_formats": ["PDF"],
        "supported_logo_formats": ["JPG", "PNG", "JPEG"],
        "max_dimensions": {
            "width": "8.5 inches",
            "height": "11 inches"
        }
    }
    