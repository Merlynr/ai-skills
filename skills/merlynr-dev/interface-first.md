# Interface-First：接口先行（M2.5）

**来源**：个人经验「模块边界比实现更重要」；案例「先定义接口再分模块实现」。

在 **M3 写实现代码之前** 完成接口定义与冻结。L 级强制；M 级在跨模块或 public API 变更时强制。

## 何时启用

| 级别 | 条件 |
|------|------|
| **S** | 跳过 |
| **M** | 跨模块调用、新增/改 public 头文件、多文件联动 |
| **L** | 一律强制 |

## 执行步骤

```text
1. 模块职责（一句话 + 不做什么）
2. 输入 / 输出（类型、所有权、线程上下文）
3. 错误码 / 返回值约定
4. 状态机（若有）
5. 生命周期与资源所有权（谁 alloc/free、谁 hold ref）
6. 与现有代码的符号对照表
7. 用户或 reviewer 确认 → 冻结
```

**冻结后**：implement 阶段 **禁止** 静默修改已冻结的 public 签名。

L 级若有 [grill-pro.md](grill-pro.md) Handoff，Interface Handoff 应与其中 **模块候选、验证策略** 一致；不一致须在 Decisions 说明。

## Interface Handoff 模板

产出写入模块目录 `INTERFACE.md`，或在有 `.planning/` 时写入 `.planning/interface/{module}.md`。**同时**在回复中粘贴 Handoff 块。

```markdown
## Interface Handoff（YYYY-MM-DD）

- **模块**: {name}
- **级别**: M | L | M+ | L-lite
- **handoff_version**: v1（冻结后递增；D2 见 interface-change-protocol）
- **Playbook 倾向**: 插件型 | 规则引擎型 | 流量分派型 | 自定义 | 待定
- **Grill-Pro 引用**: {日期或路径}（L 级若有）
- **状态**: 草案 | 已冻结

### 职责
- **做**: …
- **不做**: …

### 输入
| 名称 | 类型/格式 | 来源 | 线程/上下文 |
|------|-----------|------|-------------|
| … | … | … | … |

### 输出
| 名称 | 类型/格式 | 消费者 | 所有权转移 |
|------|-----------|--------|------------|
| … | … | … | … |

### 错误码 / 返回值
| 码 | 含义 | 调用方处理 |
|----|------|------------|
| … | … | … |

### 状态机（可选）
```text
INIT → LOADED → ACTIVE → SHUTDOWN
         ↓ 失败
       ROLLBACK
```

### 生命周期
- **创建**: …
- **转移**: …（如 Flow transfer 到输出线程）
- **销毁**: …

### 符号对照表
| 新接口 | 现有符号（Cymbal 或 path:symbol） | 关系 |
|--------|----------------------------------|------|
| `foo_init` | `modules/x/mgr.c:legacy_init` | 替换 |
| … | … | 复用 / 新增 |

### 独立验证方式
- 命令: `…`
- 通过标准: …

### 冻结确认
- [ ] 用户 / reviewer 已确认可进入 M3
```

## 无 Cymbal 时的符号对照表

改用 **文件路径 + 函数名**：

```text
modules/dispatch/dispatch-rule.c:dispatch_rule_reload
src/frame/matcher.c:matcher_match_flow
```

## 接口变更协议

简要版见上节冻结约束。**完整六步流程与 G4 回归影响面** → Read [interface-change-protocol.md](interface-change-protocol.md)。

已冻结后改 public 签名 **必须** 走 D2，禁止静默修改。

## 与 GSD 的衔接

| 有 `.planning/` | 无 `.planning/` |
|-----------------|-----------------|
| Handoff 作为 `gsd-spec-phase` / `gsd-plan-phase` 输入 | Handoff + `INTERFACE.md` 即 spec；可直接 M3 |
| spec 不得与已冻结 Handoff 矛盾 | 同上 |

## 反模式

- 未冻结就写多文件实现
- Handoff 只有 prose 没有 IO 表
- 符号对照表为空（未做 M1 探库）
- 把未验证的「大概这样」标为已冻结
