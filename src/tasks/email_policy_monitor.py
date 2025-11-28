#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Email Policy Monitor
Background task to periodically check email for new policy URLs
"""

import time
import logging
from datetime import datetime

from src.utils.email_reader import EmailReader
from src.analysis.policy_analysis_integrator import PolicyAnalysisIntegrator
from app import db, PolicyAnalysis, create_app

logger = logging.getLogger(__name__)


def check_email_for_policies():
    """Check email for new policy URLs and process them"""
    try:
        # Create app context
        app = create_app()
        
        with app.app_context():
            from app import db
            logger.info("🔍 Starting email policy check...")
            
            # Initialize email reader
            email_reader = EmailReader()
            
            # Get new emails with URLs
            emails_with_urls = email_reader.get_unread_emails_with_urls()
            
            new_policies_count = 0
            
            if emails_with_urls:
                # Initialize policy integrator
                integrator = PolicyAnalysisIntegrator()
                
                for email_info in emails_with_urls:
                    logger.info(f"Processing email: {email_info['subject'][:50]}...")
                    for url in email_info['urls']:
                        try:
                            logger.info(f"Analyzing policy from URL: {url}")
                            
                            # Analyze the policy from URL
                            analysis_result = integrator.analyze_policy_from_url(url)
                            
                            if analysis_result.get('success'):
                                # Extract classification info
                                classification = analysis_result.get('classification', {})
                                
                                # Create PolicyAnalysis record
                                policy_analysis = PolicyAnalysis(
                                    title=analysis_result.get('title', 'Unknown Title'),
                                    original_url=analysis_result.get('url'),
                                    source_type='email',
                                    content=analysis_result.get('content', ''),
                                    content_summary=analysis_result.get('content_summary', analysis_result.get('title', ''))[:500],  # Better summary
                                    analysis_result=analysis_result,
                                    classification_region=classification.get('region', [None])[0] if classification.get('region') else None,
                                    classification_industry=classification.get('industry', [None])[0] if classification.get('industry') else None,
                                    classification_year=classification.get('year'),
                                    classification_policy_type=classification.get('policy_type'),
                                    applicability_score=analysis_result.get('policy_analysis', {}).get('applicability', {}).get('score', 0) if analysis_result.get('policy_analysis', {}).get('applicability') else 0,
                                    entities=analysis_result.get('entities'),
                                    knowledge_graph=analysis_result.get('knowledge_graph'),
                                    llm_interpretation=analysis_result.get('llm_interpretation'),
                                    tags=','.join(classification.get('region', []) + classification.get('industry', [])),
                                    status='completed'
                                )
                                
                                db.session.add(policy_analysis)
                                db.session.commit()
                                new_policies_count += 1
                                
                                logger.info(f"✅ Successfully added policy: {policy_analysis.title[:50]}...")
                                
                            else:
                                logger.error(f"❌ Failed to analyze policy from URL: {url}")
                                
                        except Exception as e:
                            logger.error(f"Error processing policy from email {email_info['id']}, URL {url}: {e}")
                            
                            # Create failed record
                            policy_analysis = PolicyAnalysis(
                                title=f"分析失败 - {url}",
                                original_url=url,
                                source_type='email',
                                status='failed',
                                content_summary=f"分析失败: {str(e)}"
                            )
                            db.session.add(policy_analysis)
                            db.session.commit()

                logger.info(f"✅ Email check completed. Added {new_policies_count} new policies.")
            else:
                logger.info("✅ No new emails with policy URLs found.")
                
        return new_policies_count
        
    except Exception as e:
        logger.error(f"❌ Error in email policy check: {e}")
        return 0


def start_email_monitor(interval_minutes=30):
    """Start the email monitoring service"""
    logger.info(f"🚀 Starting email policy monitor (checking every {interval_minutes} minutes)")
    
    while True:
        try:
            # Check for new policies
            new_count = check_email_for_policies()
            logger.info(f"Completed check. Found {new_count} new policies")
            
            # Wait for the specified interval
            logger.info(f"⏳ Waiting {interval_minutes} minutes before next check...")
            time.sleep(interval_minutes * 60)
            
        except KeyboardInterrupt:
            logger.info("🛑 Email monitor stopped by user")
            break
        except Exception as e:
            logger.error(f"❌ Error in email monitor: {e}")
            time.sleep(interval_minutes * 60)  # Wait before retrying


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Start the email monitor
    start_email_monitor(interval_minutes=30)