from Socket import dispatcher
from flask import Flask
import subprocess
from argparse import ArgumentParser
from multiprocessing import cpu_count
from flask_debugtoolbar import DebugToolbarExtension

HOST = 'localhost:9090'
PORT = 9090

if __name__ == '__main__':
    arg_parser = ArgumentParser()
    arg_parser.add_argument('-d', '--debug', action='store_true')
    args = arg_parser.parse_args()
    if args.debug:
        #app.run(debug=True)
        #print 'here'
        dispatcher.debug= True
        dispatcher.config['SECRET_KEY'] = 'hadjhkwh'
        #toolbar = DebugToolbarExtension()
        #toolbar.init_app(dispatcher)
        dispatcher.run(port=PORT)
    else:
        #print 'there'
        num_workers = cpu_count() * 2 + 1
        cmd = 'gunicorn -w %d -b %s -D server:app --log-level error --log-file fhir.log'% (num_workers, HOST)
        subprocess.call(cmd, shell=True)
