# Live deployment

- Platform: InsForge Custom Compute (Fly.io-backed container)
- Project: 9b68328e-9517-4d47-815d-0b3454d8066a
- Service: studypath-mentor
- URL: https://studypath-mentor-9b68328e-9517-4d47-815d-0b3454d8066a.fly.dev
- Container port: 8501
- Memory: 512 MB
- Scaling: scale-to-zero (cold starts possible)
- Verification: public homepage returned HTTP 200; /_stcore/health returned ok.

Runtime uses Dockerfile and an allowlisted .dockerignore. Authentication files, session data and project credentials are not copied into the image. Streamlit CORS and XSRF protections are not disabled in the production command.

Progress is session-only and may reset on refresh, reconnect or container stop. This is a public demo, not an authenticated student-record system. Hosting usage may incur charges under your InsForge plan; check the dashboard.

To redeploy after authenticating and linking the project, install flyctl and run from this folder:

```bash
npx @insforge/cli compute deploy . --name studypath-mentor --port 8501 --memory 512 --scale-to-zero
```

Do not commit .insforge, authentication tokens, environment secrets or .streamlit/secrets.toml to a public repository.
