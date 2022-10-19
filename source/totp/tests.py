import pyotp
import pyqrcode
import os
from pyqrcode import QRCode
totp_str = "UOM6AVBKNHDCIMUM3JBKQEZ425OMNO4Z"
totp = pyotp.totp.TOTP(totp_str)
print(totp.now())
#s = totp.provisioning_uri(name=user_name, issuer_name='App')

# Generate QR code
#url = pyqrcode.create(s)

    # os.chdir("./content/media/")
    # # Create and save the png file naming "myqr.png"
    # url.png(user_name + '_qr.png', scale = 6)
