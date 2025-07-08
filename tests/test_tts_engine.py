import queue
from unittest.mock import Mock, patch, MagicMock
import pytest
import numpy as np
import sys
from pathlib import Path

# Mock the external dependencies before importing
sys.modules['mlx'] = MagicMock()
sys.modules['mlx.core'] = MagicMock()
sys.modules['mlx.nn'] = MagicMock()
sys.modules['sentencepiece'] = MagicMock()
sys.modules['moshi_mlx'] = MagicMock()
sys.modules['moshi_mlx.models'] = MagicMock()
sys.modules['moshi_mlx.models.tts'] = MagicMock()
sys.modules['moshi_mlx.utils'] = MagicMock()
sys.modules['moshi_mlx.utils.loaders'] = MagicMock()
sys.modules['moshi_mlx.client_utils'] = MagicMock()

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.tts_engine import TTSEngine


class TestTTSEngine:
    def test_init(self):
        engine = TTSEngine()
        assert engine.hf_repo is not None
        assert engine.voice_repo is not None
        assert engine.quantize is None
        assert engine.model is None
        assert engine.audio_tokenizer is None
        assert engine.text_tokenizer is None
        assert engine.tts_model is None
        assert engine.mimi is None
        assert isinstance(engine.wav_frames, queue.Queue)

    def test_init_with_params(self):
        engine = TTSEngine(
            hf_repo="custom/repo",
            voice_repo="custom/voice",
            quantize=4
        )
        assert engine.hf_repo == "custom/repo"
        assert engine.voice_repo == "custom/voice"
        assert engine.quantize == 4

    def test_log(self, capsys):
        with patch('moshi_mlx.client_utils.make_log') as mock_make_log:
            mock_make_log.return_value = "[INFO] test message"
            engine = TTSEngine()
            engine.log("info", "test message")
            captured = capsys.readouterr()
            assert "[INFO] test message" in captured.out
            mock_make_log.assert_called_once_with("info", "test message")

    @patch('src.tts_engine.hf_get')
    @patch('src.tts_engine.models')
    @patch('src.tts_engine.sentencepiece')
    @patch('src.tts_engine.TTSModel')
    @patch('src.tts_engine.mx')
    @patch('builtins.open')
    @patch('src.tts_engine.json.load')
    def test_initialize(self, mock_json_load, mock_open, mock_mx, mock_tts_model, 
                       mock_sp, mock_models, mock_hf_get):
        mock_config = {
            "mimi_name": "mimi.bin",
            "moshi_name": "model.safetensors",
            "tokenizer_name": "tokenizer.model"
        }
        mock_json_load.return_value = mock_config
        mock_hf_get.side_effect = ["config.json", "config.json", "mimi.bin", "model.safetensors", "tokenizer.model"]
        
        mock_lm_config = Mock()
        mock_lm_config.generated_codebooks = 8
        mock_models.LmConfig.from_config_dict.return_value = mock_lm_config
        
        mock_lm = Mock()
        mock_models.Lm.return_value = mock_lm
        
        mock_mimi_model = Mock()
        mock_models.mimi.Mimi.return_value = mock_mimi_model
        
        mock_tokenizer = Mock()
        mock_sp.SentencePieceProcessor.return_value = mock_tokenizer
        
        mock_tts = Mock()
        mock_tts.valid_cfg_conditionings = False
        mock_tts.mimi = Mock(sample_rate=24000, frame_rate=12.5)
        mock_tts_model.return_value = mock_tts
        
        engine = TTSEngine()
        engine.initialize()
        
        assert engine.model is not None
        assert engine.audio_tokenizer is not None
        assert engine.text_tokenizer is not None
        assert engine.tts_model is not None
        assert engine.mimi is not None
        assert engine.cfg_is_no_text == True
        assert engine.cfg_is_no_prefix == True

    @patch('src.tts_engine.hf_get')
    @patch('src.tts_engine.models')
    @patch('src.tts_engine.sentencepiece')
    @patch('src.tts_engine.TTSModel')
    @patch('src.tts_engine.mx')
    @patch('src.tts_engine.nn')
    @patch('builtins.open')
    @patch('src.tts_engine.json.load')
    def test_initialize_with_quantization(self, mock_json_load, mock_open, mock_nn, mock_mx, 
                                         mock_tts_model, mock_sp, mock_models, mock_hf_get):
        mock_config = {
            "mimi_name": "mimi.bin",
            "moshi_name": "model.safetensors",
            "tokenizer_name": "tokenizer.model"
        }
        mock_json_load.return_value = mock_config
        mock_hf_get.side_effect = ["config.json", "config.json", "mimi.bin", "model.safetensors", "tokenizer.model"]
        
        mock_lm_config = Mock()
        mock_lm_config.generated_codebooks = 8
        mock_models.LmConfig.from_config_dict.return_value = mock_lm_config
        
        mock_lm = Mock()
        mock_lm.depformer = Mock()
        mock_lm.transformer = Mock()
        mock_lm.transformer.layers = [Mock(self_attn=Mock(), gating=Mock()) for _ in range(2)]
        mock_models.Lm.return_value = mock_lm
        
        mock_mimi_model = Mock()
        mock_models.mimi.Mimi.return_value = mock_mimi_model
        
        mock_tokenizer = Mock()
        mock_sp.SentencePieceProcessor.return_value = mock_tokenizer
        
        mock_tts = Mock()
        mock_tts.valid_cfg_conditionings = False
        mock_tts.mimi = Mock(sample_rate=24000, frame_rate=12.5)
        mock_tts_model.return_value = mock_tts
        
        engine = TTSEngine(quantize=4)
        engine.initialize()
        
        mock_nn.quantize.assert_called()
        assert mock_nn.quantize.call_count >= 3

    def test_on_frame(self):
        engine = TTSEngine()
        engine.tts_model = Mock()
        engine.tts_model.mimi = Mock()
        
        mock_pcm = np.random.randn(1, 1, 1920)
        engine.tts_model.mimi.decode_step.return_value = mock_pcm
        
        frame = np.random.randn(8, 1)
        engine._on_frame(frame)
        
        assert engine.wav_frames.qsize() == 1
        result = engine.wav_frames.get_nowait()
        assert isinstance(result, np.ndarray)

    def test_on_frame_with_negative_values(self):
        engine = TTSEngine()
        frame = np.array([[-1, -1, -1]])
        engine._on_frame(frame)
        assert engine.wav_frames.qsize() == 0

    def test_generate_audio_not_initialized(self):
        engine = TTSEngine()
        with pytest.raises(RuntimeError, match="Engine not initialized"):
            engine.generate_audio("Test text")

    def test_generate_audio(self):
        engine = TTSEngine()
        engine.tts_model = Mock()
        engine.tts_model.multi_speaker = True
        engine.tts_model.prepare_script.return_value = Mock()
        engine.tts_model.get_voice_path.return_value = "voice/path"
        engine.tts_model.make_condition_attributes.return_value = Mock()
        
        mock_result = Mock()
        mock_result.frames = [np.random.randn(8, 1, 480) for _ in range(10)]
        engine.tts_model.generate.return_value = mock_result
        
        engine.mimi = Mock(frame_rate=12.5)
        engine.cfg_coef_conditioning = None
        engine.cfg_is_no_prefix = False
        engine.cfg_is_no_text = False
        
        with patch('src.tts_engine.mx.concat') as mock_concat:
            mock_concat.return_value = Mock(shape=(8, 4800))
            result = engine.generate_audio("Test text", voice="test_voice")
        
        assert result == mock_result
        engine.tts_model.prepare_script.assert_called_once()
        engine.tts_model.get_voice_path.assert_called_once_with("test_voice")
        engine.tts_model.generate.assert_called_once()

    def test_generate_audio_with_custom_callback(self):
        engine = TTSEngine()
        engine.tts_model = Mock()
        engine.tts_model.multi_speaker = False
        engine.tts_model.prepare_script.return_value = Mock()
        engine.tts_model.make_condition_attributes.return_value = Mock()
        
        mock_result = Mock()
        mock_result.frames = [np.random.randn(8, 1, 480) for _ in range(10)]
        engine.tts_model.generate.return_value = mock_result
        
        engine.mimi = Mock(frame_rate=12.5)
        engine.cfg_coef_conditioning = None
        engine.cfg_is_no_prefix = True
        engine.cfg_is_no_text = True
        
        custom_callback = Mock()
        
        with patch('src.tts_engine.mx.concat') as mock_concat:
            mock_concat.return_value = Mock(shape=(8, 4800))
            result = engine.generate_audio("Test text", on_frame_callback=custom_callback)
        
        generate_call = engine.tts_model.generate.call_args
        assert generate_call.kwargs['on_frame'] == custom_callback

    def test_get_audio_frames_empty(self):
        engine = TTSEngine()
        frames = engine.get_audio_frames()
        assert frames == []

    def test_get_audio_frames_with_data(self):
        engine = TTSEngine()
        test_frames = [np.random.randn(1920) for _ in range(5)]
        for frame in test_frames:
            engine.wav_frames.put(frame)
        
        result = engine.get_audio_frames()
        assert len(result) == 5
        for i, frame in enumerate(result):
            np.testing.assert_array_equal(frame, test_frames[i])

    def test_sample_rate_not_initialized(self):
        engine = TTSEngine()
        with pytest.raises(RuntimeError, match="Engine not initialized"):
            _ = engine.sample_rate

    def test_sample_rate(self):
        engine = TTSEngine()
        engine.mimi = Mock(sample_rate=24000)
        assert engine.sample_rate == 24000

    def test_frame_rate_not_initialized(self):
        engine = TTSEngine()
        with pytest.raises(RuntimeError, match="Engine not initialized"):
            _ = engine.frame_rate

    def test_frame_rate(self):
        engine = TTSEngine()
        engine.mimi = Mock(frame_rate=12.5)
        assert engine.frame_rate == 12.5

    @patch('src.tts_engine.hf_get')
    @patch('src.tts_engine.models')
    @patch('src.tts_engine.sentencepiece')
    @patch('src.tts_engine.TTSModel')
    @patch('src.tts_engine.mx')
    @patch('builtins.open')
    @patch('src.tts_engine.json.load')
    def test_initialize_with_valid_cfg_conditionings(self, mock_json_load, mock_open, mock_mx, 
                                                    mock_tts_model, mock_sp, mock_models, mock_hf_get):
        """Test initialization when tts_model has valid_cfg_conditionings=True (covers lines 91-94)."""
        mock_config = {
            "mimi_name": "mimi.bin",
            "moshi_name": "model.safetensors",
            "tokenizer_name": "tokenizer.model"
        }
        mock_json_load.return_value = mock_config
        mock_hf_get.side_effect = ["config.json", "config.json", "mimi.bin", "model.safetensors", "tokenizer.model"]
        
        mock_lm_config = Mock()
        mock_lm_config.generated_codebooks = 8
        mock_models.LmConfig.from_config_dict.return_value = mock_lm_config
        
        mock_lm = Mock()
        mock_models.Lm.return_value = mock_lm
        
        mock_mimi_model = Mock()
        mock_models.mimi.Mimi.return_value = mock_mimi_model
        
        mock_tokenizer = Mock()
        mock_sp.SentencePieceProcessor.return_value = mock_tokenizer
        
        mock_tts = Mock()
        mock_tts.valid_cfg_conditionings = True  # This triggers the code path we want to test
        mock_tts.cfg_coef = 2.5  # Some test value
        mock_tts.mimi = Mock(sample_rate=24000, frame_rate=12.5)
        mock_tts_model.return_value = mock_tts
        
        engine = TTSEngine()
        engine.initialize()
        
        # Verify the cfg_coef was stored and reset
        assert engine.cfg_coef_conditioning == 2.5
        assert mock_tts.cfg_coef == 1.0
        assert engine.cfg_is_no_text == False
        assert engine.cfg_is_no_prefix == False