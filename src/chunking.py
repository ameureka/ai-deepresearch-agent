"""
分块处理器 - 处理超长文本的分块和合并

功能:
1. 按语义边界（段落）智能分块
2. 保持块间上下文连贯性（重叠区域）
3. 智能合并处理结果
4. 支持自定义块大小和重叠
"""

import logging
import re
from typing import List, Callable, Dict, Any, Optional
from src.model_adapter import ModelAdapter

logger = logging.getLogger(__name__)


class ChunkingProcessor:
    """分块处理器 - 将长文本分块处理后合并"""

    def __init__(self, max_chunk_size: int = 6000, overlap_size: int = 200):
        """
        初始化分块处理器

        Args:
            max_chunk_size: 单个块的最大 token 数（默认: 6000）
            overlap_size: 块间重叠的 token 数（默认: 200）
        """
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size

    def chunk_by_semantic(self, text: str) -> List[str]:
        """
        按语义边界分块（保持段落完整）

        Args:
            text: 需要分块的文本

        Returns:
            分块后的文本列表
        """
        # 1. 按段落分割（双换行）
        paragraphs = text.split('\n\n')

        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = ModelAdapter.estimate_tokens(para)

            # 如果加上这段会超出限制
            if current_tokens + para_tokens > self.max_chunk_size:
                # 保存当前块
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                    current_chunk = []
                    current_tokens = 0

            # 如果单段就超了，强制分割
            if para_tokens > self.max_chunk_size:
                sub_chunks = self._split_long_paragraph(para)
                # 将子块添加到结果
                for sub_chunk in sub_chunks:
                    chunks.append(sub_chunk)
            else:
                current_chunk.append(para)
                current_tokens += para_tokens

        # 最后一块
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))

        logger.info(f"📦 文本分块完成: {len(chunks)} 块")
        return chunks

    def _split_long_paragraph(self, para: str) -> List[str]:
        """
        强制分割超长段落（按句子分割）

        Args:
            para: 超长段落

        Returns:
            分割后的子块列表
        """
        # 按句子分割（支持中英文）
        # 英文: . ! ? 后跟空格
        # 中文: 。！？
        sentences = re.split(r'([.!?。！？])\s+', para)

        # 重新组合句子和标点
        full_sentences = []
        for i in range(0, len(sentences) - 1, 2):
            if i + 1 < len(sentences):
                full_sentences.append(sentences[i] + sentences[i + 1])
            else:
                full_sentences.append(sentences[i])

        # 如果没有成功分割，按固定长度强制分割
        if len(full_sentences) <= 1:
            # 按字符数强制分割（估算 4 字符 = 1 token）
            chunk_chars = self.max_chunk_size * 4
            return [para[i:i+chunk_chars] for i in range(0, len(para), chunk_chars)]

        # 按句子组合成块
        chunks = []
        current_chunk = []
        current_tokens = 0

        for sent in full_sentences:
            sent_tokens = ModelAdapter.estimate_tokens(sent)

            if current_tokens + sent_tokens > self.max_chunk_size:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = []
                    current_tokens = 0

            current_chunk.append(sent)
            current_tokens += sent_tokens

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks

    def process_with_context(
        self,
        chunks: List[str],
        processor_func: Callable[[str], str],
        show_progress: bool = True
    ) -> List[str]:
        """
        带上下文处理每个块

        Args:
            chunks: 文本块列表
            processor_func: 处理函数，接收文本返回处理结果
            show_progress: 是否显示进度（默认: True）

        Returns:
            处理结果列表
        """
        results = []

        for i, chunk in enumerate(chunks):
            if show_progress:
                logger.info(f"📝 处理块 {i+1}/{len(chunks)}...")

            # 构建上下文信息
            context_info = {
                'position': f"{i+1}/{len(chunks)}",
                'is_first': i == 0,
                'is_last': i == len(chunks) - 1,
                'prev_text': self._get_overlap(chunks[i-1], is_end=True) if i > 0 else None,
                'next_text': self._get_overlap(chunks[i+1], is_end=False) if i < len(chunks)-1 else None
            }

            # 构建带上下文的提示
            prompt = self._build_chunk_prompt(chunk, context_info)

            # 处理
            result = processor_func(prompt)
            results.append(result)

        return results

    def _get_overlap(self, text: str, is_end: bool) -> str:
        """
        获取重叠区域的文本

        Args:
            text: 源文本
            is_end: True 表示取结尾，False 表示取开头

        Returns:
            重叠区域的文本
        """
        # 估算重叠字符数（按 4 字符 = 1 token）
        overlap_chars = self.overlap_size * 4

        if is_end:
            # 取最后 overlap_size tokens
            return text[-overlap_chars:] if len(text) > overlap_chars else text
        else:
            # 取前 overlap_size tokens
            return text[:overlap_chars] if len(text) > overlap_chars else text

    def _build_chunk_prompt(self, chunk: str, context: Dict[str, Any]) -> str:
        """
        构建带上下文的提示

        Args:
            chunk: 当前文本块
            context: 上下文信息字典

        Returns:
            完整的提示文本
        """
        parts = []

        # 添加位置信息
        parts.append(f"[📍 文档位置: {context['position']}]")

        # 添加前文
        if context['prev_text']:
            parts.append(f"[⬆️ 前文结尾]:\n...{context['prev_text']}\n")

        # 添加当前内容
        parts.append(f"[📄 当前段落]:\n{chunk}\n")

        # 添加后文
        if context['next_text']:
            parts.append(f"[⬇️ 后文开头]:\n{context['next_text']}...\n")

        # 添加处理说明
        if context['is_first']:
            parts.append("ℹ️ 这是文档的第一部分。")
        elif context['is_last']:
            parts.append("ℹ️ 这是文档的最后一部分。")
        else:
            parts.append("ℹ️ 这是文档的中间部分，请注意与前后文的连贯性。")

        parts.append("\n请处理当前段落，确保与前后文保持连贯。")

        return '\n'.join(parts)

    def merge_chunks(self, chunks: List[str], remove_redundancy: bool = True) -> str:
        """
        合并处理后的块

        Args:
            chunks: 处理后的文本块列表
            remove_redundancy: 是否移除重叠区域的冗余内容（默认: True）

        Returns:
            合并后的文本
        """
        if not chunks:
            return ""

        if len(chunks) == 1:
            return chunks[0]

        # 简单合并（用双换行连接）
        # TODO: 未来可以实现更智能的合并，检测和移除重复内容
        merged = '\n\n'.join(chunks)

        logger.info(f"✅ 合并完成: {len(chunks)} 块 → 1 个文档")
        return merged

    def chunk_and_process(
        self,
        text: str,
        processor_func: Callable[[str], str],
        show_progress: bool = True
    ) -> str:
        """
        一站式分块处理：分块 → 处理 → 合并

        Args:
            text: 需要处理的文本
            processor_func: 处理函数
            show_progress: 是否显示进度

        Returns:
            最终处理结果
        """
        logger.info(f"🚀 开始分块处理 (估算: {ModelAdapter.estimate_tokens(text)} tokens)")

        # 1. 分块
        chunks = self.chunk_by_semantic(text)

        # 2. 处理
        results = self.process_with_context(chunks, processor_func, show_progress)

        # 3. 合并
        final_result = self.merge_chunks(results)

        logger.info("🎉 分块处理完成")
        return final_result
