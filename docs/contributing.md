# Install and contribute

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
  make install # install what's needed for dev
  ```

## Tips to contribute

+ A good place to start is the [list of issues](https://github.com/pierre-24/pybibtex/issues).
  In fact, it is easier if you start by filling an issue, and if you want to work on it, says so there, so that everyone knows that the issue is handled.

+ Don't forget to work on a separate branch: you should base your branch on `master`, not work in it directly:

    ```bash
    git checkout -b new_branch origin/master
    ```
 
+ Don't forget to regularly run the linting and tests:

    ```bash
    make lint
    make test
    ```
    
    Indeed, the code follows the [PEP-8 style recommendations](http://legacy.python.org/dev/peps/pep-0008/), checked by [`flake8`](https://flake8.pycqa.org/en/latest/), for the python part and use [`jshint`](https://jshint.com/) for the JS part.
    Having an extensive test suite is also a good idea to prevent regressions.

+ If you want to see and edit the doc, you can run the `mkdocs` webserver:

    ```bash
    make doc-serve
    ```

+ Pull requests should be unitary, and include unit test(s) and documentation if needed. 
  The test suite and lint must succeed for the merge request to be accepted.