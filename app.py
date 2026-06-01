"""Streamlit arayüzü: transcript alma, Gemini özetleme, YAKE ve çeviri."""

from __future__ import annotations

import html
import os

import pandas as pd
import streamlit as st

from utils.audience import (
    AudienceAnalysisError,
    analyze_target_audience,
    parse_audience_table,
)
from utils.keywords import extract_keywords
from utils.preprocess import clean_text, preview_text
from utils.report import build_pdf_report
from utils.sentiment import (
    SentimentAnalysisError,
    analyze_sentiment_and_tone,
    build_sentiment_visual_data,
    parse_sentiment_table,
)
from utils.slang import analyze_slang, parse_slang_table
from utils.storage import (
    authenticate_user,
    create_user,
    get_analysis_by_id,
    get_cached_analysis,
    get_user_history,
    init_db,
    save_analysis,
    upsert_cached_analysis,
)
from utils.summarizer import DEFAULT_SUMMARIZER_MODEL, SummarizationError, summarize_text
from utils.transcript import TranscriptError, fetch_transcript_payload
from utils.translator import DEFAULT_LANGUAGE_CODE, LANGUAGE_OPTIONS, translate_text


def inject_styles() -> None:
    """Koyu temalı, okunaklı bir arayüz stili ekler."""
    st.markdown(
        """
        <style>
            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(56, 189, 248, 0.10), transparent 24%),
                    linear-gradient(180deg, #020617 0%, #0f172a 60%, #111827 100%);
                color: #e2e8f0;
            }
            [data-testid="stHeader"] { background: transparent; }
            h1, h2, h3, p, label, span, div { color: #e2e8f0; }
            .block-container { padding-top: 2rem; padding-bottom: 3rem; }
            [data-baseweb="input"] > div,
            [data-baseweb="select"] > div,
            .stTextInput input,
            .stTextArea textarea,
            .stSelectbox div[data-baseweb="select"] > div {
                background: #111827 !important;
                color: #f8fafc !important;
                border: 1px solid #334155 !important;
                border-radius: 12px !important;
            }
            .stButton > button {
                background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%);
                color: #eff6ff !important;
                border: none;
                border-radius: 12px;
                font-weight: 700;
                min-height: 3rem;
            }
            .stButton > button:hover {
                background: linear-gradient(135deg, #38bdf8 0%, #3b82f6 100%);
            }
            .result-card {
                background: rgba(15, 23, 42, 0.82);
                border: 1px solid rgba(148, 163, 184, 0.18);
                border-radius: 18px;
                padding: 1rem 1.1rem;
                margin-bottom: 1rem;
                box-shadow: 0 16px 35px rgba(0, 0, 0, 0.18);
            }
            .result-card h3 { margin-top: 0; color: #f8fafc; }
            .result-card p { color: #dbe7f5; white-space: pre-wrap; }
            .metric-chip {
                border-radius: 16px;
                padding: 0.9rem 1rem;
                margin-bottom: 0.75rem;
                color: #f8fafc;
                min-height: 88px;
                box-shadow: 0 12px 28px rgba(0, 0, 0, 0.15);
            }
            .metric-chip h4 {
                margin: 0 0 0.35rem 0;
                font-size: 0.95rem;
                color: #e2e8f0;
            }
            .metric-chip p {
                margin: 0;
                font-size: 1.5rem;
                font-weight: 800;
                color: #ffffff;
            }
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #020617 0%, #0f172a 50%, #111827 100%);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> tuple[str, str, float, str]:
    """Kullanıcının hedef dil, özet yoğunluğu ve transcript kaynağını seçmesini sağlar."""
    st.sidebar.header("Ayarlar")
    language_label = st.sidebar.selectbox(
        "Çıktı Dili",
        options=list(LANGUAGE_OPTIONS.keys()),
        index=list(LANGUAGE_OPTIONS.values()).index(DEFAULT_LANGUAGE_CODE),
    )
    summary_mode = st.sidebar.selectbox(
        "Özet Uzunluğu",
        options=["Kısa", "Orta", "Detaylı"],
        index=1,
    )

    summary_ratio_map = {
        "Kısa": 0.20,
        "Orta": 0.28,
        "Detaylı": 0.38,
    }

    st.sidebar.markdown("**Transcript Kaynağı**")
    st.sidebar.info("Hızlı (YouTube API)")
    st.sidebar.caption("Bu sürümde transcript kaynağı sabit olarak YouTube API kullanır.")
    st.sidebar.caption(f"Kullanılan özetleme yaklaşımı: `{DEFAULT_SUMMARIZER_MODEL}`")
    return (
        language_label,
        LANGUAGE_OPTIONS[language_label],
        summary_ratio_map[summary_mode],
        "youtube",
    )


def render_auth_section() -> None:
    """Kullanıcı giriş ve kayıt alanını gösterir."""
    st.sidebar.divider()
    st.sidebar.subheader("Kullanıcı")

    user = st.session_state.get("current_user")
    if user:
        st.sidebar.success(f"Giriş yapıldı: {user['username']}")
        if st.sidebar.button("Çıkış Yap", use_container_width=True):
            st.session_state["current_user"] = None
            st.session_state["selected_analysis_id"] = None
            st.rerun()
        return

    login_tab, register_tab = st.sidebar.tabs(["Giriş", "Kayıt"])

    with login_tab:
        login_username = st.text_input("Kullanıcı Adı", key="login_username")
        login_password = st.text_input("Parola", type="password", key="login_password")
        if st.button("Giriş Yap", use_container_width=True):
            user_payload = authenticate_user(login_username, login_password)
            if user_payload:
                st.session_state["current_user"] = user_payload
                st.rerun()
            else:
                st.sidebar.error("Kullanıcı adı veya parola hatalı.")

    with register_tab:
        register_username = st.text_input("Yeni Kullanıcı Adı", key="register_username")
        register_password = st.text_input("Yeni Parola", type="password", key="register_password")
        if st.button("Kayıt Ol", use_container_width=True):
            success, message = create_user(register_username, register_password)
            if success:
                st.sidebar.success(message)
            else:
                st.sidebar.error(message)


def render_auth_page() -> None:
    """Giriş yapılmadığında ayrı tam ekran giriş/kayıt görünümü gösterir."""
    st.markdown("## Kullanıcı Girişi")
    st.caption("Devam etmek için giriş yap.")

    auth_col_left, auth_col_center, auth_col_right = st.columns([1, 1.4, 1])
    with auth_col_center:
        st.markdown("### Giriş Yap")
        login_username = st.text_input("Kullanıcı Adı", key="page_login_username")
        login_password = st.text_input("Parola", type="password", key="page_login_password")
        if st.button("Giriş Yap", use_container_width=True, key="page_login_button"):
            user_payload = authenticate_user(login_username, login_password)
            if user_payload:
                st.session_state["current_user"] = user_payload
                st.rerun()
            else:
                st.error("Kullanıcı adı veya parola hatalı.")

        show_register = st.session_state.get("show_register_form", False)
        toggle_label = "Kayıt ol" if not show_register else "Kayıt ekranını kapat"
        if st.button(toggle_label, key="toggle_register_form"):
            st.session_state["show_register_form"] = not show_register
            st.rerun()

        if st.session_state.get("show_register_form", False):
            st.markdown("### Kayıt Ol")
            register_username = st.text_input("Yeni Kullanıcı Adı", key="page_register_username")
            register_password = st.text_input("Yeni Parola", type="password", key="page_register_password")
            if st.button("Kayıt Ol", use_container_width=True, key="page_register_button"):
                success, message = create_user(register_username, register_password)
                if success:
                    st.success(message)
                    st.session_state["show_register_form"] = False
                else:
                    st.error(message)


def render_history_section() -> None:
    """Kullanıcının geçmiş analizlerini listeler."""
    user = st.session_state.get("current_user")
    if not user:
        st.sidebar.info("Geçmiş analizleri görmek için giriş yap.")
        return

    history = get_user_history(int(user["id"]))
    if not history:
        st.sidebar.info("Henüz kayıtlı analiz yok.")
        return

    st.sidebar.divider()
    st.sidebar.subheader("Geçmiş Analizler")
    labels = {
        item["id"]: f"{item['created_at'][:16]} | {item['video_url'][:35]}"
        for item in history
    }
    selected_id = st.sidebar.selectbox(
        "Kayıtlı Analizler",
        options=list(labels.keys()),
        format_func=lambda analysis_id: labels[analysis_id],
    )
    st.session_state["selected_analysis_id"] = selected_id

    selected_payload = get_analysis_by_id(int(selected_id))
    if selected_payload:
        with st.sidebar.expander("Geçmiş Analizi Görüntüle", expanded=False):
            st.caption(f"Tarih: {selected_payload.get('created_at', '-')}")
            st.markdown("**Özet**")
            st.write(str(selected_payload.get("summary_text", "-")))
            st.markdown("**Anahtar Kelimeler**")
            st.write(" | ".join(selected_payload.get("keywords", [])) or "-")
            render_download_buttons(
                selected_payload,
                button_key=f"sidebar_saved_pdf_{selected_payload.get('id', 'unknown')}",
            )


def render_download_buttons(payload: dict, button_key: str) -> None:
    """PDF rapor indirme düğmesini gösterir."""
    pdf_bytes = build_pdf_report(payload)

    st.download_button(
        "PDF Raporu İndir",
        data=pdf_bytes,
        file_name="youtube_analiz_raporu.pdf",
        mime="application/pdf",
        use_container_width=True,
        key=button_key,
    )


def render_saved_analysis(payload: dict) -> None:
    """Kaydedilmiş analiz sonucunu gösterir."""
    render_summary_toggle(
        summary_text=str(payload.get("summary_text", "-")),
        translated_summary=str(payload.get("translated_summary", "-")),
    )

    slang_rows = parse_slang_table(str(payload.get("translated_slang_analysis", "")))
    if slang_rows:
        st.markdown("### Argo Analizi")
        st.table(pd.DataFrame(slang_rows, columns=["Ölçüt", "Sonuç"]))

    sentiment_rows = parse_sentiment_table(str(payload.get("translated_sentiment_analysis", "")))
    if sentiment_rows:
        render_sentiment_results(sentiment_rows)

    audience_rows = parse_audience_table(str(payload.get("translated_audience_analysis", "")))
    if audience_rows:
        st.markdown("### Hedef Kitle Tahmini")
        st.table(pd.DataFrame(audience_rows, columns=["Ölçüt", "Sonuç"]))

    keyword_content = " | ".join(payload.get("keywords", [])) or "Anahtar kelime çıkarılamadı."
    render_result_card("Anahtar Kelimeler", keyword_content)
    render_download_buttons(payload, button_key=f"saved_pdf_{payload.get('id', 'unknown')}")


def render_input_section() -> str:
    """Video linki giriş alanını oluşturur."""
    st.markdown("## Video Analizi")
    return st.text_input(
        "YouTube Video Linki",
        placeholder="https://www.youtube.com/watch?v=...",
    ).strip()


def render_result_card(title: str, content: str) -> None:
    """Sonuçları kart görünümünde gösterir."""
    safe_title = html.escape(title)
    safe_content = html.escape(content)
    st.markdown(
        f"""
        <div class="result-card">
            <h3>{safe_title}</h3>
            <p>{safe_content}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_summary_toggle(summary_text: str, translated_summary: str) -> None:
    """Özet ve çevrilmiş özeti tek alanda seçimli olarak gösterir."""
    summary_tab, translated_tab = st.tabs(["Oluşturulan Özet", "Çevrilmiş Özet"])
    with summary_tab:
        render_result_card("Oluşturulan Özet", summary_text)
    with translated_tab:
        render_result_card("Çevrilmiş Özet", translated_summary)


def render_metric_chip(title: str, value: int, background: str) -> None:
    """Kısa görsel metrik kartı gösterir."""
    safe_title = html.escape(title)
    st.markdown(
        f"""
        <div class="metric-chip" style="background:{background};">
            <h4>{safe_title}</h4>
            <p>%{value}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sentiment_results(sentiment_rows: list[tuple[str, str]]) -> None:
    """Duygu analizini tablo, skor kartları ve akış grafiğiyle gösterir."""
    st.markdown("### Duygu Analiz Tablosu")
    st.table(pd.DataFrame(sentiment_rows, columns=["Ölçüt", "Sonuç"]))

    visual_data = build_sentiment_visual_data(sentiment_rows)
    if not visual_data:
        return

    metric_cols = st.columns(len(visual_data))
    metric_colors = [
        "linear-gradient(135deg, #16a34a 0%, #22c55e 100%)",
        "linear-gradient(135deg, #dc2626 0%, #ef4444 100%)",
        "linear-gradient(135deg, #ea580c 0%, #f97316 100%)",
        "linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)",
        "linear-gradient(135deg, #7c3aed 0%, #8b5cf6 100%)",
    ]
    for index, (label, score) in enumerate(visual_data.items()):
        with metric_cols[index]:
            render_metric_chip(label, score, metric_colors[index % len(metric_colors)])

    st.markdown("### Duygu Akış Grafiği")
    chart_df = pd.DataFrame(
        [{"Ölçüt": label, "Skor": score} for label, score in visual_data.items()]
    ).set_index("Ölçüt")
    st.line_chart(chart_df, color="#38bdf8")


def main() -> None:
    """Uygulamanın ana akışı."""
    st.set_page_config(
        page_title="YouTube Video Özetleme Uygulaması",
        page_icon="🧠",
        layout="wide",
    )
    init_db()
    inject_styles()

    st.title("YouTube Video Özetleme Uygulaması")

    if "current_user" not in st.session_state:
        st.session_state["current_user"] = None
    if "selected_analysis_id" not in st.session_state:
        st.session_state["selected_analysis_id"] = None
    if "show_register_form" not in st.session_state:
        st.session_state["show_register_form"] = False

    current_user = st.session_state.get("current_user")
    if not current_user:
        render_auth_page()
        return

    _language_label, target_language, summary_ratio, transcript_mode = render_sidebar()
    render_auth_section()
    render_history_section()
    video_url = render_input_section()

    if st.button("Analizi Başlat", use_container_width=True):
        try:
            if not video_url:
                raise TranscriptError("Lütfen geçerli bir YouTube video linki girin.")

            cached_payload = get_cached_analysis(
                video_url=video_url,
                transcript_source="youtube",
                output_language=target_language,
                summary_ratio=summary_ratio,
            )
            if cached_payload:
                st.success("Önceden üretilmiş analiz önbellekten yüklendi.")
                render_saved_analysis(cached_payload)
                return

            with st.spinner("Transcript alınıyor..."):
                transcript_payload = fetch_transcript_payload(video_url, mode=transcript_mode)
                transcript_text = transcript_payload["text"]
                transcript_segments = transcript_payload["segments"]
                transcript_source = transcript_payload["source"]
                transcript_warning = transcript_payload["warning"]

            cleaned_text = clean_text(transcript_text)
            notices: list[str] = []
            keyword_language = "tr" if target_language == "tr" else "en"

            with st.spinner("Gemini ile özet oluşturuluyor..."):
                summary_text = summarize_text(
                    cleaned_text,
                    segments=transcript_segments,
                    summary_ratio=summary_ratio,
                )

            with st.spinner("Anahtar kelimeler çıkarılıyor..."):
                keywords = extract_keywords(
                    cleaned_text,
                    summary_text=summary_text,
                    language=keyword_language,
                    top_n=10,
                )

            with st.spinner("Özet çevriliyor..."):
                translated_summary, translation_note = translate_text(summary_text, target_language)

            with st.spinner("Argo analizi yapılıyor..."):
                slang_analysis = analyze_slang(cleaned_text, summary_text=summary_text)
                translated_slang_analysis, _ = translate_text(slang_analysis, target_language)

            translated_sentiment_analysis = "Duygu ve ton analizi şu anda üretilemedi."
            translated_audience_analysis = "Hedef kitle analizi şu anda üretilemedi."
            try:
                with st.spinner("Duygu ve ton analizi yapılıyor..."):
                    sentiment_analysis = analyze_sentiment_and_tone(cleaned_text, summary_text=summary_text)
                    translated_sentiment_analysis, _ = translate_text(sentiment_analysis, target_language)
            except SentimentAnalysisError as sentiment_exc:
                notices.append(f"Duygu/ton analizi atlandı: {sentiment_exc}")

            try:
                with st.spinner("Hedef kitle analizi yapılıyor..."):
                    audience_analysis = analyze_target_audience(cleaned_text, summary_text=summary_text)
                    translated_audience_analysis, _ = translate_text(audience_analysis, target_language)
            except AudienceAnalysisError as audience_exc:
                notices.append(f"Hedef kitle analizi atlandı: {audience_exc}")

            if any("atlandı" in note.lower() for note in notices):
                st.warning("Analiz kısmen tamamlandı. Bazı LLM tabanlı bölümler geçici olarak atlandı.")
            else:
                st.success("Analiz başarıyla tamamlandı.")
            source_label = "Whisper" if transcript_source == "whisper" else "YouTube Transcript API (fallback)"
            st.caption(f"Kullanılan transcript kaynağı: {source_label}")
            if transcript_warning:
                st.warning(transcript_warning)
            if "GEMINI_API_KEY" not in os.environ:
                st.info("Not: Gemini özetleme ve analizler için GEMINI_API_KEY ortam değişkeni gerekir.")
            for notice in notices:
                st.info(notice)

            render_summary_toggle(
                summary_text=summary_text,
                translated_summary=translated_summary,
            )

            analysis_left, analysis_right = st.columns(2)
            with analysis_left:
                st.markdown("### Argo Analizi")
                slang_rows = parse_slang_table(translated_slang_analysis)
                if slang_rows:
                    st.table(pd.DataFrame(slang_rows, columns=["Ölçüt", "Sonuç"]))
                else:
                    render_result_card("Argo Analizi", translated_slang_analysis)
            with analysis_right:
                sentiment_rows = parse_sentiment_table(translated_sentiment_analysis)
                if not sentiment_rows:
                    render_result_card("Duygu ve Ton Analizi", translated_sentiment_analysis)

            audience_rows = parse_audience_table(translated_audience_analysis)
            if audience_rows:
                st.markdown("### Hedef Kitle Tahmini")
                st.table(pd.DataFrame(audience_rows, columns=["Ölçüt", "Sonuç"]))
            else:
                render_result_card("Hedef Kitle Tahmini", translated_audience_analysis)

            if sentiment_rows:
                render_sentiment_results(sentiment_rows)

            keyword_content = " | ".join(keywords) if keywords else "Anahtar kelime çıkarılamadı."
            render_result_card("Anahtar Kelimeler", keyword_content)
            payload = {
                "video_url": video_url,
                "transcript_source": source_label,
                "summary_text": summary_text,
                "translated_summary": translated_summary,
                "translated_slang_analysis": translated_slang_analysis,
                "translated_sentiment_analysis": translated_sentiment_analysis,
                "translated_audience_analysis": translated_audience_analysis,
                "keywords": keywords,
                "output_language": target_language,
            }
            upsert_cached_analysis(
                video_url=video_url,
                transcript_source="youtube",
                output_language=target_language,
                summary_ratio=summary_ratio,
                payload=payload,
            )
            render_download_buttons(payload, button_key=f"live_pdf_{video_url}_{target_language}")

            current_user = st.session_state.get("current_user")
            if current_user:
                analysis_id = save_analysis(
                    user_id=int(current_user["id"]),
                    video_url=video_url,
                    transcript_source=source_label,
                    output_language=target_language,
                    summary_ratio=summary_ratio,
                    payload=payload,
                )
                st.session_state["selected_analysis_id"] = analysis_id
                st.success("Analiz geçmişe kaydedildi.")
            else:
                st.info("Geçmişe kaydetmek için giriş yapabilirsin.")

            if translation_note:
                st.info(translation_note)

        except TranscriptError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"Beklenmeyen bir hata oluştu: {exc}")


if __name__ == "__main__":
    main()
