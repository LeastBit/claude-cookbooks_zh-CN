# ElevenLabs <> Claude 烹饪书

[ElevenLabs](https://elevenlabs.io/) 提供基于AI的语音转文本和文本转语音API，用于创建具有自然语音的应用，包含语音克隆和流式合成等高级功能。

本烹饪书演示如何通过结合ElevenLabs的语音处理和Claude的智能响应，构建低延迟语音助手，并逐步优化以实现实时性能。

## 包含内容

* **[低延迟语音助手笔记本](./low_latency_stt_claude_tts.ipynb)** - 交互式教程，带您逐步构建语音助手，展示通过流式传输最小化延迟的各种优化技术。

* **[WebSocket流式传输脚本](./stream_voice_assistant_websocket.py)** - 生产就绪的对话语音助手，具有连续麦克风输入、无缝音频播放和通过WebSocket流式传输实现的最低可能延迟。

## 如何使用本烹饪书

我们建议按照以下顺序使用，以充分发挥本烹饪书的作用：

### 步骤 1: 设置环境

1. **创建虚拟环境：**
   ```bash
   # 导航到ElevenLabs目录
   cd /path/to/claude-cookbooks/third_party/ElevenLabs

   # 创建虚拟环境
   python -m venv venv

   # 激活它
   source venv/bin/activate  # 在 macOS/Linux 上
   # 或者
   venv\Scripts\activate     # 在 Windows 上
   ```

2. **获取您的API密钥：**
   - **ElevenLabs API密钥：** [elevenlabs.io/app/developers/api-keys](https://elevenlabs.io/app/developers/api-keys)

     创建API密钥时，请确保它具有以下最低权限：
     - 文本转语音
     - 语音转文本
     - 语音读取权限
     - 模型读取权限

   - **Anthropic API密钥：** [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)

3. **配置您的环境：**
   ```bash
   cp .env.example .env
   ```

   编辑 `.env` 并添加您的API密钥：
   ```
   ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
   ANTHROPIC_API_KEY=sk-ant-api03-...
   ```

4. **安装依赖：**
   ```bash
   # 激活venv后
   pip install -r requirements.txt
   ```

### 步骤 2: 学习笔记本

从 **[低延迟语音助手笔记本](./low_latency_stt_claude_tts.ipynb)** 开始。这个交互式指南将教您：

- 如何使用ElevenLabs进行语音转文本转录
- 如何生成Claude响应并测量延迟
- 流式传输如何减少首token时间
- 如何流式传输文本转语音以实现更快的音频播放
- 不同流式传输方法之间的权衡
- 为什么WebSocket流式传输提供了延迟和质量的最佳平衡

笔记本在每个步骤都包含性能指标和比较，帮助您了解每种优化的影响。

### 步骤 3: 尝试生产脚本

理解笔记本中的概念后，运行 **[WebSocket流式传输脚本](./stream_voice_assistant_websocket.py)** 来体验功能齐全的语音助手：

```bash
python stream_voice_assistant_websocket.py
```

**工作原理：**
1. 按Enter键开始录音
2. 将您的问题对着麦克风说出
3. 按Enter键停止录音
4. 助手将以自然语音回应
5. 重复或按Ctrl+C退出

脚本展示了生产就绪的实现：
- 使用sounddevice进行实时麦克风录音
- 具有上下文保留的连续对话
- 基于WebSocket的流式传输，实现最小延迟
- 自定义音频队列，实现无缝播放

## 故障排除

### 音频爆音或咔嗒声

**症状：** 您可能在播放期间偶尔听到短暂的爆音、咔嗒声或音频丢失。

**解释：**

发生这种情况是因为脚本使用MP3格式音频，这是ElevenLabs免费套餐所要求的。当实时流式传输MP3数据块时，FFmpeg偶尔会接收到无法解码的不完整帧。这通常发生在：
- 流式传输开始时（第一个块可能太小）
- 短暂网络延迟期间
- 音频生成结束时（最后一个块可能不完整）

脚本通过跳过这些失败的块来自动处理（使用音频解码逻辑中的try-except模式），这可以防止错误出现在控制台中，但可能导致短暂的音频间隙，表现为爆音或咔嗒声。

**影响：**
- 音频播放继续正常
- 短暂的爆音或咔嗒声通常难以察觉或很小
- WebSocket连接保持稳定
- 没有功能丢失

**解决方案：**

在免费套餐上使用MP3格式时，这是预期行为。如果你想完全消除音频爆音：
1. 升级到付费的ElevenLabs套餐
2. 修改脚本使用 `pcm_44100` 格式而不是MP3
3. PCM格式提供更清晰的流式传输，没有解码问题

### API密钥问题

**症状：** `AssertionError: ELEVENLABS_API_KEY is not set` 或 `AssertionError: ANTHROPIC_API_KEY is not set`

**解决方案：**
1. 验证您已将 `.env.example` 复制到 `.env`：`cp .env.example .env`
2. 编辑 `.env` 并确保两个API密钥都正确设置
3. 检查API密钥中的拼写错误或多余空格
4. 确认您的ElevenLabs密钥具有所需权限（参见步骤1）

### 依赖问题

**症状：** 类似 `ImportError: PortAudio library not found` 的错误或音频播放失败

**解决方案：**

**macOS：**
```bash
brew install portaudio ffmpeg
```

**Ubuntu/Debian：**
```bash
sudo apt-get install portaudio19-dev ffmpeg
```

**Windows：**
- 从 [ffmpeg.org](https://ffmpeg.org/download.html) 安装FFmpeg
- 将FFmpeg添加到系统PATH
- PortAudio通常在Windows上随sounddevice自动安装

然后重新安装Python依赖：
```bash
pip install -r requirements.txt
```

### 麦克风权限

**症状：** `OSError: [Errno -9999] Unanticipated host error` 或麦克风无法访问

**解决方案：**
- **macOS：** 进入系统偏好设置 → 安全性与隐私 → 隐私 → 麦克风，并启用终端（或您的Python IDE）
- **Windows：** 进入设置 → 隐私 → 麦克风，并为Python/终端启用麦克风访问
- **Linux：** 检查您的用户是否在 `audio` 组中：`sudo usermod -a -G audio $USER`（然后登出并重新登录）

测试您的麦克风设置：
```bash
python -c "import sounddevice as sd; print(sd.query_devices())"
```

### WebSocket连接失败

**症状：** 连接错误、超时或流中断

**解决方案：**
1. 检查您的互联网连接稳定
2. 验证防火墙未阻止WebSocket连接（端口443）
3. 尝试暂时禁用VPN或代理
4. 确保您未超过API速率限制（参见ElevenLabs仪表板的使用情况）

如果您继续遇到问题，请查看 [ElevenLabs状态](https://status.elevenlabs.io/) 以获取服务更新。

## 项目创意

一旦您熟悉了语音助手，以下是一些可以构建的启发性项目：

- **会议记录员** - 实时记录和转录会议，然后使用Claude生成摘要、行动项目和对话要点。

- **语言学习导师** - 用任何语言练习对话并获得实时反馈。Claude可以纠正发音、建议更好的措辞，并根据您的技能水平调整难度。

- **互动故事讲述者** - 创建选择你自己的冒险游戏，让Claude讲述故事并回应您的口语选择，每个角色都有不同的声音特征。

- **免手动编码助手** - 口头描述代码更改、错误或功能，同时保持双手在键盘上。非常适合橡皮鸭调试或单人结对编程。

- **语音激活智能家居** - 为控制家庭设备构建自然对话界面。问复杂的问题，如"天气冷到足以打开暖气吗？"而不是简单的开/关命令。

- **个人语音日志** - 通过说出您的想法来保持每日日志。Claude可以按主题组织条目，跟踪您的情绪随时间的变化，并在您需要时展示相关过去条目。

## 更多关于ElevenLabs

以下是一些有助于深化您理解的资源：

- [ElevenLabs平台](https://elevenlabs.io/) - 官方网站
- [API文档](https://elevenlabs.io/docs/overview) - 完整的API参考
- [语音库](https://elevenlabs.io/voice-library) - 探索可用语音
- [API游乐场](https://elevenlabs.io/app/speech-synthesis/text-to-speech) - 交互式测试语音
- [Python SDK](https://github.com/elevenlabs/elevenlabs-python) - 官方Python SDK