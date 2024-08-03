import aiohttp
import asyncio
from frame_sdk import Frame
from frame_sdk.display import Alignment
from frame_sdk.camera import AutofocusType
import datetime
from openai import AsyncOpenAI
from PIL import Image
import urllib.request
import base64
import os

client = AsyncOpenAI()


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


async def take_photo(f):
    print("Taking photo")
    await f.display.show_text("Taking photo...", align=Alignment.MIDDLE_CENTER)
    photo_bytes = await f.camera.take_photo(
        # autofocus_seconds=2,
        quality=50,
        autofocus_type=AutofocusType.CENTER_WEIGHTED,
    )

    with open("photo.jpg", "wb") as fh:
        fh.write(photo_bytes)

    im = Image.open("photo.jpg")

    # convert image to png
    im.convert("RGBA").rotate(90).save("photo.png")

    # response = await client.images.edit(
    #     model="dall-e-2",
    #     image=open("photo.png", "rb"),
    #     mask=open("transparent.png", "rb"),
    #     prompt="sharpen",
    #     n=1,
    #     size="512x512",
    # )

    # edited_url = response.data[0].url
    # urllib.request.urlretrieve(edited_url, "edited_photo.png")


async def poke():
    base64_image = encode_image("photo.png")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
    }

    payload = {
        "model": "gpt-4-turbo",
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "If this person were a Pokemon, what would be the Description, Type, HP, Attack, Defense, and Speed of this Pokemon?\n"
                        'Respond with a JSON like this: {"description": "Obviously prefers hot places. When it rains, steam is said to spout from the tip of its tail.". "type": "Fire", "typeBackgroundColor": "#fd7d24", "hp": 100, "attack": 100, "defense": 100, "speed": 100}',
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
        "max_tokens": 300,
    }

    # response = await requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.openai.com/v1/chat/completions", json=payload, headers=headers
        ) as response:

            print("Status:", response.status)
            print("Content-type:", response.headers["content-type"])

            json = await response.json()
            print(json["choices"][0]["message"]["content"])


async def record_audio(f):
    SECONDS = 10

    print("Recording audio...")
    await f.display.show_text("Recording audio...", align=Alignment.MIDDLE_CENTER)

    await f.microphone.save_audio_file("audio.wav", max_length_in_seconds=SECONDS)

    print("Audio recorded")
    # await f.display.show_text("Audio recorded", align=Alignment.MIDDLE_CENTER)


async def speech_to_text(f):
    print("Transcribing audio")
    # await f.display.show_text("Transcribing audio...", align=Alignment.MIDDLE_CENTER)

    with open("audio.wav", "rb") as audio_file:
        transcription = await client.audio.transcriptions.create(
            model="whisper-1", file=audio_file
        )
        print("Transcription:")
        print(transcription.text)
        await f.display.show_text("Transcribed", align=Alignment.MIDDLE_CENTER)


async def countdown(i):
    if i <= 0:
        return

    while i > 0:
        print(f"COUNTDOWN: {i}")
        await asyncio.sleep(1)
        i = i - 1


async def main():
    await poke()
    return

    async with Frame() as f:
        print("Frame initialized")
        # f.bluetooth.print_debugging = True
        await f.display.show_text("Tap to start", align=Alignment.MIDDLE_CENTER)
        # await f.motion.wait_for_tap()

        # record audio
        # await record_audio(f)
        # await speech_to_text(f)

        # take a photo and save to disk
        await roast()

        # response = await client.images.edit(
        #     model="dall-e-2",
        #     image=open("photo.png", "rb"),
        #     prompt="photo stacked high resolution macro photograph",
        #     n=1,
        #     size="512x512",
        # )

        # edited_url = response.data[0].url
        # urllib.request.urlretrieve(edited_url, "edited_photo.jpg")

        # await f.camera.save_photo("photo.jpg", autofocus_seconds=1)

        # record
        # print(f"Recording audio with maximum of {SECONDS} seconds")
        # await f.display.show_text("Recording audio", align=Alignment.MIDDLE_CENTER)
        # # [audio_data, _] = await asyncio.gather(
        # #     *[
        # #         f.microphone.record_audio(max_length_in_seconds=SECONDS),
        # #         countdown(SECONDS),
        # #     ]
        # # )
        # audio_data = await f.microphone.record_audio(max_length_in_seconds=SECONDS)

        # await f.display.show_text(
        #     f"Playing back {len(audio_data) / f.microphone.sample_rate:01.1f} seconds of audio",
        #     align=Alignment.MIDDLE_CENTER,
        # )
        # f.microphone.play_audio(audio_data)

        # # display battery level, time, and date
        # text_to_display = (
        #     f"{await f.get_battery_level()}%\n"
        #     + datetime.datetime.now().strftime("%-I:%M %p\n%a, %B %d, %Y")
        # )
        # await f.display.show_text(text_to_display, align=Alignment.MIDDLE_CENTER)

        print("done")


asyncio.run(main())
