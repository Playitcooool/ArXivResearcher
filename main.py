"""
arXiv 研究助手 - 主程序
每日推荐指定领域的论文，并提供总结和问答功能
"""

import sys
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict

from arxiv_fetcher import ArxivFetcher
from ollama_client import OllamaClient, PaperSummarizer


class ArxivResearchAssistant:
    """arXiv 研究助手主类"""

    def __init__(self, config_path: str = "config.yaml"):
        """初始化研究助手"""
        # 加载配置
        self.config = self.load_config(config_path)

        # 初始化组件
        self.fetcher = ArxivFetcher(
            categories=self.config['arxiv']['categories'],
            max_results=self.config['arxiv']['max_results'],
            query=self.config['arxiv'].get('query', '')
        )

        self.ollama_client = OllamaClient(
            base_url=self.config['ollama']['base_url'],
            model=self.config['ollama']['model']
        )

        self.summarizer = PaperSummarizer(self.ollama_client)

        # 数据
        self.papers = []
        self.save_dir = Path(self.config['output']['save_dir'])
        self.save_dir.mkdir(exist_ok=True)

    def load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            print(f"配置文件 {config_path} 不存在，使用默认配置")
            return self.get_default_config()

    def get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            'arxiv': {
                'categories': ['cs.AI', 'cs.LG'],
                'max_results': 10,
                'query': ''
            },
            'ollama': {
                'base_url': 'http://localhost:11434',
                'model': 'qwen3:14b',
                'temperature': 0.7,
                'max_tokens': 2000
            },
            'output': {
                'save_dir': './papers',
                'download_pdf': False
            }
        }

    def fetch_daily_papers(self, days: int = 1):
        """获取每日论文"""
        print("\n" + "=" * 60)
        print("📚 获取最新论文")
        print("=" * 60)

        self.papers = self.fetcher.fetch_recent_papers(days=days)

        if not self.papers:
            print("❌ 没有找到符合条件的论文")
            return False

        # 保存论文信息
        today = datetime.now().strftime('%Y%m%d')
        papers_file = self.save_dir / f"papers_{today}.json"
        self.fetcher.save_papers(self.papers, str(papers_file))

        return True

    def summarize_papers(self):
        """总结论文并分析趋势"""
        if not self.papers:
            print("❌ 没有论文需要总结")
            return

        print("\n" + "=" * 60)
        print("🤖 AI 总结与分析")
        print("=" * 60)

        # 处理论文
        results = self.summarizer.process_papers(self.papers)

        # 保存结果
        today = datetime.now().strftime('%Y%m%d')
        summary_file = self.save_dir / f"summaries_{today}.json"
        self.summarizer.save_results(str(summary_file))

        return results

    def display_results(self):
        """显示结果"""
        if not self.papers:
            return

        print("\n" + "=" * 60)
        print("📊 每日论文推荐")
        print("=" * 60)

        for i, paper in enumerate(self.papers, 1):
            print(f"\n【论文 {i}】")
            print(f"标题: {paper['title']}")
            print(f"作者: {', '.join(paper['authors'][:3])}{'...' if len(paper['authors']) > 3 else ''}")
            print(f"发布: {paper['published']}")
            print(f"分类: {', '.join(paper['categories'][:3])}")
            print(f"链接: {paper['pdf_url']}")

            # 显示总结
            if paper['arxiv_id'] in self.summarizer.summaries:
                print(f"\n📝 AI 总结:")
                print(self.summarizer.summaries[paper['arxiv_id']])

            print("-" * 60)

        # 显示趋势分析
        if self.summarizer.trend_analysis:
            print("\n" + "=" * 60)
            print("🔥 研究热点分析")
            print("=" * 60)
            print(self.summarizer.trend_analysis)

    def interactive_qa(self):
        """交互式问答"""
        if not self.papers:
            print("❌ 没有论文可供问答")
            return

        print("\n" + "=" * 60)
        print("💬 论文问答模式")
        print("=" * 60)
        print("输入 'list' 查看论文列表")
        print("输入 'quit' 或 'exit' 退出问答")
        print("=" * 60)

        current_paper = None

        while True:
            try:
                user_input = input("\n请输入命令或问题: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 退出问答模式")
                    break

                if user_input.lower() == 'list':
                    print("\n可用论文:")
                    for i, paper in enumerate(self.papers, 1):
                        print(f"{i}. {paper['title'][:80]}")
                    continue

                # 选择论文
                if user_input.isdigit():
                    idx = int(user_input) - 1
                    if 0 <= idx < len(self.papers):
                        current_paper = self.papers[idx]
                        print(f"\n✅ 已选择论文: {current_paper['title']}")
                        print(f"输入问题开始提问...")
                    else:
                        print(f"❌ 无效的论文编号，请输入 1-{len(self.papers)}")
                    continue

                # 回答问题
                if current_paper:
                    print("\n🤔 思考中...")
                    context = self.summarizer.summaries.get(current_paper['arxiv_id'])
                    answer = self.ollama_client.answer_question(
                        current_paper, user_input, context
                    )
                    print(f"\n💡 回答:\n{answer}")
                else:
                    print("❌ 请先选择一篇论文（输入论文编号）")

            except KeyboardInterrupt:
                print("\n\n👋 退出问答模式")
                break
            except Exception as e:
                print(f"❌ 错误: {e}")

    def run_daily_update(self):
        """运行每日更新流程"""
        print("\n" + "=" * 60)
        print("🌟 arXiv 研究助手 - 每日更新")
        print("=" * 60)

        # 1. 获取论文
        if not self.fetch_daily_papers():
            return

        # 2. 总结论文
        self.summarize_papers()

        # 3. 显示结果
        self.display_results()

        # 4. 进入问答模式
        print("\n是否进入问答模式？(y/n): ", end='')
        choice = input().strip().lower()
        if choice in ['y', 'yes']:
            self.interactive_qa()


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='arXiv 研究助手')
    parser.add_argument('--config', default='config.yaml', help='配置文件路径')
    parser.add_argument('--days', type=int, default=1, help='获取最近几天的论文')
    parser.add_argument('--no-summary', action='store_true', help='不生成总结')
    parser.add_argument('--qa', action='store_true', help='直接进入问答模式')

    args = parser.parse_args()

    try:
        assistant = ArxivResearchAssistant(args.config)

        if args.qa:
            # 加载最近的论文
            today = datetime.now().strftime('%Y%m%d')
            papers_file = assistant.save_dir / f"papers_{today}.json"
            summary_file = assistant.save_dir / f"summaries_{today}.json"

            if papers_file.exists():
                assistant.papers = assistant.fetcher.load_papers(str(papers_file))
                if summary_file.exists():
                    assistant.summarizer.load_results(str(summary_file))
                assistant.interactive_qa()
            else:
                print(f"❌ 未找到今天的论文数据，请先运行每日更新")
        else:
            # 运行每日更新
            assistant.run_daily_update()

    except KeyboardInterrupt:
        print("\n\n👋 程序已退出")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
