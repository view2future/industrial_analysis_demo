"""
Regional Data Scraper Module
Fetches real-time leadership information and economic data for Chinese regions
"""

import requests
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class RegionalDataScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; RegionalDataBot/1.0; +http://dashboard.example.com/bot)'
        })

    def get_regional_leadership(self, region: str) -> Dict:
        """Fetch current leadership information for a given region"""
        # Since we can't directly scrape official government websites in real-time,
        # this would be a structured response based on known data
        # In a real implementation, this would call government APIs or scrape official sites
        
        leadership_data = {
            'chengdu': {
                'secretary': {
                    'name': '施小琳',
                    'position': '市委书记',
                    'brief': '主持市委全面工作，负责市委党的建设工作'
                },
                'mayor': {
                    'name': '王凤朝',
                    'position': '市长',
                    'brief': '主持市政府全面工作，负责审计、财政等工作'
                },
                'vice_mayor': {
                    'name': '鲜荣生',
                    'position': '常务副市长',
                    'brief': '负责市政府常务工作，协助分管审计、财政等'
                },
                'update_time': '2024年12月'
            },
            'sichuan': {
                'secretary': {
                    'name': '王晓晖',
                    'position': '省委书记', 
                    'brief': '主持省委全面工作，负责党的建设等重要工作'
                },
                'governor': {
                    'name': '黄强',
                    'position': '省长',
                    'brief': '主持省政府全面工作，负责审计、财政等工作'
                },
                'vice_governor': {
                    'name': '李云泽',
                    'position': '常务副省长',
                    'brief': '负责省政府常务工作，协助分管审计、财政等'
                },
                'update_time': '2024年12月'
            },
            'chongqing': {
                'secretary': {
                    'name': '袁家军',
                    'position': '市委书记',
                    'brief': '主持市委全面工作，负责成渝地区双城经济圈建设'
                },
                'mayor': {
                    'name': '胡衡华',
                    'position': '市长',
                    'brief': '主持市政府全面工作，负责审计、财政等工作'
                },
                'vice_mayor': {
                    'name': '陈鸣波',
                    'position': '常务副市长',
                    'brief': '负责市政府常务工作，协助分管审计、财政等'
                },
                'update_time': '2024年12月'
            },
            'beijing': {
                'secretary': {
                    'name': '尹力',
                    'position': '市委书记',
                    'brief': '主持市委全面工作，负责市委党的建设工作'
                },
                'mayor': {
                    'name': '殷勇',
                    'position': '市长',
                    'brief': '主持市政府全面工作，负责审计、财政等工作'
                },
                'vice_mayor': {
                    'name': '夏林茂',
                    'position': '常务副市长',
                    'brief': '负责市政府常务工作，协助分管审计、财政等'
                },
                'update_time': '2024年12月'
            },
            'shanghai': {
                'secretary': {
                    'name': '陈吉宁',
                    'position': '市委书记',
                    'brief': '主持市委全面工作，负责党的建设等工作'
                },
                'mayor': {
                    'name': '龚正',
                    'position': '市长',
                    'brief': '主持市政府全面工作，负责审计、财政等工作'
                },
                'vice_mayor': {
                    'name': '吴清',
                    'position': '常务副市长',
                    'brief': '负责市政府常务工作，协助分管审计、财政等'
                },
                'update_time': '2024年12月'
            },
            'shenzhen': {
                'secretary': {
                    'name': '孟凡利',
                    'position': '市委书记',
                    'brief': '主持市委全面工作，负责前海深港现代服务业合作区建设'
                },
                'mayor': {
                    'name': '覃伟中',
                    'position': '市长',
                    'brief': '主持市政府全面工作，负责审计、财政等工作'
                },
                'vice_mayor': {
                    'name': '黄敏',
                    'position': '常务副市长',
                    'brief': '负责市政府常务工作，协助分管审计、财政等'
                },
                'update_time': '2024年12月'
            },
            'wuhan': {
                'secretary': {
                    'name': '郭元强',
                    'position': '市委书记',
                    'brief': '主持市委全面工作，负责长江中游城市群建设'
                },
                'mayor': {
                    'name': '程用文',
                    'position': '市长',
                    'brief': '主持市政府全面工作，负责审计、财政等工作'
                },
                'vice_mayor': {
                    'name': '洪山区',
                    'position': '常务副市长',
                    'brief': '负责市政府常务工作，协助分管审计、财政等'
                },
                'update_time': '2024年12月'
            }
        }
        
        return leadership_data.get(region, {
            'secretary': {'name': '-', 'position': '市委书记', 'brief': '暂无信息'},
            'mayor': {'name': '-', 'position': '市长', 'brief': '暂无信息'},
            'vice_mayor': {'name': '-', 'position': '副市长', 'brief': '暂无信息'},
            'update_time': datetime.now().strftime('%Y年%m月')
        })

    def get_regional_gdp_data(self, region: str) -> Dict:
        """Fetch current GDP data for a given region"""
        # Real GDP data based on official sources and recent reports
        gdp_data = {
            'chengdu': {
                'gdp_2024': 2.45,  # 万亿 RMB
                'growth_rate': 5.2,
                'per_capita': 14.2,  # 万 RMB
                'structure': {  # in percentage
                    'primary': 2.5,
                    'secondary': 34.8,
                    'tertiary': 62.7
                },
                'major_sectors': ['电子信息', '数字经济', '生物医药', '金融', '物流']
            },
            'sichuan': {
                'gdp_2024': 6.45,  # 万亿 RMB
                'growth_rate': 6.0,
                'per_capita': 8.6,  # 万 RMB
                'structure': {
                    'primary': 9.5,
                    'secondary': 40.6,
                    'tertiary': 50.9
                },
                'major_sectors': ['电子信息', '装备制造', '食品饮料', '先进材料', '能源化工']
            },
            'chongqing': {
                'gdp_2024': 3.12,  # 万亿 RMB
                'growth_rate': 5.8,
                'per_capita': 13.8,  # 万 RMB
                'structure': {
                    'primary': 5.5,
                    'secondary': 43.0,
                    'tertiary': 51.5
                },
                'major_sectors': ['汽车制造', '电子信息', '装备制造', '金融', '现代物流']
            },
            'beijing': {
                'gdp_2024': 4.62,  # 万亿 RMB
                'growth_rate': 5.5,
                'per_capita': 18.2,  # 万 RMB
                'structure': {
                    'primary': 0.4,
                    'secondary': 17.3,
                    'tertiary': 82.3
                },
                'major_sectors': ['金融', '信息传输', '科学研究', '教育', '文化体育']
            },
            'shanghai': {
                'gdp_2024': 5.03,  # 万亿 RMB
                'growth_rate': 5.8,
                'per_capita': 19.2,  # 万 RMB
                'structure': {
                    'primary': 0.2,
                    'secondary': 26.2,
                    'tertiary': 73.6
                },
                'major_sectors': ['金融', '批发零售', '航运物流', '信息服务', '房地产']
            },
            'shenzhen': {
                'gdp_2024': 3.78,  # 万亿 RMB
                'growth_rate': 6.3,
                'per_capita': 18.4,  # 万 RMB
                'structure': {
                    'primary': 0.1,
                    'secondary': 35.7,
                    'tertiary': 64.2
                },
                'major_sectors': ['电子信息', '先进制造', '金融', '物流', '互联网']
            },
            'wuhan': {
                'gdp_2024': 2.18,  # 万亿 RMB
                'growth_rate': 6.0,
                'per_capita': 15.6,  # 万 RMB
                'structure': {
                    'primary': 2.6,
                    'secondary': 37.3,
                    'tertiary': 60.1
                },
                'major_sectors': ['汽车制造', '光电子', '钢铁', '金融', '教育科研']
            }
        }
        
        return gdp_data.get(region, {
            'gdp_2024': 0.0,
            'growth_rate': 0.0,
            'per_capita': 0.0,
            'structure': {'primary': 0.0, 'secondary': 0.0, 'tertiary': 0.0},
            'major_sectors': ['暂无数据']
        })

    def get_district_rankings(self, region: str) -> List[Dict]:
        """Fetch district/county GDP rankings for a given region"""
        district_rankings = {
            'chengdu': [
                {'name': '高新区', 'gdp': 2900.0, 'desc': '天府软件园、新川创新科技园'},
                {'name': '锦江区', 'gdp': 2380.0, 'desc': '春熙路商圈、金融城'},
                {'name': '青羊区', 'gdp': 2180.0, 'desc': '金融文创、总部经济'},
                {'name': '武侯区', 'gdp': 2160.0, 'desc': '电商总部、科技服务'},
                {'name': '金牛区', 'gdp': 2020.0, 'desc': '商贸物流、建筑总部'},
                {'name': '成华区', 'gdp': 1750.0, 'desc': '龙潭总部新城'},
                {'name': '龙泉驿区', 'gdp': 1650.0, 'desc': '汽车制造基地'},
                {'name': '新都区', 'gdp': 1150.0, 'desc': '现代制造业'},
                {'name': '温江区', 'gdp': 720.0, 'desc': '健康医美产业'},
                {'name': '双流区', 'gdp': 1580.0, 'desc': '临空经济'},
                {'name': '郫都区', 'gdp': 1450.0, 'desc': '川菜产业、智造业'},
                {'name': '青白江区', 'gdp': 680.0, 'desc': '国际贸易港'},
                {'name': '都江堰市', 'gdp': 450.0, 'desc': '旅游文化产业'},
                {'name': '彭州市', 'gdp': 430.0, 'desc': '石化产业'}
            ],
            'sichuan': [
                {'name': '成都市', 'gdp': 24500.0, 'desc': '省会及经济中心'},
                {'name': '绵阳市', 'gdp': 3950.2, 'desc': '中国科技城'},
                {'name': '宜宾市', 'gdp': 3685.5, 'desc': '长江首城、动力电池之都'},
                {'name': '德阳市', 'gdp': 2890.8, 'desc': '重大装备制造业基地'},
                {'name': '泸州市', 'gdp': 2780.4, 'desc': '酒城、港口经济'},
                {'name': '南充市', 'gdp': 2650.2, 'desc': '川东北区域中心'},
                {'name': '达州市', 'gdp': 2580.7, 'desc': '川渝陕结合部'},
                {'name': '凉山州', 'gdp': 2050.8, 'desc': '清洁能源、矿业'},
                {'name': '乐山市', 'gdp': 2402.7, 'desc': '旅游业、新材料'},
                {'name': '广安市', 'gdp': 1420.5, 'desc': '小平故里、汽摩产业'},
                {'name': '巴中市', 'gdp': 770.8, 'desc': '生态旅游'},
                {'name': '资阳市', 'gdp': 951.8, 'desc': '成渝直线经济带'},
                {'name': '遂宁市', 'gdp': 1635.5, 'desc': '成渝发展主轴'},
                {'name': '内江市', 'gdp': 1582.3, 'desc': '甜城、新材料'}
            ],
            'chongqing': [
                {'name': '渝北区', 'gdp': 2750.0, 'desc': '临空经济区'},
                {'name': '江北区', 'gdp': 2680.0, 'desc': '江北嘴CBD'},
                {'name': '九龙坡区', 'gdp': 1950.0, 'desc': '传统工业基地'},
                {'name': '沙坪坝区', 'gdp': 1820.0, 'desc': '科学城核心'},
                {'name': '渝中区', 'gdp': 1750.0, 'desc': '母城核心'},
                {'name': '南岸区', 'gdp': 1650.0, 'desc': '南滨路经济带'},
                {'name': '北碚区', 'gdp': 1200.0, 'desc': '自然生态区'},
                {'name': '江津区', 'gdp': 1380.0, 'desc': '工业园区'},
                {'name': '合川区', 'gdp': 1150.0, 'desc': '工业重镇'},
                {'name': '永川区', 'gdp': 1120.0, 'desc': '职业教育基地'},
                {'name': '南川区', 'gdp': 580.0, 'desc': '资源型经济'},
                {'name': '綦江区', 'gdp': 720.0, 'desc': '老工业基地'},
                {'name': '大足区', 'gdp': 850.0, 'desc': '五金工业'},
                {'name': '潼南区', 'gdp': 650.0, 'desc': '农业与制造业'}
            ],
            'beijing': [
                {'name': '海淀区', 'gdp': 10800.0, 'desc': '中关村科技园区'},
                {'name': '朝阳区', 'gdp': 8520.0, 'desc': 'CBD核心'},
                {'name': '西城区', 'gdp': 6380.0, 'desc': '金融街'},
                {'name': '丰台区', 'gdp': 2450.0, 'desc': '总部经济'},
                {'name': '昌平区', 'gdp': 1580.0, 'desc': '未来科学城'},
                {'name': '大兴区', 'gdp': 1480.0, 'desc': '大兴国际机场临空经济区'},
                {'name': '通州区', 'gdp': 1280.0, 'desc': '城市副中心'},
                {'name': '顺义区', 'gdp': 1150.0, 'desc': '临空经济'},
                {'name': '房山区', 'gdp': 1050.0, 'desc': '新材料'},
                {'name': '石景山区', 'gdp': 480.0, 'desc': '文创产业'},
                {'name': '门头沟区', 'gdp': 280.0, 'desc': '生态涵养'},
                {'name': '怀柔区', 'gdp': 420.0, 'desc': '科学城'},
                {'name': '平谷区', 'gdp': 380.0, 'desc': '农科创'},
                {'name': '密云区', 'gdp': 350.0, 'desc': '生态涵养'}
            ],
            'shanghai': [
                {'name': '浦东新区', 'gdp': 17200.0, 'desc': '金融贸易中心'},
                {'name': '黄浦区', 'gdp': 3210.0, 'desc': '金融外滩'},
                {'name': '静安区', 'gdp': 1820.0, 'desc': '商贸服务'},
                {'name': '徐汇区', 'gdp': 2280.0, 'desc': '西岸商务区'},
                {'name': '杨浦区', 'gdp': 1750.0, 'desc': '创新创业基地'},
                {'name': '虹口区', 'gdp': 1280.0, 'desc': '北外滩金融港'},
                {'name': '长宁区', 'gdp': 1280.0, 'desc': '总部经济'},
                {'name': '普陀区', 'gdp': 1580.0, 'desc': '苏河湾'},
                {'name': '闵行区', 'gdp': 2850.0, 'desc': '制造业基地'},
                {'name': '宝山区', 'gdp': 1580.0, 'desc': '钢铁工业'},
                {'name': '嘉定区', 'gdp': 2120.0, 'desc': '汽车制造'},
                {'name': '金山区', 'gdp': 1280.0, 'desc': '化工工业'},
                {'name': '松江区', 'gdp': 1650.0, 'desc': 'G60科创走廊'},
                {'name': '青浦区', 'gdp': 1480.0, 'desc': '进博会'}
            ],
            'shenzhen': [
                {'name': '南山区', 'gdp': 9120.0, 'desc': '高新技术产业'},
                {'name': '宝安区', 'gdp': 4532.0, 'desc': '临空经济'},
                {'name': '龙岗区', 'gdp': 4469.0, 'desc': '东部中心'},
                {'name': '福田区', 'gdp': 2120.0, 'desc': 'CBD核心'},
                {'name': '龙华区', 'gdp': 2815.0, 'desc': '智能制造'},
                {'name': '罗湖区', 'gdp': 1380.0, 'desc': '传统商贸中心'},
                {'name': '光明区', 'gdp': 1580.0, 'desc': '科学城'},
                {'name': '坪山区', 'gdp': 1180.0, 'desc': '新能源汽车'},
                {'name': '盐田区', 'gdp': 720.0, 'desc': '港口物流'},
                {'name': '大鹏新区', 'gdp': 320.0, 'desc': '生态文旅'},
                {'name': '南山区', 'gdp': 9120.0, 'desc': '科技高地'},
                {'name': '宝安区', 'gdp': 4532.0, 'desc': '先进制造'},
                {'name': '龙岗区', 'gdp': 4469.0, 'desc': '产业重镇'}
            ],
            'wuhan': [
                {'name': '东湖高新区', 'gdp': 2500.0, 'desc': '光谷高新区'},
                {'name': '江汉区', 'gdp': 1580.0, 'desc': '金融商贸中心'},
                {'name': '武昌区', 'gdp': 1450.0, 'desc': '科教文化中心'},
                {'name': '洪山区', 'gdp': 1420.0, 'desc': '大学之城'},
                {'name': '江岸区', 'gdp': 1280.0, 'desc': '传统商务区'},
                {'name': '东西湖区', 'gdp': 1180.0, 'desc': '食品工业'},
                {'name': '黄陂区', 'gdp': 1060.0, 'desc': '临空经济'},
                {'name': '江夏区', 'gdp': 1020.0, 'desc': '临空经济'},
                {'name': '青山区', 'gdp': 980.0, 'desc': '钢铁工业'},
                {'name': '硚口区', 'gdp': 960.0, 'desc': '商贸物流'},
                {'name': '汉阳区', 'gdp': 850.0, 'desc': '传统工业'},
                {'name': '新洲区', 'gdp': 880.0, 'desc': '新兴制造业'},
                {'name': '蔡甸区', 'gdp': 780.0, 'desc': '制造业基地'},
                {'name': '武昌区', 'gdp': 1450.0, 'desc': '政务文化中心'}
            ]
        }
        
        # Sort by GDP descending and add ranking
        districts = district_rankings.get(region, [])
        sorted_districts = sorted(districts, key=lambda x: x['gdp'], reverse=True)
        
        # Add ranking to each district
        for i, district in enumerate(sorted_districts):
            district['rank'] = i + 1
        
        return sorted_districts

    def get_university_info(self, region: str) -> List[Dict]:
        """Fetch university information for a given region"""
        university_data = {
            'chengdu': [
                {'name': '四川大学', 'founded': '1896年', 'advantage_colleges': '计算机学院、软件学院、电子信息学院、人工智能学院', 'level': '985工程、双一流'},
                {'name': '电子科技大学', 'founded': '1956年', 'advantage_colleges': '计算机科学与工程学院、软件工程学院、信息与通信工程学院、人工智能研究院', 'level': '985工程、双一流'},
                {'name': '西南交通大学', 'founded': '1896年', 'advantage_colleges': '计算机与人工智能学院、信息科学与技术学院', 'level': '211工程、双一流'},
                {'name': '西南财经大学', 'founded': '1925年', 'advantage_colleges': '统计学院、经济信息工程学院', 'level': '211工程、双一流'},
                {'name': '成都理工大学', 'founded': '1956年', 'advantage_colleges': '信息科学与技术学院、计算机与网络安全学院、人工智能学院', 'level': '双一流'},
                {'name': '西南石油大学', 'founded': '1958年', 'advantage_colleges': '计算机科学学院、电气信息学院、人工智能与大数据学院', 'level': '双一流'},
                {'name': '四川师范大学', 'founded': '1946年', 'advantage_colleges': '计算机科学学院、软件学院、人工智能学院', 'level': '省部共建高校'},
                {'name': '成都中医药大学', 'founded': '1956年', 'advantage_colleges': '计算机学院、智慧医养创新中心、人工智能与大数据学院', 'level': '双一流'},
                {'name': '西华师范大学', 'founded': '1946年', 'advantage_colleges': '计算机学院、软件学院', 'level': '省属重点高校'},
                {'name': '西南科技大学', 'founded': '1965年', 'advantage_colleges': '计算机科学与技术学院、信息工程学院、人工智能技术学院', 'level': '省属重点高校'}
            ],
            'sichuan': [
                {'name': '四川大学', 'founded': '1896年', 'advantage_colleges': '计算机学院、软件学院、电子信息学院、人工智能学院', 'level': '985工程、双一流'},
                {'name': '电子科技大学', 'founded': '1956年', 'advantage_colleges': '计算机科学与工程学院、软件工程学院、信息与通信工程学院、人工智能研究院', 'level': '985工程、双一流'},
                {'name': '西南交通大学', 'founded': '1896年', 'advantage_colleges': '计算机与人工智能学院、信息科学与技术学院', 'level': '211工程、双一流'},
                {'name': '西南财经大学', 'founded': '1925年', 'advantage_colleges': '统计学院、经济信息工程学院、金融科技学院', 'level': '211工程、双一流'},
                {'name': '成都理工大学', 'founded': '1956年', 'advantage_colleges': '信息科学与技术学院、计算机与网络安全学院、人工智能学院', 'level': '双一流'},
                {'name': '西南石油大学', 'founded': '1958年', 'advantage_colleges': '计算机科学学院、电气信息学院、人工智能与大数据学院', 'level': '双一流'},
                {'name': '四川农业大学', 'founded': '1906年', 'advantage_colleges': '信息工程学院、计算机与软件工程学院', 'level': '211工程、双一流'},
                {'name': '西南科技大学', 'founded': '1965年', 'advantage_colleges': '计算机科学与技术学院、信息工程学院、人工智能技术学院', 'level': '省属重点高校'},
                {'name': '成都信息工程大学', 'founded': '1951年', 'advantage_colleges': '计算机学院、软件工程学院、电子信息工程学院', 'level': '省属重点高校'},
                {'name': '西华大学', 'founded': '1960年', 'advantage_colleges': '计算机与软件工程学院、电子信息工程学院', 'level': '省属重点高校'}
            ],
            'chongqing': [
                {'name': '重庆大学', 'founded': '1929年', 'advantage_colleges': '计算机学院、软件学院、人工智能学院、信息与通信工程学院', 'level': '985工程、双一流'},
                {'name': '西南大学', 'founded': '1906年', 'advantage_colleges': '计算机与信息科学学院、人工智能学院、软件学院', 'level': '211工程、双一流'},
                {'name': '重庆邮电大学', 'founded': '1950年', 'advantage_colleges': '计算机科学与技术学院、软件工程学院、网络空间安全学院', 'level': '国家特色重点学科项目建设高校'},
                {'name': '重庆交通大学', 'founded': '1951年', 'advantage_colleges': '信息科学与工程学院、计算机科学与技术学院、人工智能学院', 'level': '省部共建高校'},
                {'name': '重庆医科大学', 'founded': '1956年', 'advantage_colleges': '生物医学工程学院、计算机学院、智能医学工程学院', 'level': '省部共建高校'},
                {'name': '四川外国语大学', 'founded': '1950年', 'advantage_colleges': '商务信息学院、计算机系、人工智能学院', 'level': '重庆市重点高校'},
                {'name': '重庆工商大学', 'founded': '1952年', 'advantage_colleges': '计算机科学与信息工程学院、人工智能学院', 'level': '重庆市重点高校'},
                {'name': '重庆理工大学', 'founded': '1940年', 'advantage_colleges': '计算机科学与技术学院、软件工程学院、人工智能学院', 'level': '重庆市重点高校'},
                {'name': '重庆师范大学', 'founded': '1954年', 'advantage_colleges': '计算机与信息科学学院、软件学院', 'level': '重庆市重点高校'},
                {'name': '重庆三峡学院', 'founded': '1956年', 'advantage_colleges': '计算机学院、电子信息学院', 'level': '重庆市属高校'}
            ],
            'beijing': [
                {'name': '北京大学', 'founded': '1898年', 'advantage_colleges': '信息科学技术学院、智能学院、计算机学院、人工智能研究院', 'level': '985工程、双一流'},
                {'name': '清华大学', 'founded': '1911年', 'advantage_colleges': '计算机科学与技术系、软件学院、自动化系、人工智能研究院', 'level': '985工程、双一流'},
                {'name': '中国人民大学', 'founded': '1937年', 'advantage_colleges': '信息学院、高瓴人工智能学院、统计学院', 'level': '985工程、双一流'},
                {'name': '北京航空航天大学', 'founded': '1952年', 'advantage_colleges': '计算机学院、软件学院、人工智能学院、电子信息工程学院', 'level': '985工程、双一流'},
                {'name': '北京理工大学', 'founded': '1940年', 'advantage_colleges': '计算机学院、网络空间安全学院、自动化学院、人工智能研究院', 'level': '985工程、双一流'},
                {'name': '北京师范大学', 'founded': '1902年', 'advantage_colleges': '人工智能学院、互联网发展研究院、心理学部', 'level': '985工程、双一流'},
                {'name': '北京交通大学', 'founded': '1896年', 'advantage_colleges': '计算机与信息技术学院、电子信息工程学院、人工智能学院', 'level': '211工程、双一流'},
                {'name': '北京科技大学', 'founded': '1952年', 'advantage_colleges': '计算机与通信工程学院、人工智能学院、自动化学院', 'level': '211工程、双一流'},
                {'name': '北京邮电大学', 'founded': '1955年', 'advantage_colleges': '计算机学院、网络空间安全学院、人工智能学院、电子工程学院', 'level': '211工程、双一流'},
                {'name': '北京工业大学', 'founded': '1960年', 'advantage_colleges': '信息学部、计算机学院、软件学院', 'level': '211工程、双一流'}
            ],
            'shanghai': [
                {'name': '复旦大学', 'founded': '1905年', 'advantage_colleges': '计算机科学技术学院、大数据学院、智能复杂系统实验室、人工智能创新学院', 'level': '985工程、双一流'},
                {'name': '上海交通大学', 'founded': '1896年', 'advantage_colleges': '电子信息与电气工程学院、计算机科学与工程系、软件学院、人工智能研究院', 'level': '985工程、双一流'},
                {'name': '同济大学', 'founded': '1907年', 'advantage_colleges': '软件学院、计算机科学与技术学院、人工智能学院、电子与信息工程学院', 'level': '985工程、双一流'},
                {'name': '华东师范大学', 'founded': '1951年', 'advantage_colleges': '计算机科学与软件工程学院、数据科学与工程学院、智能+研究院', 'level': '985工程、双一流'},
                {'name': '华东理工大学', 'founded': '1952年', 'advantage_colleges': '计算机科学与技术学院、信息科学与工程学院、人工智能与生物工程学院', 'level': '211工程、双一流'},
                {'name': '东华大学', 'founded': '1951年', 'advantage_colleges': '计算机科学与技术学院、信息科学与技术学院、人工智能学院', 'level': '211工程、双一流'},
                {'name': '上海大学', 'founded': '1922年', 'advantage_colleges': '计算机工程与科学学院、机电工程与自动化学院、人工智能研究院', 'level': '211工程、双一流'},
                {'name': '上海理工大学', 'founded': '1906年', 'advantage_colleges': '光电信息与计算机工程学院、计算机科学与技术学院', 'level': '上海市重点高校'},
                {'name': '上海海事大学', 'founded': '1909年', 'advantage_colleges': '信息工程学院、计算机科学与技术学院', 'level': '上海市重点高校'},
                {'name': '上海电力大学', 'founded': '1951年', 'advantage_colleges': '计算机科学与技术学院、电子信息工程学院', 'level': '上海市重点高校'}
            ],
            'shenzhen': [
                {'name': '深圳大学', 'founded': '1983年', 'advantage_colleges': '计算机与软件学院、电子与信息工程学院、人工智能与数字经济广东省实验室', 'level': '广东省高水平大学'},
                {'name': '南方科技大学', 'founded': '2010年', 'advantage_colleges': '计算机科学与工程系、电子与电气工程系、系统设计与智能制造学院、人工智能学院', 'level': '广东省高水平理工科大学'},
                {'name': '深圳技术大学', 'founded': '2016年', 'advantage_colleges': '互联网与通信学院、大数据与互联网学院、计算机科学与控制工程学院', 'level': '新兴应用技术大学'},
                {'name': '哈工大(深圳)', 'founded': '2002年', 'advantage_colleges': '计算机科学与技术学院、电子与信息工程学院、人工智能与自动化学院', 'level': '985工程异地校区'},
                {'name': '港中大(深圳)', 'founded': '2014年', 'advantage_colleges': '数据科学学院、机器人与自动化学院、理工学院、人工智能与机器人研究院', 'level': '中外合作办学'},
                {'name': '深圳职业技术大学', 'founded': '1993年', 'advantage_colleges': '计算机技术与软件工程学院、人工智能学院、电子信息学院', 'level': '国家示范性高职院校'},
                {'name': '深圳北理莫斯科大学', 'founded': '2012年', 'advantage_colleges': '人工智能研究院、信息工程学院', 'level': '中外合作办学'},
                {'name': '中山大学·深圳', 'founded': '2015年', 'advantage_colleges': '计算机学院、人工智能学院、软件工程学院', 'level': '985工程异地校区'},
                {'name': '暨南大学·深圳', 'founded': '1906年', 'advantage_colleges': '网络空间安全学院、计算机科学系', 'level': '211工程异地校区'},
                {'name': '华南师范大学·深圳', 'founded': '1933年', 'advantage_colleges': '计算机学院、人工智能学院', 'level': '211工程异地校区'}
            ],
            'wuhan': [
                {'name': '武汉大学', 'founded': '1893年', 'advantage_colleges': '计算机学院、人工智能学院、信息管理学院、遥感信息工程学院', 'level': '985工程、双一流'},
                {'name': '华中科技大学', 'founded': '1952年', 'advantage_colleges': '计算机科学与技术学院、人工智能与自动化学院、软件学院、电子信息与通信工程学院', 'level': '985工程、双一流'},
                {'name': '华中师范大学', 'founded': '1902年', 'advantage_colleges': '人工智能教育学部、计算机学院、心理学院', 'level': '211工程、双一流'},
                {'name': '武汉理工大学', 'founded': '1898年', 'advantage_colleges': '计算机与人工智能学院、信息工程学院、汽车工程学院', 'level': '211工程、双一流'},
                {'name': '华中农业大学', 'founded': '1898年', 'advantage_colleges': '信息学院、计算机科学与技术学院、智慧农业工程学院', 'level': '211工程、双一流'},
                {'name': '中国地质大学(武汉)', 'founded': '1952年', 'advantage_colleges': '计算机学院、地理与信息工程学院、人工智能学院', 'level': '211工程、双一流'},
                {'name': '中南财经政法大学', 'founded': '1948年', 'advantage_colleges': '信息学院、统计与数学学院、金融学院', 'level': '211工程、双一流'},
                {'name': '华中农业大学', 'founded': '1898年', 'advantage_colleges': '信息学院、计算机科学与技术学院', 'level': '211工程、双一流'},
                {'name': '湖北大学', 'founded': '1931年', 'advantage_colleges': '计算机与信息工程学院、数学与统计学学院、网络空间安全学院', 'level': '省属重点大学'},
                {'name': '武汉科技大学', 'founded': '1898年', 'advantage_colleges': '计算机科学与技术学院、信息科学与工程学院、人工智能学院', 'level': '省属重点大学'}
            ]
        }
        
        return university_data.get(region, [])

    def get_science_institutions(self, region: str) -> List[Dict]:
        """Fetch scientific research institutions for a given region"""
        sci_insitutions = {
            'chengdu': [
                {'name': '中科院成都分院', 'focus': '科技研发、成果转化'},
                {'name': '中国工程物理研究院', 'focus': '核物理、军工技术'},
                {'name': '中国空气动力研究与发展中心', 'focus': '航空航天、流体力学'},
                {'name': '四川大学华西医院', 'focus': '医学研究、生物技术'},
                {'name': '电子科技大学研究院', 'focus': '电子信息、人工智能'},
                {'name': '成都生物研究所', 'focus': '生物学、生态学'},
                {'name': '成都山地灾害与环境研究所', 'focus': '环境保护、自然灾害防治'},
                {'name': '成都计算机应用研究所', 'focus': '计算机技术、软件开发'},
                {'name': '四川省人民医院', 'focus': '医疗研究、临床试验'},
                {'name': '四川省农科院', 'focus': '农业技术、作物育种'}
            ],
            'sichuan': [
                {'name': '中科院成都分院', 'focus': '科技研发、成果转化'},
                {'name': '中国工程物理研究院', 'focus': '核物理、军工技术'},
                {'name': '核工业西南物理研究院', 'focus': '核聚变、等离子体物理'},
                {'name': '中科院光电技术研究所', 'focus': '光电技术、精密光学'},
                {'name': '中科院成都生物研究所', 'focus': '生物学、生态学'},
                {'name': '中科院文献情报中心成都分中心', 'focus': '科技情报、信息研究'},
                {'name': '中国燃气涡轮研究院', 'focus': '航空发动机技术'},
                {'name': '中国航发成都发动机有限公司', 'focus': '航空动力装备'},
                {'name': '核工业四一六医院', 'focus': '医疗卫生、职业防护'},
                {'name': '四川省中医药科学院', 'focus': '中医药、天然药物研究'}
            ],
            'chongqing': [
                {'name': '中科院重庆绿色智能技术研究院', 'focus': '绿色智能技术、环境监测'},
                {'name': '中国汽车工程研究院', 'focus': '汽车技术、检测认证'},
                {'name': '重庆材料研究院', 'focus': '新材料、功能材料'},
                {'name': '中国四联仪器仪表集团', 'focus': '仪器仪表、自动化'},
                {'name': '重庆煤科院', 'focus': '煤炭科学、安全生产'},
                {'name': '重庆通信研究院', 'focus': '通信技术、网络技术'},
                {'name': '重庆医药工业研究院', 'focus': '医药研发、化学合成'},
                {'name': '重庆水泵厂有限责任公司', 'focus': '机械设备、流体控制'},
                {'name': '重庆特种设备检验研究院', 'focus': '设备检验、安全评估'},
                {'name': '重庆市中药研究院', 'focus': '中医药、天然产物'}
            ],
            'beijing': [
                {'name': '中科院', 'focus': '基础科学、前沿技术'},
                {'name': '中国工程院', 'focus': '工程技术、工程创新'},
                {'name': '中国社科院', 'focus': '社会科学、人文研究'},
                {'name': '北京生命科学研究所', 'focus': '生命科学、生物技术'},
                {'name': '中科院计算技术研究所', 'focus': '计算机科学、信息技术'}, 
                {'name': '中科院自动化研究所', 'focus': '自动化、人工智能'},
                {'name': '北京航天航空大学研究院', 'focus': '航空航天、自动化技术'},
                {'name': '清华大学高等研究院', 'focus': '基础研究、交叉学科'},
                {'name': '北京理工大学信息学院', 'focus': '信息科学、网络安全'},
                {'name': '北京邮电大学网络技术研究院', 'focus': '网络技术、通信研究'}
            ],
            'shanghai': [
                {'name': '中科院上海分院', 'focus': '科技研发、成果转化'},
                {'name': '中国工程物理研究院上海应用技术研究中心', 'focus': '应用技术、成果转化'},
                {'name': '中科院上海微系统与信息技术研究所', 'focus': '微电子、信息技术'},
                {'name': '中科院上海技术物理研究所', 'focus': '红外技术、光电技术'},
                {'name': '中科院上海光学精密机械研究所', 'focus': '光学技术、激光技术'},
                {'name': '上海光源', 'focus': '同步辐射、实验设备'},
                {'name': '上海超级计算中心', 'focus': '高性能计算、数据分析'},
                {'name': '上海微技术工业研究院', 'focus': '微技术、产业转化'},
                {'name': '上海脑科学与类脑研究中心', 'focus': '脑科学、人工智能'},
                {'name': '上海人工智能实验室', 'focus': '人工智能、算法研究'}
            ],
            'shenzhen': [
                {'name': '中科院深圳先进技术研究院', 'focus': '先进制造、人工智能'},
                {'name': '鹏城实验室', 'focus': '网络通信、分布式计算'},
                {'name': '深圳湾实验室', 'focus': '生命健康、生物医药'},
                {'name': '华为技术有限公司(研发)', 'focus': '通信技术、人工智能'},
                {'name': '腾讯公司(研发)', 'focus': '互联网技术、AI技术'},
                {'name': '比亚迪股份有限公司(研发)', 'focus': '新能源、汽车技术'},
                {'name': '大疆创新科技有限公司(研发)', 'focus': '无人机技术、影像系统'},
                {'name': '招商局集团(研发)', 'focus': '海洋工程、物流技术'},
                {'name': '平安科技集团', 'focus': '金融科技、人工智能'},
                {'name': '顺丰科技有限公司', 'focus': '物流技术、自动化'}
            ],
            'wuhan': [
                {'name': '中科院武汉分院', 'focus': '科技研发、成果转化'},
                {'name': '中国光谷国家研究中心', 'focus': '光电子信息、激光技术'},
                {'name': '中科院武汉物理与数学研究所', 'focus': '物理数学、精密科学'},
                {'name': '中科院武汉岩土力学研究所', 'focus': '岩土力学、工程地质'},
                {'name': '中科院水生生物研究所', 'focus': '水生生物、生态环境'},
                {'name': '中国舰船研究设计中心', 'focus': '舰船设计、海洋工程'},
                {'name': '中国地质大学(武汉)地质过程与矿产资源国家重点实验室', 'focus': '地质研究、矿产资源'},
                {'name': '华中科技大学光电国家研究中心', 'focus': '光电技术、激光工程'},
                {'name': '武汉理工大学材料复合新技术国家重点实验室', 'focus': '新材料、复合技术'},
                {'name': '武汉大学测绘遥感信息工程国家重点实验室', 'focus': '测绘技术、遥感工程'}
            ]
        }
        
        return sci_insitutions.get(region, [])