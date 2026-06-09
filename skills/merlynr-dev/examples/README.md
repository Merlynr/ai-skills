# G3：案例锚点索引

三案例来自《AI 编程案例分享》；用于 module-patterns Playbook 对照。**本任务像哪种模式** → 打开对应摘要。

| Playbook | 摘要 | 规模 | 代码锚点（内网） |
|----------|------|------|------------------|
| **插件型** | [plugin-module.md](plugin-module.md) | 24 文件 / 3858 行 | http://192.168.126.14:60001/root/perseus7/-/tree/plugin |
| **规则引擎型** | [rule-engine.md](rule-engine.md) | 117 文件 / 27247 行 | http://192.168.126.241:60001/root/perseus7-dev/-/tree/p7-2-full-traffic/jxh-rule |
| **流量分派型** | [traffic-dispatch.md](traffic-dispatch.md) | 9 文件 / 5880 行 | http://192.168.126.241:60001/root/perseus7-dev/-/tree/base-dpi-p7-2-add-disp-ring/dispatch |

> 上表链接为 **Merlynr 内网 Perseus 实例**，外网/无 VPN 不可访问。**不阻塞** Playbook 使用——以外链下 [摘要 md](plugin-module.md) 为准。

## 用法（M2）

1. 读任务描述 → 选最接近 Playbook（可混合，在模块清单注明「主模式」）。
2. 打开摘要 → 复制模块树作 **初稿**，按当前项目 M1 证据改命名。
3. L 级：在 Grill-Pro Handoff 填 `Playbook 倾向`；可选 `merlynr-handoff.json` → `"playbook": "rule-engine"`。

## 与 module-health（G1）

每个 Playbook leaf 模块做 [module-health.md](../module-health.md) 评分后再 M2.5。

## 外链不可用

降级：仅读摘要 md，不依赖 Git 浏览器；M1 探库当前仓库类似目录结构。
