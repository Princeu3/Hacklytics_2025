import re
from PyPDF2 import PdfReader

def extract_acroform_fields(pdf_path: str) -> dict:
    """
    Extracts AcroForm fields from the PDF and returns a dictionary with normalized keys.
    """
    reader = PdfReader(pdf_path)
    acroform = reader.trailer["/Root"].get("/AcroForm")
    fields_dict = {}
    if acroform:
        acroform = acroform.get_object()  # Resolve the indirect object
        if "/Fields" in acroform:
            for f in acroform["/Fields"]:
                field_obj = f.get_object()
                field_name = field_obj.get("/T")
                field_value = field_obj.get("/V")
                if field_name and field_value:
                    # Normalize key: strip whitespace and lowercase
                    key = field_name.strip().lower()
                    value = field_value.strip() if isinstance(field_value, str) else field_value
                    fields_dict[key] = value
    return fields_dict

def is_valid_mobile(number: str) -> bool:
    """Check if a number (after removing non-digits) has 10 digits."""
    digits = re.sub(r'\D', '', number)
    return len(digits) == 10

def main():
    pdf_path = "FORM-Dwelling-Property-ENG-9.2022.pdf"  # Update with your PDF file path
    fields = extract_acroform_fields(pdf_path)
    
    # Debug print: show all extracted form field keys and values
    
    
    # Extract required fields using the known field names.
    insured_name = fields.get("named insureds full namerow1") or fields.get("full namerow1")
    
    physical_address = fields.get("physical address of the insured propertyrow1")
    if not physical_address:
        physical_address = fields.get("postal addressrow1")
    
    # For mobile number, prefer the value from "text1" (if valid) otherwise use "fill_24"
    mobile_candidate = fields.get("text1")
    if mobile_candidate and is_valid_mobile(mobile_candidate):
        mobile_number = mobile_candidate
    else:
        mobile_number = fields.get("fill_24")
    
    email = fields.get("email")
    
    type_of_loss = fields.get("undefined_4")
    
    loss_description = fields.get("description of loss and damagesrow1")
    
    # Extract damages from numeric field keys ("1", "2", "3", etc.)
    damages = []
    for key in fields:
        if re.fullmatch(r"\d+", key):
            try:
                num = int(key)
                damages.append((num, fields[key]))
            except ValueError:
                pass
    damages.sort(key=lambda x: x[0])
    damages_list = [re.sub(r"^\d+\s*", "", d[1].strip()) for d in damages if d[1] and d[1].strip()]
    
    # --- Date of Loss ---
    # Instead of using page 4 fields, use page 3 fields: "undefined_5", "undefined_6", and "undefined_7"
    month = fields.get("undefined_5")
    day = fields.get("undefined_6")
    year = fields.get("undefined_7")
    date_of_loss = None
    if month and day and year:
        date_of_loss = f"{month.strip()}/{day.strip()}/{year.strip()}"
    
    # Print the extracted information in the desired header: value format.
    print("\nExtracted Information:")
    print("======================")
    print(f"insured full name: {insured_name}")
    print(f"physical address: {physical_address}")
    print(f"mobile number: {mobile_number}")
    print(f"email: {email}")
    print(f"type of loss: {type_of_loss}")
    print(f"description of loss and damages: {loss_description}")
    print("list of damages:")
    for i, damage in enumerate(damages_list, 1):
        print(f"{i}. {damage}")
    print(f"date of loss: {date_of_loss}")

if __name__ == "__main__":
    main()
