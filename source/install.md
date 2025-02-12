# Installation

Mercurial is written in Python, C and Rust with platform independence in mind. As a
result, Mercurial is available on [Microsoft Windows], [GNU/Linux], [macOS],
[Solaris 11 Express] and others. You can either download a binary package for the system
of your choice or build from [source](https://www.mercurial-scm.org/release).

For those looking for the utmost performance, a growing part of Mercurial is being
written in Rust. For more information, see [](./help/topics/rust.rst).

Windows users are likely to enjoy the [TortoiseHg] GUI the most, which integrates
Mercurial directly into File Explorer.

Packages for common Linux and BSD distributions can be installed from the system specific
repositories:

`````{tab-set}
````{tab-item} Debian/Ubuntu
```sh
apt install mercurial
```
````
````{tab-item} Fedora
```sh
dnf install mercurial
```
````
````{tab-item} Arch Linux
```sh
pacman -S mercurial
```
````
````{tab-item} Gentoo
```sh
emerge mercurial
```
````
````{tab-item} macOS (Homebrew)
```sh
brew install mercurial
```
````
````{tab-item} FreeBSD
```sh
cd /usr/ports/devel/mercurial
make install
```
````
`````

Mercurial is available on PyPI as wheels and sdist, so one can install the last stable
version with any PyPI front-ends (like [UV], [pipx], [pip], ...):

`````{tab-set}
````{tab-item} UV
```sh
uv tool install mercurial
```
````
````{tab-item} pipx
```sh
pipx install mercurial
```
````
````{tab-item} pip
```sh
pip install mercurial
```
````
`````

Finally, the Mercurial [conda-forge] package can be installed as a global tool with
[Miniforge] or [Pixi]:

`````{tab-set}
````{tab-item} Miniforge
```sh
conda activate base
pip install conda-app
conda-app install mercurial
```
````
````{tab-item} Pixi
```sh
pixi global install mercurial
```
````
`````

[conda-forge]: https://conda-forge.org/
[gnu/linux]: http://kernel.org/
[macos]: http://www.apple.com/
[microsoft windows]: http://www.microsoft.com/windows
[miniforge]: https://github.com/conda-forge/miniforge
[pip]: https://pip.pypa.io
[pipx]: https://pipx.pypa.io
[pixi]: https://pixi.sh
[solaris 11 express]: http://oracle.com/solaris
[tortoisehg]: http://tortoisehg.org/
[uv]: https://docs.astral.sh/uv
