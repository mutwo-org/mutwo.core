with import <nixpkgs> {};
with pkgs.python3Packages;

let

  pythonRanges = pkgs.python39Packages.buildPythonPackage rec {
    name = "python-ranges";
    src = fetchFromGitHub {
      owner = "Superbird11";
      repo = "ranges";
      rev = "e285da71f3572e7d1c753d3bafd7d0fc07a70f69";
      sha256 = "sha256-JwF41ygY1w8v/ftzr4Ja0NelAx45t8oi84v3iXHt27o=";
    };
    doCheck = false;
  };

in

  buildPythonPackage rec {
    name = "mutwo.core";
    src = fetchFromGitHub {
      owner = "mutwo-org";
      repo = "mutwo.core";
      rev = "56218a3abd42e4ac93b6a31fc3db2ecfcdef73b1";
      sha256 = "sha256-odA2+pTtjRyRbyJDKfmFh+nzXJfrizWcHUClhpcYx2s=";
    };
    propagatedBuildInputs = [ 
      python39Packages.numpy
      python39Packages.scipy
      pythonRanges
    ];
  }
