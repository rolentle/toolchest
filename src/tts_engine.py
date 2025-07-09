import json
import queue
import time
from typing import Callable, List, Optional

import mlx.core as mx
import mlx.nn as nn
import numpy as np
import sentencepiece
from moshi_mlx import models
from moshi_mlx.models.tts import (
    DEFAULT_DSM_TTS_REPO,
    DEFAULT_DSM_TTS_VOICE_REPO,
    TTSModel,
)
from moshi_mlx.utils.loaders import hf_get

try:
    from .config import AudioConfig, TTSConfig
    from .logger import Logger
except ImportError:
    from config import AudioConfig, TTSConfig
    from logger import Logger


class TTSEngine:
    def __init__(
        self,
        hf_repo: str = DEFAULT_DSM_TTS_REPO,
        voice_repo: str = DEFAULT_DSM_TTS_VOICE_REPO,
        quantize: Optional[int] = None,
    ):
        self.hf_repo = hf_repo
        self.voice_repo = voice_repo
        self.quantize = quantize
        self.model = None
        self.audio_tokenizer = None
        self.text_tokenizer = None
        self.tts_model = None
        self.mimi = None
        self.wav_frames = queue.Queue()
        self.logger = Logger("TTSEngine")
        
    def initialize(self):
        mx.random.seed(TTSConfig.RANDOM_SEED)
        
        self.logger.info("retrieving checkpoints")
        
        raw_config = hf_get(TTSConfig.CONFIG_FILE_NAME, self.hf_repo)
        with open(hf_get(raw_config), "r") as fobj:
            raw_config = json.load(fobj)
        
        mimi_weights = hf_get(raw_config["mimi_name"], self.hf_repo)
        moshi_name = raw_config.get("moshi_name", TTSConfig.DEFAULT_MODEL_NAME)
        moshi_weights = hf_get(moshi_name, self.hf_repo)
        tokenizer = hf_get(raw_config["tokenizer_name"], self.hf_repo)
        lm_config = models.LmConfig.from_config_dict(raw_config)
        self.model = models.Lm(lm_config)
        self.model.set_dtype(getattr(mx, TTSConfig.DEFAULT_MODEL_DTYPE))
        
        self.logger.info(f"loading model weights from {moshi_weights}")
        self.model.load_pytorch_weights(str(moshi_weights), lm_config, strict=True)
        
        if self.quantize is not None:
            self.logger.info(f"quantizing model to {self.quantize} bits")
            nn.quantize(self.model.depformer, bits=self.quantize)
            for layer in self.model.transformer.layers:
                nn.quantize(layer.self_attn, bits=self.quantize)
                nn.quantize(layer.gating, bits=self.quantize)
        
        self.logger.info(f"loading the text tokenizer from {tokenizer}")
        self.text_tokenizer = sentencepiece.SentencePieceProcessor(str(tokenizer))  # type: ignore
        
        self.logger.info(f"loading the audio tokenizer {mimi_weights}")
        generated_codebooks = lm_config.generated_codebooks
        self.audio_tokenizer = models.mimi.Mimi(models.mimi_202407(generated_codebooks))
        self.audio_tokenizer.load_pytorch_weights(str(mimi_weights), strict=True)
        
        cfg_coef_conditioning = None
        self.tts_model = TTSModel(
            self.model,
            self.audio_tokenizer,
            self.text_tokenizer,
            voice_repo=self.voice_repo,
            temp=TTSConfig.DEFAULT_TEMP,
            cfg_coef=TTSConfig.DEFAULT_CFG_COEF,
            max_padding=TTSConfig.DEFAULT_MAX_PADDING,
            initial_padding=TTSConfig.DEFAULT_INITIAL_PADDING,
            final_padding=TTSConfig.DEFAULT_FINAL_PADDING,
            padding_bonus=TTSConfig.DEFAULT_PADDING_BONUS,
            raw_config=raw_config,
        )
        
        if self.tts_model.valid_cfg_conditionings:
            cfg_coef_conditioning = self.tts_model.cfg_coef
            self.tts_model.cfg_coef = TTSConfig.DEFAULT_CFG_COEF
            self.cfg_is_no_text = False
            self.cfg_is_no_prefix = False
        else:
            self.cfg_is_no_text = True
            self.cfg_is_no_prefix = True
            
        self.mimi = self.tts_model.mimi
        self.cfg_coef_conditioning = cfg_coef_conditioning
        
    def _on_frame(self, frame):
        if (frame == -1).any():
            return
        _pcm = self.tts_model.mimi.decode_step(frame[:, :, None])
        _pcm = np.array(mx.clip(_pcm[0, 0], AudioConfig.AUDIO_CLIP_MIN, AudioConfig.AUDIO_CLIP_MAX))
        self.wav_frames.put_nowait(_pcm)
        
    def generate_audio(
        self,
        text: str,
        voice: str = TTSConfig.DEFAULT_VOICE,
        on_frame_callback: Optional[Callable] = None,
    ):
        if self.tts_model is None:
            raise RuntimeError("Engine not initialized. Call initialize() first.")
            
        all_entries = [self.tts_model.prepare_script([text])]
        if self.tts_model.multi_speaker:
            voices = [self.tts_model.get_voice_path(voice)]
        else:
            voices = []
        all_attributes = [
            self.tts_model.make_condition_attributes(voices, self.cfg_coef_conditioning)
        ]
        
        self.wav_frames = queue.Queue()
        
        callback = on_frame_callback or self._on_frame
        
        self.logger.info("starting the inference loop")
        begin = time.time()
        result = self.tts_model.generate(
            all_entries,
            all_attributes,
            cfg_is_no_prefix=self.cfg_is_no_prefix,
            cfg_is_no_text=self.cfg_is_no_text,
            on_frame=callback,
        )
        frames = mx.concat(result.frames, axis=-1)
        total_duration = frames.shape[0] * frames.shape[-1] / self.mimi.frame_rate
        time_taken = time.time() - begin
        total_speed = total_duration / time_taken
        self.logger.info(f"[LM] took {time_taken:.2f}s, total speed {total_speed:.2f}x")
        
        return result
        
    def get_audio_frames(self) -> List[np.ndarray]:
        frames = []
        while True:
            try:
                frames.append(self.wav_frames.get_nowait())
            except queue.Empty:
                break
        return frames
        
    @property
    def sample_rate(self) -> int:
        if self.mimi is None:
            raise RuntimeError("Engine not initialized. Call initialize() first.")
        return self.mimi.sample_rate
        
    @property
    def frame_rate(self) -> float:
        if self.mimi is None:
            raise RuntimeError("Engine not initialized. Call initialize() first.")
        return self.mimi.frame_rate