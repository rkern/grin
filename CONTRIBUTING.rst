How to contribute:

- Clone the repository
- Create a virtualenv
- Install the project in dev mode using ``python setup.py develop``
- Install the test runner: ``pip install nose``
- Run the tests: ``nosetest tests/*``
- Check that tests all pass. They won't pass on an FAT/NTFS partition,
  use WSL if you are on Windows.
- Edit the code, add some test.
- Commit and make a PR.
