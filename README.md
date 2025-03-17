# Plate Finder

Use a pretrained model to display license plates extracted from images.

Demo: <https://better.platefinder.space>

Development notes: [DEVLOG.md](DEVLOG.md)

## Architecture

- Vite + React + TypeScript frontend
- FastAPI backend using [a pretrained YOLO-based model][openimagemodels] in a Docker container

## Development

This repo includes a [devcontainer] that has the github CLI and `act`, a local Github actions runner.

- Github authentication: To use `act`, you need to authenticate with Github. Run:
  ```bash
  gh auth login -s repo,gist,read:org,write:packages,read:packages,delete:packages
  ```
  The package permissions are needed for `act` to write to the Github package registry.
  
  If you want to run just a single action, you can use the `--job` flag:
   ```bash
   act --job build-and-push
   ```
- Host mounting: the host's Docker socket (assuming MacOS and Linux) is mounted into the container workspace.

You'll want to run both the frontend and api to test things locally:
```bash
cd api/src && uv run python3.12 -m uvicorn main:app --port 8000
```
```bash
cd web && pnpm dev
```

[openimagemodels]: https://github.com/ankandrew/open-image-models
[devcontainer]: https://code.visualstudio.com/docs/devcontainers/containers#_quick-start-open-an-existing-folder-in-a-container