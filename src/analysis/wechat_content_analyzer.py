#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeChat Public Account Content Analyzer
Analyze and process WeChat articles using existing policy analysis capabilities
"""

import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import asdict, dataclass

from src.analysis.policy_analyzer import PolicyAnalyzer
from src.analysis.policy_document_processor import PolicyInfo

@dataclass
class WeChatArticle:
    """Simple data class for WeChat articles used in analysis (separate from database model)"""
    title: str = ""
    content: str = ""
    publish_date: str = ""
    author: str = ""
    source_account: str = ""
    url: str = ""
    summary: str = ""
    keywords: str = ""
    industry_relevance: str = ""
    content_html: str = ""

logger = logging.getLogger(__name__)


class WeChatContentAnalyzer:
    """Analyze and process WeChat public account content"""

    def __init__(self):
        """Initialize the WeChat content analyzer"""
        self.policy_analyzer = PolicyAnalyzer()

    def analyze_article_content(self, article: WeChatArticle, company_profile: Optional[Dict] = None) -> Dict:
        """
        Analyze WeChat article content using policy analysis techniques

        Args:
            article: WeChat article to analyze
            company_profile: Company profile for applicability assessment (optional)

        Returns:
            Analysis result
        """
        try:
            # Clean content by removing HTML tags for text analysis
            clean_content = self._clean_html_content(article.content)
            
            # Extract policy highlights
            highlights = self.policy_analyzer.extract_policy_highlights(clean_content)
            
            # Identify subsidies and tax benefits
            subsidies_taxes = self.policy_analyzer.identify_subsidies_and_taxes(clean_content)
            
            # Extract timeline
            timeline = self.policy_analyzer.extract_timeline(clean_content)
            
            # Generate summary
            summary = self.policy_analyzer.generate_policy_summary(clean_content)
            
            # Perform applicability assessment if company profile provided
            applicability = None
            if company_profile:
                applicability = self.policy_analyzer.match_applicability(clean_content, company_profile)

            # Enhance with article metadata
            analysis_result = {
                "article_metadata": {
                    "title": article.title,
                    "author": article.author,
                    "source_account": article.source_account,
                    "publish_date": article.publish_date,
                    "url": article.url,
                    "summary": article.summary,
                    "keywords": article.keywords,
                    "industry_relevance": article.industry_relevance
                },
                "policy_analysis": {
                    "highlights": highlights,
                    "subsidies_and_taxes": subsidies_taxes,
                    "timeline": timeline,
                    "summary": summary
                },
                "applicability": applicability,
                "content_keywords": self._extract_content_keywords(clean_content),
                "sentiment": self._analyze_sentiment(clean_content),
                "related_policies": self._find_related_policies(clean_content)
            }

            logger.info(f"✅ Article analysis completed for: {article.title}")
            return analysis_result

        except Exception as e:
            logger.error(f"❌ Article analysis failed: {e}")
            return {
                "error": str(e),
                "article_metadata": asdict(article) if isinstance(article, WeChatArticle) else {"title": "Unknown"}
            }

    def _clean_html_content(self, html_content: str) -> str:
        """Remove HTML tags from content"""
        try:
            # Remove HTML tags using regex
            clean_text = re.sub(r'<[^>]*>', ' ', html_content)
            # Remove extra whitespace
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            return clean_text
        except Exception as e:
            logger.error(f"Error cleaning HTML content: {e}")
            return html_content  # Return original if cleaning fails

    def _extract_content_keywords(self, content: str) -> List[str]:
        """Extract keywords from content"""
        try:
            keywords = []
            
            # Policy-related keywords
            policy_keywords = [
                "政策", "补贴", "扶持", "资金", "税收", "优惠", "人才", "研发", 
                "创新", "产业", "发展", "计划", "申报", "资格", "条件", "项目",
                "支持", "措施", "要求", "标准", "金额", "比例", "期限", "截止日期"
            ]
            
            for kw in policy_keywords:
                if kw in content and kw not in keywords:
                    keywords.append(kw)
            
            # Extract amounts and percentages
            amounts = re.findall(r'(\d+(?:\.\d+)?)\s*(?:[亿万千百]|万元?|%)', content)
            for amount in amounts[:10]:  # Limit to 10 amounts
                if amount not in keywords:
                    keywords.append(amount)
            
            # Extract time-related keywords
            time_patterns = [
                r'(\d{4})年(\d{1,2})月(\d{1,2})日',
                r'(\d{4})-(\d{1,2})-(\d{1,2})',
                r'(\d{1,2})个月',
                r'(\d{1,3})天'
            ]
            for pattern in time_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if isinstance(match, tuple):
                        if len(match) >= 3 and match[0] and match[1] and match[2]:
                            keywords.append(f"{match[0]}年{match[1]}月{match[2]}日")
            
            return list(set(keywords))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error extracting content keywords: {e}")
            return []

    def _analyze_sentiment(self, content: str) -> Dict[str, float]:
        """Analyze sentiment of the content"""
        try:
            # Simple sentiment analysis based on positive/negative keywords
            positive_keywords = [
                "支持", "鼓励", "促进", "推动", "发展", "利好", "优惠", "补贴", 
                "扶持", "奖励", "增长", "提升", "创新", "突破", "成就"
            ]
            
            negative_keywords = [
                "限制", "禁止", "暂停", "取消", "整改", "处罚", "风险", "挑战",
                "困难", "下降", "减少", "关停", "问题", "障碍", "不利"
            ]
            
            content_lower = content.lower()
            
            positive_count = sum(1 for kw in positive_keywords if kw in content_lower)
            negative_count = sum(1 for kw in negative_keywords if kw in content_lower)
            total_count = positive_count + negative_count
            
            if total_count == 0:
                return {
                    "positive": 0.5,
                    "negative": 0.0,
                    "neutral": 0.5,
                    "overall": "neutral"
                }
            
            positive_score = positive_count / total_count
            negative_score = negative_count / total_count
            neutral_score = 1 - (positive_score + negative_score)
            
            # Determine overall sentiment
            if positive_score > negative_score * 1.5:
                overall = "positive"
            elif negative_score > positive_score * 1.5:
                overall = "negative"
            else:
                overall = "neutral"
            
            return {
                "positive": round(positive_score, 3),
                "negative": round(negative_score, 3),
                "neutral": round(neutral_score, 3),
                "overall": overall
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {
                "positive": 0.5,
                "negative": 0.0,
                "neutral": 0.5,
                "overall": "neutral"
            }

    def _find_related_policies(self, content: str) -> List[str]:
        """Find related policies mentioned in the content"""
        try:
            related_policies = []
            
            # Look for policy document names or references
            policy_patterns = [
                r'(?:关于|印发|发布|制定)(.*?)(?:政策|办法|条例|规定|意见|实施方案|指导意见|通知|细则)',
                r'(.*?)(?:政策|办法|条例|规定|意见|实施方案|指导意见|通知|细则)(?:相关|有关|具体)',
                r'(?:参考|依据|按照)(.*?)(?:政策|文件|规定|要求)'
            ]
            
            for pattern in policy_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if match and match not in related_policies and len(match) > 2:
                        related_policies.append(match.strip())
            
            return related_policies[:10]  # Limit to 10 related policies
            
        except Exception as e:
            logger.error(f"Error finding related policies: {e}")
            return []

    def analyze_multiple_articles(self, articles: List[WeChatArticle], 
                                  company_profile: Optional[Dict] = None) -> List[Dict]:
        """Analyze multiple articles"""
        try:
            results = []
            
            for article in articles:
                analysis = self.analyze_article_content(article, company_profile)
                results.append(analysis)
            
            logger.info(f"✅ Analyzed {len(results)} articles")
            return results
            
        except Exception as e:
            logger.error(f"❌ Multiple article analysis failed: {e}")
            return []

    def extract_policy_info_from_article(self, article: WeChatArticle) -> PolicyInfo:
        """Extract policy information from a WeChat article"""
        try:
            # Clean content for analysis
            clean_content = self._clean_html_content(article.content)
            
            # Use existing policy info extraction from policy_document_processor
            # This simulates extracting key information from the article
            policy_info = PolicyInfo()
            
            # Extract title
            policy_info.title = article.title
            
            # Extract issuing authority (source account)
            policy_info.issuing_authority = article.source_account
            
            # Extract release date
            policy_info.release_date = article.publish_date
            
            # Extract applicable region (this would require more sophisticated NER in production)
            # For now, we'll use a simplified approach
            regions = ["四川省", "成都市", "高新区", "北京市", "上海市"]  # Sample regions
            for region in regions:
                if region in clean_content:
                    policy_info.applicable_region = region
                    break
            
            # Extract key industries
            industry_keywords = ["人工智能", "新能源", "生物医药", "新材料", "高端制造", "数字经济"]
            for industry in industry_keywords:
                if industry in clean_content and industry not in policy_info.key_industries:
                    policy_info.key_industries.append(industry)
            
            # Extract support measures
            measure_keywords = [
                "资金支持", "税收优惠", "补贴", "奖励", "扶持资金", "专项资金",
                "贷款贴息", "融资支持", "租金减免", "人才补贴"
            ]
            for measure in measure_keywords:
                if measure in clean_content and measure not in policy_info.support_measures:
                    policy_info.support_measures.append(measure)
            
            # Extract funding scale
            funding_matches = re.findall(r'(\d+(?:\.\d+)?)\s*([亿万千百]?元)', clean_content)
            if funding_matches:
                # Take the largest funding amount mentioned
                max_amount = max([float(m[0]) for m in funding_matches])
                for match in funding_matches:
                    if float(match[0]) == max_amount:
                        policy_info.funding_scale = f"{match[0]}{match[1]}"
                        break
            
            # Extract quantified indicators
            policy_info.quantified_indicators = self._extract_quantified_indicators_from_content(clean_content)
            
            # Extract time nodes
            policy_info.time_nodes = self._extract_time_nodes_from_content(clean_content)
            
            logger.info(f"✅ Policy info extracted from article: {article.title}")
            return policy_info
            
        except Exception as e:
            logger.error(f"❌ Policy info extraction failed: {e}")
            return PolicyInfo()

    def _extract_quantified_indicators_from_content(self, content: str) -> List[Dict]:
        """Extract quantified indicators from content"""
        try:
            indicators = []
            
            # Match various quantitative indicators
            patterns = [
                r'(\d+(?:\.\d+)?)[亿万千百]?元',  # Amounts
                r'(\d+(?:\.\d+)?)%',  # Percentages
                r'(\d+(?:\.\d+)?)[亿万千百](?:项|个|家)',  # Quantities
                r'(\d+(?:\.\d+)?)年',  # Durations
            ]

            for pattern in patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    # Get context
                    start = max(0, match.start() - 20)
                    end = min(len(content), match.end() + 20)
                    context = content[start:end].strip()

                    indicators.append({
                        "value": match.group(1),
                        "unit": match.group(0)[-1] if match.group(0)[-1].isalpha() else "amount",
                        "context": context,
                        "position": match.start()
                    })

            # Remove duplicates and sort by position
            seen = set()
            unique_indicators = []
            for indicator in sorted(indicators, key=lambda x: x["position"]):
                key = (indicator["value"], indicator["unit"])
                if key not in seen:
                    seen.add(key)
                    unique_indicators.append(indicator)

            return unique_indicators[:20]  # Limit number

        except Exception as e:
            logger.error(f"❌ Quantified indicator extraction failed: {e}")
            return []

    def _extract_time_nodes_from_content(self, content: str) -> List[Dict]:
        """Extract time nodes from content"""
        try:
            time_nodes = []
            
            # Match date formats
            date_patterns = [
                (r'(\d{4})年(\d{1,2})月(\d{1,2})日',
                 lambda m: f"{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3).zfill(2)}"),
                (r'(\d{4})-(\d{1,2})-(\d{1,2})',
                 lambda m: m.group(0)),
                (r'(\d{4})年(\d{1,2})月',
                 lambda m: f"{m.group(1)}-{m.group(2).zfill(2)}-01")
            ]

            for pattern, formatter in date_patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    date_str = formatter(match)

                    # Get context
                    start = max(0, match.start() - 30)
                    end = min(len(content), match.end() + 30)
                    context = content[start:end].strip()

                    # Determine event type
                    event_type = "other"
                    if any(kw in context for kw in ["发布", "颁布", "实施"]):
                        event_type = "release_implementation"
                    elif any(kw in context for kw in ["截止", "之前", "到期", "申报"]):
                        event_type = "deadline"
                    elif any(kw in context for kw in ["申报", "申请"]):
                        event_type = "application_period"

                    time_nodes.append({
                        "date": date_str,
                        "event_type": event_type,
                        "context": context,
                        "is_future": self._is_future_date(date_str)
                    })

            # Sort by date
            time_nodes.sort(key=lambda x: x["date"])

            return time_nodes

        except Exception as e:
            logger.error(f"❌ Time node extraction failed: {e}")
            return []

    def _is_future_date(self, date_str: str) -> bool:
        """Check if date is in the future"""
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d") if len(date_str) == 10 else datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj > datetime.now()
        except:
            return False

    def aggregate_analysis_results(self, analysis_results: List[Dict]) -> Dict:
        """Aggregate analysis results from multiple articles"""
        try:
            # Initialize aggregation structure
            aggregated = {
                "total_articles": len(analysis_results),
                "time_range": {"start": None, "end": None},
                "top_keywords": [],
                "common_subsidies": [],
                "trending_topics": [],
                "policy_summary": {
                    "total_highlights": 0,
                    "total_subsidies": 0,
                    "total_tax_benefits": 0,
                    "upcoming_deadlines": 0
                },
                "sentiment_analysis": {
                    "overall_positive": 0,
                    "overall_negative": 0,
                    "overall_neutral": 0
                }
            }
            
            # Collect all keywords
            all_keywords = []
            all_subsidies = []
            publish_dates = []
            
            # Process each analysis result
            for result in analysis_results:
                if "policy_analysis" in result:
                    analysis = result["policy_analysis"]
                    
                    # Update policy summary counts
                    if "summary" in analysis:
                        summary = analysis["summary"]
                        aggregated["policy_summary"]["total_highlights"] += summary.get("statistics", {}).get("total_highlights", 0)
                        aggregated["policy_summary"]["total_subsidies"] += summary.get("statistics", {}).get("total_subsidies", 0)
                        aggregated["policy_summary"]["total_tax_benefits"] += summary.get("statistics", {}).get("total_tax_benefits", 0)
                        aggregated["policy_summary"]["upcoming_deadlines"] += summary.get("statistics", {}).get("upcoming_deadlines", 0)
                    
                    # Extract subsidies
                    subsidies = analysis.get("subsidies_and_taxes", {}).get("subsidies", [])
                    all_subsidies.extend([s.get("description", "")[:50] for s in subsidies])
                
                # Extract keywords
                if "content_keywords" in result:
                    all_keywords.extend(result["content_keywords"])
                
                # Collect publish dates
                if "article_metadata" in result:
                    date_str = result["article_metadata"].get("publish_date")
                    if date_str:
                        try:
                            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                            publish_dates.append(date_obj)
                        except:
                            pass
                
                # Aggregate sentiment
                if "sentiment" in result:
                    sentiment = result["sentiment"]
                    aggregated["sentiment_analysis"]["overall_positive"] += sentiment.get("positive", 0)
                    aggregated["sentiment_analysis"]["overall_negative"] += sentiment.get("negative", 0)
                    aggregated["sentiment_analysis"]["overall_neutral"] += sentiment.get("neutral", 0)
            
            # Calculate aggregates
            if publish_dates:
                aggregated["time_range"]["start"] = min(publish_dates).strftime("%Y-%m-%d")
                aggregated["time_range"]["end"] = max(publish_dates).strftime("%Y-%m-%d")
            
            # Get top keywords
            if all_keywords:
                keyword_counts = {}
                for kw in all_keywords:
                    keyword_counts[kw] = keyword_counts.get(kw, 0) + 1
                # Sort by count and take top 10
                top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                aggregated["top_keywords"] = [{"keyword": item[0], "count": item[1]} for item in top_keywords]
            
            # Get common subsidies
            if all_subsidies:
                subsidy_counts = {}
                for sub in all_subsidies:
                    subsidy_counts[sub] = subsidy_counts.get(sub, 0) + 1
                # Sort by count and take top 10
                common_subsidies = sorted(subsidy_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                aggregated["common_subsidies"] = [{"subsidy": item[0], "count": item[1]} for item in common_subsidies]
            
            # Calculate average sentiment
            if analysis_results:
                count = len(analysis_results)
                aggregated["sentiment_analysis"]["overall_positive"] /= count
                aggregated["sentiment_analysis"]["overall_negative"] /= count
                aggregated["sentiment_analysis"]["overall_neutral"] /= count
            
            logger.info(f"✅ Analysis results aggregated for {len(analysis_results)} articles")
            return aggregated
            
        except Exception as e:
            logger.error(f"❌ Analysis aggregation failed: {e}")
            return {"error": str(e)}


if __name__ == "__main__":
    # Test the analyzer
    logging.basicConfig(level=logging.INFO)
    
    analyzer = WeChatContentAnalyzer()
    
    # Create a sample WeChat article
    sample_article = WeChatArticle(
        title="四川省人工智能产业支持政策解读",
        content="<h2>四川省AI产业发展政策</h2><p>四川省发布新政策，对AI企业给予最高500万元资金支持。</p><p>申报截止日期为2024年6月30日。</p>",
        publish_date="2024-01-15",
        author="政策解读",
        source_account="四川政策发布",
        url="https://example.com/sichuan_ai_policy"
    )
    
    # Analyze the article
    result = analyzer.analyze_article_content(sample_article)
    print(f"\nAnalysis completed for: {sample_article.title}")
    print(f"Highlights: {len(result['policy_analysis']['highlights'])}")
    print(f"Subsidies: {len(result['policy_analysis']['subsidies_and_taxes']['subsidies'])}")
    
    # Test multiple articles analysis
    articles = [sample_article] * 3  # Create 3 similar articles for testing
    results = analyzer.analyze_multiple_articles(articles)
    print(f"\nAnalyzed {len(results)} articles")
    
    # Test aggregation
    aggregated = analyzer.aggregate_analysis_results(results)
    print(f"\nAggregated results for {aggregated['total_articles']} articles")
    print(f"Top keywords: {len(aggregated['top_keywords'])}")
    
    print("\n✅ WeChat content analyzer module ready!")