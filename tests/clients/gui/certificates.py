"""Create private, short-lived GUI fixture credentials; never install trust."""
from pathlib import Path
from datetime import datetime,timedelta,timezone
import hashlib,json,ipaddress,sys
from cryptography import x509
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID,ExtendedKeyUsageOID

root=Path(sys.argv[1]).resolve()
expected=Path('H:/IM-platform/.git/worktrees/IM-platform3/gui-runtime/tls-v2').resolve()
if root!=expected or root.exists():raise RuntimeError('New exact owned fixture directory required')
root.mkdir(parents=True)
now=datetime.now(timezone.utc);end=now+timedelta(hours=24)
ca_key=rsa.generate_private_key(public_exponent=65537,key_size=2048)
name=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'IM GUI owned fixture 20261004')])
ca=(x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(ca_key.public_key()).serial_number(x509.random_serial_number()).not_valid_before(now-timedelta(minutes=5)).not_valid_after(end).add_extension(x509.BasicConstraints(ca=True,path_length=0),True).add_extension(x509.KeyUsage(False,False,False,False,False,True,True,False,False),True).add_extension(x509.NameConstraints([x509.DNSName('localhost'),x509.IPAddress(ipaddress.ip_network('127.0.0.1/32'))],None),True).sign(ca_key,hashes.SHA256()))
key=rsa.generate_private_key(public_exponent=65537,key_size=2048)
server=(x509.CertificateBuilder().subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'localhost')])).issuer_name(name).public_key(key.public_key()).serial_number(x509.random_serial_number()).not_valid_before(now-timedelta(minutes=5)).not_valid_after(end).add_extension(x509.BasicConstraints(ca=False,path_length=None),True).add_extension(x509.SubjectAlternativeName([x509.DNSName('localhost'),x509.IPAddress(ipaddress.ip_address('127.0.0.1'))]),False).add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]),False).sign(ca_key,hashes.SHA256()))
for label,cert,k in [('ca',ca,ca_key),('server',server,key)]:
    (root/(label+'.pem')).write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    (root/(label+'.der')).write_bytes(cert.public_bytes(serialization.Encoding.DER))
    if label=='server':(root/(label+'.key')).write_bytes(k.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()))
public={'owner':'/root/gui_product_implementation','directory':str(root),'endpoint':'https://localhost:18443','notAfter':end.isoformat(),'caSHA256':ca.fingerprint(hashes.SHA256()).hex(),'caWindowsThumbprintSHA1':ca.fingerprint(hashes.SHA1()).hex(),'serverSHA256':server.fingerprint(hashes.SHA256()).hex()}
(root/'public.json').write_text(json.dumps(public,indent=2)+'\n')
print(json.dumps(public,indent=2))
