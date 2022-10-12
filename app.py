from flask import Flask, send_file, request
from flask_cors import CORS, cross_origin
import os
import pymongo
import uuid
import shutil

MONGO_CLIENT = "mongodb+srv://user:user@cluster0.ajoof.mongodb.net"

def addRenderToDb(user, title, url):
    # connecting to the cinematic database
    client = pymongo.MongoClient(MONGO_CLIENT)
    # accessing collection renders
    db = client["cinematic"]
    renderTable = db["renders"]
    # print(db)
    # select all
    rendersUser = renderTable.find_one({"user": user})
    #renderList = rendersUser["renders"].append({"title": title, "url": url})
    renderTable.update_one(
        {"user": user},
        {
            "$push":{
                "renders": {"title": title, "url": url}
            }
        }
    )

app = Flask(__name__)
cors = CORS(app)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
BLENDER_PATH = "C:/Program Files/Blender Foundation/Blender 3.2/blender.exe"

@app.route('/')
def index():
    return 'Server Works!'

@app.route('/greet/<name>')
def say_hello(name):
    return f"Hello to {name}"

@app.route('/get-scene/<text>')
@cross_origin()
def get_scene(text):
    # appel script génération fichier gltf de la scène
    #test avec subprocess
    os.system(f"blender --background --python sceneGenerator/exportSceneGltf.py {text}")
    return send_file(os.path.join(os.getcwd(), "scene.gltf"))

@app.route('/render', methods=['GET'])
def render():
    text = request.args.get('text')
    mat = request.args.get('mat')
    font = request.args.get('font')

    renderFilename = str(uuid.uuid4()) + ".png"

    SNAPSHOT_FILE = "test.png"
    HTTP_SERVER_LOCALHOST_PATH = os.path.join("http://localhost:8000/files/", renderFilename)

    os.system(f'"{BLENDER_PATH}" --background --python sceneGenerator/render.py {text} {mat} {font}')

    # copy file to HTTP SERVER for distribution
    RENDER_PATH = f"C:/Users/seeds/PycharmProjects/simpleApi/{SNAPSHOT_FILE}"
    HTTP_SERVER_FILES_PATH = f"C:/SHARE_CONTENT_RENDERS/files"
    HTTP_SERVER_RENDER_FILE_PATH = os.path.join(HTTP_SERVER_FILES_PATH, renderFilename)
    shutil.copy(RENDER_PATH, HTTP_SERVER_RENDER_FILE_PATH)

    # send image to database
    addRenderToDb("ElPollo", "My super render", HTTP_SERVER_LOCALHOST_PATH)
    print("Render sent to database successfully !")
    return f"Rendu terminé"
