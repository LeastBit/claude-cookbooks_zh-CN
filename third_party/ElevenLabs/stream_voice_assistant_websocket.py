"""具有WebSocket流式传输的低延迟语音助手

生产就绪的对话语音助手，展示实时语音转文本、Claude集成和低延迟文本转语音。

用法：
    1. 设置环境变量：
       - 将 .env.example 复制到 .env
       - 将您的API密钥添加到 .env：
         * 获取ElevenLabs API密钥：https://elevenlabs.io/app/developers/api-keys
         * 获取Anthropic API密钥：https://console.anthropic.com/settings/keys

    2. 安装依赖：
       pip install -r requirements.txt

    3. 运行脚本：
       python stream_voice_assistant_websocket.py

    4. 交互流程：
       - 按Enter键开始录音
       - 对着麦克风说话
       - 按Enter键停止录音
       - Claude将以合成语音回应
       - 重复或按Ctrl+C退出

关键优化：
- 从Claude收到的文本块立即发送到TTS
- 无需句子缓冲 - 音频生成立即开始
- MP3音频格式与免费套餐兼容
- 带预缓冲的连续音频流防止爆音
"""

import base64
import io
import json
import os
import threading
import time

import anthropic
import elevenlabs
import numpy as np
import sounddevice as sd
import websocket
from dotenv import load_dotenv
from pydub import AudioSegment
from scipy.io import wavfile

# 从 .env 文件加载环境变量
load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

assert ELEVENLABS_API_KEY is not None, "错误：未找到ELEVENLABS_API_KEY。请将 .env.example 复制到 .env 并添加您的API密钥。"
assert ANTHROPIC_API_KEY is not None, "错误：未找到ANTHROPIC_API_KEY。请将 .env.example 复制到 .env 并添加您的API密钥。"

SAMPLE_RATE = 44100  # 录音音频采样率
CHANNELS = 1  # 单声道音频

elevenlabs_client = elevenlabs.ElevenLabs(
    api_key=ELEVENLABS_API_KEY,
    base_url="https://api.elevenlabs.io"
)

anthropic_client = anthropic.Anthropic(
    api_key=ANTHROPIC_API_KEY
)

# 获取可用语音并选择第一个
voices = elevenlabs_client.voices.search().voices
selected_voice = voices[0]
VOICE_ID = selected_voice.voice_id
print(f"使用语音: {selected_voice.name} (ID: {VOICE_ID})")

# TTS配置
TTS_MODEL_ID = "eleven_turbo_v2_5"  # 快速、低延迟模型
TTS_OUTPUT_FORMAT = "mp3_44100_128"  # MP3格式（免费套餐兼容）


class AudioQueue:
    """管理连续音频播放，最小化延迟。

    使用sounddevice OutputStream与基于回调的流式传输：
    - 维护一个字节缓冲区用于传入音频块
    - 流式回调实时从缓冲区读取
    - 预缓冲防止缓冲区下溢导致的爆音
    """
    # 音频缓冲区配置常量
    PRE_BUFFER_SIZE = 8192  # 播放开始前的最小缓冲区大小（防止初始爆音）
    BUFFER_CLEANUP_THRESHOLD = 100000  # 缓冲区清理前的字节数，防止内存增长
    REMAINING_BYTES_THRESHOLD = 1000  # 考虑播放有效完成的字节数

    def __init__(self):
        self.buffer = bytearray()
        self.buffer_lock = threading.Lock()
        self.playing = False
        self.stream = None
        self.first_audio_played = False
        self.first_audio_time = None
        self.sample_rate = 44100
        self.channels = 2
        self.finished = False
        self.read_position = 0

    def add(self, audio_data):
        """将MP3音频块添加到播放缓冲区。

        Args:
            audio_data: 原始MP3音频字节
        """
        try:
            # 将MP3解码为PCM
            audio_segment = AudioSegment.from_mp3(io.BytesIO(audio_data))

            # 转换为numpy数组
            samples = np.array(audio_segment.get_array_of_samples(), dtype=np.int16)
            samples = samples.astype(np.float32) / 32768.0

            if not self.playing:
                self.sample_rate = audio_segment.frame_rate
                self.channels = audio_segment.channels

            # 根据通道数重新整形
            if self.channels > 1:
                samples = samples.reshape((-1, self.channels))
            else:
                samples = samples.reshape((-1, 1))

            with self.buffer_lock:
                self.buffer.extend(samples.tobytes())

            # 预缓冲后开始播放
            if not self.playing and len(self.buffer) >= self.PRE_BUFFER_SIZE:
                self.start_playback()
        except:
            # 静默跳过无法解码的无效MP3块
            # 这在实时流式传输MP3数据时很常见，因为块可能包含
            # 不完整的帧。跳过这些可以防止控制台错误，但可能导致
            # 短暂的音频爆音。要消除爆音，升级到付费ElevenLabs套餐
            # 并使用pcm_44100格式而不是MP3。
            pass

    def start_playback(self):
        """启动音频输出流。"""
        self.playing = True

        def callback(outdata, frames, _time_info, _status):
            """由sounddevice调用以填充输出缓冲区。"""
            if not self.first_audio_played:
                self.first_audio_time = time.time()
                self.first_audio_played = True

            bytes_needed = frames * self.channels * 4

            with self.buffer_lock:
                bytes_available = len(self.buffer) - self.read_position
                bytes_to_read = min(bytes_needed, bytes_available)

                if bytes_to_read > 0:
                    data = bytes(self.buffer[self.read_position:self.read_position + bytes_to_read])
                    self.read_position += bytes_to_read

                    if self.read_position > self.BUFFER_CLEANUP_THRESHOLD:
                        self.buffer = self.buffer[self.read_position:]
                        self.read_position = 0
                else:
                    data = b''

            if len(data) > 0:
                audio_array = np.frombuffer(data, dtype=np.float32)
                audio_array = audio_array.reshape((-1, self.channels))

                samples_to_write = min(len(audio_array), frames)
                if samples_to_write > 0:
                    outdata[:samples_to_write] = audio_array[:samples_to_write]
                if samples_to_write < frames:
                    outdata[samples_to_write:] = 0
            else:
                outdata[:] = 0

        self.stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            callback=callback,
            dtype=np.float32,
            blocksize=2048
        )
        self.stream.start()


    def wait_until_done(self):
        """阻塞直到所有缓冲音频播放完成。"""
        while True:
            with self.buffer_lock:
                remaining = len(self.buffer) - self.read_position
            if remaining < self.REMAINING_BYTES_THRESHOLD:
                break
            time.sleep(0.1)

        time.sleep(0.5)

        if self.stream:
            self.stream.stop()
            self.stream.close()
        self.playing = False


def record_audio():
    """从麦克风录音，使用Enter键开始和停止。

    Returns:
        io.BytesIO: WAV格式音频缓冲区
    """
    input("按Enter键开始录音...")
    print("录音中... 按Enter键停止。")
    recording = []

    def callback(indata, _frames, _time_info, _status):
        """回调函数，将音频块追加到录音列表中。"""
        recording.append(indata.copy())

    # 创建音频输入流
    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        callback=callback,
        dtype=np.float32
    )

    stream.start()
    input()  # 等待Enter键按下
    stream.stop()
    stream.close()

    # 将所有音频块连接为单个数组
    audio_data = np.concatenate(recording, axis=0)

    # 将float32音频转换为int16 WAV格式
    audio_buffer = io.BytesIO()
    audio_int16 = (audio_data * 32767).astype(np.int16)
    wavfile.write(audio_buffer, SAMPLE_RATE, audio_int16)
    audio_buffer.seek(0)

    return audio_buffer


def transcribe_audio(audio_buffer):
    """使用ElevenLabs语音转文本转录音频。

    Args:
        audio_buffer: WAV格式的音频数据

    Returns:
        str: 转录文本
    """
    print("\n转录中...")

    # 使用ElevenLabs Scribe模型进行语音转文本
    transcription = elevenlabs_client.speech_to_text.convert(
        file=audio_buffer,
        model_id="scribe_v1"
    )

    print(f"转录: {transcription.text}")

    return transcription.text


def stream_claude_and_synthesize_ws(messages, audio_queue):
    """直接将Claude响应流式传输到ElevenLabs WebSocket。

    文本块立即发送到TTS，无需缓冲，
    实现从第一个token到第一个音频的最小延迟。

    Args:
        messages: 对话历史记录（消息字典列表）
        audio_queue: AudioQueue实例

    Returns:
        str: 完整的助手响应文本
    """
    print("\n流式传输Claude响应...\n")

    ws_url = f"wss://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream-input?model_id={TTS_MODEL_ID}&output_format={TTS_OUTPUT_FORMAT}"

    ws_connected = False
    ws_finished = False

    def on_message(ws, message):
        """处理传入的WebSocket消息。"""
        nonlocal ws_finished
        data = json.loads(message)

        if "audio" in data and data["audio"]:
            audio_bytes = base64.b64decode(data["audio"])
            audio_queue.add(audio_bytes)

        # 检查生成是否完成
        if data.get("isFinal"):
            ws_finished = True

    def on_error(ws, error):
        print(f"\nWebSocket错误: {error}")

    def on_close(ws, close_status_code, close_msg):
        """处理WebSocket连接关闭。"""
        if close_status_code or close_msg:
            print(f"\nWebSocket关闭，状态码: {close_status_code}: {close_msg}")

    def on_open(ws):
        nonlocal ws_connected
        ws_connected = True

        initial_message = {
            "text": " ",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.8
            },
            "xi_api_key": ELEVENLABS_API_KEY
        }
        ws.send(json.dumps(initial_message))

    ws = websocket.WebSocketApp(
        ws_url,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open
    )

    ws_thread = threading.Thread(target=ws.run_forever)
    ws_thread.daemon = True
    ws_thread.start()

    while not ws_connected:
        time.sleep(0.01)

    response_text = ""

    # 流式传输Claude响应并将每个块发送到WebSocket
    with anthropic_client.messages.stream(
        model="claude-haiku-4-5",
        max_tokens=1000,
        temperature=0,
        system="""您是一个有用的语音助手。您的响应将使用ElevenLabs转换为语音。
不要使用markdown格式，因为这样无法正常朗读。""",
        messages=messages
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            response_text += text
            ws.send(json.dumps({
                "text": text,
                "try_trigger_generation": True
            }))

    ws.send(json.dumps({"text": ""}))

    # 等待WebSocket发出完成信号
    while not ws_finished:
        time.sleep(0.1)

    ws.close()
    ws_thread.join(timeout=2)
    print()

    return response_text


def main():
    """主执行循环。"""
    print("=== 低延迟语音助手 (WebSocket) ===\n")
    print("按Ctrl+C退出\n")

    conversation_history = []

    try:
        while True:
            audio_buffer = record_audio()
            enter_pressed_time = time.time()

            transcription = transcribe_audio(audio_buffer)
            conversation_history.append({"role": "user", "content": transcription})

            audio_queue = AudioQueue()
            response_text = stream_claude_and_synthesize_ws(conversation_history, audio_queue)
            conversation_history.append({"role": "assistant", "content": response_text})

            audio_queue.wait_until_done()

            if audio_queue.first_audio_time:
                time_to_first_audio = audio_queue.first_audio_time - enter_pressed_time
                print(f"首音频时间: {time_to_first_audio:.2f}s\n")
    except KeyboardInterrupt:
        print("\n\n退出中...")


if __name__ == "__main__":
    main()
