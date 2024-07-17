import modal

image = modal.Image.debian_slim().pip_install("anthropic", "jericho")

app = modal.App(name="llm-text-adv", image=image)
vol = modal.Volume.from_name("llm-text-adv-volume", create_if_missing=True)
