import pyotp

def validate_otp(otp, totp_id):
    totp = pyotp.TOTP(totp_id)
    totp_verify = totp.verify(otp)
    return totp_verify