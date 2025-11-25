# 测试文件说明

本目录包含用于自动化演示和测试的样例文件。

## 文件列表

### chengdu_ai_demo.md
- **用途**: 演示文件上传和分析功能
- **内容**: 成都人工智能产业分析报告样例
- **大小**: 约2KB
- **格式**: Markdown

### sample_industry_report.txt
- **用途**: 文本文件上传测试
- **内容**: 通用产业分析报告
- **格式**: 纯文本

## 在演示场景中使用

在YAML场景文件中引用这些文件：

```yaml
- action: fill
  selector: "input[type='file']"
  value: "auto_demo/test_files/chengdu_ai_demo.md"
  description: "上传测试文件"
```

## 添加新测试文件

1. 将文件放入此目录
2. 更新本README
3. 在场景YAML中引用新文件
