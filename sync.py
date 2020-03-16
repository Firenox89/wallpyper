import sys
import os
from os.path import dirname
from os.path import join
from multiprocessing import Pool
import subprocess

from nextcloud import NextCloud
from wallpyper import get_image_size

NEXTCLOUD_URL = os.environ.get('NEXTCLOUD_URL')
NEXTCLOUD_USERNAME = os.environ.get('NEXTCLOUD_USER')
NEXTCLOUD_PASSWORD = os.environ.get('NEXTCLOUD_PASSWORD')

assert NEXTCLOUD_URL, "EnvVar NEXTCLOUD_URL not set"
assert NEXTCLOUD_USERNAME, "EnvVar NEXTCLOUD_USER not set"
assert NEXTCLOUD_PASSWORD, "EnvVar NEXTCLOUD_PASSWORd not set"

shinobooru_dir = "Shinobooru"
shinobooru_waifu2x_dir = "ShinobooruWaifu2x"
# True if you want to get response as JSON
# False if you want to get response as XML
to_js = True

nxc = NextCloud(endpoint=NEXTCLOUD_URL, user=NEXTCLOUD_USERNAME, password=NEXTCLOUD_PASSWORD, json_output=to_js)


def href_to_path(href):
    return href.replace("/remote.php/dav/files/"+NEXTCLOUD_USERNAME+"/", "")

def do_in_shinobooru_dir(func):
    if not os.path.exists(shinobooru_dir):
        os.mkdir(shinobooru_dir)

    def wrapper():
        os.chdir(shinobooru_dir)
        func()
        os.chdir("..")

    return wrapper

def fetch_posts():
    fetch_posts = nxc.list_folders(uid = NEXTCLOUD_USERNAME, path = "Shinobooru")
    if fetch_posts.is_ok:
        print("post count :" + str(len(fetch_posts.data)))
        return fetch_posts.data[1:]
    else:
        print(fetch_posts.raw)

def download_post(post):
    print("Download " + post)
    nxc.download_file(NEXTCLOUD_USERNAME, post)

def get_posts_to_download():
    posts = fetch_posts()
    post_names = [href_to_path(post["href"]) for post in posts]
        
    local_posts = os.listdir(".")
    local_postPaths = ["Shinobooru/" + local_post for local_post in local_posts]

    return list(set(post_names).difference(local_postPaths))

def upscale_posts():
    local_posts = os.listdir(shinobooru_dir)

    if not os.path.exists(shinobooru_waifu2x_dir):
        os.mkdir(shinobooru_waifu2x_dir)

    postsToUpscale = []
    upscaled_posts = os.listdir(shinobooru_waifu2x_dir)

    for local_post in local_posts:
        if local_post not in upscaled_posts:
            size = get_image_size(shinobooru_dir+"/"+local_post)
            if size[0] < 3840 and size[1] < 2160:
                postsToUpscale.append(local_post)

    total = len(postsToUpscale)
    current = 0

    for post in postsToUpscale:
        current = current + 1
        print("process (" + str(current) + "/" + str(total) + ") " + post)
        subprocess.run(["waifu2x-ncnn-vulkan", "-i", shinobooru_dir+"/"+post, "-o", shinobooru_waifu2x_dir+"/"+post, "-n", "2", "-j", "2:2:2"])

@do_in_shinobooru_dir
def download_with_pool(): 
    with Pool(4) as p:
        p.map(download_post, get_posts_to_download())

download_with_pool()

upscale_posts()


