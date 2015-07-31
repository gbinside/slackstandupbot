from slackstandupbot import dopost
import ConfigParser
import sys
import os

types = {
    'channels': ('channels.list', 'channels'),
    'users': ('users.list', 'members'),
}


def main(argv):
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    config = ConfigParser.ConfigParser()
    config.readfp(open('config.ini'))
    token = config.get('general', 'token')

    for what in argv[1:]:
        if what in types:
            cmd, key = types[what]
            for x in dopost(cmd, token)[key]:
                print "%s\t%s" % (x['id'], x['name'])

    if not argv[1:]:
        print """
USAGE :
    python list.py [users] [channels]"""

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
