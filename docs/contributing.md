If you want to contribute, this is the usual deal: 

1. Start by [forking](https://guides.github.com/activities/forking/), then clone your fork
  ```bash
  git clone git@github.com:<YOUR_USERNAME>/pybibtex.git
  cd pybibtex
  ```
2. Then setup... And you are good to go :)
  ```bash
  python -m venv venv # a virtualenv is always a good idea
  source venv/bin/activate
  make init  # install what's needed for dev
  ```
3. You can also build the documentation with
  ```bash
  make doc
  ```
  And then visit [`site/index.html`](site/index.html).

Don't forget to work on a separate branch, and to run the linting and tests:

```bash
make lint  # flake8
make test  # unit tests
```

## Design rules

+ The code is written in Python 3, and follows the (in)famous [PEP-8](http://legacy.python.org/dev/peps/pep-0008/). You can check it by running ``make lint``, which launch the ``flake`` utility.
+ Codes and comments are written in english.
+ The code is documented using docstrings and [mkdocs](https://mkdocs.org/). 
  The docstrings must contain the basic description of the function, as well as a description of the parameters.
+ The code is tested. You can launch the test series by using ``make test``.
  Every functionality should be provided with at least one unit test.
+ The package is documented. You can generate this documentation by using ``make doc``. 
  Non-basic stuffs should be explained in this documentation. 
  Don't forget to cite some articles or website if needed.

## Workflow

Adapted from the (in)famous [Git flow](http://nvie.com/posts/a-successful-git-branching-model/).
This project is not large enough to have a `dev` branch, the tags should be sufficient.

+ Development is made in the ``master`` branch, which contains the production version.
+ Functionality are added through merge request (MR) in the ``master`` branch. Do not work in ``master`` directly, but create a new branch (``git checkout -b my_branch origin/master``).
+ Theses merge requests should be unitary, and include unit test(s) and documentation if needed. The test suite must succeed for the merge request to be accepted.
+ At some (random) points, a new version is created, with a tag of the form ``vX.Y.Z``.