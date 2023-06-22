import asyncio
import logging
import openai
import requests
import settings
from midjourney_api import TNL

logging.basicConfig(level=4, filename='logs.txt')
# configure apis
tnl = TNL(settings.TNL_API_KEY)
openai.api_key = settings.OPENAI_API_KEY


def call_midjourney(scene):
    res = tnl.imagine(prompt=scene)
    print(str(res))


async def acall_api(system_prompt, content_prompt, n=1, temp=0.5, model='gpt-3.5-turbo-16k'):
    res = openai.ChatCompletion.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": content_prompt
            }
        ],
        n=n,
        temperature=temp
    )
    return res


def call_api(system_prompt, content_prompt, n=1, temp=0.5, model='gpt-3.5-turbo-16k'):
    res = openai.ChatCompletion.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": content_prompt
            }
        ],
        n=n,
        temperature=temp
    )
    return res


# story generation function to call gpt4 and create story from params
def generate_story(system_prompt: str, content_prompt: str) -> str:
    api_call_response = call_api(system_prompt, content_prompt)
    story = api_call_response["choices"][0]["message"]["content"]
    return story


# story gen output broken into chapters, chapters broken into visual scenes.
def create_scenes(story: str) -> list:
    chapters = []
    split_story: list = story.split("\n")
    for c in split_story:
        if c.find('Chapter') == -1:
            chapters.append(c)
    return list(filter(None, chapters))


# asynchronous function calls for scene description
async def get_scene_description(scene: str, system_prompt: str, content_prompt: str, setting: str, suffix: str):
    response = await acall_api(system_prompt, content_prompt)
    description = response["choices"][0]["message"]["content"]
    description = description + setting + suffix
    return description


# loops through scenes, creates a set of prompts custom to the scene, and asynchronously calls for descriptions of all scenes
async def describe_scenes(scenes: list, setting: str) -> list:
    system_prompt = """You are a world famous illustrator of children's books and illustrated novels.
     You have mastered the art of describing the elements of a story as visually captivating scenery."""
    # this should allow for a semi consistent style to be called across images
    image_gen_prompt_suffix = " whimsical brightly lit stylized animation fantasy cartoon kids books ultra high detail"
    tasks = []
    for scene in scenes:
        content_prompt = f"""Using the provided scene of a short story, and a list of the characters in the story, describe the visual aspects of the scene in a few sentences.
        
        Your description must be short and concise, yet retain the key details of the scene. 
        
        Your description should follow the pattern of the following examples:
        EXAMPLE: Characters: ['Lily - a young girl with curly red hair' , 'Oliver - a boy with brown hair'] Scene: 'As Lily and Oliver faced each challenge together, their bond grew stronger. They learned to trust their instincts, listen to their hearts, and believe in themselves. Along the way, they discovered the true power of friendship and the magic it holds.' Answer: 'a girl with curly red hair and a boy with brown hair stand side by side, their faces filled with determination and trust. Their hands are clasped tightly together, symbolizing their unbreakable bond. Surrounding them, vibrant colors swirl in the air, representing the magic of friendship and the strength it brings.'
        EXAMPLE: Characters: ['Daisy - a grumpy cow', 'Charlie - a friendly dog'], Scene: "They came across a babbling brook, and Charlie leaped across with ease. Daisy hesitated, unsure of her ability to jump. But with Charlie's encouragement, she took a leap of faith and cleared the brook, landing on the other side with a thud." Answer: "a grumpy cow leaps over a brook, while a friendly dog encourages"
        You should describe it in a way that an artist could easily recreate the scene from your description. For context, when you are describing a part of the story, refer to the entire story {scenes}. Ensure you describe the characters as they would appear, rather than referring to them by name. The following is the scene you are to describe: {scene}"""
        tasks.append(get_scene_description(scene, system_prompt, content_prompt, setting, image_gen_prompt_suffix))
    descriptions = await asyncio.gather(*tasks)
    return list(descriptions)


# send visual scene descriptions to midjourney to generate images
def create_illustrations(scene_descriptions: list) -> list:
    images = []
    for scene in scene_descriptions:
        images.append("image goes here")

    #       images.append(call_midjourney(scene))
    return images


# todo take the images and match them to each scene, use them as parameters to do a function call
# to generate the page component using gpt-4 function calls
# https://platform.openai.com/docs/guides/gpt/function-calling
def create_page_component(scene: str, illustration):
    page_comp = {"scene": scene, "image": illustration}
    return page_comp


def send_pages_to_client(pages):
    # todo api post call to client
    pass


async def main():
    print("Welcome to FableSTREAM!")
    # story generation params
    characters = []
    setting = ""
    rating = ""
    storybook_book_gen_system_prompt = """You are a masterful storyteller, skilled in the art of visual storytelling. 
        Your stories are always captivating and whimsical, and emotionally engaging."""

    storybook_book_gen_content_prompt = f"""You are tasked with creating an original short story about the following characters and setting. 
        RATING {rating},
        CHARACTERS: {characters},
        SETTING: {setting},
        If no character, setting, or plot is provided, you should make up a story involving original characters, 
        an original setting from any time period, and the plot should revolve around overcoming 
        common trials and issues encountered by young people coming of age. all content should be written 
        in a way such that the content would be rated according to the age appropriateness rating that was provided.
        If no rating is provided, stories should be written in a way that would be considered 'rated PG: appropriate for all ages'.

        Tell the story in a series of small chapters, comprised of visually compelling scenes.
        
        Your answer MUST contain ONLY THE STORY, with no separate descriptions of story elements or comments. """

    story = generate_story(storybook_book_gen_system_prompt, storybook_book_gen_content_prompt)
    scenes = create_scenes(story)
    scene_descriptions = await describe_scenes(scenes, setting)
    for s in scene_descriptions:
        print(str(s))

    # # todo once scene component function works, this can be used.
    # illustrations = create_illustrations(scene_descriptions)
    # pages = []
    # for i in range(len(scenes)):
    #     cur_scene = scenes[i]
    #     cur_img = illustrations[i]
    #     pages.append((cur_scene, cur_img))
    # send_pages_to_client(pages)
    #


if __name__ == '__main__':
    asyncio.run(main())
