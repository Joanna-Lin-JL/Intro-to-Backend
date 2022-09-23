import json
from tkinter import X

from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)

# This pre-populates dictionary for testing purposes
posts = {
    0: {"id": 0,
        "upvotes": 1,
        "title": "My cat is the cutest!",
        "link": "https://i.imgur.com/jseZqNK.jpg",
        "username": "alicia98"},
    1: {
        "id": 1,
        "upvotes": 3,
        "title": "Cat loaf",
        "link": "https://i.imgur.com/TJ46wX4.jpg",
        "username": "alicia98"}
}

comments = {
    0: {
        2: {
            "id": 2,
            "upvotes": 8,
            "text": "Wow, my first Reddit gold!",
            "username": "alicia98"
        },
        3: {
            "id": 3,
            "upvotes": 5,
            "text": "Wow!",
            "username": "alicia98"
        }},
    1: {
        4: {
            "id": 4,
            "upvotes": 8,
            "text": "Wow, my first comment!",
            "username": "alicia98"
        },
        5: {
            "id": 5,
            "upvotes": 100,
            "text": "HAHA!",
            "username": "alicia98"
        }}
}


# Keep track of the next id
id_counter = 6


@ app.route("/")
def hello_world():
    return "Hello world!"


@ app.route("/posts/")
def get_all_posts():
    """
    Return all posts in server
    """
    res = {
        "posts": list(posts.values())
    }
    return json.dumps(res), 200


@ app.route("/posts/", methods=["POST"])
def create_post():
    """
    Create a post
    """
    global id_counter
    body = json.loads(request.data)
    title = body.get("title")
    link = body.get("link")
    username = body.get("username")
    # Put all data into a dictionary that contains all info of the post
    post = {
        "id": id_counter,
        "upvotes": 0,
        "title": title,
        "link": link,
        "username": username
    }
    posts[id_counter] = post
    id_counter += 1
    return json.dumps(post), 201


@app.route("/posts/<int:post_id>/")
def get_post(post_id):
    """
    Get post by id
    """
    post = posts.get(post_id)
    if post is None:
        return json.dumps({"error": "Post not found!"}), 404
    return json.dumps(post), 200


@app.route("/posts/<int:post_id>/", methods=["DELETE"])
def delete_post(post_id):
    """
    Delete post by id
    """
    post = posts.get(post_id)
    if post is None:
        return json.dumps({"error": "Post not found!"}), 404
    del posts[post_id]
    return json.dumps(post), 200


@ app.route("/posts/<int:post_id>/comments/")
def get_all_comments(post_id):
    """
    Return all comments of a specific post
    """
    post = posts.get(post_id)
    if post is None:
        return json.dumps({"error": "Post not found!"}), 404

    res = {
        "comments": list(comments[post_id].values())
    }
    return json.dumps(res), 200


@ app.route("/posts/<int:post_id>/comments/", methods=["POST"])
def create_comment(post_id):
    """
    Create a comment for a post
    """
    global id_counter
    body = json.loads(request.data)
    text = body.get("text")
    username = body.get("username")
    # Put all data into a dictionary that contains all info of the post
    comment = {
        "id": id_counter,
        "upvotes": 0,
        "text": text,
        "username": username
    }
    post = posts.get(post_id)
    if post is None:
        return json.dumps({"error": "Post not found!"}), 404
    comments[post_id][id_counter] = comment
    id_counter += 1
    return json.dumps(comment), 201


# your routes here
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
