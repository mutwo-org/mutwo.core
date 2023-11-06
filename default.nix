let
  sourcesTarball = fetchTarball "https://github.com/mutwo-org/mutwo-nix/archive/refs/heads/main.tar.gz";
  sources = import (sourcesTarball + "/nix/sources.nix");
  pkgs = import sources.nixpkgs {};
  python-ranges = import (sourcesTarball + "/python-ranges/default.nix") {};
  mutwo-core = import (sourcesTarball + "/mutwo.core/default.nix") {};
  mutwo-core-local = mutwo-core.overrideAttrs (
    finalAttrs: previousAttrs: {
       src = ./.;
      propagatedBuildInputs = [ 
      pkgs.python310Packages.numpy
      pkgs.python310Packages.scipy
      python-ranges
      pkgs.python310Packages.sympy
    ];
    }
  );
in
  mutwo-core-local

