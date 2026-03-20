import streamlit as st
import spacy
from spacy import displacy
import nltk
from nltk.tree import Tree
import json
import re
import io

# 设置页面配置
st.set_page_config(
    page_title="歧义侦探 - 句法透视仪",
    page_icon="🔍",
    layout="wide"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #667eea;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        color: #764ba2;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .section-title {
        color: #495057;
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #667eea;
        padding-bottom: 0.5rem;
    }
    .info-box {
        background-color: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 8px 8px 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f5f7fa;
        border-radius: 8px 8px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# 自动下载nltk必要数据
@st.cache_resource
def download_nltk_data():
    """自动下载nltk必要的数据包"""
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

download_nltk_data()

# 加载spaCy模型
@st.cache_resource
def load_models():
    """加载spaCy模型"""
    models = {}
    try:
        models['en'] = spacy.load("en_core_web_sm")
    except OSError:
        st.info("正在下载spaCy英文模型...")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        models['en'] = spacy.load("en_core_web_sm")
    
    try:
        models['zh'] = spacy.load("zh_core_web_sm")
    except OSError:
        st.info("正在下载spaCy中文模型...")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "zh_core_web_sm"])
        models['zh'] = spacy.load("zh_core_web_sm")
    
    return models

# 词性标签中文翻译
POS_TRANSLATIONS = {
    'NOUN': '名词', 'VERB': '动词', 'ADJ': '形容词', 'ADV': '副词',
    'ADP': '介词', 'DET': '限定词', 'NUM': '数词', 'PART': '小品词',
    'PRON': '代词', 'PROPN': '专有名词', 'PUNCT': '标点', 'SYM': '符号',
    'INTJ': '感叹词', 'X': '其他', 'CCONJ': '并列连词', 'SCONJ': '从属连词',
    'AUX': '助动词', 'SPACE': '空格',
}

# 依存关系中文翻译
DEP_TRANSLATIONS = {
    'ROOT': '根节点', 'root': '根节点', 'nsubj': '主语', 'nsubjpass': '被动主语',
    'dobj': '直接宾语', 'iobj': '间接宾语', 'pobj': '介词宾语', 'obj': '宾语',
    'attr': '属性', 'compound': '复合词', 'amod': '形容词修饰语',
    'advmod': '副词修饰语', 'det': '限定词', 'prep': '介词', 'agent': '施事者',
    'aux': '助动词', 'auxpass': '被动助动词', 'neg': '否定词', 'conj': '并列词',
    'cc': '并列连词', 'mark': '标记词', 'acl': '形容词从句', 'acl:relcl': '关系从句',
    'relcl': '关系从句', 'advcl': '状语从句', 'csubj': '从句主语',
    'csubjpass': '被动从句主语', 'xcomp': '开放性补语', 'ccomp': '从句补语',
    'parataxis': '并列结构', 'appos': '同位语', 'nummod': '数词修饰语',
    'poss': '所有格', 'case': '格标记', 'nmod': '名词修饰语',
    'nmod:poss': '所有格修饰语', 'nmod:prep': '介词修饰语', 'obl': '斜向依存',
    'obl:agent': '施事斜向依存', 'expl': '形式主语', 'punct': '标点',
    'dep': '依存', 'discourse': '话语标记', 'list': '列表',
    'dislocated': '错位', 'orphan': '孤立', 'reparandum': '修正',
    'vocative': '呼格', 'fixed': '固定搭配', 'flat': '扁平结构',
    'goeswith': '连写', 'clf': '量词', 'cop': '系动词',
}

def detect_language(text):
    """检测文本语言"""
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
    if chinese_pattern.search(text):
        return 'zh'
    return 'en'

def translate_pos(pos):
    """翻译词性标签"""
    return POS_TRANSLATIONS.get(pos, pos)

def translate_dep(dep):
    """翻译依存关系标签"""
    return DEP_TRANSLATIONS.get(dep, dep)

def generate_constituency_tree(sentence, lang='en', nlp_models=None):
    """使用nltk生成成分句法树"""
    if lang == 'zh':
        nlp = nlp_models['zh']
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
    """提取核心论元"""
    core_args = []
    for token in doc:
        dep_lower = token.dep_.lower()
        if dep_lower in ['root']:
            core_args.append({
                'type': 'Root', 'type_zh': '根节点',
                'text': token.text, 'position': token.i + 1,
                'description': '根节点（谓语）'
            })
        elif dep_lower in ['nsubj', 'nsubj:pass']:
            core_args.append({
                'type': 'nsubj', 'type_zh': '主语',
                'text': token.text, 'position': token.i + 1,
                'description': '主语'
            })
        elif dep_lower in ['dobj', 'obj']:
            core_args.append({
                'type': 'dobj', 'type_zh': '直接宾语',
                'text': token.text, 'position': token.i + 1,
                'description': '直接宾语'
            })
        elif dep_lower in ['pobj', 'iobj']:
            core_args.append({
                'type': dep_lower, 'type_zh': '宾语',
                'text': token.text, 'position': token.i + 1,
                'description': '宾语'
            })
    return core_args

def display_tree(tree_dict, level=0):
    """递归显示成分树"""
    indent = "  " * level
    if tree_dict['type'] == 'word':
        pos = tree_dict.get('pos_zh', tree_dict.get('pos', ''))
        return f"{indent}{tree_dict['text']} ({pos})"
    else:
        result = f"{indent}[{tree_dict['label']}]"
        for child in tree_dict.get('children', []):
            result += "\n" + display_tree(child, level + 1)
        return result

def main():
    # 加载模型
    with st.spinner("正在加载语言模型..."):
        nlp_models = load_models()
    
    # 标题
    st.markdown('<div class="main-title">🔍 歧义侦探 - 句法透视仪</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">双视角句法分析工具 | 依存句法 + 成分句法</div>', unsafe_allow_html=True)
    
    # 输入区域
    st.markdown('<div class="section-title">📝 句子输入</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        sentence = st.text_input(
            "输入要分析的句子",
            value="The boy saw the man with the telescope.",
            placeholder="输入英文或中文句子..."
        )
    
    with col2:
        st.write("")
        st.write("")
        analyze_btn = st.button("🔍 开始分析", type="primary", use_container_width=True)
    
    # 快速测试按钮
    st.markdown("**快速测试：**")
    test_cols = st.columns(4)
    test_sentences = [
        ("介词短语附着歧义", "The boy saw the man with the telescope."),
        ("词汇歧义", "Fruit flies like a banana."),
        ("中文歧义句", "我看见了一只狗在公园里。"),
        ("经典歧义", "Flying planes can be dangerous."),
    ]
    
    for i, (label, test_sent) in enumerate(test_sentences):
        with test_cols[i]:
            if st.button(label, key=f"test_{i}"):
                sentence = test_sent
                analyze_btn = True
    
    # 分析结果
    if analyze_btn and sentence:
        st.markdown('<div class="section-title">📊 分析结果</div>', unsafe_allow_html=True)
        
        # 检测语言
        lang = detect_language(sentence)
        nlp = nlp_models['zh'] if lang == 'zh' else nlp_models['en']
        lang_name = "中文" if lang == 'zh' else "英文"
        
        st.info(f"🌐 检测到的语言：**{lang_name}**")
        
        # 处理句子
        doc = nlp(sentence)
        
        # 创建标签页
        tab1, tab2, tab3 = st.tabs(["🔗 依存关系", "🌳 成分结构", "📋 核心论元"])
        
        # Tab 1: 依存关系
        with tab1:
            st.markdown("**依存句法分析**")
            
            # 生成依存图
            dep_html = displacy.render(doc, style='dep', jupyter=False, 
                                       options={'compact': False, 'distance': 150})
            
            # 替换词性标签为中文
            for token in doc:
                pos_zh = translate_pos(token.pos_)
                dep_zh = translate_dep(token.dep_)
                dep_html = dep_html.replace(f'>{token.pos_}<', f'>{pos_zh}<')
                dep_html = dep_html.replace(f'>{token.dep_}<', f'>{dep_zh}<')
            
            # 显示SVG
            st.components.v1.html(dep_html, height=400, scrolling=True)
            
            # 显示依存关系表格
            st.markdown("**依存关系详情：**")
            dep_data = []
            for token in doc:
                dep_data.append({
                    '词语': token.text,
                    '词性': translate_pos(token.pos_),
                    '依存关系': translate_dep(token.dep_),
                    '依存词': token.head.text,
                    '位置': token.i + 1
                })
            st.dataframe(dep_data, use_container_width=True, hide_index=True)
        
        # Tab 2: 成分结构
        with tab2:
            st.markdown("**成分句法分析**")
            
            # 生成成分树
            constituency_tree = generate_constituency_tree(sentence, lang, nlp_models)
            
            # 显示树结构
            tree_text = display_tree(constituency_tree)
            st.code(tree_text, language=None)
            
            # 显示成分信息
            st.markdown("**成分说明：**")
            st.markdown("""
            - **NP**: 名词短语 (Noun Phrase)
            - **VP**: 动词短语 (Verb Phrase)
            - **PP**: 介词短语 (Prepositional Phrase)
            - **ADJP**: 形容词短语 (Adjective Phrase)
            - **ADVP**: 副词短语 (Adverb Phrase)
            """)
        
        # Tab 3: 核心论元
        with tab3:
            st.markdown("**核心论元提取**")
            
            core_args = extract_core_args(doc)
            
            if core_args:
                arg_data = []
                for arg in core_args:
                    arg_data.append({
                        '类型': arg['type_zh'],
                        '词语': arg['text'],
                        '位置': arg['position'],
                        '说明': arg['description']
                    })
                st.dataframe(arg_data, use_container_width=True, hide_index=True)
            else:
                st.info("未检测到核心论元")
            
            # 显示所有词的信息
            st.markdown("**所有词语信息：**")
            word_data = []
            for token in doc:
                word_data.append({
                    '词语': token.text,
                    '词性': translate_pos(token.pos_),
                    '依存关系': translate_dep(token.dep_),
                    '依存词': token.head.text,
                    '子节点': ', '.join([child.text for child in token.children]) if list(token.children) else '-'
                })
            st.dataframe(word_data, use_container_width=True, hide_index=True)
    
    # 底部信息
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6c757d; font-size: 0.9rem;">
        <p>🔍 歧义侦探 - 句法透视仪 | 基于 spaCy + NLTK 开发</p>
        <p>支持中英文双语分析 | 依存句法 + 成分句法双视角</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == '__main__':
    main()
