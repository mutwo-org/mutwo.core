let
  sourcesTarball = fetchTarball "https://github.com/mutwo-org/mutwo-nix/archive/refs/heads/main.tar.gz";
  mutwo-core = import (sourcesTarball + "/mutwo.core/default.nix") {};
  mutwo-core-local = mutwo-core.overrideAttrs (
    finalAttrs: previousAttrs: {
       src = ./.;
    }
  );
in
  mutwo-core-local

