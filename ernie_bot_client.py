import json
import os
import requests
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Load configuration from config.json
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config
    else:
        logger.error("config.json not found")
        return {}

config = load_config()
api_keys = config.get('api_keys', {})

# Baidu ERNIE Bot configuration
ERNIE_BOT_CONFIG = {
    'api_key': api_keys.get('baidu_ernie', ''),
    'model_name': 'ernie-bot-4.5'
}

class ErnieBotClient:
    def __init__(self):
        # Extract the API key from the full key string
        full_api_key = ERNIE_BOT_CONFIG['api_key']
        # The format appears to be "bce-v3/ALTAK-<api_key>/signature"
        if full_api_key.startswith('bce-v3/ALTAK-'):
            # Extract the API key part (between ALTAK- and the next /)
            parts = full_api_key.split('/')
            if len(parts) >= 3:
                self.api_key = parts[2]  # This should be the signature part after the main key
                # For Baidu ERNIE Bot, typically we need client_id and client_secret from the API key
                # The format suggests this might be a complete access token rather than separate keys
                self.access_token = full_api_key  # Using the full key as access token
            else:
                self.access_token = full_api_key
        else:
            self.access_token = full_api_key
        
        self.model_name = ERNIE_BOT_CONFIG['model_name']
        self.base_url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_adv"
    
    def _get_access_token(self) -> str:
        """Get access token using API key and secret key if needed"""
        # Since your API key appears to be a complete access token already, we'll use it as-is
        # The format "bce-v3/ALTAK-..." is already an access token format
        return self.access_token
    
    def extract_policy_info(self, document_text: str) -> Dict:
        """Extract structured policy information using ERNIE Bot"""

        # Create a detailed prompt for policy document analysis
        prompt = f"""
        请仔细分析以下政策文档，并按以下要求输出：

        1. 政策要点解读和总结：
        - 深度解读政策核心内容，提供简洁准确的政策摘要
        - 提炼政策的主要目标、核心措施和支持对象
        - 总结关键要求和重要时间节点

        2. 量化指标提取：
        - 专门识别并列出所有量化指标，包括但不限于：
          * 具体金额（如补贴金额、资助标准等）
          * 比例和百分比
          * 人数要求
          * 时间限制
          * 面积规模
          * 增长目标
          * 覆盖范围数据
          * 门槛和标准数值
        - 将这些量化指标单独列出，并使用加粗、换行等方式突出显示

        3. 其他结构化信息：
        - 文档基本信息：政策标题、发文机关、发布日期、适用区域、重点产业
        - 支持措施（资金补贴、税收优惠、人才支持等）
        - 申请条件和要求
        - 时间节点和期限
        - 政策条款和规定
        - 重要条件和前置要求
        - 关系分析：哪些条件可能导致哪些结果、哪些主体能获得哪些支持、时间依赖关系

        请以JSON格式返回分析结果，确保所有中文键值对都使用拼音或英文键名，避免中文键名。
        JSON应包含以下字段：summary（政策摘要）、quantitative_indicators（量化指标列表）、basic_info（基本信息）、support_measures（支持措施）、requirements（要求条件）、timeline（时间节点）、relationships（关系分析）。

        文档内容：
        {document_text[:8000]}  # Limit to avoid token limits
        """

        headers = {
            'Content-Type': 'application/json'
        }

        data = {
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "model": "ernie-4.5-8k",  # Updated model name for ERNIE Bot 4.5
            "temperature": 0.1,  # Low temperature for consistent results
            "max_output_tokens": 4096,
            "top_p": 0.9
        }

        try:
            if not self.access_token:
                logger.error("No access token available for ERNIE Bot API")
                return {"error": "No access token configured"}

            # Use the access token directly from config
            response = requests.post(
                f"{self.base_url}?access_token={self.access_token}",
                headers=headers,
                json=data
            )

            if response.status_code == 200:
                result = response.json()
                if "result" in result:
                    # Try to parse the JSON response from ERNIE Bot
                    try:
                        # The result["result"] is a string that may contain JSON
                        policy_data = json.loads(result["result"])
                        return policy_data
                    except json.JSONDecodeError:
                        # If it's not valid JSON, return as raw text but structured
                        logger.warning("ERNIE Bot response is not valid JSON, returning as raw text")
                        return {
                            "raw_response": result["result"],
                            "parsing_failed": True
                        }
                else:
                    logger.error(f"ERNIE Bot API error: {result}")
                    return {"error": result}
            elif response.status_code == 401:
                logger.error("ERNIE Bot API authentication failed - invalid access token")
                return {"error": "Authentication failed - invalid access token"}
            elif response.status_code == 404:
                logger.error("ERNIE Bot API endpoint not found")
                return {"error": "API endpoint not found"}
            else:
                logger.error(f"ERNIE Bot API request failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return {"error": f"API request failed with status {response.status_code}: {response.text}"}

        except requests.exceptions.ConnectionError:
            logger.error("Failed to connect to ERNIE Bot API - network error")
            return {"error": "Network connection error - please check your internet connection"}
        except requests.exceptions.Timeout:
            logger.error("ERNIE Bot API request timed out")
            return {"error": "API request timed out"}
        except Exception as e:
            logger.error(f"Error calling ERNIE Bot API: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {"error": f"Error calling ERNIE Bot API: {str(e)}"}
    
    def generate_summary(self, document_text: str) -> str:
        """Generate a summary of the policy document"""
        prompt = f"""
        请深度分析以下政策文档，提供简洁准确的政策解读摘要，重点关注：
        1. 政策的主要目标和核心内容
        2. 关键支持措施和适用对象
        3. 重要申请条件和时间节点
        4. 特别强调所有量化指标（如具体金额、比例、门槛等）

        请突出显示量化指标，使用分段、加粗等方式使其更明显。

        文档内容：
        {document_text[:4000]}
        """

        headers = {
            'Content-Type': 'application/json'
        }

        data = {
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "model": "ernie-4.5-8k",
            "temperature": 0.3,
            "max_output_tokens": 1024
        }

        try:
            response = requests.post(
                f"{self.base_url}?access_token={self.access_token}",
                headers=headers,
                json=data
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("result", "无法生成摘要")
            else:
                logger.error(f"Summary generation failed: {response.status_code}, {response.text}")
                return "摘要生成失败"

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"摘要生成失败: {str(e)}"
    
    def extract_key_points(self, document_text: str) -> List[str]:
        """Extract key points from the policy"""
        prompt = f"""
        请从以下政策文档中提取关键要点，特别关注量化指标，以列表形式返回：
        1. 按重要性排序列出关键要点
        2. 将所有量化指标（如具体金额、比例、门槛、时间限制等）单独突出显示
        3. 非量化要点每点不超过50字，量化指标可适当详细

        文档内容：
        {document_text[:6000]}
        """
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        data = {
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "model": "ernie-4.5-8k",
            "temperature": 0.2,
            "max_output_tokens": 1024
        }
        
        try:
            response = requests.post(
                f"{self.base_url}?access_token={self.access_token}",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                # Parse the result and return as a list
                content = result.get("result", "")
                
                # Split by numbered lists, bullet points, or newlines
                import re
                # Look for numbered lists (1. 2. etc) or bullet points
                points = re.split(r'\n\d+\.\s*|\n\s*[-*]\s*', content)
                
                # Clean up the points
                cleaned_points = []
                for point in points:
                    point = point.strip()
                    if len(point) > 5:  # Filter out very short items
                        # Remove numbering that might still be in the text
                        point = re.sub(r'^\d+\.\s*', '', point)
                        point = re.sub(r'^[-*]\s*', '', point)
                        if point:
                            cleaned_points.append(point)
                
                return cleaned_points[:10]  # Return up to 10 key points
            else:
                logger.error(f"Key points extraction failed: {response.status_code}, {response.text}")
                return ["要点提取失败"]
                
        except Exception as e:
            logger.error(f"Error extracting key points: {e}")
            return [f"要点提取失败: {str(e)}"]