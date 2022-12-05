import speech_recognition as sr
import pyttsx3
import cv2
import time
import csv
import nltk
import ctypes
from moviepy.audio.fx.audio_fadein import audio_fadein
from moviepy.audio.fx.audio_fadeout import audio_fadeout
from moviepy.audio.fx.audio_left_right import audio_left_right
from moviepy.audio.fx.audio_loop import audio_loop
from moviepy.audio.fx.audio_normalize import audio_normalize
from moviepy.audio.fx.volumex import volumex
from moviepy.editor import VideoFileClip
from moviepy.editor import concatenate_videoclips
from moviepy.video.fx.accel_decel import accel_decel
from moviepy.video.fx.blackwhite import blackwhite
from moviepy.video.fx.blink import blink
from moviepy.video.fx.colorx import colorx
from moviepy.video.fx.crop import crop
from moviepy.video.fx.even_size import even_size
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.fadeout import fadeout
from moviepy.video.fx.freeze import freeze
from moviepy.video.fx.freeze_region import freeze_region
from moviepy.video.fx.gamma_corr import gamma_corr
from moviepy.video.fx.headblur import headblur
from moviepy.video.fx.invert_colors import invert_colors
from moviepy.video.fx.loop import loop
from moviepy.video.fx.lum_contrast import lum_contrast
from moviepy.video.fx.make_loopable import make_loopable
from moviepy.video.fx.margin import margin
from moviepy.video.fx.mask_and import mask_and
from moviepy.video.fx.mask_color import mask_color
from moviepy.video.fx.mask_or import mask_or
from moviepy.video.fx.mirror_x import mirror_x
from moviepy.video.fx.mirror_y import mirror_y
from moviepy.video.fx.painting import painting
from moviepy.video.fx.resize import resize
from moviepy.video.fx.rotate import rotate
from moviepy.video.fx.scroll import scroll
from moviepy.video.fx.speedx import speedx
from moviepy.video.fx.supersample import supersample
from moviepy.video.fx.time_mirror import time_mirror
from moviepy.video.fx.time_symmetrize import time_symmetrize
from pathlib import Path
from tkinter import *
from collections import defaultdict
# Natural Language Toolkits
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# nltk.download('punkt')
# nltk.download('wordnet')
# nltk.download('averaged_perceptron_tagger')
voice = sr.Recognizer()

lem = WordNetLemmatizer()
# Identify verb
def verb_identification(verb_tag):
    if verb_tag.startswith('V') or verb_tag.startswith('JJ'):
        return 'v'
    return None

def language_processing(sentence):
    ### Tokenizing
    txt = word_tokenize(sentence)
    txt_tag = nltk.pos_tag(txt)

    ### Lemmatizing
    processed = []

    for i in txt_tag:
        word_verb = verb_identification(i[1])
        if word_verb is not None:
            # Process verb to present tense
            processed.append(lem.lemmatize(i[0], word_verb))
        else:
            # Process noun and adjective to simple form
            processed.append(lem.lemmatize(i[0]))

    # Eliminate "be"
    if 'not' in processed:
        processed = ['do' if word == 'be' else word for word in processed]
        if 'do' in processed:
            processed.remove('do')
    elif 'be' in processed:
        processed.remove('be')
    
    return processed

def SpeakText(command):
    engine = pyttsx3.init()
    engine.say(command)
    engine.runAndWait()


def runRecognition():
    print("Please say something: ")
    with sr.Microphone() as source2:
        voice.adjust_for_ambient_noise(source2, duration=0.2)
        audio2 = voice.listen(source2)

        try:
            myText = voice.recognize_google(audio2)
            myText = myText.lower()

            processed_words = language_processing(myText)
            print(processed_words)
            found = defaultdict(list)
            clips = []
            for word in processed_words:
                found[word] = []
            map_file = csv.reader(open("simple_mapping.csv", "r", encoding='utf-8'))
            for row in map_file:
                for word in processed_words:
                    if word == row[0]:
                        found[word].append(row[1])
                        found[word].append(row[2])
            not_found = []
            print(found)
            for sign in found:
                if len(found[sign]) > 0:
                    path = str(Path.cwd()) + "/minimum_output/" + found[sign][0] + ".mp4.avi"
                    path2 = str(Path.cwd()) + "/minimum_output/" + found[sign][1] + ".mp4.avi"
                    check_path = cv2.VideoCapture(path)
                    check_path2 = cv2.VideoCapture(path2)
                    if check_path.isOpened():
                        video = VideoFileClip(path)
                        clips.append(video)
                    elif check_path2.isOpened():
                        video = VideoFileClip(path2)
                        clips.append(video)
                    else:
                        not_found.append(sign)
                else:
                    not_found.append(sign)

            if not_found:
                ctypes.windll.user32.MessageBoxW(0, str(not_found) + " do not have corresponding signs yet!", "Sign Not Found", 1)

            final_clip = concatenate_videoclips(clips, method = "compose")
            final_clip.write_videofile("mergedtest.mp4")
            cap= cv2.VideoCapture('mergedtest.mp4')
            fps= int(cap.get(cv2.CAP_PROP_FPS))

            if cap.isOpened() == False:
                print("Error File Not Found")

            while cap.isOpened():
                ret,frame= cap.read()

                if ret == True:

                    time.sleep(1/fps)
                    cv2.imshow('frame', frame)

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                else:
                    break

            cap.release()
            cv2.destroyAllWindows()

        except Exception as e:
            print("Error line: " + str(e))
    
runRecognition()

