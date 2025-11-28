#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alternative 163 Email Connection Test
"""

import sys
import os
import json
import imaplib
import time

def test_163_alternative_connection():
    """Test 163 email connection with specific settings"""
    print("📧 测试163邮箱连接 (替代方法)...")
    
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        email_config = config.get('email', {})
        server = email_config.get('server', 'imap.163.com')
        port = email_config.get('port', 993)
        username = email_config.get('username')
        password = email_config.get('password')
        
        if not all([server, username, password]):
            print("❌ 配置信息不完整")
            return False
        
        print(f"连接到 {server}:{port} 使用账户 {username}")
        
        # Create IMAP connection with specific options for 163
        mail = imaplib.IMAP4_SSL(server, port)
        
        # Login
        login_result = mail.login(username, password)
        print(f"✅ 登录成功: {login_result[0]}")
        
        # List available folders to see what's available
        print("📋 获取可用文件夹列表...")
        status, folders = mail.list()
        if status == 'OK':
            print("可用文件夹:")
            for folder in folders:
                print(f"  {folder.decode()}")
        else:
            print("❌ 获取文件夹列表失败")
        
        # Try a few different folder names that 163 might use
        possible_folders = ['INBOX', 'inbox', '"INBOX"', '"收件箱"', '收件箱']
        selected = False
        
        for folder in possible_folders:
            print(f"尝试选择文件夹: {folder}")
            try:
                select_result = mail.select(folder)
                if select_result[0] == 'OK':
                    print(f"✅ 成功选择文件夹 {folder}")
                    selected = True
                    break
                else:
                    print(f"   选择失败: {select_result}")
            except Exception as e:
                print(f"   选择失败异常: {e}")
        
        if not selected:
            print("❌ 无法选择任何文件夹")
            mail.logout()
            return False
        
        # Test search functionality
        print("🔍 测试搜索邮件...")
        try:
            # Search for unread emails
            status, messages = mail.search(None, 'UNSEEN')
            if status == 'OK':
                email_ids = messages[0].split()
                print(f"✅ 成功搜索到 {len(email_ids)} 封未读邮件")
                
                # Try to fetch first email if any exist
                if email_ids:
                    print(f"尝试获取第一封邮件信息...")
                    status, msg_data = mail.fetch(email_ids[0], '(RFC822.HEADER)')
                    if status == 'OK':
                        print("✅ 成功获取邮件头部信息")
                        # Show some basic info about the first email
                        for response_part in msg_data:
                            if isinstance(response_part, tuple):
                                print("   获取到邮件头部数据")
                                break
                    else:
                        print("❌ 获取邮件信息失败")
            else:
                print(f"❌ 搜索邮件失败: {status}")
        except Exception as e:
            print(f"❌ 搜索邮件时出错: {e}")
        
        # Close and logout
        try:
            mail.close()
        except:
            pass  # May fail if folder wasn't properly selected
        mail.logout()
        print("✅ 连接测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        if 'Unsafe Login' in str(e) or 'kefu@188.com' in str(e):
            print("   这是163邮箱的安全限制问题，需要进一步配置")
        return False


def main():
    print("🔍 163邮箱连接诊断工具 (替代方法)")
    print("=" * 50)
    
    success = test_163_alternative_connection()
    
    if success:
        print("\n✅ 邮箱连接测试成功！")
        print("您的系统现在应该能够读取邮件了。")
    else:
        print("\n❌ 邮箱连接测试失败")
        print("\n建议解决方案:")
        print("1. 登录163邮箱网页版，检查是否需要进行额外的安全验证")
        print("2. 尝试在不同的网络环境下运行（有些IP被限制）")
        print("3. 重新生成授权码并确认使用的是最新生成的代码")
        print("4. 确认授权码是为IMAP服务生成的")
        print("5. 等待一段时间（5-10分钟）后再试，有时需要服务器同步")
    
    return success


if __name__ == "__main__":
    main()