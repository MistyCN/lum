
import os
import ssl
from datetime import datetime, timedelta

def generate_self_signed_cert():
    """生成自签名SSL证书"""
    # 创建证书目录
    cert_dir = os.path.join('certs')
    os.makedirs(cert_dir, exist_ok=True)

    cert_file = os.path.join(cert_dir, 'cert.pem')
    key_file = os.path.join(cert_dir, 'key.pem')

    # 检查证书是否已存在
    if os.path.exists(cert_file) and os.path.exists(key_file):
        print("证书文件已存在，跳过生成")
        return cert_file, key_file

    # 生成私钥
    from OpenSSL import crypto
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 2048)

    # 创建证书
    cert = crypto.X509()
    cert.get_subject().CN = "Luminest"
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(365 * 24 * 60 * 60)  # 1年有效期
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha256')

    # 写入证书文件
    with open(cert_file, "wt") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode('utf-8'))

    # 写入私钥文件
    with open(key_file, "wt") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k).decode('utf-8'))

    print(f"已生成自签名SSL证书：")
    print(f"证书文件: {cert_file}")
    print(f"私钥文件: {key_file}")

    return cert_file, key_file

if __name__ == "__main__":
    generate_self_signed_cert()
