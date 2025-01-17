# LLM IF Wrarpper

Improved text adventure game syntax parsing and style rewrite with LLM

![LLM-IF-Wrapper in Browser](/screenshot.png "Screenshot")

## Summary

Interactive fictions (IF) have been a treasure trove of unconventional and impactful storytelling, with groundbreaking work like [Galatea](https://ifdb.org/viewgame?id=urxrv27t7qtu52lb) and [Spider and Web](https://ifdb.org/viewgame?id=2xyccw3pe0uovfad). Sadly, the unforgiving command syntax makes the barrier to entry high for many players. There's been more than one time where I rushed to show my wife a text adventure game just to see her quickly loses patience because the engine cannot automatically infer the "cup" is the same as "glass", or knowing "grab X" is the same as "take X". It's long been an issue that many IF writers tried to alleviate via clever tricks, but the technology was limited. Only if we had an easy way to understand arbitrary text and deduce meaning from them...

Enter LLMs. What if we can leverage them to repair unrecognized commands, improve error messages to provide narrative continuity, or even rewrite game content themselves? I came across UlfarErl's [lampgpt](https://github.com/UlfarErl/lampgpt), an implementation of this idea. This repo is a rework of lampgpt, replacing `bocfel` with [Jericho](https://github.com/microsoft/jericho) to run the game engine, in addition to other prompt and flow improvements.

You can run the example locally with an Anthropic API key. Alternatively, you can deploy the project using [Modal](https://modal.com/) (they offer $30 worth of hosting credit for free each month) to play it from the web, using a LLM of your choice.

## Setting up your Anthropic/OpenAI API Key

To use Anthropic or OpenAI models for the project, you need to specify your keys. To do so, create a `.env` file in the project directory, and then enter your API keys:

```
ANTHROPIC_API_KEY=sk-...
OPENAI_API_KEY=sk-proj...
```

### Changing the Anthropic/OpenAI Model

By default, the project uses Claude 3.5 Sonnet on Anthropic, and gpt-4o-mini on OpenAI.

You can change the model to use by modifying `ANTHROPIC_MODEL` and `OPENAI_MODEL` in `utils.py`.

## Running Locally

To run the game `9:05` locally with Anthropic (defaults to Claude 3.5 Sonnet):

```
python local.py games/905.z5 --llm anthropic
```

If you want to use an OpenAI model (defaults to gpt-4o-mini):

```
python local.py games/905.z5 --llm openai
```

You can also supply a tone to perform an optional rewrite on the game text. You can choose one of these following tones: `pratchett`, `gumshoe`, `legal`, `spaceopera`, `original`. For example:

```
python local.py games/905.z5 --llm anthropic --tone gumshoe
```

Leaving out tone will disable rewrite of game text and only perform rewrite on player's command when getting parser errors.

## Running Locally from Browser

To run the game in browser, you need to setup Modal - an easy way to manage serverless deployment with optional GPU support.

### Configuring Modal

- Get a [Modal](http://modal.com/) account
- Install `modal` in your current Python virtual environment (`pip install modal`)
- Get a Modal token set up in your environment (`modal token new`)

Once you have the account setup, create the file `frontend/.env.local` with your modal username like the following:

```
NEXT_PUBLIC_MODAL_USERNAME=<your_account>
```

### Start Local Client and Server

The server contains the logic to interface with the IF interpreter and making calls to LLM to perform the parsing check and rewrites. It also can serve an open source model (`Meta-Llama-3-8B-Instruct` by default) as an option instead of using Anthropic or OpenAI API. To start the server, run the following:

```
modal serve web
```

The client uses `next.js`, and to start it, run the following:

```
cd frontend
npm install # if you have not installed the packages
npm run dev
```

When both the client and server are ready, navigate to `http://localhost:3000` in your browser to run the project.

### Deploying Modal

To deploy the project so you can access it from anywhere, do a build on the frontend project and then deploy everything via modal with the following command:

```
cd frontend
npm run build
cd ..
modal deploy web
```

The output will look something like the following:

```
...
├── 🔨 Created function download_model_to_image.
├── 🔨 Created function LLM.*.
├── 🔨 Created function LLM.warm_up.
├── 🔨 Created function LLM.completion_stream.
└── 🔨 Created web function web => https://xyz--llm-text-adv-web.modal.run
```

Then navigate to `https://xyz--llm-text-adv-web.modal.run` in your browser to access the project.

### Changing the Hosted Model

Open up `llm_serve.py`, and you can change the `MODEL_NAME` to point to another model available on HuggingFace that is supported by vLLM. Be sure to `modal deploy web` again after making the change, and Modal will rebuild the image and deploy accordingly.

## TODO

- [x] Visually distinguish game response from player commands
- [x] Hook up debug log viewing from the web
- [x] Add support for OpenAI models
- [x] Moved detection of parser error to LLM, instead of simplistic string matching.

## Known Issues

- The rewrite sometimes make up unrelated content or completely lose the structure of original game text, especially when using less capable models.
- Certain console based display (e.g., the help menu in Lost Pig) will not display correctly.

## Other Ideas

- Instead of string match to detect parser error, fine-tune an LLM for this.
- Could fork [Parchment](https://github.com/curiousdannii/parchment) for a fully browser based experience, skipping the need for a backend.
- Generate images via Stable Diffusion along with room descriptions.
