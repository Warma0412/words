from flask import Flask, render_template, request, jsonify
import spacy
from spacy import displacy
import nltk
from nltk.tree import Tree
import json
import re
import io

app = Flask(__name__)

# 自动下载nltk必要数据
def download_nltk_data():
    """
    自动下载nltk必要的数据包
    """
    required_packages = ['punkt', 'punkt_tab', 'averaged_perceptron_tagger', 'averaged_perceptron_tagger_eng']
    for package in required_packages:
        try:
            if 'punkt' in package:
                nltk.data.find(f'tokenizers/{package}')
            else:
                nltk.data.find(f'taggers/{package}')
        except LookupError:
            try:
                nltk.download(package, quiet=True)
            except:
                pass

# 下载nltk数据
download_nltk_data()

# 加载spaCy模型
try:
    nlp_en = spacy.load("en_core_web_sm")
except OSError:
    print("正在下载spaCy英文模型...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    nlp_en = spacy.load("en_core_web_sm")

try:
    nlp_zh = spacy.load("zh_core_web_sm")
except OSError:
    print("正在下载spaCy中文模型...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "zh_core_web_sm"])
    nlp_zh = spacy.load("zh_core_web_sm")

# 词性标签中文翻译
POS_TRANSLATIONS = {
    'NOUN': '名词',
    'VERB': '动词',
    'ADJ': '形容词',
    'ADV': '副词',
    'ADP': '介词',
    'DET': '限定词',
    'NUM': '数词',
    'PART': '小品词',
    'PRON': '代词',
    'PROPN': '专有名词',
    'PUNCT': '标点',
    'SYM': '符号',
    'INTJ': '感叹词',
    'X': '其他',
    'CCONJ': '并列连词',
    'SCONJ': '从属连词',
    'AUX': '助动词',
    'SPACE': '空格',
}

# 依存关系中文翻译 - 完整版
DEP_TRANSLATIONS = {
    'ROOT': '根节点',
    'root': '根节点',
    'nsubj': '主语',
    'nsubjpass': '被动主语',
    'dobj': '直接宾语',
    'iobj': '间接宾语',
    'pobj': '介词宾语',
    'obj': '宾语',
    'attr': '属性',
    'compound': '复合词',
    'amod': '形容词修饰语',
    'advmod': '副词修饰语',
    'det': '限定词',
    'prep': '介词',
    'agent': '施事者',
    'aux': '助动词',
    'auxpass': '被动助动词',
    'neg': '否定词',
    'conj': '并列词',
    'cc': '并列连词',
    'mark': '标记词',
    'acl': '形容词从句',
    'acl:relcl': '关系从句',
    'relcl': '关系从句',
    'advcl': '状语从句',
    'csubj': '从句主语',
    'csubjpass': '被动从句主语',
    'xcomp': '开放性补语',
    'ccomp': '从句补语',
    'parataxis': '并列结构',
    'appos': '同位语',
    'nummod': '数词修饰语',
    'poss': '所有格',
    'case': '格标记',
    'nmod': '名词修饰语',
    'nmod:poss': '所有格修饰语',
    'nmod:prep': '介词修饰语',
    'obl': '斜向依存',
    'obl:agent': '施事斜向依存',
    'expl': '形式主语',
    'punct': '标点',
    'dep': '依存',
    'discourse': '话语标记',
    'list': '列表',
    'dislocated': '错位',
    'orphan': '孤立',
    'reparandum': '修正',
    'vocative': '呼格',
    'fixed': '固定搭配',
    'flat': '扁平结构',
    'goeswith': '连写',
    'clf': '量词',
    'cop': '系动词',
    'csubj:pass': '被动从句主语',
    'obl:arg': '论元斜向依存',
    'obl:patient': '患者斜向依存',
    'nsubj:pass': '被动主语',
    'nummod:entity': '实体数词修饰语',
    'mark:relcl': '关系从句标记',
    'compound:nn': '名词复合词',
    'compound:vc': '动词复合词',
    'conj:exp': '扩展并列',
    'det:clf': '量词限定词',
    'flat:vv': '动词扁平结构',
    'flat:name': '姓名扁平结构',
    'name': '姓名',
    'range': '范围',
    'etc': '等',
}

def detect_language(text):
    """
    检测文本语言
    """
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
    if chinese_pattern.search(text):
        return 'zh'
    return 'en'

def translate_pos(pos):
    """
    翻译词性标签
    """
    return POS_TRANSLATIONS.get(pos, pos)

def translate_dep(dep):
    """
    翻译依存关系标签
    """
    return DEP_TRANSLATIONS.get(dep, dep)

def customize_svg(svg_html, doc):
    """
    自定义SVG，将词性标签翻译为中文，并优化样式
    """
    for token in doc:
        pos_zh = translate_pos(token.pos_)
        dep_zh = translate_dep(token.dep_)
        svg_html = svg_html.replace(f'>{token.pos_}<', f'>{pos_zh}<')
        svg_html = svg_html.replace(f'>{token.dep_}<', f'>{dep_zh}<')
    
    svg_html = svg_html.replace('fill: #000000', 'fill: #333333')
    svg_html = svg_html.replace('font-size: 11px', 'font-size: 13px')
    svg_html = svg_html.replace('font-family: inherit', 'font-family: "Segoe UI", Arial, sans-serif')
    
    return svg_html

@app.route('/')
def index():
    """
    主页面
    """
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    分析句子的API接口
    """
    data = request.json
    sentence = data.get('sentence', 'The boy saw the man with the telescope.')
    
    lang = detect_language(sentence)
    
    if lang == 'zh':
        nlp = nlp_zh
        lang_name = '中文'
    else:
        nlp = nlp_en
        lang_name = '英文'
    
    doc = nlp(sentence)
    
    dep_svg = displacy.render(doc, style='dep', jupyter=False, 
                               options={'compact': False, 'distance': 150, 'word_spacing': 50})
    
    dep_svg = customize_svg(dep_svg, doc)
    
    dependencies = []
    for token in doc:
        dependencies.append({
            'text': token.text,
            'lemma': token.lemma_,
            'pos': token.pos_,
            'pos_zh': translate_pos(token.pos_),
            'tag': token.tag_,
            'dep': token.dep_,
            'dep_zh': translate_dep(token.dep_),
            'head': token.head.text,
            'head_i': token.head.i,
            'i': token.i,
            'children': [child.text for child in token.children]
        })
    
    constituency_tree = generate_constituency_tree(sentence, lang)
    core_args = extract_core_args(doc)
    
    return jsonify({
        'dep_svg': dep_svg,
        'dependencies': dependencies,
        'constituency_tree': constituency_tree,
        'core_args': core_args,
        'language': lang,
        'language_name': lang_name
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    上传文档并提取文本
    """
    if 'file' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    filename = file.filename.lower()
    
    try:
        if filename.endswith('.txt'):
            text = file.read().decode('utf-8')
        elif filename.endswith('.pdf'):
            text = extract_text_from_pdf(file)
        elif filename.endswith('.docx'):
            text = extract_text_from_docx(file)
        else:
            return jsonify({'error': '不支持的文件格式，请上传 .txt, .pdf 或 .docx 文件'}), 400
        
        text = text.strip()
        if not text:
            return jsonify({'error': '文件内容为空'}), 400
        
        sentences = extract_sentences(text)
        
        return jsonify({
            'success': True,
            'text': text,
            'sentences': sentences,
            'sentence_count': len(sentences)
        })
        
    except Exception as e:
        return jsonify({'error': f'文件处理失败: {str(e)}'}), 500

def extract_text_from_pdf(file):
    """
    从PDF文件提取文本
    """
    try:
        import PyPDF2
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text() + '\n'
        return text
    except ImportError:
        return "错误: 请安装 PyPDF2 库 (pip install PyPDF2)"

def extract_text_from_docx(file):
    """
    从Word文档提取文本
    """
    try:
        from docx import Document
        doc = Document(io.BytesIO(file.read()))
        text = ''
        for paragraph in doc.paragraphs:
            text += paragraph.text + '\n'
        return text
    except ImportError:
        return "错误: 请安装 python-docx 库 (pip install python-docx)"

def extract_sentences(text):
    """
    从文本中提取句子
    """
    sentences = re.split(r'[。.!?！？\n]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences[:20]

def generate_constituency_tree(sentence, lang='en'):
    """
    使用nltk生成成分句法树
    """
    if lang == 'zh':
        nlp = nlp_zh
        doc = nlp(sentence)
        tokens = [token.text for token in doc]
        tagged = [(token.text, token.pos_) for token in doc]
    else:
        tokens = nltk.word_tokenize(sentence)
        tagged = nltk.pos_tag(tokens)
    
    if lang == 'zh':
        grammar = r"""
            NP: {<NOUN|PROPN|PRON>+}
            VP: {<VERB|AUX><NP|PP|ADJP>*}
            PP: {<ADP><NP>}
            ADJP: {<ADJ>+}
            ADVP: {<ADV>+}
        """
    else:
        grammar = r"""
            NP: {<DT>?<JJ.*>*<NN.*>+}
            PP: {<IN><NP>}
            VP: {<VB.*><NP|PP|CLAUSE>+$}
            CLAUSE: {<NP><VP>}
        """
    
    chunk_parser = nltk.RegexpParser(grammar)
    tree = chunk_parser.parse(tagged)
    
    def tree_to_dict(t):
        if isinstance(t, tuple):
            return {'type': 'word', 'text': t[0], 'pos': t[1], 'pos_zh': translate_pos(t[1])}
        elif isinstance(t, str):
            return {'type': 'word', 'text': t}
        else:
            return {
                'type': 'phrase',
                'label': t.label(),
                'children': [tree_to_dict(child) for child in t]
            }
    
    return tree_to_dict(tree)

def extract_core_args(doc):
    """
    提取核心论元（带中文翻译）
    """
    core_args = []
    
    for token in doc:
        dep_lower = token.dep_.lower()
        
        if dep_lower in ['root']:
            core_args.append({
                'type': 'Root',
                'type_zh': '根节点',
                'text': token.text,
                'position': token.i + 1,
                'description': '根节点（谓语）'
            })
        elif dep_lower in ['nsubj', 'nsubj:pass']:
            core_args.append({
                'type': 'nsubj',
                'type_zh': '主语',
                'text': token.text,
                'position': token.i + 1,
                'description': '主语'
            })
        elif dep_lower in ['dobj', 'obj']:
            core_args.append({
                'type': 'dobj',
                'type_zh': '直接宾语',
                'text': token.text,
                'position': token.i + 1,
                'description': '直接宾语'
            })
        elif dep_lower in ['pobj', 'iobj']:
            core_args.append({
                'type': dep_lower,
                'type_zh': '宾语',
                'text': token.text,
                'position': token.i + 1,
                'description': '宾语'
            })
    
    return core_args

if __name__ == '__main__':
    import os
    print("=" * 60)
    print("歧义侦探 - 句法透视仪")
    print("=" * 60)
    print("支持语言: 中文 / 英文")
    print("支持文件: .txt / .pdf / .docx")
    print("启动Web服务器...")
    port = int(os.environ.get('PORT', 5000))
    print(f"请在浏览器中打开: http://localhost:{port}")
    print("=" * 60)
    app.run(debug=False, host='0.0.0.0', port=port)
