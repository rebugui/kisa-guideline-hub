# KISA Guideline Hub

[![Version](https://img.shields.io/badge/version-1.1.0-blue)](https://github.com/rebugui/kisa-guideline-hub)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

> KISA(한국인터넷진흥원)와 Boho(보호나라)에서 보안 가이드라인을 자동으로 수집하여 Notion에 발행하는 시스템

## 개요

KISA Guideline Hub는 한국 보안 기관(KISA, Boho)의 보안 가이드라인을 자동으로 수집하여 Notion에 발행하는 시스템입니다.

일반 보안 뉴스와 달리 **LLM 처리 없이 직접 발행**하며, **PDF 파일 첨부**를 지원합니다.

**GitHub 저장소와 동일**: https://github.com/rebugui/kisa-guideline-hub

## 지원 소스

### KISA (한국인터넷진흥원)
- 보안 가이드라인 및 모범 사례
- 구성 가이드
- 정책 문서
- URL: https://인터넷진흥원.한국/2060207

### Boho (보호나라/KRCERT)
- 보안 취약점 가이드
- 사건 대응 가이드
- 기술 가이드라인
- URL: https://www.boho.or.kr
- **PDF 다운로드 포함**

## 워크플로우

```
KISA 크롤러 (10개 가이드라인)
    ↓
Boho 크롤러 (11개 가이드라인 + PDF)
    ↓
temp_downloads/ 디렉토리에 PDF 저장
    ↓
처리 큐에 저장
    ↓
Notion GUIDE_DATABASE_ID에 발행
```

## 주요 기능

### 1. 가이드라인 수집 (Collection)
- **KISA 크롤러**: 10개 가이드라인 수집
- **Boho 크롤러**: 11개 가이드라인 수집 + PDF 다운로드
- **PDF 저장**: `temp_downloads_boho/` 디렉토리

### 2. Notion 발행 (Publishing)
- **직접 발행**: LLM 처리 없이 바로 발행
- **PDF 업로드**: Notion 파일 블록으로 PDF 업로드
- **중복 방지**: URL 기반 자동 중복 체크

### 3. 별도 데이터베이스 (Separate Database)
- **GUIDE_DATABASE_ID**: 가이드라인 전용 Notion DB
- 미설정 시 SECURITY_NEWS_DATABASE_ID 사용

## 설치

### 1. 의존성 설치
```bash
cd ~/.openclaw/workspace/skills/kisa-guideline-hub
# 의존성은 security-news-feed/modules 공유
```

### 2. 환경 변수 설정

```bash
# ~/.openclaw/workspace/.env

# Notion
NOTION_API_KEY=ntn_xxx
SECURITY_NEWS_DATABASE_ID=xxx
SECURITY_GUIDE_DATABASE_ID=xxx  # 선택사항, 미설정 시 SECURITY_NEWS_DATABASE_ID 사용
```

## 사용법

### 1. 가이드라인 수집만
```bash
cd ~/.openclaw/workspace/skills/kisa-guideline-hub
python3 scripts/publish_guidelines.py --collect
```

### 2. Notion 발행만
```bash
python3 scripts/publish_guidelines.py --publish
```

### 3. 전체 파이프라인 (수집 + 발행)
```bash
python3 scripts/publish_guidelines.py --full
```

## Cron 등록

```bash
# crontab -e
# 매일 새벽 2시에 실행
0 2 * * * cd ~/.openclaw/workspace/skills/kisa-guideline-hub && /usr/bin/python3 scripts/publish_guidelines.py --collect >> /tmp/kisa-guideline-hub.log 2>&1
```

## Notion 데이터베이스 속성

| 속성 | 타입 | 설명 |
|------|------|------|
| Title | title | 가이드라인 제목 |
| Category | select | "KISA 가이드라인" 또는 "보호나라 가이드라인" |
| URL | url | 원본 URL |
| Date | date | 발행일 |
| Files | files | PDF 첨부 (Boho만) |

## 보안 뉴스와의 차이점

| 항목 | 보안 뉴스 | 가이드라인 |
|------|----------|-----------|
| **처리 방식** | LLM 요약 + 분석 | 직접 발행 (LLM 없음) |
| **PDF 첨부** | ❌ | ✅ (Boho) |
| **Notion DB** | SECURITY_NEWS_DB | GUIDE_DB (별도) |
| **소스** | 9개 뉴스 사이트 | KISA + Boho (2개) |

## PDF 다운로드

Boho 크롤러는 PDF 파일을 자동으로 다운로드합니다:

```
temp_downloads_boho/
├── 가이드라인1.pdf
├── 가이드라인2.pdf
└── ...
```

PDF는 Notion에 파일 블록으로 업로드됩니다.

## 트러블슈팅

### 가이드라인이 수집되지 않음
- KISA/Boho 웹사이트 접근 확인
- Notion API 키 및 데이터베이스 ID 확인
- 네트워크 연결 확인

### PDF 업로드 실패
- Notion API 파일 업로드 지원 확인
- 파일 크기 제한 확인 (최대 20MB)
- `temp_downloads/` 디렉토리 존재 확인

### 중복 가이드라인
- Notion `Duplicate_check()`가 중복 방지
- URL 기반 매칭
- 여러 번 실행해도 안전

## 디렉토리 구조

```
kisa-guideline-hub/
├── scripts/
│   └── publish_guidelines.py    # 메인 스크립트
├── references/
│   ├── schema.md               # Notion DB 스키마
│   └── examples.md             # 예시 가이드라인
├── SKILL.md
└── README.md
```

## security-news-feed와의 통합

이 스킬은 Security News Feed의 크롤러 모듈을 사용합니다:

```bash
# security-news-feed/modules/crawlers/
├── kisa.py   # KISA 크롤러
└── boho.py   # Boho 크롤러
```

## 기여

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 라이선스

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 저장소

- GitHub: https://github.com/rebugui/kisa-guideline-hub
