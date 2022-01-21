Since most of the attendee's notes I have seen focus on summarizing
lecturers videos, here is a complete list of commands used to set-up
my test environment which might help preparing your own env from scratch.

I am using WSL2 (*Ubuntu-20.04*) on Windows 10 (*21H1*).

Prequesities
-----------------------
1. WSL2 activated, kernel up-to-date and operable distro
2. Update apt lists
   - `sudo apt update`
3. Install Python 3.9 (they use 3.8)
   - `sudo apt install software-properties-common`
   - `sudo add-apt-repository ppa:deadsnakes/ppa`
   - `sudo apt install python3.9 python3.9-dev python3.9-venv python3-testresources`
4. Update `pip wheel setuptools`
   - `python3.9 -m pip install --upgrade pip wheel setuptools`
5. Install Docker Engine
   - https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository
6. Add yourself to `docker` group
   - `sudo usermod -aG docker $USER`
   - *re-open WSL2 to apply changes*
7. Configure Docker
   - `sudo vim /etc/docker/daemon.json`
     - *{"hosts": ["unix:///var/run/docker.sock"]}*
9. Run Docker in background
   - `sudo dockerd > /dev/null 2>&1 &`

Before we start
----------------------
I am a big fan of clean, separated environments for each project so let's create a new one.

   - `python3.9 -m venv venvs/decamp`
   - `source venvs/decamp/bin/activate`
   - `python -m pip install --upgrade pip wheel setuptools`

Ready!
-----------------------