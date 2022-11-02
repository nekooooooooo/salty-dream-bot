# Salty Dream Bot
An simple, unoptimized locally run Stable Diffusion discord bot

<img src="https://raw.githubusercontent.com/nekooooooooo/nekooooooooo.github.io/master/pics/preview_dream_bot.png">

This was mostly made for my friend's private server.
I won't be maintaining this repo that much (like most of my repos) but I'll try my best to finish everything on the [to do](#to-do) list

## Setup

- Set up [AUTOMATIC1111's Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui)
- Run the Web UI with the api command line argument inside (`COMMANDLINE_ARGS=--api`)
- Clone this repository
- Create a text file inside the repo ".env"

```dotenv
# .env
TOKEN = bot token here
```

## Features

- Basic txt2img
- Negative Prompts
- Image orientation/aspect ratio (square, landscape, portrait)
- Image size presets (small, normal, large)
- Seed

## Optional .env variables:

```dotenv
URL = set URL

# will move default prompts to configurable per-server config when it's implemented

DEFAULTPROMPT = default prompt for generations (not that useful added it in for more customizability)
NEGATIVEPROMPT = default negative prompt for generations
```

## To Do

-   [ ] Refactor code
-   -   [ ] Subclasses
-   -   [ ] Cogs
-   [ ] Remove test code comments
-   [ ] Add comments for better code readability (mostly for myself)
-   [ ] Optimize code
-   [ ] Queues
-   [ ] Per-server config
-   [ ] Save prompts into styles
-   [ ] Extras
-   -   [ ] Upscaling
-   [ ] Model/checkpoint swapping
-   [ ] Hypernetwork swapping
-   -   [ ] Hypernetwork strenght
-   [ ] img2img
-   [ ] PNG info
-   [ ] Display progress
-   [ ] Interrupt
-   [ ] Interrogate/DeepDanbooru
-   [ ] Locally save images
-   [ ] Optional custom width/height
-   [ ] Stats command
-   [ ] AIO setup/run
-   [ ] Error handling