<!-- ABOUT THE PROJECT -->
## About The Project

**Interactive web application to use this tool**: https://malcolmjones.pythonanywhere.com/

**Purpose**: This tool removes unused items from a `.bib` file.

**Requirement**: You have a `.bbl` file containing only used entries (e.g. automatically produced by [BibTeX](https://www.bibtex.org/Using/))

**More precisely**: Given `.bib` and `.bbl` files, this tool returns a reduced version of the `.bib`, the _yescite_, containing entries from `.bib` only if they occur in the `.bbl`.

**Notes**:
- The _yescite_ (reduced `.bib` file) preserves the entries of the `.bib` file that it keeps. i.e. is doesn't tamper with the entries themselves (unless they are unused in which case they are completely deleted). This is advantageous compared to bibliography managers that modify your entries.
- The `.bbl` file is hidden for some editors. For example, in Overleaf, click "Logs and output files", scroll down, click "Other logs and files", click to download "output.bbl". If there is no `.bbl` file, try recompiling and checking you are using BibTeX.

**Motivation**: The `.bib` file for a project had become very large over time. I no longer cited many entries. Using `\nocite{*}` would show which entries I no longer cited, but there would still have been a lot of manual labour looking them up in the `.bib` and deleting them. Hence, _yescite_ was intended to automatically find which entries I _did_ cite, instead of those I did not.

<!-- GETTING STARTED -->
## Installation

Check out the [web application](https://malcolmjones.pythonanywhere.com/) if you just want to copy-paste. 

If you prefer to run the script locally:

1. Clone the repo
   ```sh
   git clone https://github.com/malcolm-jones/yescite.git
   ```
2. Install requirements
   ```sh
   pip install -r requirements
   ```

<!-- USAGE EXAMPLES -->
## Usage

To check you are set up, run:
```
from yescite import yescite
yescite()
```
which should write the _yescite_ to a new file `output/yescite.bib`.

If you have your own files saved as `my.bbl` and `my.bib`, then run:
```
from yescite import yescite
yescite(path_bbl="my.bbl", path_bib="my.bib")
```

<!-- CONTRIBUTING -->
## Contributing

Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<!-- CONTACT -->
## Contact

Malcolm Jones - [malcolmjones.me](https://malcolmjones.me) - hello@malcolmjones.me

yescite on GitHub: [https://github.com/malcolm-jones/yescite](https://github.com/malcolm-jones/yescite)

<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [BibTeX](https://www.bibtex.org/Using/) (for automatically producing the `.bbl` without which this project would be pointless)
* Othneil Drew's [README template](https://github.com/othneildrew/Best-README-Template/tree/master)
