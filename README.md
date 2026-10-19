# Student Dashboard Android APK build files

Place these files at the root of your GitHub repository:

- `main.py`
- `student_data.json`
- `buildozer.spec`
- `.github/workflows/build.yml`

## Build

1. Commit and push the files to the `main` or `master` branch, or open GitHub Actions and run **Build Android APK** with **Run workflow**.
2. Open the completed workflow run.
3. Download the `student-dashboard-debug-apk` artifact.

This creates a **debug APK** for testing, not a Play Store release-signed APK.

## Important notes

- Keep the JSON filename exactly `student_data.json`, matching the filename used in `main.py`.
- Android app data is stored in the app's writable private data directory; it is not the same file as the original JSON in your GitHub repository.
- The app's current OTP flow prints the code to the terminal instead of sending an SMS. That flow will not work as a real SMS verification flow on a normal Android install.
- The workflow accepts Android SDK license prompts for the build environment. Only accept third-party licenses when you agree to their terms.
- A broken pipe from `yes` is handled without masking a non-zero Buildozer exit code. Network errors, incompatible dependencies, or actual compiler errors can still fail a build and must be fixed from the logs.
