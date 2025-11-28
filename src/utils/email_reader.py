#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Email Reader Module
Read emails from configured mailbox and extract URLs for policy analysis
"""

import imaplib
import email
import re
import logging
import json
from typing import List, Dict, Optional
from pathlib import Path


logger = logging.getLogger(__name__)


class EmailReader:
    """
    Email reader to fetch URLs from configured mailbox
    """

    def __init__(self, config_path: str = 'config.json'):
        """Initialize the email reader with configuration"""
        self.config_path = config_path
        self.config = self._load_config()
        
        # Get email configuration
        self.email_config = self.config.get('email', {})
        self.server = self.email_config.get('server', 'imap.gmail.com')
        self.port = int(self.email_config.get('port', 993))
        self.username = self.email_config.get('username', '')
        self.password = self.email_config.get('password', '')
        self.folder = self.email_config.get('folder', 'INBOX')

    def _load_config(self) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {self.config_path}, using default config")
            return {
                "email": {
                    "server": "imap.gmail.com",
                    "port": 993,
                    "username": "PLACEHOLDER_EMAIL",  # Will be replaced by user
                    "password": "PLACEHOLDER_PASSWORD",  # Will be replaced by user
                    "folder": "INBOX"
                }
            }
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {
                "email": {
                    "server": "imap.gmail.com",
                    "port": 993,
                    "username": "PLACEHOLDER_EMAIL",
                    "password": "PLACEHOLDER_PASSWORD",
                    "folder": "INBOX"
                }
            }

    def connect(self) -> Optional[imaplib.IMAP4_SSL]:
        """Connect to the email server"""
        try:
            # Connect to the server
            server = imaplib.IMAP4_SSL(self.server, self.port)

            # Login
            server.login(self.username, self.password)

            # Select the folder (this changes the state from AUTH to SELECTED)
            status, message = server.select(self.folder)
            if status != 'OK':
                # Handle specific error for 163 email
                error_str = str(message)
                if 'Unsafe Login' in error_str or 'kefu@188.com' in error_str:
                    logger.error("❌ 163邮箱登录失败: 请检查是否启用了IMAP/SMTP服务，并使用授权码而非登录密码")
                    logger.error("   解决方法: 登录163邮箱网页版 -> 设置 -> POP3/SMTP/IMAP -> 开启IMAP服务 -> 生成授权码")
                logger.error(f"❌ Failed to select folder {self.folder}: {message}")
                server.logout()
                return None

            logger.info(f"✅ Successfully connected to email server: {self.server}, folder: {self.folder}")
            return server

        except Exception as e:
            # Check if this is likely a 163 email configuration issue
            error_str = str(e)
            if 'Unsafe Login' in error_str or 'kefu@188.com' in error_str:
                logger.error("❌ 163邮箱登录失败: 请检查是否启用了IMAP/SMTP服务，并使用授权码而非登录密码")
                logger.error("   解决方法: 登录163邮箱网页版 -> 设置 -> POP3/SMTP/IMAP -> 开启IMAP服务 -> 生成授权码")
            logger.error(f"❌ Failed to connect to email server: {e}")
            return None

    def extract_urls_from_text(self, text: str) -> List[str]:
        """Extract URLs from text content"""
        # Regular expression to match URLs
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        
        # Remove duplicates while preserving order
        unique_urls = []
        for url in urls:
            if url not in unique_urls:
                unique_urls.append(url)
                
        return unique_urls

    def extract_urls_from_html(self, html_content: str) -> List[str]:
        """Extract URLs from HTML content"""
        # Simple regex for href attributes in HTML
        href_pattern = r'href\s*=\s*["\']([^"\']+)["\']'
        src_pattern = r'src\s*=\s*["\']([^"\']+)["\']'
        
        href_urls = re.findall(href_pattern, html_content)
        src_urls = re.findall(src_pattern, html_content)
        
        all_urls = href_urls + src_urls
        
        # Remove duplicates while preserving order
        unique_urls = []
        for url in all_urls:
            if url not in unique_urls:
                unique_urls.append(url)
                
        return unique_urls

    def get_unread_emails_with_urls(self) -> List[Dict]:
        """Get unread emails that contain URLs"""
        server = self.connect()
        if not server:
            return []

        try:
            # Search for unread emails
            status, messages = server.search(None, 'UNSEEN')
            if status != 'OK':
                logger.error("Failed to search for unread emails")
                return []

            email_ids = messages[0].split()
            emails_with_urls = []

            for email_id in email_ids:
                try:
                    # Fetch the email
                    status, msg_data = server.fetch(email_id, '(RFC822)')
                    if status != 'OK':
                        continue

                    # Parse the email
                    msg = email.message_from_bytes(msg_data[0][1])

                    # Extract subject and sender
                    subject = msg.get('Subject', '')
                    sender = msg.get('From', '')

                    # Get email body
                    email_body = ''
                    urls = []

                    if msg.is_multipart():
                        # Handle multipart emails
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))

                            # Skip attachments
                            if "attachment" in content_disposition:
                                continue

                            # Extract text/html content
                            if content_type == "text/plain" or content_type == "text/html":
                                body = part.get_payload(decode=True)
                                if body:
                                    try:
                                        body_text = body.decode('utf-8')
                                        email_body += body_text

                                        # Extract URLs based on content type
                                        if content_type == "text/plain":
                                            urls.extend(self.extract_urls_from_text(body_text))
                                        elif content_type == "text/html":
                                            urls.extend(self.extract_urls_from_html(body_text))
                                    except UnicodeDecodeError:
                                        # Try with different encoding
                                        try:
                                            body_text = body.decode('gbk')
                                            email_body += body_text

                                            if content_type == "text/plain":
                                                urls.extend(self.extract_urls_from_text(body_text))
                                            elif content_type == "text/html":
                                                urls.extend(self.extract_urls_from_html(body_text))
                                        except:
                                            logger.warning(f"Failed to decode email part for email ID: {email_id}")
                    else:
                        # Handle single part email
                        body = msg.get_payload(decode=True)
                        if body:
                            try:
                                body_text = body.decode('utf-8')
                                email_body = body_text

                                content_type = msg.get_content_type()
                                if content_type == "text/plain":
                                    urls = self.extract_urls_from_text(body_text)
                                elif content_type == "text/html":
                                    urls = self.extract_urls_from_html(body_text)
                            except UnicodeDecodeError:
                                # Try with different encoding
                                try:
                                    body_text = body.decode('gbk')
                                    email_body = body_text
                                    if content_type == "text/plain":
                                        urls = self.extract_urls_from_text(body_text)
                                    elif content_type == "text/html":
                                        urls = self.extract_urls_from_html(body_text)
                                except:
                                    logger.warning(f"Failed to decode single part email: {email_id}")

                    # If we found URLs, add to our list
                    if urls:
                        email_info = {
                            'id': email_id.decode('utf-8'),
                            'subject': subject,
                            'sender': sender,
                            'body': email_body,
                            'urls': urls,
                            'timestamp': msg.get('Date', ''),
                            'has_urls': len(urls) > 0
                        }
                        emails_with_urls.append(email_info)

                        # Mark as read
                        server.store(email_id, '+FLAGS', '\\Seen')

                except Exception as e:
                    logger.error(f"Error processing email {email_id}: {e}")
                    continue

            logger.info(f"✅ Found {len(emails_with_urls)} emails with URLs")
            return emails_with_urls

        except Exception as e:
            logger.error(f"❌ Error fetching emails: {e}")
            return []
        finally:
            try:
                server.expunge()  # Clean up deleted messages
                server.close()   # Close the mailbox
                server.logout()  # Logout from server
            except:
                server.logout()  # Ensure logout even if close fails

    def get_all_emails_with_urls(self) -> List[Dict]:
        """Get all emails (read and unread) that contain URLs"""
        server = self.connect()
        if not server:
            return []

        try:
            # Search for all emails
            status, messages = server.search(None, 'ALL')
            if status != 'OK':
                logger.error("Failed to search for emails")
                return []

            email_ids = messages[0].split()
            emails_with_urls = []

            for email_id in email_ids:
                try:
                    # Fetch the email
                    status, msg_data = server.fetch(email_id, '(RFC822)')
                    if status != 'OK':
                        continue

                    # Parse the email
                    msg = email.message_from_bytes(msg_data[0][1])

                    # Extract subject and sender
                    subject = msg.get('Subject', '')
                    sender = msg.get('From', '')

                    # Get email body
                    email_body = ''
                    urls = []

                    if msg.is_multipart():
                        # Handle multipart emails
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))

                            # Skip attachments
                            if "attachment" in content_disposition:
                                continue

                            # Extract text/html content
                            if content_type == "text/plain" or content_type == "text/html":
                                body = part.get_payload(decode=True)
                                if body:
                                    try:
                                        body_text = body.decode('utf-8')
                                        email_body += body_text

                                        # Extract URLs based on content type
                                        if content_type == "text/plain":
                                            urls.extend(self.extract_urls_from_text(body_text))
                                        elif content_type == "text/html":
                                            urls.extend(self.extract_urls_from_html(body_text))
                                    except UnicodeDecodeError:
                                        # Try with different encoding
                                        try:
                                            body_text = body.decode('gbk')
                                            email_body += body_text

                                            if content_type == "text/plain":
                                                urls.extend(self.extract_urls_from_text(body_text))
                                            elif content_type == "text/html":
                                                urls.extend(self.extract_urls_from_html(body_text))
                                        except:
                                            logger.warning(f"Failed to decode email part for email ID: {email_id}")
                    else:
                        # Handle single part email
                        body = msg.get_payload(decode=True)
                        if body:
                            try:
                                body_text = body.decode('utf-8')
                                email_body = body_text

                                content_type = msg.get_content_type()
                                if content_type == "text/plain":
                                    urls = self.extract_urls_from_text(body_text)
                                elif content_type == "text/html":
                                    urls = self.extract_urls_from_html(body_text)
                            except UnicodeDecodeError:
                                # Try with different encoding
                                try:
                                    body_text = body.decode('gbk')
                                    email_body = body_text
                                    if content_type == "text/plain":
                                        urls = self.extract_urls_from_text(body_text)
                                    elif content_type == "text/html":
                                        urls = self.extract_urls_from_html(body_text)
                                except:
                                    logger.warning(f"Failed to decode single part email: {email_id}")

                    # If we found URLs, add to our list
                    if urls:
                        email_info = {
                            'id': email_id.decode('utf-8'),
                            'subject': subject,
                            'sender': sender,
                            'body': email_body,
                            'urls': urls,
                            'timestamp': msg.get('Date', ''),
                            'has_urls': len(urls) > 0
                        }
                        emails_with_urls.append(email_info)

                except Exception as e:
                    logger.error(f"Error processing email {email_id}: {e}")
                    continue

            logger.info(f"✅ Found {len(emails_with_urls)} emails with URLs")
            return emails_with_urls

        except Exception as e:
            logger.error(f"❌ Error fetching emails: {e}")
            return []
        finally:
            try:
                server.expunge()  # Clean up deleted messages
                server.close()   # Close the mailbox
                server.logout()  # Logout from server
            except:
                server.logout()  # Ensure logout even if close fails

    def mark_email_as_read(self, email_id: str) -> bool:
        """Mark a specific email as read"""
        server = self.connect()
        if not server:
            return False
            
        try:
            server.store(email_id.encode(), '+FLAGS', '\\Seen')
            logger.info(f"✅ Email {email_id} marked as read")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to mark email as read: {e}")
            return False
        finally:
            try:
                server.close()
                server.logout()
            except:
                pass


if __name__ == "__main__":
    # Test the email reader
    logging.basicConfig(level=logging.INFO)
    
    reader = EmailReader()
    
    # Test connection
    server = reader.connect()
    if server:
        print("✅ Email server connection successful")
        server.logout()
    else:
        print("❌ Email server connection failed")
    
    print("\n✅ Email reader module ready!")