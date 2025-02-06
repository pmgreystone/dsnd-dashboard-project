from pathlib import Path
from setuptools import setup, find_packages

cwd = Path(__file__).resolve().parent
requirements = (cwd / 'employee_events' /
                'requirements.txt').read_text().split('\n')

setup_args = dict(
    name='employee_events',
    version='2.3',
    description='Udacity Sample Employee Events',
    packages=find_packages(),
    package_data={'': ['employee_events.db', 'requirements.txt']},
    install_requires=requirements,
    python_requires='>=3.1'
)

if __name__ == "__main__":
    setup(**setup_args)

# pyparsing pluggy h11 sniffio anyio apsw apswutils beautifulsoup4 certifi fastcore fastlite fonttools itsdangerous kiwisolver scikit-learn websockets pytest scipy matplotlib python-fasthtml setuptools
# traitlets decorator pexpect prompt_toolkit jedi parso

'''
jupyter

Installing collected packages: webencodings, fastjsonschema, widgetsnbextension, websocket-client, webcolors, urllib3, uri-template, types-python-dateutil, traitlets, tornado, tinycss2, send2trash, rpds-py, rfc3986-validator, rfc3339-validator, pyzmq, python-json-logger, pycparser, psutil, prompt-toolkit, prometheus-client, platformdirs, pexpect, parso, pandocfilters, overrides, nest-asyncio, mistune, markupsafe, jupyterlab-widgets, jupyterlab-pygments, jsonpointer, json5, fqdn, defusedxml, decorator, debugpy, charset-normalizer, bleach, babel, attrs, async-lru, appnope, terminado, requests, referencing, jupyter-core, jinja2, jedi, comm, cffi, arrow, jupyter-server-terminals, jupyter-client, jsonschema-specifications, isoduration, ipython, argon2-cffi-bindings, jsonschema, ipywidgets, ipykernel, argon2-cffi, nbformat, jupyter-console, nbclient, jupyter-events, nbconvert, jupyter-server, notebook-shim, jupyterlab-server, jupyter-lsp, jupyterlab, notebook, jupyter
'''
