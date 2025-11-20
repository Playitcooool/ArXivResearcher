"""
Ollama 集成模块
用于调用本地 Ollama 大模型进行论文总结和问答
"""

import requests
from typing import List, Dict, Optional
import json


class OllamaClient:
    """Ollama 客户端"""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "qwen3:8b"):
        """
        初始化 Ollama 客户端

        Args:
            base_url: Ollama API 地址
            model: 使用的模型名称
        """
        self.base_url = base_url.rstrip('/')
        self.model = model

    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """
        生成响应

        Args:
            prompt: 输入提示词
            temperature: 温度参数
            max_tokens: 最大生成长度

        Returns:
            模型生成的文本
        """
        url = f"{self.base_url}/api/generate"

        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        try:
            response = requests.post(url, json=data, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result.get('response', '')
        except requests.exceptions.RequestException as e:
            print(f"调用 Ollama API 出错: {e}")
            return ""

    def summarize_paper(self, paper: Dict) -> str:
        """
        总结单篇论文

        Args:
            paper: 论文信息字典

        Returns:
            论文总结
        """
        prompt = f"""请对以下学术论文进行总结，包括：
1. 研究问题和动机
2. 主要方法
3. 关键贡献
4. 实验结果（如果提到）

论文标题：{paper['title']}

摘要：{paper['summary']}

请用中文简洁地总结（200字以内）："""

        return self.generate(prompt, temperature=0.5)

    def summarize_papers_batch(self, papers: List[Dict]) -> Dict[str, str]:
        """
        批量总结论文

        Args:
            papers: 论文列表

        Returns:
            论文ID到总结的映射
        """
        summaries = {}
        total = len(papers)

        print(f"\n开始总结 {total} 篇论文...")

        for i, paper in enumerate(papers, 1):
            print(f"\n[{i}/{total}] 正在总结: {paper['title'][:50]}...")
            summary = self.summarize_paper(paper)
            summaries[paper['arxiv_id']] = summary
            print(f"完成！")

        return summaries

    def analyze_research_trends(self, papers: List[Dict], summaries: Dict[str, str]) -> str:
        """
        分析研究热点趋势

        Args:
            papers: 论文列表
            summaries: 论文总结字典

        Returns:
            研究趋势分析
        """
        # 构建论文摘要列表
        papers_info = []
        for paper in papers:
            paper_id = paper['arxiv_id']
            summary = summaries.get(paper_id, paper['summary'][:200])
            papers_info.append(f"- {paper['title']}\n  {summary}\n")

        papers_text = "\n".join(papers_info)

        prompt = f"""以下是最近发表的 {len(papers)} 篇学术论文的标题和总结：

{papers_text}

请分析这些论文，回答以下问题：
1. 当前的研究热点是什么？
2. 主要使用了哪些技术方法？
3. 有哪些新的研究方向或趋势？
4. 是否有共同关注的问题或挑战？

请用中文提供详细的分析（300-500字）："""

        print("\n正在分析研究趋势...")
        return self.generate(prompt, temperature=0.7, max_tokens=3000)

    def answer_question(self, paper: Dict, question: str, context: Optional[str] = None) -> str:
        """
        针对特定论文回答问题

        Args:
            paper: 论文信息
            question: 用户问题
            context: 额外的上下文信息（如论文总结）

        Returns:
            回答
        """
        context_text = f"\n\n论文总结：{context}" if context else ""

        prompt = f"""基于以下论文信息，请回答问题。

论文标题：{paper['title']}

作者：{', '.join(paper['authors'][:5])}

摘要：{paper['summary']}{context_text}

问题：{question}

请用中文详细回答："""

        return self.generate(prompt, temperature=0.6, max_tokens=1500)


class PaperSummarizer:
    """论文总结器（包含总结结果的管理）"""

    def __init__(self, ollama_client: OllamaClient):
        self.client = ollama_client
        self.summaries = {}
        self.trend_analysis = ""

    def process_papers(self, papers: List[Dict]) -> Dict:
        """
        处理论文：总结 + 趋势分析

        Args:
            papers: 论文列表

        Returns:
            包含总结和趋势分析的结果字典
        """
        # 总结每篇论文
        self.summaries = self.client.summarize_papers_batch(papers)

        # 分析研究趋势
        self.trend_analysis = self.client.analyze_research_trends(papers, self.summaries)

        return {
            'summaries': self.summaries,
            'trend_analysis': self.trend_analysis
        }

    def save_results(self, filepath: str):
        """保存总结结果"""
        results = {
            'summaries': self.summaries,
            'trend_analysis': self.trend_analysis
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n总结结果已保存到: {filepath}")

    def load_results(self, filepath: str):
        """加载总结结果"""
        with open(filepath, 'r', encoding='utf-8') as f:
            results = json.load(f)
        self.summaries = results.get('summaries', {})
        self.trend_analysis = results.get('trend_analysis', '')


if __name__ == "__main__":
    # 测试代码
    client = OllamaClient()

    # 测试生成
    response = client.generate("请用中文说'你好，世界！'")
    print(f"测试响应: {response}")
