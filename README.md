# LLM IF Wrarpper

Improved text adventure game syntax parsing and style rewrite with LLM

## Summary

Interactive fictions (IF) have been a treasure trove of unconventional and impactful storytelling, with groundbreaking work like [Galatea](https://ifdb.org/viewgame?id=urxrv27t7qtu52lb) and [Spider and Web](https://ifdb.org/viewgame?id=2xyccw3pe0uovfad). Sadly, the unforgiving command syntax makes the barrier to entry high for many players. There's been more than one time where I rushed to show my wife a text adventure game just to see her quickly loses patience because the engine cannot automatically infer the "cup" is the same as "glass", or knowing "grab X" is the same as "take X". It's long been an issue that many IF writers tried to alleviate via clever tricks, but the technology was limited. Only if we had an easy way to understand arbitrary text and deduce meaning from them...

Enter LLMs. What if we can leverage them to repair unrecognized commands, improve error messages to provide narrative continuity, or even rewrite game content themselves? I came across [lampgpt](https://github.com/UlfarErl/lampgpt), repository for an implementation of this idea. This repo is a rework built on UlfarErl's effort, using [Jericho](https://github.com/microsoft/jericho) for running the game engine.

You can run the example locally with an Anthropic API key. Alternatively, you can deploy the project using [Modal](https://modal.com/) (they offer $30 worth of hosting credit for free each month) to play it from the web, using a LLM of your choice.

## Running Locally

To run the project locally in Anthropic:

```
export ANTHROPIC_API_KEY=sk-...
python local.py
```

## Deploy and Play from Browser

You can deploy this project to Modal to try this out with a web based UI and an open source LLM of your choice. 

### Requirements ### 
* modal installed in your current Python virtual environment (`pip install modal`)
* A [Modal](http://modal.com/) account
* A Modal token set up in your environment (`modal token new`)

```
modal deploy src.app
```