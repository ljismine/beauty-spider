import os
import secrets
import base64
import json

def generate_secure_key(length=32):
    """生成指定长度的加密安全随机密钥"""
    return secrets.token_bytes(length)

def save_key_to_environment(key, env_var_name='AES_SECRET_KEY'):
    """将密钥保存到环境变量（仅当前进程有效）"""
    encoded_key = base64.b64encode(key).decode('utf-8')
    os.environ[env_var_name] = encoded_key
    print(f"密钥已保存到环境变量 {env_var_name}")
    print(f"密钥值: {encoded_key}")
    return encoded_key

def save_key_to_config_file(key, config_file='config/secret_config.json'):
    """将密钥保存到配置文件"""
    encoded_key = base64.b64encode(key).decode('utf-8')
    config_dir = os.path.dirname(config_file)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    config = {}
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    
    config['AES_SECRET_KEY'] = encoded_key
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)
    
    print(f"密钥已保存到配置文件: {config_file}")
    print(f"密钥值: {encoded_key}")
    return encoded_key

def update_aes_module(config_file='config/secret_config.json'):
    """更新aesEncodeAndDecode.py文件以从配置加载密钥"""
    aes_file = 'src/utils/aesEncodeAndDecode.py'
    
    # 读取现有文件内容
    with open(aes_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换硬编码的密钥和IV
    new_content = content.replace(
        "AESKEY = b'my wonderful day'",
        "import json\nimport os\nimport base64\n\n# 从配置文件或环境变量加载密钥\nconfig_file = 'config/secret_config.json'\nif os.path.exists(config_file):\n    with open(config_file, 'r', encoding='utf-8') as f:\n        config = json.load(f)\n    AESKEY = base64.b64decode(config.get('AES_SECRET_KEY', ''))\n    AESIV = base64.b64decode(config.get('AES_IV', ''))\nelse:\n    # 回退到环境变量\n    AESKEY = base64.b64decode(os.environ.get('AES_SECRET_KEY', ''))\n    AESIV = base64.b64decode(os.environ.get('AES_IV', ''))"
    )
    
    # 写入更新后的内容
    with open(aes_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"已更新 {aes_file} 文件以从配置加载密钥")

def main():
    print("=== 安全密钥生成工具 ===")
    
    # 生成密钥和IV
    key = generate_secure_key(32)  # 256位AES密钥
    iv = generate_secure_key(16)   # AES-CBC模式需要16字节IV
    
    print(f"生成的原始密钥 (32字节): {key}")
    print(f"生成的原始IV (16字节): {iv}")
    
    # 编码为base64以便存储
    encoded_key = base64.b64encode(key).decode('utf-8')
    encoded_iv = base64.b64encode(iv).decode('utf-8')
    
    print(f"Base64编码密钥: {encoded_key}")
    print(f"Base64编码IV: {encoded_iv}")
    
    # 保存密钥和IV到配置文件
    config_file = 'config/secret_config.json'
    config = {}
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    
    config['AES_SECRET_KEY'] = encoded_key
    config['AES_IV'] = encoded_iv
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)
    
    print(f"密钥和IV已保存到配置文件: {config_file}")
    
    # 更新aesEncodeAndDecode.py文件
    update_aes_module(config_file)
    
    print("\n=== 安全建议 ===")
    print("1. 请确保 config/secret_config.json 文件已添加到 .gitignore 中，避免提交到版本控制系统")
    print("2. 生产环境中，建议使用环境变量或专业的密钥管理服务存储密钥")
    print("3. 不要在代码中硬编码密钥，这会导致密钥泄露")
    print("4. 定期轮换密钥以提高安全性")

if __name__ == '__main__':
    main()