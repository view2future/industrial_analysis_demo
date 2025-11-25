from typing import Dict, List, Any
import json

class MindMapGenerator:
    def __init__(self):
        pass
    
    def generate_mindmap_data(self, parsed_content: Dict) -> Dict:
        """Generate mindmap structure from parsed content"""
        root_topic = parsed_content.get('metadata', {}).get('title', 'Policy Document')
        
        mindmap_data = {
            'meta': {
                'name': 'Policy Mindmap',
                'author': 'Policy Analysis System'
            },
            'format': 'node_array',
            'data': self._build_mindmap_structure(parsed_content, root_topic)
        }
        return mindmap_data
    
    def _build_mindmap_structure(self, parsed_content: Dict, root_topic: str) -> Dict:
        """Build hierarchical mindmap structure"""
        root_node = {
            'id': 'root',
            'topic': root_topic,
            'isroot': True,
            'children': []
        }
        
        # Add main categories as top-level nodes
        children = []
        
        # Add metadata
        metadata = parsed_content.get('metadata', {})
        if metadata:
            meta_node = {
                'id': 'metadata',
                'topic': '文档信息',
                'children': []
            }
            meta_children = []
            if metadata.get('issuing_authority'):
                meta_children.append({
                    'id': 'authority',
                    'topic': f"发文机关: {metadata['issuing_authority']}"
                })
            if metadata.get('publication_date'):
                meta_children.append({
                    'id': 'date',
                    'topic': f"发布日期: {metadata['publication_date']}"
                })
            if metadata.get('applicable_regions'):
                regions_str = ', '.join(metadata['applicable_regions'][:3])
                if len(metadata['applicable_regions']) > 3:
                    regions_str += f" 等{len(metadata['applicable_regions'])}个地区"
                meta_children.append({
                    'id': 'regions',
                    'topic': f"适用区域: {regions_str}"
                })
            if metadata.get('key_industries'):
                industries_str = ', '.join(metadata['key_industries'][:3])
                if len(metadata['key_industries']) > 3:
                    industries_str += f" 等{len(metadata['key_industries'])}个产业"
                meta_children.append({
                    'id': 'industries',
                    'topic': f"重点产业: {industries_str}"
                })
            if meta_children:
                meta_node['children'] = meta_children
                children.append(meta_node)
        
        # Add provisions
        provisions = parsed_content.get('provisions', [])
        if provisions:
            prov_node = {
                'id': 'provisions',
                'topic': f'政策条款 ({len(provisions)}项)',
                'children': []
            }
            for i, prov in enumerate(provisions[:10]):  # Limit to 10 provisions
                if isinstance(prov, dict):
                    prov_text = prov.get('description', prov.get('type', '条款'))
                else:
                    prov_text = str(prov)
                prov_node['children'].append({
                    'id': f'prov_{i}',
                    'topic': f"{i+1}. {prov_text[:50]}{'...' if len(str(prov)) > 50 else ''}"
                })
            children.append(prov_node)
        
        # Add requirements
        requirements = parsed_content.get('requirements', [])
        if requirements:
            req_node = {
                'id': 'requirements',
                'topic': f'申请要求 ({len(requirements)}项)',
                'children': []
            }
            for i, req in enumerate(requirements[:10]):
                if isinstance(req, dict):
                    req_text = req.get('requirement', '要求')
                    req_type = req.get('type', '要求')
                else:
                    req_text = str(req)
                    req_type = '要求'
                req_node['children'].append({
                    'id': f'req_{i}',
                    'topic': f"{i+1}. {req_type}: {req_text[:50]}{'...' if len(str(req)) > 50 else ''}"
                })
            children.append(req_node)
        
        # Add quantitative data
        quant_data = parsed_content.get('quantitative_data', {})
        if any(quant_data.values()):
            quant_node = {
                'id': 'quantitative',
                'topic': '量化数据',
                'children': []
            }
            if quant_data.get('amounts'):
                amounts_node = {
                    'id': 'amounts',
                    'topic': f'资金金额 ({len(quant_data["amounts"])}项)',
                    'children': []
                }
                for i, amount in enumerate(quant_data['amounts'][:5]):
                    amounts_node['children'].append({
                        'id': f'amount_{i}',
                        'topic': str(amount)
                    })
                quant_node['children'].append(amounts_node)
            
            if quant_data.get('thresholds'):
                thresholds_node = {
                    'id': 'thresholds',
                    'topic': f'门槛条件 ({len(quant_data["thresholds"])}项)',
                    'children': []
                }
                for i, threshold in enumerate(quant_data['thresholds'][:5]):
                    thresholds_node['children'].append({
                        'id': f'threshold_{i}',
                        'topic': str(threshold)
                    })
                quant_node['children'].append(thresholds_node)
            
            if quant_data.get('ratios'):
                ratios_node = {
                    'id': 'ratios',
                    'topic': f'比例数据 ({len(quant_data["ratios"])}项)',
                    'children': []
                }
                for i, ratio in enumerate(quant_data['ratios'][:5]):
                    ratios_node['children'].append({
                        'id': f'ratio_{i}',
                        'topic': str(ratio)
                    })
                quant_node['children'].append(ratios_node)
            
            if quant_node['children']:  # Only add if there are children
                children.append(quant_node)
        
        # Add timeline
        timeline = parsed_content.get('timeline', [])
        if timeline:
            timeline_node = {
                'id': 'timeline',
                'topic': f'时间安排 ({len(timeline)}个)',
                'children': []
            }
            for i, event in enumerate(timeline[:10]):
                if isinstance(event, dict):
                    event_str = f"{event.get('date', '')} {event.get('event', '')}"
                else:
                    event_str = str(event)
                timeline_node['children'].append({
                    'id': f'event_{i}',
                    'topic': f"{i+1}. {event_str[:50]}{'...' if len(event_str) > 50 else ''}"
                })
            children.append(timeline_node)
        
        # Add document structure if available
        doc_structure = parsed_content.get('document_structure', [])
        if doc_structure:
            structure_node = {
                'id': 'structure',
                'topic': f'文档结构 ({len(doc_structure)}节)',
                'children': []
            }
            for i, section in enumerate(doc_structure[:10]):
                if isinstance(section, dict):
                    section_str = f"{section.get('identifier', '')} {section.get('title', '')}"
                else:
                    section_str = str(section)
                structure_node['children'].append({
                    'id': f'section_{i}',
                    'topic': f"{i+1}. {section_str[:50]}{'...' if len(section_str) > 50 else ''}"
                })
            children.append(structure_node)
        
        # Add relationships if available
        relationships = parsed_content.get('relationships', [])
        if relationships:
            rel_node = {
                'id': 'relationships',
                'topic': f'关系分析 ({len(relationships)}个)',
                'children': []
            }
            for i, rel in enumerate(relationships[:10]):
                if isinstance(rel, dict):
                    rel_str = f"{rel.get('from_entity', '')} → {rel.get('to_entity', '')} ({rel.get('relationship', '')})"
                else:
                    rel_str = str(rel)
                rel_node['children'].append({
                    'id': f'rel_{i}',
                    'topic': f"{i+1}. {rel_str[:50]}{'...' if len(rel_str) > 50 else ''}"
                })
            children.append(rel_node)
        
        root_node['children'] = children
        return root_node