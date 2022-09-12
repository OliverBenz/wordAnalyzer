from pydub.silence import split_on_silence
import speech_recognition as sr 
from pydub import AudioSegment
import moviepy.editor as me
import os


def mp4_to_mp3(filename):
    """ filename is the full path to file without file extension. """
    if os.path.exists(filename + ".mp3"):
        return

    video = me.VideoFileClip(filename + ".mp4")
    video.audio.write_audiofile(filename + ".mp3")


def get_audio_transcription(path, lang):
    """ Get the audio transcript of a mp3 file under the path: 'path' with a specific language 'lang'. """
    sound = AudioSegment.from_mp3(path)

    r = sr.Recognizer()

    chunks = split_on_silence(sound,
        min_silence_len = 2000,
        silence_thresh = sound.dBFS-14,
        keep_silence=500,
    )
    
    folder_name = "audio-chunks"
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    
    # TODO: Immediately remove audio chunks when not needed anymore
    whole_text = ""
    for i, audio_chunk in enumerate(chunks, start=1):
        chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")
    
        with sr.AudioFile(chunk_filename) as source:
            audio_listened = r.record(source)
            try:
                text = r.recognize_google(audio_listened, language=lang)
            except sr.UnknownValueError as e:
                print("Error:", str(e))
            else:
                text = f"{text.capitalize()}. "
                print(chunk_filename, ":", text)
                whole_text += text
    
    
    # Write whole_text to output file
    outFilename = "output/data.txt"
    
    outFile = open(outFilename, "w") 
    outFile.write(whole_text)
    outFile.close()

    return outFilename


def analyze(outfile, word):
    with open('output/data.txt') as f:
        lines = f.readlines()

        counter = 0
        for line in lines:
            words = line.split(" ")
            for _ in (w for w in words if w.lower() == word):
                counter += 1

    print(counter)


if __name__ == "__main__":
    # Parameters to update:
    inFile = "input/data"  # Input mp4 file path without the file extension
    language = "de-DE"     # Language of the mp4 file
    word = "exampleWord"   # Word to find the usage count of

    # Convert mp4 to mp3 file
    mp4_to_mp3(inFile)

    # Get transcript for mp3 file in a specific language
    outFile = get_audio_transcription(inFile + ".mp3", language)

    # Find number of 'word' in the transcript
    analyze(outFile, word)
    