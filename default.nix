with import <nixpkgs> {};
with pkgs.python310Packages;

let

  python-ranges = pkgs.python310Packages.buildPythonPackage rec {
    name = "python-ranges";
    src = fetchFromGitHub {
      owner = "Superbird11";
      repo = "ranges";
      rev = "38ac789b61e1e33d1a8be999ca969f909bb652c0";
      sha256 = "sha256-oRQCtDBQnViNP6sJZU0NqFWkn2YpcIeGWmfx3Ne/n2c=";
    };
    # TypeError: calling <class 'ranges.RangeDict.RangeDict'> returned {}, not a test
    doCheck = false;
    checkInputs = [ python310Packages.pytest ];
  };

  quicktions = pkgs.python310Packages.buildPythonPackage rec {
    name = "quicktions";
    src = fetchPypi {
      pname = name;
      version = "1.10";
      sha256 = "sha256-Oy072x22dBvFHOHbmmWdkcUpdCC5GmIAnILJdKNlwO4=";
    };
    doCheck = true;
    propagatedBuildInputs = [
      python310Packages.cython
      python310Packages.codecov
    ];
  };

in

  buildPythonPackage rec {
    name = "mutwo.core";
    src = fetchFromGitHub {
      owner = "mutwo-org";
      repo = name;
      rev = "fa096398042201825ffa9bf96226f4ad9d778b7f";
      sha256 = "sha256-MFTIgS8JzZ6Pw3XXgIIj4oQYcvLkx0Ekb2NfVKAx9WI=";
    };
    checkInputs = [
      python310Packages.pytest
    ];
    propagatedBuildInputs = [ 
      python310Packages.numpy
      python310Packages.scipy
      python-ranges
      quicktions
    ];
    checkPhase = ''
      runHook preCheck
      pytest
      runHook postCheck
    '';
    doCheck = true;
  }
