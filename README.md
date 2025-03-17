# Plate Finder

Uses pretrained model to display license plates extracted from images.

Development notes: [DEVLOG.md](DEVLOG.md)

## Architecture

- Vite + React + TypeScript frontend
- FastAPI backend using a pretrained YOLO-based model.

## Development

This devcontainer has the github CLI and `act`, a local Github actions runner.

- Github authentication: To use `act`, you need to authenticate with Github. Run:
  ```bash
  gh auth login -s repo,gist,read:org,write:packages,read:packages,delete:packages
  ```
  The package permissions are needed for `act` to write to the Github package registry.
  
  If you want to run just a single action, you can use the `--job` flag:
   ```bash
   act --job build-and-push
   ```
- Host mounting: the host's Docker socket and `~/.kube` directory are mounted into the container workspace.