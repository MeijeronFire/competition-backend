# competition-game-backend (better name TBA)
## Installing

Install and run by running the following commands:
```sh
$ git clone <this repo>
$ cd <project name>
$ uv sync
source .venv/bin/activate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes # parameters do NOT matter. Can be random
./run.sh
```

For proper rendering of the website, you either need to change [base.html](templates/base.html) to request the bootstrap files from the CDN, or you need to manually place them like: `static/bootstrap/{bootstrap.js,bootstrap.css}`.

## Constraints and limitations
There is *no proper auth layer included*. This program is meant to be integrated in larger, already existing systems, where there are existing databases for users and such. As a default, for testing and development, the auth functions just read [users.csv](users.csv), which should obviously never be done in any serious system.

## Documentation
The current documentation is a bit lacking, but can be found in [docs/](docs/). Feel free to raise any issue or discussion for further explanation (or better yet, write your own and send a pull request).

## License

This project is licensed under the GNU General Public License v3.0
or any later version. See the LICENSE file for details.