# AuraCap Timeline

This file appends one markdown-json entry per trigger.
### entry-cc8bf6991ca147b9af5d7b09f1dfb7fa
```json
{
  "id": "entry-cc8bf6991ca147b9af5d7b09f1dfb7fa",
  "timestamp": "2026-02-26T15:49:19.820443+00:00",
  "timestamp_display": "2026-02-26 15:49:19 UTC",
  "extracted_content": "### 核心内容\n\n- **测试对象**：Qwen3.5 的 35B 和 27B 模型，均使用 FP8 精度。\n- **硬件配置**：单卡 4090，显存 48G。\n- **测试结果**：\n  - **35B 模型**：\n    - 单卡请求速度 120-130 时，200k 上下文仅能衰退到 90，性能不足。\n  - **27B 模型**：\n    - Dense 模型性能较好，输出稳定在 20t/s。\n    - 200k 前缓冲 4k 输入时，保持 19t/s 左右，prefill 时间约 200 毫秒。\n    - 使用 Agent Teams 并发，六个并发稳定输出 120t，任务完成。\n\n### 行动项\n\n- **优化方向**：27B 模型性能表现较好，值得进一步挖掘其潜力。\n- **改进建议**：尝试提升 27B 模型的速度，优化时间消耗。\n\n### 待确认\n\n- **时间优化**：是否有进一步提升 prefill 时间的可能性。"
}
```

### entry-29855104f239432c9e0e9735838e20b6
```json
{
  "id": "entry-29855104f239432c9e0e9735838e20b6",
  "timestamp": "2026-02-26T16:27:35.771356+00:00",
  "timestamp_display": "2026-02-26 16:27:35 UTC",
  "extracted_content": "### 核心内容\n- **研究背景**：探讨了LLM（大语言模型）的Base与Instruct之间的权重相似性，定义了权重的sigma值。\n- **关键数据**：Qwen 3.5 A3B的Base模型sigma值为 **0.01768391**，约为1%上下，表明相似性极高。\n- **补充说明**：主流LLM的sigma值普遍较小，具体细节可参考P2论文。\n\n### 行动项\n- 进一步研究P2和P3论文中的相关细节。\n\n### 标签\n#Qwen3 #weight #LLM #HKU #相似性 #reasoning"
}
```

