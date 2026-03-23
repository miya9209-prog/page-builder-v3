import io
from typing import Dict

import streamlit as st
from openai import OpenAI
from docx import Document

st.set_page_config(page_title="PAGE BUILDER V3", layout="wide")

if "reset_nonce" not in st.session_state:
    st.session_state.reset_nonce = 0

st.title("PAGE BUILDER V3 (고객고민 자동생성)")
st.caption("상세페이지 + 고객고민 + FAQ + 스텝반응 통합 생성기")

api_key = st.secrets.get("OPENAI_API_KEY", "")
if not api_key:
    st.warning("OPENAI_API_KEY가 설정되지 않았습니다.")
    st.stop()

client = OpenAI(api_key=api_key)

PROMPT = """
너는 4050 여성 패션 전문 쇼핑몰 미샵의 시니어 MD이자 카피라이터다.

목표:
- 구매전환이 일어나는 상세페이지 원고 작성
- 고객의 고민을 정확히 짚고 해결하는 콘텐츠 작성

구성 순서:

1. 고객 고민
- 이 상품을 찾는 고객이 실제로 가질 고민 3~5개 생성

2. 상세페이지 본문
- 추천 이유
- 원단
- 핏
- 추천 고객
- 코디 제안

3. 자주 하시는 상품 질문
- 실제 고객 질문 4개 + 답변

4. 먼저 입어본 스텝, 모델 반응
- 후기 스타일 4~5개

5. 이미지 ALT 텍스트
- 6개

규칙:
- 실무에서 바로 복붙 가능하게 작성
- 짧고 명확하게
- 고객 고민 → 본문 → FAQ 흐름이 자연스럽게 이어지도록 작성
"""

def build_prompt(data: Dict[str, str]) -> str:
    return PROMPT + "\n\n입력:" + str(data)

def to_docx(text):
    doc = Document()
    for line in text.splitlines():
        doc.add_paragraph(line)
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio.getvalue()

h1, h2 = st.columns([2,1])
with h1:
    st.subheader("상품 입력")
with h2:
    if st.button("초기화"):
        st.session_state.reset_nonce += 1
        st.rerun()

n = st.session_state.reset_nonce

col1, col2 = st.columns(2)

with col1:
    name = st.text_input("상품명", key=f"n{n}")
    cat = st.text_input("카테고리", key=f"c{n}")
    mat = st.text_input("소재", key=f"m{n}")
    color = st.text_input("컬러", key=f"co{n}")
    size = st.text_input("사이즈", key=f"s{n}")
    fit = st.text_input("핏", key=f"f{n}")
    detail = st.text_area("디테일", key=f"d{n}")

with col2:
    tpo = st.text_input("착용 상황", key=f"t{n}")
    coordi = st.text_area("코디", key=f"coo{n}")
    target = st.text_input("타겟", value="4050 여성", key=f"ta{n}")

st.subheader("이미지 / 영상")
st.file_uploader("이미지", accept_multiple_files=True, key=f"img{n}")
st.file_uploader("영상", accept_multiple_files=True, key=f"vid{n}")

if st.button("생성하기"):
    data = {
        "상품명": name,
        "카테고리": cat,
        "소재": mat,
        "컬러": color,
        "사이즈": size,
        "핏": fit,
        "디테일": detail,
        "TPO": tpo,
        "코디": coordi,
        "타겟": target
    }

    prompt = build_prompt(data)

    with st.spinner("생성중입니다..."):
        res = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role":"system","content":"구조 유지"},
                {"role":"user","content":prompt}
            ]
        )
        result = res.choices[0].message.content

    st.text_area("결과", result, height=900)

    docx = to_docx(result)

    st.download_button("TXT 다운로드", result)
    st.download_button("DOCX 다운로드", docx)

st.markdown("---")
st.markdown("© MISHARP")
