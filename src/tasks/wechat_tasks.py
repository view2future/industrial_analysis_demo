"""
WeChat Article Fetching Tasks
Celery tasks for fetching WeChat articles periodically
"""

import logging
from datetime import datetime
from src.data.wechat_scraper import WeChatScraper
from .celery_app import celery_app  # Use existing celery_app

# Avoid circular import - import db and models from their proper location
# These imports will be resolved when the task is actually run within the app context
def get_db():
    from app import db
    return db

def get_WeChatArticle():
    from app import WeChatArticle
    return WeChatArticle

logger = logging.getLogger(__name__)


@celery_app.task
def fetch_wechat_articles_task():
    """
    Task to fetch WeChat articles from specified accounts and store in database
    """
    try:
        logger.info("Starting WeChat articles fetch task")

        # Initialize the scraper
        scraper = WeChatScraper()

        # Get articles from specified WeChat accounts
        articles = scraper.get_specified_account_articles(limit=20)  # Fetch up to 20 articles per account

        logger.info(f"Retrieved {len(articles)} articles from WeChat accounts")

        # Store articles in database
        new_articles_count = 0
        WeChatArticle = get_WeChatArticle()
        db = get_db()

        for article_data in articles:
            # Check if article already exists in database (based on URL)
            existing_article = WeChatArticle.query.filter_by(url=article_data['url']).first()

            if not existing_article:
                # Create new article record
                new_article = WeChatArticle(
                    title=article_data['title'],
                    content=article_data['content'],
                    publish_date=article_data['publish_date'],
                    author=article_data['author'],
                    source_account=article_data['source_account'],
                    url=article_data['url'],
                    summary=article_data['summary'],
                    content_html=article_data['content_html'],
                    keywords=','.join(article_data['keywords']) if article_data['keywords'] else '',
                    industry_relevance=','.join(article_data['industry_relevance']) if article_data['industry_relevance'] else ''
                )

                db.session.add(new_article)
                new_articles_count += 1
            else:
                # Update existing article if needed
                existing_article.content = article_data['content']
                existing_article.summary = article_data['summary']
                existing_article.content_html = article_data['content_html']
                existing_article.updated_at = datetime.utcnow()

        # Commit changes to database
        db.session.commit()

        logger.info(f"Successfully stored {new_articles_count} new articles in database")

        # Close scraper
        scraper.close()

        return {
            'status': 'success',
            'new_articles_count': new_articles_count,
            'total_articles_processed': len(articles)
        }

    except Exception as e:
        logger.error(f"Error in WeChat articles fetch task: {e}")
        import traceback
        logger.error(traceback.format_exc())

        # Rollback in case of error
        db.session.rollback()

        return {
            'status': 'error',
            'error': str(e)
        }


def schedule_wechat_fetching():
    """
    Schedule the WeChat articles fetching task to run periodically
    This function is called when the app starts
    """
    # Currently disabled - fetch on app start instead
    # If you want to re-enable periodic scheduling, uncomment the following:
    """
    try:
        from celery.schedules import crontab

        # Add periodic task to fetch WeChat articles every day at 2 AM
        celery_app.conf.beat_schedule = {
            'fetch-wechat-articles-daily': {
                'task': 'src.tasks.wechat_tasks.fetch_wechat_articles_task',
                'schedule': crontab(hour=2, minute=0),  # Run daily at 2:00 AM
            },
        }

        logger.info("WeChat articles fetching task scheduled successfully")

    except Exception as e:
        logger.error(f"Error scheduling WeChat articles fetching task: {e}")
    """


if __name__ == "__main__":
    # For testing the task directly
    logging.basicConfig(level=logging.INFO)
    result = fetch_wechat_articles_task()
    print(f"Task result: {result}")