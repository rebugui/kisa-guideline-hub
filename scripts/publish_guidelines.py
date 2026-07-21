#!/usr/bin/env python3
"""
가이드라인 발행 스크립트
KISA, Boho 가이드라인 수집 및 Notion 발행
"""

import sys
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')
import argparse

# 환경 변수 로드
from dotenv import load_dotenv
env_file = Path.home() / '.hermes' / '.skills.env'
load_dotenv(env_file)

# openclaw_logging 경로 추가 (현재 프로젝트 디렉토리)
import os
project_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_path))

from openclaw_logging import setup_skill_logger, ExecutionContext

logger = setup_skill_logger('kisa-guideline-hub')

# Security News Module 경로 추가 (security-news-feed의 modules 사용)
skill_path = Path(__file__).parent.parent.parent / 'security-news-feed'
sys.path.insert(0, str(skill_path))
# working directory 변경 불필요 - sys.path만으로 모듈 로딩 가능

from modules.crawlers.kisa import KISACrawler
from modules.crawlers.boho import BohoCrawler
from modules.publisher_service import PublisherService
from config import GUIDE_DATABASE_ID

logger.info("=" * 70)
logger.info("GUIDELINE PUBLISHER")
logger.info("=" * 70)

def collect_guidelines(exec_ctx):
    """가이드라인 수집"""
    logger.info("가이드라인 수집 시작...")

    crawlers = [
        ("KISA", KISACrawler),
        ("Boho", BohoCrawler),
    ]

    all_guidelines = []

    for name, crawler_class in crawlers:
        logger.info(f"{name}...")
        try:
            crawler = crawler_class()
            result = crawler.run(publisher_service=None)

            collected = len(result.get('queue', []))
            logger.info(f"  {name} 수집: {collected}개")

            if collected > 0:
                all_guidelines.extend(result['queue'])

        except Exception as e:
            logger.error(f"  {name} Error: {str(e)[:50]}")

    logger.info(f"총 수집: {len(all_guidelines)}개 가이드라인")
    return all_guidelines

def publish_guidelines(guidelines, exec_ctx):
    """Notion 발행"""
    if not guidelines:
        logger.warning("발행할 가이드라인이 없습니다.")
        return

    logger.info(f"Notion 발행 시작... ({len(guidelines)}개)")

    # Publisher Service 초기화
    publisher = PublisherService(
        enable_notion=True,
        enable_tistory=False,
        notion_database_id=GUIDE_DATABASE_ID
    )

    success_count = 0
    fail_count = 0

    for i, guideline in enumerate(guidelines, 1):
        logger.info(f"[{i}/{len(guidelines)}] {guideline['title'][:50]}...")

        try:
            # Notion 발행 (LLM 없이 바로 발행)
            pub_result = publisher.publish_article(
                title=guideline['title'],
                content=guideline.get('content', '내용 없음'),
                url=guideline['url'],
                date=guideline['posting_date'].strftime('%Y-%m-%d'),
                category=guideline['category'],
                details=guideline.get('content', ''),  # 본문을 children block으로 추가
                files=guideline.get('files', []),  # PDF 파일
                database_id=GUIDE_DATABASE_ID
            )

            if pub_result.get('notion'):
                success_count += 1
                logger.info("  발행 성공")
            else:
                fail_count += 1
                logger.warning("  발행 실패")

        except Exception as e:
            fail_count += 1
            logger.error(f"  Error: {str(e)[:50]}")

    logger.info("=" * 70)
    logger.info("발행 완료")
    logger.info("=" * 70)
    logger.info(f"성공: {success_count}개 | 실패: {fail_count}개 | 성공률: {success_count/len(guidelines)*100:.1f}%")

def main():
    parser = argparse.ArgumentParser(description='가이드라인 발행')
    parser.add_argument('--collect', action='store_true', help='가이드라인 수집만')
    parser.add_argument('--publish', action='store_true', help='Notion 발행만')
    parser.add_argument('--full', action='store_true', help='수집 + 발행')

    args = parser.parse_args()

    if not any([args.collect, args.publish, args.full]):
        parser.print_help()
        return

    exec_ctx = ExecutionContext('kisa-guideline-hub')
    guidelines = []

    try:
        if args.collect or args.full:
            with exec_ctx.phase('collect') as phase:
                guidelines = collect_guidelines(exec_ctx)
                phase.set_output_count(len(guidelines))

        if args.publish:
            # 수집 후 발행 (--full과 동일 동작)
            if not guidelines:
                with exec_ctx.phase('collect') as phase:
                    guidelines = collect_guidelines(exec_ctx)
                    phase.set_output_count(len(guidelines))
            if guidelines:
                with exec_ctx.phase('publish') as phase:
                    phase.set_input_count(len(guidelines))
                    publish_guidelines(guidelines, exec_ctx)
            else:
                logger.warning("수집된 가이드라인이 없어 발행을 건너뜁니다.")
            return

        if args.full and guidelines:
            with exec_ctx.phase('publish') as phase:
                phase.set_input_count(len(guidelines))
                publish_guidelines(guidelines, exec_ctx)
    finally:
        summary = exec_ctx.finalize()
        logger.info(f"Execution ID: {exec_ctx.execution_id} | Duration: {summary['total_duration']}s")

if __name__ == '__main__':
    main()
