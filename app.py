import streamlit as st
import pandas as pd
import easyocr
from PIL import Image
import numpy as np
import io
from docx import Document

reader = easyocr.Reader(['en', 'ch_sim'])

st.set_page_config(page_title="英语词汇扩展系统", layout="centered")
st.title("📘 高三常忘英语词汇扩展学习系统")

uploaded_files = st.file_uploader("上传中英文截图（支持多张）", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

results = []

def enrich_word_data(word, meaning):
    sample_dict = {
        "violate": {
            "pos": "v.",
            "collocation": "violate the law（违法）",
            "example": "He was fined for violating traffic rules.（他因违反交通规则被罚款。）",
            "derivatives": "violates (第三人称单数), violating (现在分词), violated (过去式/过去分词), violation (n. 违反), violator (n. 违规者)",
            "confusing": "violet（紫罗兰）violent（暴力的）"
        }
    }
    data = sample_dict.get(word.lower(), {})
    return {
        "word": word,
        "pos": data.get("pos", ""),
        "cn_meaning": meaning,
        "collocation": data.get("collocation", ""),
        "example": data.get("example", ""),
        "derivatives": data.get("derivatives", ""),
        "confusing": data.get("confusing", "")
    }

if uploaded_files:
    for file in uploaded_files:
        image = Image.open(file)
        result = reader.readtext(np.array(image))
        text = "\n".join([line[1] for line in result])
        lines = text.strip().split('\n')
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 3 and parts[0].isdigit():
                word = parts[1]
                meaning = ''.join(parts[2:])
                result = enrich_word_data(word, meaning)
                results.append(result)

if results:
    df = pd.DataFrame(results)
    st.success(f"共提取到 {len(results)} 个词汇")
    st.dataframe(df)

    doc = Document()
    doc.add_heading("高三英语常忘词扩展记忆手册", level=1)
    for item in results:
        doc.add_paragraph(f"■ {item['word']}  {item['pos']}  {item['cn_meaning']}")
        doc.add_paragraph(f"常见搭配：{item['collocation']}")
        doc.add_paragraph(f"例句：{item['example']}")
        doc.add_paragraph(f"词形变化：{item['derivatives']}")
        doc.add_paragraph(f"形近词辨析：{item['confusing']}")
        doc.add_paragraph("")
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    st.download_button("📄 下载 Word 文档", buffer, file_name="词汇扩展结果.docx")
else:
    st.info("请上传包含中英文单词的截图，系统将自动识别并补全词汇信息。")
