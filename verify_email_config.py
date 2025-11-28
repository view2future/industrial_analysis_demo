#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Email Configuration Verification Script
"""

import sys
import os
import json
import imaplib
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def verify_config():
    """Verify email configuration in config.json"""
    print("🔍 检查邮箱配置文件...")
    
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        email_config = config.get('email', {})
        
        if not email_config:
            print("❌ 未找到邮箱配置信息")
            return False
        
        print(f"✅ 邮箱服务器: {email_config.get('server', '未设置')}")
        print(f"✅ 用户名: {email_config.get('username', '未设置')}")
        print(f"✅ 端口: {email_config.get('port', '未设置')}")
        print(f"✅ 密码长度: {len(email_config.get('password', ''))} 位")
        print(f"✅ 文件夹: {email_config.get('folder', '未设置')}")
        
        # Check if password looks like an authorization code
        password = email_config.get('password', '')
        if len(password) == 0:
            print("❌ 密码为空")
            return False
        elif len(password) < 8:
            print("⚠️  密码长度较短，可能不是授权码")
        else:
            print("✅ 密码长度正常")
        
        return True
        
    except FileNotFoundError:
        print("❌ config.json 文件不存在")
        return False
    except json.JSONDecodeError:
        print("❌ config.json 文件格式错误")
        return False
    except Exception as e:
        print(f"❌ 配置检查失败: {e}")
        return False


def test_imap_connection():
    """Test direct IMAP connection"""
    print("\n🔌 测试IMAP连接...")
    
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        email_config = config.get('email', {})
        server = email_config.get('server', 'imap.163.com')
        port = email_config.get('port', 993)
        username = email_config.get('username')
        password = email_config.get('password')
        folder = email_config.get('folder', 'INBOX')
        
        if not all([server, username, password]):
            print("❌ 配置信息不完整")
            return False
        
        # Create IMAP connection
        print(f"尝试连接到 {server}:{port}...")
        mail = imaplib.IMAP4_SSL(server, port)
        
        # Try to login
        print(f"尝试登录用户 {username}...")
        login_result = mail.login(username, password)
        print(f"✅ 登录成功: {login_result}")
        
        # Try to select folder
        print(f"尝试选择文件夹 {folder}...")
        select_result = mail.select(folder)
        print(f"✅ 文件夹选择结果: {select_result}")
        
        # Test search for emails
        print("测试搜索邮件...")
        status, messages = mail.search(None, 'UNSEEN')
        if status == 'OK':
            email_ids = messages[0].split()
            print(f"✅ 找到 {len(email_ids)} 封未读邮件")
            
            # Try to fetch first email if exists
            if email_ids:
                status, msg_data = mail.fetch(email_ids[0], '(RFC822.HEADER)')
                if status == 'OK':
                    print("✅ 成功获取邮件头部信息")
                else:
                    print("❌ 获取邮件信息失败")
        else:
            print(f"❌ 搜索邮件失败: {status}")
        
        # Clean up
        mail.close()
        mail.logout()
        print("✅ 连接测试完成，已安全退出")
        return True
        
    except imaplib.IMAP4.error as e:
        if 'Unsafe Login' in str(e) or 'kefu@188.com' in str(e):
            print("❌ 163邮箱登录失败: 请检查是否启用了IMAP/SMTP服务，并使用授权码而非登录密码")
            print("   解决方法: 登录163邮箱网页版 -> 设置 -> POP3/SMTP/IMAP -> 开启IMAP服务 -> 生成授权码")
        else:
            print(f"❌ IMAP连接失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        return False


def main():
    print("📧 163邮箱配置验证工具")
    print("=" * 50)
    
    config_ok = verify_config()
    if config_ok:
        connection_ok = test_imap_connection()
        
        if connection_ok:
            print("\n✅ 邮箱配置验证成功！")
            print("系统可以正常连接到您的邮箱。")
            return True
        else:
            print("\n❌ 邮箱连接测试失败！")
            print("请按以下步骤检查：")
            print("1. 登录163邮箱网页版")
            print("2. 进入 设置 -> POP3/SMTP/IMAP")
            print("3. 确保IMAP服务已开启")
            print("4. 重新生成授权码")
            print("5. 用新授权码更新config.json文件")
            return False
    else:
        print("\n❌ 配置检查失败！")
        print("请检查config.json文件中的邮箱配置")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)