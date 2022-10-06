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
      rev = "9accb5f03d0155a4872cb429111b7d6c5a47ce28";
      sha256 = "sha256-cr30PxPtePZCwDYsfxM7l+M5fDNrxqh8OybLiHz+Ip4=";
    };
    propagatedBuildInputs = [ 
      python39Packages.numpy
      python39Packages.scipy
      python-ranges
    ];
    doCheck = true;
  }
