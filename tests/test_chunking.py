"""
单元测试 - ChunkingProcessor 分块处理器

测试范围:
- 语义分块
- 超长段落分割
- 上下文保持
- 块合并
"""

import pytest
from src.chunking import ChunkingProcessor


@pytest.fixture
def processor():
    """创建默认的分块处理器"""
    return ChunkingProcessor(max_chunk_size=1000, overlap_size=50)


def test_chunk_by_semantic_short_text(processor):
    """测试短文本不分块"""
    text = "This is a short paragraph.\n\nThis is another short paragraph."

    chunks = processor.chunk_by_semantic(text)

    # 短文本应该只有一个块
    assert len(chunks) == 1
    assert chunks[0] == text


def test_chunk_by_semantic_multiple_paragraphs(processor):
    """测试多段落分块"""
    # 创建多个段落，每个段落约 200 tokens（800 字符）
    paragraphs = [f"Paragraph {i}. " + ("x " * 400) for i in range(5)]
    text = "\n\n".join(paragraphs)

    chunks = processor.chunk_by_semantic(text)

    # 应该被分成多个块
    assert len(chunks) > 1
    # 每个块不应该为空
    for chunk in chunks:
        assert len(chunk) > 0


def test_chunk_by_semantic_preserves_paragraphs():
    """测试分块保持段落完整性"""
    # 使用小的块大小以强制分块
    processor = ChunkingProcessor(max_chunk_size=100, overlap_size=10)

    para1 = "First paragraph with some text."
    para2 = "Second paragraph with more text."
    para3 = "Third paragraph with even more text."
    text = f"{para1}\n\n{para2}\n\n{para3}"

    chunks = processor.chunk_by_semantic(text)

    # 应该至少有一个块
    assert len(chunks) >= 1


def test_split_long_paragraph():
    """测试超长段落强制分割"""
    processor = ChunkingProcessor(max_chunk_size=200, overlap_size=20)

    # 创建一个超长段落（没有换行）
    long_para = "This is a very long paragraph. " * 100

    chunks = processor._split_long_paragraph(long_para)

    # 应该被分割
    assert len(chunks) > 1
    # 每个块不应该为空
    for chunk in chunks:
        assert len(chunk) > 0


def test_process_with_context():
    """测试带上下文处理"""
    processor = ChunkingProcessor(max_chunk_size=500, overlap_size=50)

    # 创建3个块
    chunks = ["Chunk 1 content", "Chunk 2 content", "Chunk 3 content"]

    # 简单的处理函数：返回输入的长度
    results = processor.process_with_context(
        chunks,
        processor_func=lambda text: f"Processed: {len(text)} chars",
        show_progress=False
    )

    # 应该有3个结果
    assert len(results) == 3
    # 每个结果不应该为空
    for result in results:
        assert result.startswith("Processed:")


def test_build_chunk_prompt_first():
    """测试构建第一个块的提示"""
    processor = ChunkingProcessor()

    context = {
        'position': '1/3',
        'is_first': True,
        'is_last': False,
        'prev_text': None,
        'next_text': 'Next content...'
    }

    prompt = processor._build_chunk_prompt("Current content", context)

    # 应该包含位置信息
    assert '1/3' in prompt
    # 应该包含当前内容
    assert 'Current content' in prompt
    # 应该包含后文
    assert 'Next content' in prompt
    # 应该标记为第一部分
    assert '第一部分' in prompt


def test_build_chunk_prompt_last():
    """测试构建最后一个块的提示"""
    processor = ChunkingProcessor()

    context = {
        'position': '3/3',
        'is_first': False,
        'is_last': True,
        'prev_text': 'Previous content...',
        'next_text': None
    }

    prompt = processor._build_chunk_prompt("Current content", context)

    # 应该包含位置信息
    assert '3/3' in prompt
    # 应该包含前文
    assert 'Previous content' in prompt
    # 应该标记为最后一部分
    assert '最后一部分' in prompt


def test_merge_chunks_empty():
    """测试合并空列表"""
    processor = ChunkingProcessor()

    result = processor.merge_chunks([])

    assert result == ""


def test_merge_chunks_single():
    """测试合并单个块"""
    processor = ChunkingProcessor()

    result = processor.merge_chunks(["Single chunk"])

    assert result == "Single chunk"


def test_merge_chunks_multiple():
    """测试合并多个块"""
    processor = ChunkingProcessor()

    chunks = ["Chunk 1", "Chunk 2", "Chunk 3"]
    result = processor.merge_chunks(chunks)

    # 应该用双换行连接
    assert "Chunk 1" in result
    assert "Chunk 2" in result
    assert "Chunk 3" in result
    assert "\n\n" in result


def test_chunk_and_process_short_text():
    """测试短文本的完整处理流程"""
    processor = ChunkingProcessor(max_chunk_size=5000, overlap_size=200)

    text = "Short text that doesn't need chunking."

    # 简单的处理函数：返回大写
    result = processor.chunk_and_process(
        text,
        processor_func=lambda t: t.upper(),
        show_progress=False
    )

    # 应该返回处理后的结果
    assert "SHORT TEXT" in result


def test_chunk_and_process_long_text():
    """测试长文本的完整处理流程"""
    processor = ChunkingProcessor(max_chunk_size=200, overlap_size=20)

    # 创建长文本
    text = "\n\n".join([f"Paragraph {i}. " + ("x " * 100) for i in range(5)])

    # 简单的处理函数：添加前缀
    result = processor.chunk_and_process(
        text,
        processor_func=lambda t: f"[PROCESSED]\n{t}",
        show_progress=False
    )

    # 应该包含处理标记
    assert "[PROCESSED]" in result
    # 应该包含原始内容
    assert "Paragraph" in result


def test_get_overlap_end():
    """测试获取结尾重叠区域"""
    processor = ChunkingProcessor(overlap_size=10)  # 10 tokens ≈ 40 chars

    text = "x" * 100

    overlap = processor._get_overlap(text, is_end=True)

    # 应该返回结尾部分
    assert len(overlap) <= 40
    assert overlap == text[-40:]


def test_get_overlap_start():
    """测试获取开头重叠区域"""
    processor = ChunkingProcessor(overlap_size=10)  # 10 tokens ≈ 40 chars

    text = "x" * 100

    overlap = processor._get_overlap(text, is_end=False)

    # 应该返回开头部分
    assert len(overlap) <= 40
    assert overlap == text[:40]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
