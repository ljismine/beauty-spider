from Crypto.Cipher import AES
import base64
import os
from Crypto.Cipher import AES
import json

def load_secret_keys():
    """从配置文件或环境变量加载密钥和IV"""
    config_file = 'config/secret_config.json'
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            key = base64.b64decode(config.get('AES_SECRET_KEY', ''))
            iv = base64.b64decode(config.get('AES_IV', ''))
            if len(key) not in [16, 24, 32] or len(iv) != 16:
                raise ValueError("密钥或IV长度不正确")
            return key, iv
        except Exception as e:
            print(f"从配置文件加载密钥失败: {e}")
    
    # 回退到环境变量
    try:
        key = base64.b64decode(os.environ.get('AES_SECRET_KEY', ''))
        iv = base64.b64decode(os.environ.get('AES_IV', ''))
        if len(key) not in [16, 24, 32] or len(iv) != 16:
            raise ValueError("环境变量中的密钥或IV长度不正确")
        return key, iv
    except Exception as e:
        print(f"从环境变量加载密钥失败: {e}")
        # 开发环境下的默认值，生产环境中应移除
        return b'default_development_key_12345678', b'default_iv_12345678'

def aes_decode(data :str):
    AESKEY, AESIV = load_secret_keys()
    decrypted_data = ''
    try:
        aes = AES.new(AESKEY, AES.MODE_CBC, AESIV)
        decrypted_data = aes.decrypt(base64.decodebytes(bytes(data, encoding = 'utf8'))).decode('utf8')
        decrypted_data = decrypted_data.encode('utf8')[:-ord(decrypted_data[-1])].decode('utf8')
    except Exception as e:
        print(f"解密失败: {e}")
    return decrypted_data

def aes_encode(data :str):
    AESKEY, AESIV = load_secret_keys()
    resdata = bytes(data, encoding = 'utf8')
    # 填充数据使其成为16的倍数
    padding_length = 16 - len(resdata) % 16
    resdata += padding_length * chr(padding_length).encode('utf8')
    aes = AES.new(AESKEY, AES.MODE_CBC, AESIV)
    res = str(base64.encodebytes(aes.encrypt(resdata)), encoding = 'utf8').replace('\n', '')
    return res

def parseSecretFile(filePath :str):
    backupfpath = filePath + '.backup'
    try:
        # 按照file命令结果，尝试以ASCII编码读取文件
        with open(filePath, 'r', encoding='ascii') as scrt:
            read_data = scrt.read()
            decrypt = aes_decode(read_data)
    except UnicodeDecodeError:
        # 如果ASCII解码失败，尝试UTF-8并忽略错误字符
        with open(filePath, 'r', encoding='utf8', errors='ignore') as scrt:
            read_data = scrt.read()
            decrypt = aes_decode(read_data)
    except Exception as e:
        print(f"读取密钥文件失败: {e}")
        return None
    
    # 解密成功后写入备份文件
    with open(backupfpath, 'w', encoding = 'utf8') as backup:
        backup.write(decrypt)
        return backupfpath
        
def buildSecretFile(backupfpath :str):
    filePath = backupfpath.rstrip('.backup')
    try:
        # 先读取备份文件内容
        with open(backupfpath, 'r', encoding = 'utf8') as backup:
            filecontent = backup.readlines()
            totalstr = ''
            for line in filecontent:
                totalstr += line
            encrypt = aes_encode(totalstr)
        
        # 写入加密文件
        with open(filePath, 'w', encoding = 'utf8') as scrt:
            scrt.write(encrypt)
        
        # 确保所有文件都已关闭后再删除备份文件
        import time
        time.sleep(0.5)
        os.remove(backupfpath)
        return filePath
    except Exception as e:
        print(f"构建密钥文件错误: {e}")
        return None

# 从备份文件构建密钥文件
# buildSecretFile('keypass.backup')
# 解析生成的密钥文件
# parseSecretFile('keypass')


# 密钥文件keypass.backup 内容示例
# {'savepath': None, 'maxcount': 30}
