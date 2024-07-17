import os
import time
from pathlib import Path
import modal
from common import app

MODEL_NAME = "NousResearch/Meta-Llama-3-8B-Instruct"
MODEL_DIR = "/root/model/model_input"
GPU_CONFIG = modal.gpu.L4()  # See https://modal.com/docs/guide/gpu


def download_model_to_image(model_dir, model_name):

    from huggingface_hub import snapshot_download
    from transformers.utils import move_cache

    os.makedirs(model_dir, exist_ok=True)

    snapshot_download(
        model_name,
        local_dir=model_dir,
        ignore_patterns=["*.pt", "*.bin"],  # Using safetensors
    )
    move_cache()


llm_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "vllm==0.5.1",
        "torch==2.3.0",
        "transformers==4.42.3",
        "ray==2.31.0",
        "hf-transfer==0.1.6",
        "huggingface_hub==0.23.2",
    )
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
    .run_function(
        download_model_to_image,
        timeout=60 * 60 * 2,
        kwargs={
            "model_dir": MODEL_DIR,
            "model_name": MODEL_NAME,
        },
    )
)

with llm_image.imports():
    from threading import Thread
    from transformers import (
        AutoTokenizer,
    )


@app.cls(image=llm_image, gpu="L4", container_idle_timeout=300)
class LLM:
    @modal.enter()
    def start_engine(self):
        from vllm.engine.arg_utils import AsyncEngineArgs
        from vllm.engine.async_llm_engine import AsyncLLMEngine

        print("🥶 cold starting inference")
        start = time.monotonic_ns()

        engine_args = AsyncEngineArgs(
            model=MODEL_DIR,
            tensor_parallel_size=GPU_CONFIG.count,
            gpu_memory_utilization=0.90,
            enforce_eager=False,  # capture the graph for faster inference, but slower cold starts
            disable_log_stats=True,  # disable logging so we can stream tokens
            disable_log_requests=True,
        )

        # this can take some time!
        self.engine = AsyncLLMEngine.from_engine_args(engine_args)
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        duration_s = (time.monotonic_ns() - start) / 1e9
        print(f"🏎️ engine started in {duration_s:.0f}s")

    @modal.method()
    async def warm_up(self):
        llm.generate.spawn("")

    @modal.method()
    async def completion_stream(
        self, messages, temp=0.75, max_tokens=2048, rep_penalty=1.1
    ):
        from vllm import SamplingParams
        from vllm.utils import random_uuid

        sampling_params = SamplingParams(
            temperature=temp,
            max_tokens=max_tokens,
            repetition_penalty=rep_penalty,
        )

        templated_chat = self.tokenizer.apply_chat_template(
            messages, add_generation_prompt=True, tokenize=False
        )

        request_id = random_uuid()
        result_generator = self.engine.generate(
            templated_chat,
            sampling_params,
            request_id,
        )
        index, num_tokens = 0, 0
        start = time.monotonic_ns()
        async for output in result_generator:
            if output.outputs[0].text and "\ufffd" == output.outputs[0].text[-1]:
                continue
            text_delta = output.outputs[0].text[index:]
            index = len(output.outputs[0].text)
            num_tokens = len(output.outputs[0].token_ids)

            yield text_delta
        duration_s = (time.monotonic_ns() - start) / 1e9

        # See the performance logged in Modal application dashboard
        print(
            f"\n################################################################"
            f"\nGenerated {num_tokens} tokens from {MODEL_NAME} in {duration_s:.1f}s,"
            f" throughput = {num_tokens / duration_s:.0f} tokens/second on {GPU_CONFIG}.\n"
        )

    @modal.exit()
    def stop_engine(self):
        if GPU_CONFIG.count > 1:
            import ray

            ray.shutdown()


# For local testing, run `modal run -q llm_serve --input "Where is zork?"`
@app.local_entrypoint()
def main(input: str):
    model = LLM()

    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant.",
        },
        {"role": "user", "content": f"{input}"},
    ]

    for val in model.completion_stream.remote_gen(messages):
        print(val, end="", flush=True)
