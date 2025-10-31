#!/bin/bash

# 图表生成脚本
# 使用 Mermaid CLI 将 .mmd 文件转换为 SVG/PNG 图片

echo "🎨 开始生成图表图片..."

# 检查 mmdc 是否安装
if ! command -v mmdc &> /dev/null; then
    echo "❌ Mermaid CLI 未安装"
    echo "请运行: npm install -g @mermaid-js/mermaid-cli"
    exit 1
fi

# 创建输出目录
mkdir -p images/svg
mkdir -p images/png

# 转换所有 .mmd 文件
for file in mermaid/*.mmd; do
    filename=$(basename "$file" .mmd)
    echo "📊 处理: $filename"
    
    # 生成 SVG (矢量图，适合网页)
    mmdc -i "$file" -o "images/svg/${filename}.svg" -b transparent
    
    # 生成 PNG (位图，适合某些平台)
    mmdc -i "$file" -o "images/png/${filename}.png" -b white -w 1200
done

echo "✅ 图表生成完成！"
echo ""
echo "生成的文件:"
echo "- SVG: docs/blog/diagrams/images/svg/"
echo "- PNG: docs/blog/diagrams/images/png/"
echo ""
echo "使用方法:"
echo "在 Markdown 中插入:"
echo '![图表说明](./diagrams/images/svg/01-problem-evolution.svg)'
