import uuid
import hashlib
import json
import os
import platform
from datetime import datetime
import base64
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
from pathlib import Path

class AuthManager:
    def __init__(self):
        # 在用户文档目录下创建配置目录
        self.app_dir = Path.home() / "AppData" / "Local" / "SeaRouteProcessor"
        self.app_dir.mkdir(parents=True, exist_ok=True)
        self.auth_file = self.app_dir / "auth.json"
        
        # 使用环境变量或配置文件管理密钥（示例中仍使用硬编码）
        self._secret_key = b"NWH@rDKYZzh!KEY!"
        self._salt = b"K@zzh@Zuo1890807!"
        self._code_prefix = "HD"
        
        print(f"配置目录: {self.app_dir}")
    
    def get_machine_code(self):
        """获取机器唯一标识（简化版）"""
        try:
            # 使用更稳定的系统信息
            system_info = platform.uname()
            windows_uuid = None
            
            # 获取Windows UUID
            try:
                with os.popen('wmic csproduct get uuid') as p:
                    windows_uuid = p.read().split('\n')[1].strip()
            except:
                pass
            
            # 组合关键信息
            components = [
                windows_uuid if windows_uuid else str(uuid.getnode()),  # 如果无法获取UUID，使用MAC地址
                system_info.node,  # 计算机名
                system_info.machine,  # 机器类型
                os.getenv('SYSTEMDRIVE', 'C:')  # 系统盘
            ]
            
            # 生成指纹
            fingerprint = ":".join(filter(None, components))
            machine_code = hashlib.sha256(fingerprint.encode()).hexdigest()
            
            # 格式化为6位一组
            return '-'.join([machine_code[i:i+6] for i in range(0, min(len(machine_code), 32), 6)])
        except Exception as e:
            print(f"获取机器码失败: {e}")
            # 使用MAC地址作为备用方案
            return hashlib.sha256(str(uuid.getnode()).encode()).hexdigest()[:32]
    
    def _encrypt_data(self, data):
        """加密数据"""
        try:
            iv = os.urandom(16)
            cipher = AES.new(self._secret_key, AES.MODE_CBC, iv)
            ct_bytes = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
            return base64.b64encode(iv + ct_bytes).decode('utf-8')
        except Exception as e:
            print(f"加密失败: {e}")
            return None
    
    def _decrypt_data(self, encrypted_data):
        """解密数据"""
        try:
            raw_data = base64.b64decode(encrypted_data)
            iv, ct_bytes = raw_data[:16], raw_data[16:]
            cipher = AES.new(self._secret_key, AES.MODE_CBC, iv)
            pt = unpad(cipher.decrypt(ct_bytes), AES.block_size)
            return pt.decode('utf-8')
        except Exception as e:
            print(f"解密失败: {e}")
            return None
    
    def verify_register_code(self, machine_code, register_code):
        """验证注册码"""
        try:
            parts = register_code.split('-')
            if len(parts) != 6:
                return False
            
            prefix, code_part1, signature, expire_timestamp, code_part2, encrypted_part = parts
            
            if prefix != self._code_prefix:
                return False
            
            # 验证签名
            signature_base = f"{machine_code[:8]}{self._salt.decode()}{self._secret_key.decode()}"
            if signature != hashlib.sha256(signature_base.encode()).hexdigest()[:8]:
                return False
            
            # 验证注册码
            mixed_info = f"{machine_code}:{expire_timestamp}:{self._salt.decode()}:{self._secret_key.decode()}"
            if code_part1 + code_part2 != hashlib.sha256(mixed_info.encode()).hexdigest():
                return False
            
            # 验证过期时间
            try:
                if datetime.now() > datetime.fromtimestamp(int(expire_timestamp)):
                    return False
            except ValueError:
                return False
            
            return True
        except Exception as e:
            print(f"验证注册码失败: {e}")
            return False
    
    def save_auth_info(self, machine_code, register_code):
        """保存认证信息"""
        try:
            auth_data = {
                "machine_code": machine_code,
                "register_code": register_code,
                "register_time": datetime.now().isoformat(),
                "checksum": hashlib.sha256((machine_code + register_code).encode()).hexdigest()
            }
            
            # 加密并保存数据
            encrypted_data = self._encrypt_data(json.dumps(auth_data))
            if not encrypted_data:
                return False
            
            # 使用临时文件保存，成功后再替换
            temp_file = self.auth_file.with_suffix('.tmp')
            try:
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(encrypted_data)
                temp_file.replace(self.auth_file)
                return True
            except Exception as e:
                print(f"保存认证信息失败: {e}")
                if temp_file.exists():
                    temp_file.unlink()
                return False
        except Exception as e:
            print(f"准备认证信息失败: {e}")
            return False
    
    def load_auth_info(self):
        """加载认证信息"""
        try:
            if not self.auth_file.exists():
                return None
            
            with open(self.auth_file, 'r', encoding='utf-8') as f:
                encrypted_data = f.read()
            
            decrypted_data = self._decrypt_data(encrypted_data)
            if not decrypted_data:
                return None
            
            return json.loads(decrypted_data)
        except Exception as e:
            print(f"加载认证信息失败: {e}")
            return None
    
    def is_registered(self):
        """检查是否已注册"""
        try:
            auth_info = self.load_auth_info()
            if not auth_info:
                return False
            
            # 验证数据完整性
            stored_checksum = auth_info.get("checksum")
            if not stored_checksum:
                return False
            
            calculated_checksum = hashlib.sha256(
                (auth_info["machine_code"] + auth_info["register_code"]).encode()
            ).hexdigest()
            
            if stored_checksum != calculated_checksum:
                print("注册数据完整性验证失败")
                return False
            
            # 验证注册码
            return self.verify_register_code(
                auth_info["machine_code"],
                auth_info["register_code"]
            )
        except Exception as e:
            print(f"验证注册状态失败: {e}")
            return False
    
    def register(self, register_code):
        """注册软件"""
        try:
            machine_code = self.get_machine_code()
            print(f"当前机器码: {machine_code}")
            
            if not self.verify_register_code(machine_code, register_code):
                print("注册码验证失败")
                return False
            
            if not self.save_auth_info(machine_code, register_code):
                print("保存授权信息失败")
                return False
            
            print("注册成功")
            return True
        except Exception as e:
            print(f"注册过程失败: {e}")
            return False
    
    def unregister(self):
        """注销软件"""
        try:
            if self.auth_file.exists():
                self.auth_file.unlink()
            return True
        except Exception as e:
            print(f"注销失败: {e}")
            return False