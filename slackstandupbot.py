from time import sleep, strftime, time
from pprint import pprint, pformat
import ConfigParser
import threading
import urllib
import json
import sys
import os


def urlencode_utf8(params):
    if hasattr(params, 'items'):
        params = params.items()
    return '&'.join(
        (urllib.quote_plus(k.encode('utf8'), safe='/') + '=' +
         urllib.quote_plus(v.encode('utf8') if type(v) is not bool else str(v), safe='/')
         for k, v in params))


def dopost(action, _token=None, **params):
    if _token is None:
        _token = token
    params['token'] = _token
    eparams = urlencode_utf8(params)
    return json.loads(urllib.urlopen('https://slack.com/api/' + action, eparams).read())


def members():
    return dopost('users.list')['members']


def say(channel, text):
    ret = dopost('chat.postMessage', channel=channel, text=text, as_user=True)
    try:
        return ret['ts']
    except KeyError:
        pprint(ret)
        sys.exit()


def ask(channel, text, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    ts = say(channel, text)
    messages = []
    t0 = time()
    prelen = 0
    while t0 + timeout > time():
        messages = dopost('im.history', channel=channel, oldest=ts)['messages']
        if prelen != len(messages):
            t0 = time()
            prelen = len(messages)
        if messages and messages[0]['text'] == '.':
            break
    else:
        messages.insert(0, {'text': 'TIMEOUT'})
        say(channel, 'TIMEOUT')
    return map(lambda x: x['text'], messages[::-1])


def im_open(user):
    return dopost('im.open', user=user)['channel']['id']


def im_close(channel):
    return dopost('im.close', channel=channel)


def worker(member, questions, presentation, farewell):
    channel = im_open(member['id'])
    answers = []
    say(channel, presentation)
    for q in questions:
        answers.append((q, ask(channel, q)))
    say(channel, farewell)
    standup[member['id']] = [('name', member['name']), ('answers', answers)]
    im_close(channel)


def reformat(data):
    ret = []
    for k, v in data.items():
        user = dict(v)
        ret.append(user['name'] + ': ' + '#' * 60)
        for q, a in user['answers']:
            ret.append('-' * 2 + q)
            ret.extend([' ' * 4 + x for x in a])
    return '\n'.join(ret)


def read_config(f):
    global token, TIMEOUT
    config = ConfigParser.ConfigParser()
    config.readfp(open(f))
    token = config.get('general', 'token')
    threads = config.get('general', 'threads')
    report_channel = config.get('general', 'report_channel')
    TIMEOUT = int(config.get('general', 'timeout'))
    datefmt = config.get('messages', 'date_format')
    intro = config.get('messages', 'presentation')
    farewell = config.get('messages', 'farewell')
    report_channel_start = config.get('messages', 'report_channel_start')
    report_channel_stop = config.get('messages', 'report_channel_stop')
    questions = [x[1] for x in config.items('questions')]
    skip = [x[1] for x in config.items('skip')]
    return datefmt, farewell, intro, questions, report_channel, report_channel_start, report_channel_stop, skip, threads


def main(argv):
    global token, TIMEOUT, standup
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    dt_fmt, farewell, intro, questions, rep_chan, rep_chan_start, rep_chan_stop, skip, threads_limit = read_config(
        'config.ini')

    today = '[%s]' % strftime(dt_fmt)

    intro += today
    rep_chan_start += today

    say(rep_chan, rep_chan_start)

    standup = {}
    threads = []
    for member in members():
        if not member['is_bot'] and not member['deleted'] and member['id'] not in skip:
            t = threading.Thread(target=worker, args=(member, questions, intro, farewell))
            threads.append(t)

    # start only N thread at a time
    running = []
    ths = list(threads)  # copy
    done = False
    while not done:
        while len(running) < threads_limit and len(ths):
            # take one thread from threads and start it
            running.append(ths.pop(0))
            running[-1].start()
        running = [t for t in running if t.is_alive()]
        sleep(0.5)
        done = len(running) < 1

    [t.join() for t in threads]  # useless? used for double security

    say(rep_chan, '```\n' + reformat(standup) + '\n```')
    say(rep_chan, rep_chan_stop)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
