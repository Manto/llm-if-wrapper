import modal

app = modal.App(name="llm-if-wrapper")
vol = modal.Volume.from_name("llm-if-wrapper-volume", create_if_missing=True)
