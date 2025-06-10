{
  description = "flake";
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  };
  outputs = { self, nixpkgs, ... }: let
    system = "x86_64-linux";
    pkgs = nixpkgs.legacyPackages.${system};
  in {
    devShells.${system}.default = pkgs.mkShell {
      buildInputs = [
        (pkgs.python3.withPackages(p: with p; [
          fastapi
          tkinter 
          requests
          sqlalchemy
          uvicorn
        ]))
      ];
    };
  };
}
