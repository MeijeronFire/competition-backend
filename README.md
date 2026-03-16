# competition-game-backend (better name TBA)
## Installing

install and run by running the following commands:
```sh
git clone <this repo>
cd <project name>
python -m venv .venv
source .venv/bin/activate
pip install .
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes # parameters do NOT matter. Can be random
./run.sh
```

## License

This project is licensed under the GNU General Public License v3.0
or any later version. See the LICENSE file for details.