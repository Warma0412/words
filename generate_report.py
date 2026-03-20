from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# 尝试注册中文字体
def register_chinese_font():
    """
    注册中文字体
    """
    # Windows系统字体路径
    font_paths = [
        (os.path.join(os.environ.get('WINDIR', ''), 'Fonts', 'simsun.ttc'), 'SimSun'),
        (os.path.join(os.environ.get('WINDIR', ''), 'Fonts', 'simhei.ttc'), 'SimHei'),
        (os.path.join(os.environ.get('WINDIR', ''), 'Fonts', 'msyh.ttc'), 'Microsoft YaHei'),
        (os.path.join(os.environ.get('WINDIR', ''), 'Fonts', 'msyhbd.ttc'), 'Microsoft YaHei Bold'),
    ]
    
    for font_path, font_name in font_paths:
        try:
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                print(f"成功注册字体: {font_name}")
                return font_name
        except Exception as e:
            print(f"注册字体失败 {font_name}: {e}")
    
    # 如果没有找到中文字体，使用默认字体
    print("未找到中文字体，使用默认字体")
    return 'Helvetica'

# 注册中文字体
chinese_font = register_chinese_font()

# Create styles
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name='CustomNormal',
    parentStyle=styles['Normal'],
    fontName=chinese_font,
    fontSize=11,
    leading=14,
    alignment=0,
))
styles.add(ParagraphStyle(
    name='CustomTitle',
    parentStyle=styles['Heading1'],
    fontName=chinese_font,
    fontSize=18,
    leading=22,
    alignment=1,
    spaceAfter=12,
    textColor=colors.HexColor('#667eea'),
))
styles.add(ParagraphStyle(
    name='CustomSubtitle',
    parentStyle=styles['Heading2'],
    fontName=chinese_font,
    fontSize=14,
    leading=18,
    alignment=1,
    spaceAfter=8,
    textColor=colors.HexColor('#764ba2'),
))
styles.add(ParagraphStyle(
    name='CustomHeading2',
    parentStyle=styles['Heading2'],
    fontName=chinese_font,
    fontSize=14,
    leading=18,
    alignment=0,
    spaceAfter=8,
    textColor=colors.HexColor('#495057'),
))
styles.add(ParagraphStyle(
    name='CustomHeading3',
    parentStyle=styles['Heading3'],
    fontName=chinese_font,
    fontSize=12,
    leading=15,
    alignment=0,
    spaceAfter=6,
    textColor=colors.HexColor('#667eea'),
))
styles.add(ParagraphStyle(
    name='CustomCode',
    parentStyle=styles['Code'],
    fontName='Courier',
    fontSize=9,
    leading=12,
    leftIndent=20,
    backColor=colors.HexColor('#f5f7fa'),
    borderPadding=5,
))

def create_pdf():
    """
    Create PDF document
    """
    doc = SimpleDocTemplate("歧义侦探_项目报告.pdf", pagesize=letter)
    story = []
    
    # Title page
    story.append(Paragraph("歧义侦探 - 句法透视仪", styles['CustomTitle']))
    story.append(Paragraph("项目开发与歧义分析报告", styles['CustomSubtitle']))
    story.append(Spacer(1, 0.3*inch))
    
    # Part 1: Vibe Proof
    story.append(Paragraph("一、Vibe 证明：AI与编程的Prompt交互记录", styles['CustomHeading2']))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("本项目通过AI辅助开发，采用Vibe Coding模式，快速构建了功能完整的句法分析Web应用。", styles['CustomNormal']))
    story.append(Paragraph("开发过程中，AI提供了以下关键支持：", styles['CustomNormal']))
    story.append(Spacer(1, 0.1*inch))
    
    vibe_points = [
        "1. 架构设计：AI建议采用Flask前后端分离架构，实现RESTful API设计",
        "2. 双语支持：AI提示添加中英文双语支持，自动语言检测和模型切换",
        "3. 可视化优化：AI建议优化displaCy展示效果，增加词性中文翻译和滚动条",
        "4. 文档上传：AI建议集成PDF和Word文档处理功能",
        "5. 部署准备：AI协助创建Procfile、runtime.txt等部署配置",
    ]
    
    for point in vibe_points:
        story.append(Paragraph(f"• {point}", styles['CustomNormal']))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Part 2: Source Code Files
    story.append(Paragraph("二、核心源代码文件", styles['CustomHeading2']))
    story.append(Spacer(1, 0.2*inch))
    
    code_files = [
        ('app.py', 'Flask后端主程序，包含所有API接口和NLP处理逻辑'),
        ('templates/index.html', '前端HTML模板，包含页面结构和UI组件'),
        ('static/style.css', 'CSS样式文件，包含响应式设计和动画效果'),
        ('static/script.js', 'JavaScript逻辑文件，处理API调用和DOM操作'),
        ('requirements.txt', 'Python依赖列表'),
        ('Procfile', '云平台部署配置'),
        ('runtime.txt', 'Python版本指定'),
    ]
    
    for filename, description in code_files:
        story.append(Paragraph(f"<b>{filename}</b>", styles['CustomHeading3']))
        story.append(Paragraph(description, styles['CustomNormal']))
        story.append(Spacer(1, 0.1*inch))
    
    story.append(PageBreak())
    
    # Part 3: Detective Report
    story.append(Paragraph("三、侦探报告：介词短语附着歧义分析", styles['CustomHeading2']))
    story.append(Spacer(1, 0.2*inch))
    
    # Analysis sentence
    story.append(Paragraph("<b>测试句子：</b> The boy saw the man with the telescope.", styles['CustomNormal']))
    story.append(Spacer(1, 0.1*inch))
    
    # Model analysis results
    story.append(Paragraph("<b>模型分析结果：</b>", styles['CustomHeading3']))
    story.append(Spacer(1, 0.1*inch))
    
    analysis_content = """
在分析句子 "The boy saw the man with the telescope." 时，spaCy模型做出了以下"艰难决定"：

<b>1. 依存关系分析：</b>
• telescope 的依存关系指向：the man（介词宾语 pobj）
• the man 的依存关系指向：saw（直接宾语 dobj）
• with 的依存关系指向：telescope（介词 prep）

<b>2. 句法结构解读：</b>
模型将 "with the telescope" 作为一个介词短语（PP）附着在 "the man" 上，
而非附着在动词 "saw" 上。这意味着模型认为：
- "with the telescope" 是对 "the man" 的修饰
- 语义解释为："男孩看见了拿着望远镜的男人"

<b>3. 模型偏向性分析：</b>
结合课件 P48 提到的 PCFG（概率上下文无关文法）以及现代神经网络方法，模型偏向这种解释的原因如下：

<b>(1) PCFG 视角：</b>
• PCFG 基于统计概率，训练数据中 "介词 + NP" 的组合更常见
• 介词短语附着在名词上的概率高于附着在动词上
• 模型选择了概率更高的句法结构

<b>(2) 神经网络视角：</b>
• Transformer-based 模型（如 spaCy）基于大规模预训练数据
• 预训练数据中，"名词 + 介词短语"的共现频率更高
• 注意力机制倾向于将介词短语与最近的名词关联
• 这种模式在训练语料中更常见，模型习得了这种偏好

<b>(3) 语义合理性：</b>
• "拿着望远镜的男人" 是一个完整的语义单元
• "用望远镜看" 需要工具格式的理解
• 模型倾向于选择更直接、更符合语法的解释
• 这种倾向性使得模型能够处理大多数情况，但也可能产生歧义

<b>结论：</b>
模型偏向 "the man with the telescope" 这种解释，是训练数据统计规律、神经网络注意力机制和语义合理性共同作用的结果。这既体现了现代NLP模型的强大能力，也暴露了其在处理歧义时的固有倾向性。
"""
    
    story.append(Paragraph(analysis_content, styles['CustomNormal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Part 4: Application Features
    story.append(Paragraph("四、应用功能特点", styles['CustomHeading2']))
    story.append(Spacer(1, 0.2*inch))
    
    features = [
        ("双视角分析", "同时展示依存句法和成分句法"),
        ("核心论元提取", "自动识别主语、宾语等核心成分"),
        ("双语支持", "支持中文和英文句子分析"),
        ("词性翻译", "所有词性和依存关系显示中文"),
        ("文档上传", "支持 .txt, .pdf, .docx 文件"),
        ("可视化优化", "displaCy 树状图支持滚动查看"),
        ("歧义分析", "提供经典歧义句子的分析提示"),
        ("Web界面", "美观的响应式界面设计"),
    ]
    
    feature_data = [['功能', '描述']]
    for feature, desc in features:
        feature_data.append([feature, desc])
    
    feature_table = Table(feature_data, colWidths=[2.5*inch, 4*inch], style=TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f5f7fa')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), chinese_font),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(feature_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Part 5: Technology Stack
    story.append(Paragraph("五、技术栈", styles['CustomHeading2']))
    story.append(Spacer(1, 0.2*inch))
    
    tech_stack = [
        "Flask - Web应用框架",
        "spaCy - 依存句法分析",
        "NLTK - 成分句法分析",
        "displaCy - 依存关系可视化",
        "HTML/CSS/JavaScript - 前端开发",
        "PyPDF2 - PDF文档处理",
        "python-docx - Word文档处理",
    ]
    
    for tech in tech_stack:
        story.append(Paragraph(f"• {tech}", styles['CustomNormal']))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Part 6: Deployment Options
    story.append(Paragraph("六、免费部署方案", styles['CustomHeading2']))
    story.append(Spacer(1, 0.2*inch))
    
    deploy_options = [
        ("Render", "完全免费，自动部署，推荐使用"),
        ("Railway", "简单易用，免费额度充足"),
        ("PythonAnywhere", "专为Python设计，稳定可靠"),
    ]
    
    deploy_data = [['平台', '特点']]
    for platform, desc in deploy_options:
        deploy_data.append([platform, desc])
    
    deploy_table = Table(deploy_data, colWidths=[2*inch, 4*inch], style=TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f5f7fa')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), chinese_font),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(deploy_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Part 7: Project Summary
    story.append(Paragraph("七、项目总结", styles['CustomHeading2']))
    story.append(Spacer(1, 0.2*inch))
    
    summary = """
本项目成功实现了一个功能完整、界面美观的句法分析Web应用。通过AI辅助的Vibe Coding模式，快速完成了从架构设计到功能实现的全过程。

<b>主要成就：</b>
• 实现了双视角句法分析（依存+成分）
• 支持中英文双语自动检测
• 完成了词性和依存关系的中文翻译
• 优化了可视化效果，支持滚动查看
• 集成了文档上传功能
• 提供了完整的部署方案

<b>技术亮点：</b>
• 使用了两大NLP库：spaCy 和 NLTK
• 前后端分离的RESTful架构
• 响应式CSS设计，美观易用
• 自动下载和安装依赖

<b>应用价值：</b>
• 为NLP学习者提供直观的句法分析工具
• 帮助理解经典歧义句子的解析过程
• 展示了现代NLP模型的工作原理
• 可作为教学演示和实验平台

<b>未来展望：</b>
• 可扩展支持更多语言
• 可增加更多句法分析维度
• 可集成更多NLP功能（如语义角色标注）
• 可优化模型，提高歧义解析准确率
"""
    
    story.append(Paragraph(summary, styles['CustomNormal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Generate PDF
    doc.build(story)
    print("PDF生成成功：歧义侦探_项目报告.pdf")

if __name__ == '__main__':
    create_pdf()
