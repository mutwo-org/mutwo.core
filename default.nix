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
    doCheck = false;
  };

in

  buildPythonPackage rec {
    name = "mutwo.core";
    src = fetchFromGitHub {
      owner = "mutwo-org";
      repo = name;
      rev = "337cfa0c42cfa3a0974731008385a3264942e136";
      sha256 = "sha256-2fc7IMLyHwIQMOsG5W4oRbAN4+l4LFP7mhkNP5+VO+M=";
    };
    propagatedBuildInputs = [ 
      python39Packages.numpy
      python39Packages.scipy
      python-ranges
    ];
    doCheck = true;
  }
