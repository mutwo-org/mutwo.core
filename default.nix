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
      version = "1.13";
      sha256 = "sha256-HzmMN1sAUjsSgy7vNvX/hq49LZmSnTQYbamjRoXeaL0=";
    };
    doCheck = true;
    propagatedBuildInputs = [
      python310Packages.cython_3
      python310Packages.codecov
    ];
  };

in

  buildPythonPackage rec {
    name = "mutwo.core";
    src = fetchFromGitHub {
      owner = "mutwo-org";
      repo = name;
      rev = "6539e7c7a9ec83128a9e9819524d6cbee7e90e76";
      sha256 = "sha256-aQtZZJf/TbjqnYRU9dY8+BPRF7jJ77aixX/c7/CnCFs=";
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
