import * as webllm from "@mlc-ai/web-llm";

const MODEL_NAME = "Llama-3.1-8B-Instruct-q4f16_1-MLC";

export class WebLLMClient {
  private engine: webllm.MLCEngine | null = null;
  private initPromise: Promise<void> | null = null;
  private isInitialized: boolean = false;

  async initialize(
    onProgress?: (report: webllm.InitProgressReport) => void
  ): Promise<void> {
    if (this.isInitialized) {
      return;
    }

    if (this.initPromise) {
      return this.initPromise;
    }

    this.initPromise = (async () => {
      try {
        this.engine = await webllm.CreateMLCEngine(MODEL_NAME, {
          initProgressCallback: onProgress,
        });
        this.isInitialized = true;
      } catch (error) {
        this.initPromise = null;
        throw error;
      }
    })();

    return this.initPromise;
  }

  async chat(systemPrompt: string, userPrompt: string): Promise<string> {
    if (!this.engine) {
      throw new Error("WebLLM engine not initialized");
    }

    const messages: webllm.ChatCompletionMessageParam[] = [
      { role: "system", content: systemPrompt },
      { role: "user", content: userPrompt },
    ];

    console.log("=== WebLLM Request ===");
    console.log("System Prompt:", systemPrompt);
    console.log("User Prompt:", userPrompt);

    const reply = await this.engine.chat.completions.create({
      messages,
    });

    const response = reply.choices[0].message.content || "";
    console.log("=== WebLLM Response ===");
    console.log(response);
    console.log("======================");

    return response;
  }

  isReady(): boolean {
    return this.isInitialized;
  }
}

// Singleton instance
let webLLMClient: WebLLMClient | null = null;

export function getWebLLMClient(): WebLLMClient {
  if (!webLLMClient) {
    webLLMClient = new WebLLMClient();
  }
  return webLLMClient;
}
