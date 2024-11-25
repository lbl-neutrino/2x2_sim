# corsika2RooTracker

A tool for converting the output of the [CORSIKA](https://www.iap.kit.edu/corsika/index.php) cosmic ray generator to a RooTracker-like format, used as input for [edep-sim](https://github.com/ClarkMcGrew/edep-sim).

## Requirements

- C++ compiler
- ROOT

## Compilation

Compile with

```bash
make
```

## Usage

Run with

```bash
./corsikaConverter DAT000001
```

where `DAT000001` is the CORSIKA binary file. The tool will create a file named `DAT000001.root`.
