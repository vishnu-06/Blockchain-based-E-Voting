import pyotp
import pyqrcode
import os
from pyqrcode import QRCode

def create_user(id, user_name):

    totp_str = pyotp.random_base32()
    totp = pyotp.totp.TOTP(totp_str)

    s = totp.provisioning_uri(name=user_name, issuer_name='Blockchain Based Voting')

    # Generate QR code
    url = pyqrcode.create(s)
    original_dir = os.getcwd()
    os.chdir("./source/content/media")
    # Create and save the png file naming "myqr.png"
    url.png("" + user_name + '_qr.png', scale = 6)
    os.chdir(original_dir)
    
    return totp_str
