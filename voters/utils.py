import re


def format_phone_number(phone_number):
    """
    Formats a phone number by removing any non-digit characters
    and ensuring it's exactly 10 digits.
    """
    # Remove any non-digit characters
    cleaned_number = re.sub(r'\D', '', str(phone_number))

    # Ensure the number is exactly 10 digits
    if len(cleaned_number) != 10:
        raise ValueError('Phone number must be exactly 10 digits')

    return cleaned_number