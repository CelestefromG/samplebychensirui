# Insight to Idea

美妆消费者评论驱动的交互创意工作台。首版为无依赖静态网页，数据筛选、图表、评论定位与导出均在浏览器本地运行。

## v0.2 细分情绪分析

- 18 个具体体验：泛红、刺痛、冒痘、滋润、干燥、黏腻、吸收、轻薄、推开、泛白、搓泥、香味、提亮、清洁、包装、价格、效果变化和正品疑虑。
- 使用英文分句、词典与否定规则初判。不是模型输出，也不是人工逐条复核。每个标签保留命中的原句；每组每主题一条标签。
- 整体情绪分为正面、负面、褒贬并存、待判断，不使用星级替代文本情绪。
- 情绪环图、体验气泡图、品类热力图与原文联动。原始人工大类标签在 sourceAnnotations 中保留，当前图表不再使用。
- 原文 962 组中 559 组覆盖具体主题，共 890 条细分标签。未命中具体主题不被强行归入其他。

## 内容

- 上传工作簿中的 2,003 条方面标注行，按产品名与原文合并为 962 个文本组。
- 对同组、同方面、同情绪去重后，保留 1,965 条标注及所有原始工作表行号。
- 按四个品类和 110 件产品筛选；查看关注点、正负构成、原文证据与源行。
- 创意区提供 AI 预编写模块的规则组装示例，明确标注非实时模型生成。
- 提示词包含真实评论证据、统计与 Brief；支持导入外部模型结果，检查结构与证据 ID。
- 导出洞察 JSON、含原文证据的创意 Markdown 和提示词 TXT。

## 数据来源

An Aspect-Based Sentiment Analysis Dataset of Skincare Product Reviews from Bangladeshi E-Commerce Platforms, Version 2.

Mangsura Kabir Oni; Khandoker Nosiba Arifin; Iffat Ara Sanzida; Sayma Akter Rupa; Md Musfique Anwar.

https://data.mendeley.com/datasets/6vmrcypy7c/2

DOI: 10.17632/6vmrcypy7c.2. CC BY 4.0: https://creativecommons.org/licenses/by/4.0/

评论保留原文。合并与标签去重属于处理。原始日期包含异常与同文多日期情况，未用于趋势分析。文本组无法确认独立消费者，原始人工标签可能有误。数据不代表中国市场。

## 验证

`python scripts/verify_analysis.py`

`node scripts/verify.mjs`

重建数据：先运行 scripts/prepare_data.py，再运行 scripts/annotate_reviews.py。

核对来源行数、全部品类与方面统计、证据过滤、空样本、创意生成、无效模型引用拒绝和 HTML 转义。尚未完成实际浏览器视觉 QA。

## 后续

接入服务端模型接口并配置密钥后，可替换示例组装为实时创意生成。不得将 API 密钥写入网页。实时模型调用尚未接入；创意区提供明确标注的预编写示例及外部模型结果导入。


## GitHub Pages 部署

本仓库使用无依赖静态网站。网站文件位于 `docs/`，资源路径支持 GitHub Pages 项目子路径。

在仓库 Settings → Pages 中选择 Deploy from a branch，分支 `main`，目录 `/docs`。

本地预览：`python -m http.server 8000 --directory docs`。

重建数据时运行 `python scripts/prepare_data.py /path/to/Skincare_Product_Reviews_Dataset.xlsx`，随后运行 `python scripts/annotate_reviews.py`。读取 Excel 需要 openpyxl。
