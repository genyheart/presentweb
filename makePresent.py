#!/usr/bin/python3

__author__ = 'ligonliu'

import re,subprocess,os,sys

import binascii

from tempfile import mkstemp

def _GetScriptPath():
    return os.path.abspath(os.path.dirname(sys.argv[0]))


def _GetTempFileName(suffix=''):
    fd, name = mkstemp(suffix)
    os.close(fd)
    return name


def SplitText(text=''):
    # first, look for more than 4 continuous spaces by doing a re pattern matching
    pattern = r' {3,}'

    pause_locations = [(m.start(0), m.end(0)) for m in re.finditer(pattern, text)]
    pause_milliseconds = [500*(y-x-2) for (x, y) in pause_locations]
    texts_to_read = re.split(pattern, text)

    assert len(texts_to_read) == 1 + len(pause_milliseconds)
    return texts_to_read, pause_milliseconds


def SegmentToWav(segment = ''):
    # write to a temporary txt file
    tempTxt = _GetTempFileName(suffix='.txt')
    fp = open(tempTxt, 'w')
    fp.write(segment)
    fp.close()

    tempWav = _GetTempFileName(suffix='.ogg')
    cmdTTS = 'text2wave {0} -o {1} -F 44100'.format(tempTxt, tempWav)
    subprocess.call(cmdTTS, shell=True)
    os.remove(tempTxt)

    return tempWav




_Silent500msWav = _GetScriptPath() + os.sep + 'silent500ms.ogg'


if not os.path.isfile(_Silent500msWav):
    gen_Silent500msWav_cmd = 'rec -r 44100 -b 16 -c 1 silent500ms.ogg trim 0 0.5'
    subprocess.call(gen_Silent500msWav_cmd, shell=True)
    _Silent500msWav = 'silent500ms.ogg'


def CombineWavFiles(waveFiles=[], outputWav=None):

    if outputWav is None:
        outputWav = _GetTempFileName(suffix='.ogg')

    # implement here: use sox to combine audio files

    sox_cmd = 'sox '
    for waveFile in waveFiles:
        sox_cmd += waveFile + ' '

    sox_cmd += outputWav
    subprocess.call(sox_cmd, shell=True)
    return outputWav



def TextToSpeech(text = '', outputWav = None):

    if outputWav is None:
        outputWav = _GetTempFileName(suffix='.ogg')

    texts, pauses_ms = SplitText(text)
    textWavFiles = [SegmentToWav(text) for text in texts]

    waveFiles = []

    pauses_ms = [int(t/500) for t in pauses_ms]

    pauses_ms.append(0)

    i = 0

    for textWavFile in textWavFiles:
        waveFiles.append(textWavFile)
        for j in range(0, pauses_ms[i]):
            waveFiles.append(_Silent500msWav)
        i += 1

    # print(waveFiles)

    outputWav = CombineWavFiles(waveFiles, outputWav)

    # delete waveFiles if they are not _Silent500msWav
    for waveFile in waveFiles:
        if waveFile != _Silent500msWav:
            os.remove(waveFile)

    return outputWav





def GetSubtitles(slides=[]):
    # each should be a .srt file
    # use time based animation
    # a function that look for all .srt files, match them with names





def GetSlidesInDir(dir=None):
    # look for file in dir or by default, the current working directory
    # matching pattern \d+.[jpg|jpeg|png]

    if dir is None:
        dir = os.getcwdu()

    files = os.listdir(dir)

    files = [dir + os.sep + file for file in files if re.match(r'\d+\.(jpeg|png|jpg)', file, re.IGNORECASE)]

    return files



def GetTextForSlide(slideImgName):

    print("GetTextForSlide({0})".format(slideImgName))

    assert isinstance(slideImgName, str)
    slideImgName_split = slideImgName.split('.')
    suffix = slideImgName_split[len(slideImgName_split)-1]
    txtFileName = slideImgName[0:len(slideImgName)-len(suffix)-1] + '.txt'

    try:
        fp = open(txtFileName, 'r')
    except FileNotFoundError:
        return ''

    text = fp.read()
    return text



def SubTitleToCanvasHTML(text='', audiofile = '', sectionId=0):
    # use time based changing of attributes.
    # algorithm to compute time:
    # we have word per minute in festival's default
    # total time = length of audio
    # assume each word use portional time as its length
    # emit word to a screen strip, until overflow
    # and start a new screen

    queryDurationCMD = 'soxi -D {0}'.format(audiofile)

    length_sec = float(subprocess.check_output(queryDurationCMD, shell=True))

    textsplit = text.split()

    max_chars_per_screen = 80 # like unix standard terminal?



    # http://www.w3schools.com/tags/canvas_filltext.asp

    canvas_html_string = '<canvas id=canvas_{0}>\n'.format(sectionId)
    canvas_html_string += '</canvas>\n'

    canvas_html_string += '<script>\n'

    # set timeout for refresh
    canvas_html_string += 'settimeout(refreshSubTitle, 500)\n'  # refresh subtitle every 500 milliseconds

    canvas_html_string += 'var c=document.getElementById("{0}")\n'.format("canvas_{0}".format(sectionId))
    canvas_html_string += 'ctx.font = "60px SimSun"\n'
    canvas_html_string += 'ctx.font = 10px\n'

    canvas_html_string += '' # this line should put text and start time for each segment of text

    canvas_html_string += 'ctx.fillText("{0}", 0, 7)'.format()








from shutil import copy2
import base64


def GetTitle(folder):
    # open title.txt
    try:
        fp = open(folder+os.sep + 'title.txt', 'r')
    except:
        return None

    if fp is None:
        return None

    title = fp.readline()
    fp.close()
    return title


def Slides2HTML5(slides, audios, title="Multimedia Presentation by Presenter", outHTML5FileName=None):
    # HTML5 slide show, with scheduled audio output(player)

    assert isinstance(slides, list)
    assert outHTML5FileName is None or isinstance(outHTML5FileName, str)


    if outHTML5FileName is None:
        outHTML5FileName = _GetTempFileName(suffix='.html')

    # copy template.html to it:
    copy2(_GetScriptPath() + os.sep + 'template1.html', outHTML5FileName)

    # add slides:
    # each slide is a filename ending in jpg or png
    # we base64 encode them

    fp = open(outHTML5FileName, 'a+')

    fp.write('\n<title>{0}</title>\n'.format(title))

    # fp.write(r'<img src="data:image/')

    # tell if they are jpg or png based on suffix
    for i in range(0, len(slides)):

        imagefilename = slides[i]
        oggfilename = audios[i]

        assert isinstance(imagefilename,str)
        filenamesplit = imagefilename.split('.')

        filename_no_suffix = imagefilename[0:len(imagefilename)-len(filenamesplit[len(filenamesplit)-1])]

        fp.write('<section>\n')

        fp.write('    <audio autoplay src="data:audio/ogg;base64,')

        temptxt = _GetTempFileName('.txt')
        fp_temp = open(temptxt, 'wb')

        # .format(filename_no_suffix+'.ogg'))
        fp_audio = open(oggfilename, 'rb')

        base64.encode(fp_audio, fp_temp)

        fp_audio.close()
        fp_temp.close()

        # print("count lines of audio base64:")
        # subprocess.call('wc -l {0}'.format(temptxt), shell=True)

        fp_temp = open(temptxt, 'r')

        while True:
            line = fp_temp.readline()

            if len(line)==0:
                break
            elif len(line)==1:
                continue

            fp.write(line.replace('\n', ''))

        fp_temp.close()

        fp.write('">\n')
        fp.write('    </audio>\n')

        # the img files
        fp.write('    <figure>\n        <img src="data:image/')

        if filenamesplit[len(filenamesplit)-1].lower() in ['jpg', 'jpeg', 'jpe']:
            fp.write('jpg')
        elif filenamesplit[len(filenamesplit)-1].lower() in ['png']:
            fp.write('png')

        fp.write(';base64,')

        fp_image = open(imagefilename, 'rb')

        fp_temp = open(temptxt,'wb')

        base64.encode(fp_image, fp_temp)

        fp_image.close()
        fp_temp.close()

        fp_temp =open(temptxt,'r')

        while True:
            line = fp_temp.readline()

            if len(line)==0:
                break
            elif len(line)==1:
                continue

            fp.write(line.replace('\n', ''))

        fp.write('">\n')

        fp.write('        </img>\n')

        fp_temp.close()

        os.remove(temptxt)

        fp.write('    </figure>')

        fp.write('</section>\n')


    fp2 = open('template2.html', 'r')

    fp.write(fp2.read())

    fp2.close()
    fp.close()


if __name__ == "__main__":
    # get slides at argv[1]
    # output to argv[2]

    isDebug = False

    if len(sys.argv)<3:
        sys.stderr.write('Usage: {0} inputFolder outputHTMLFile [--DEBUG]\n'.format(sys.argv[0]))
        exit(0)

    if len(sys.argv)==4:
        if sys.argv[3] == '--DEBUG':
            isDebug = True

    slides = GetSlidesInDir(sys.argv[1])

    texts = [GetTextForSlide(slide) for slide in slides]

    speechOggs = [TextToSpeech(text) for text in texts]

    title = GetTitle(folder=sys.argv[1])

    if isDebug:

        sys.stderr.write(_Silent500msWav + '\n')

        sys.stderr.write(str(slides) + '\n')
        sys.stderr.write(str(texts) + '\n')
        sys.stderr.write(str(speechOggs) + '\n')
        sys.stderr.write('Title: ' + str(title) + '\n')

    Slides2HTML5(slides, speechOggs, title, sys.argv[2])

    # remove texts and speechOggs if !isDebug
    if not isDebug:
        for f in texts:
            os.remove(f)
        for f in speechOggs:
            os.remove(f)

    if _Silent500msWav == 'silent500ms.ogg':
        os.remove(_Silent500msWav)
    exit(0)
