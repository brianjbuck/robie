import sys

from robie.app import main

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        # https://github.com/jkbrzt/httpie/blob/master/httpie/__init__.py
        # http://www.tldp.org/LDP/abs/html/exitcodes.html
        sys.exit(130)
