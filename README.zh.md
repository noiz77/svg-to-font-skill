[English](README.md) ｜ 中文

# svg-to-font — Agent Skill

一个通用的 AI coding agent 技能，将一组 SVG 字形文件转换为完整的、可投入生产的字体包：**OTF 桌面字体**、**WOFF2 网络字体**、**CSS 图标类** 以及**交互式 HTML 预览页面**。

## 如何制作自己的 SVG 字体？

如果没有 SVG 字体文件，可以使用**文生图模型**（推荐 Nano Banana Pro / Nano Banana 2）生成一张字体图片，再使用设计软件处理，方法如下（适用英文）：

### Step 1 生成字体设计

#### 方法一：有字体参考图

![方法一：参考图 + 提示词](screenshots/image1.png)

参考图 + 提示词：

```
依据整个字体的设计手法，设计一份包含：a-z，A-Z，0-9，以及特殊符号的英文字体。以全小写、全大写、特殊符号的顺序排列。
```

#### 方法二：没有字体参考图

![方法二：纯提示词生成](screenshots/image2.png)

提示词描述字体风格：

```
设计一份打字机风格的英文字体。
包含：a-z，A-Z，0-9，以及特殊符号的英文字体。以全小写、全大写、0-9、特殊符号的顺序排列。
白色背景，黑色字体。
```

> 生成的图片可能会存在字母重复或符号丢失，不满意可重新生成或人工后期调整。

### Step 2 调整字体细节

![在 Figma 中整理 SVG](screenshots/image3.png)

> 将生成的图片使用插件或者 Adobe Illustrator 的「图像临摹 - 黑白徽标」转为 SVG，导入 Figma，做好形状合并 + 排列好字母的基准线 + 画板命名，整理完成后导出为 SVG（以英文为例，一般为 94 个画板）。

### Step 3 使用该 Skill，最终得到字体文件

![使用 Skill 生成字体](screenshots/image4.png)

## SKILL 功能介绍

向你的 coding agent 发出如下指令：

- "用这些 SVG 生成一个字体"
- "把我的 SVG 字形转换成图标字体"
- "从 `./svg` 目录中的文件生成 OTF 和 WOFF2"

Agent 会引导你完成命名规范和配置，然后运行内置的 Python 脚本，生成以下文件：

```
output/
├── fonts/
│   ├── my-font.otf       # 桌面字体（CFF 三次贝塞尔曲线）
│   └── my-font.woff2     # 网络字体（Brotli 压缩）
├── css/
│   └── my-font.css       # @font-face + 图标 ::before 类
└── my-font.html          # 交互式预览页面
```

## 安装

请将本仓库安装到你所使用 agent 的 skill 目录，或使用该 agent 提供的 skill 安装器。

### 推荐方式

如果你的 agent 支持从 GitHub 安装 skill，优先使用它的安装器。

对于 Codex，你可以让 Codex 使用 `$skill-installer` 安装这个仓库。

### 手动安装

将仓库克隆到你的 agent skill 搜索路径：

```bash
git clone https://github.com/noiz77/svg-to-font-skill.git <your-agent-skills-dir>/svg-to-font
```

常见示例：

```bash
# Codex
git clone https://github.com/noiz77/svg-to-font-skill.git ~/.codex/skills/svg-to-font

# Claude Code
git clone https://github.com/noiz77/svg-to-font-skill.git ~/.claude/skills/svg-to-font
```

如果你的 agent 使用其他目录，请将 `<your-agent-skills-dir>` 替换成对应路径。

然后安装所需的 Python 依赖：

```bash
python3 -m pip install fonttools brotli
```

重启或重新加载你的 agent 后，该技能即可被发现。

## 卸载

从你安装时使用的目录中删除该 skill 文件夹：

```bash
rm -rf <your-agent-skills-dir>/svg-to-font
```

常见示例：

```bash
# Codex
rm -rf ~/.codex/skills/svg-to-font

# Claude Code
rm -rf ~/.claude/skills/svg-to-font
```

## 环境要求

- Python 3.8+
- `fonttools` 和 `brotli` Python 包
- 可以运行 Python 脚本的 coding agent 或终端环境

## 许可证

MIT
