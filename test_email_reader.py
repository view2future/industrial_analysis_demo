#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Email Reader Test Script
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.email_reader import EmailReader


def test_email_connection():
    """测试邮箱连接和邮件读取功能"""
    print("📧 测试邮箱连接和邮件读取功能...")
    
    try:
        # 创建邮箱读取器实例
        reader = EmailReader()
        
        # 测试连接
        server = reader.connect()
        if server:
            print("✅ 邮箱连接成功")
            
            # 测试获取有URL的邮件
            emails_with_urls = reader.get_unread_emails_with_urls()
            
            print(f"✅ 找到 {len(emails_with_urls)} 封包含URL的邮件")
            
            for i, email_info in enumerate(emails_with_urls):
                print(f"\n邮件 {i+1}:")
                print(f"  标题: {email_info['subject'][:50]}...")
                print(f"  发件人: {email_info['sender']}")
                print(f"  时间: {email_info['timestamp']}")
                print(f"  URL数量: {len(email_info['urls'])}")
                for j, url in enumerate(email_info['urls']):
                    print(f"    {j+1}. {url}")
            
            # 如果没有找到邮件，尝试获取所有邮件中的URL
            if len(emails_with_urls) == 0:
                print("\n🔍 没有找到未读邮件，尝试获取所有邮件...")
                all_emails_with_urls = reader.get_all_emails_with_urls()
                print(f"✅ 在所有邮件中找到 {len(all_emails_with_urls)} 封包含URL的邮件")
                
                for i, email_info in enumerate(all_emails_with_urls):
                    print(f"\n邮件 {i+1}:")
                    print(f"  标题: {email_info['subject'][:50]}...")
                    print(f"  发件人: {email_info['sender']}")
                    print(f"  时间: {email_info['timestamp']}")
                    print(f"  URL数量: {len(email_info['urls'])}")
                    for j, url in enumerate(email_info['urls']):
                        print(f"    {j+1}. {url}")
            
            server.close()
            server.logout()
            print("\n✅ 邮箱测试完成")
            return True
        else:
            print("❌ 邮箱连接失败")
            return False
            
    except Exception as e:
        error_str = str(e)
        if 'Unsafe Login' in error_str or 'kefu@188.com' in error_str:
            print("❌ 163邮箱登录失败: 请检查是否启用了IMAP/SMTP服务，并使用授权码而非登录密码")
            print("   解决方法: 登录163邮箱网页版 -> 设置 -> POP3/SMTP/IMAP -> 开启IMAP服务 -> 生成授权码")
        print(f"❌ 邮箱测试失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False


if __name__ == "__main__":
    print("🧪 开始邮箱功能测试\n")
    success = test_email_connection()
    
    if success:
        print("\n🎉 邮箱功能测试成功！")
        print("系统可以正常连接到您的邮箱并读取包含URL的邮件。")
    else:
        print("\n❌ 邮箱功能测试失败！")
        print("请检查配置文件中的邮箱设置是否正确。")