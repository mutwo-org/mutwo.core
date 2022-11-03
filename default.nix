with import <nixpkgs> {};
with pkgs.python3Packages;

let

  python-ranges = pkgs.python39Packages.buildPythonPackage rec {
    name = "python-ranges";
    src = fetchFromGitHub {
      owner = "Superbird11";
      repo = "ranges";
      rev = "38ac789b61e1e33d1a8be999ca969f909bb652c0";
      sha256 = "sha256-oRQCtDBQnViNP6sJZU0NqFWkn2YpcIeGWmfx3Ne/n2c=";
    };
    # TypeError: calling <class 'ranges.RangeDict.RangeDict'> returned {}, not a test
    doCheck = false;
    propagatedBuildInputs = [ python39Packages.pytest ];
  };

in

  buildPythonPackage rec {
    name = "mutwo.core";
    src = fetchFromGitHub {
      owner = "mutwo-org";
      repo = name;
      rev = "a1fc891feb02812c413a7fb1bbcaaa8fcb6b6011";
      sha256 = "sha256-Ucaiw0sZJjungzvM3Q61npT6WSGroudhiCfzoWbse5g=";
    };
    propagatedBuildInputs = [ 
      python39Packages.numpy
      python39Packages.scipy
      python-ranges
    ];
    doCheck = true;
  }
